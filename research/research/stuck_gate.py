"""Protocol E7 gate: do keyword signals from comments and links add to the risk score for telling a stuck issue from a
fine one? Locked in documents/Protocol_stuck_E7_gate.md. No LLM."""
import glob
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

OUT = Path(os.environ.get('E7_OUT', 'artifacts/stuck_e7_gate'))
PROTOCOL = Path('documents/Protocol_stuck_E7_gate.md')
SEED, MIN_ROWS, SILENT_DAYS = 20261105, 30, 3
KEYWORDS = {
    'waiting': r'\b(waiting|wait for|pending|on hold)\b',
    'blocked': r'\b(blocked|blockers?|depends on|dependency|dependencies)\b',
    'review': r'\b(review|reviewing|reviewed|pull request|pr|merged)\b',
    'question': r'\?|\b(how|why|can you)\b',
}
PATTERNS = {k: re.compile(v, re.IGNORECASE) for k, v in KEYWORDS.items()}
FEATURES = (['has_comment', 'n_comments', 'days_since_last_comment', 'has_block_link']
            + [f'{w}_{k}' for k in KEYWORDS for w in ('last', 'any')])
SQL_COMMENTS = """select c.issue_id, c.creation_date, c.comment_text from tawos_raw.comment c
join pairs p on p.issue_id = c.issue_id and c.creation_date <= p.at"""


def comment_features(comments, at, has_block_link):
    """comments: [(creation_date, text)]. Only comments at or before `at` are seen."""
    seen = sorted((d, t or '') for d, t in comments if d <= at)
    f = dict(has_comment=int(bool(seen)), n_comments=len(seen), has_block_link=int(has_block_link),
             days_since_last_comment=(at - seen[-1][0]).total_seconds() / 86400 if seen else np.nan)
    for k, pattern in PATTERNS.items():
        f[f'last_{k}'] = int(bool(seen) and pattern.search(seen[-1][1]) is not None)
        f[f'any_{k}'] = int(any(pattern.search(t) for _, t in seen))
    return f


def _fit_auc(train, test, cols):
    model = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=1000))
    model.fit(train[cols].fillna(0), train.y)
    return roc_auc_score(test.y, model.predict_proba(test[cols].fillna(0))[:, 1])


def loo_auc_delta(df, feats):
    """Leave-one-project-out: AUC with the features minus AUC of the score alone, bootstrap CI over projects."""
    d = df.assign(logit_p=np.log(df.p.clip(1e-6, 1 - 1e-6) / (1 - df.p.clip(1e-6, 1 - 1e-6))))
    rows = []
    for project, test in d.groupby('project'):
        if len(test) < MIN_ROWS or test.y.nunique() < 2:
            continue
        train = d[d.project != project]
        base, full = _fit_auc(train, test, ['logit_p']), _fit_auc(train, test, ['logit_p'] + list(feats))
        rows.append(dict(project=project, n=len(test), auc_base=base, auc_full=full, delta=full - base))
    per = pd.DataFrame(rows)
    rng = np.random.default_rng(SEED)
    est = np.array([rng.choice(per.delta.to_numpy(), len(per)).mean() for _ in range(2000)])
    return dict(n_projects=len(per), delta=float(per.delta.mean()), ci_low=float(np.quantile(est, .025)),
                ci_high=float(np.quantile(est, .975)), projects_won=int((per.delta > 0).sum()),
                auc_base=float(per.auc_base.mean()), auc_full=float(per.auc_full.mean()),
                per_project=per.to_dict('records'))


def build_table():
    import psycopg
    preds = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(
        'artifacts/_archive_v2_momentum/predictions/cross_project__*__0.5__dynamic_catboost.parquet'))])
    snap = pd.read_parquet('data/processed/snapshots.parquet')
    snap = snap[snap.landmark == 0.5][['sprint_id', 'issue_id', 'dynamic_inactive_days', 'dynamic_status']]
    d = preds.merge(snap, on=['sprint_id', 'issue_id'], how='left', validate='one_to_one')
    d = d[(d.dynamic_is_done == 0) & (d.dynamic_inactive_days >= SILENT_DAYS)].reset_index(drop=True)
    d['at'] = pd.to_datetime(d.prediction_at, utc=True)
    pairs = d[['issue_id', 'at']].drop_duplicates()
    with psycopg.connect(os.environ.get('RESEARCH_DATABASE_URL',
                                        'postgresql://tawos:tawos_local_dev@localhost:15990/tawos')) as con:
        with con.cursor() as cur:
            cur.execute('create temp table pairs(issue_id bigint, at timestamptz)')
            with cur.copy('copy pairs from stdin') as cp:
                for r in pairs.itertuples(index=False):
                    cp.write_row((int(r.issue_id), r.at.to_pydatetime()))
            cur.execute(SQL_COMMENTS)
            by_issue = {}
            for issue_id, at, text in cur:
                by_issue.setdefault(issue_id, []).append((pd.Timestamp(at), text))
            cur.execute("select distinct issue_id from tawos_raw.issue_link where issue_id = any(%s) and "
                        "name in ('Blocks','Blockers','Depends','Dependency')", (pairs.issue_id.astype(int).tolist(),))
            linked = {r[0] for r in cur}
    feats = [comment_features(by_issue.get(int(r.issue_id), []), r.at, int(r.issue_id) in linked)
             for r in d.itertuples()]
    return pd.concat([d, pd.DataFrame(feats)], axis=1)


def main():
    if OUT.exists():
        raise SystemExit(f'{OUT} exists; protocol E7 results are not overwritten')
    d = build_table()
    summary = dict(rows=len(d), projects=int(d.project.nunique()), positive_rate=float(d.y.mean()),
                   with_comment=float(d.has_comment.mean()), with_block_link=float(d.has_block_link.mean()),
                   gate=loo_auc_delta(d, FEATURES),
                   secondary_closed_only=loo_auc_delta(d.assign(y=d.y_closed_only.astype(int)), FEATURES))
    full = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=1000))
    cols = ['logit_p'] + FEATURES
    d['logit_p'] = np.log(d.p.clip(1e-6, 1 - 1e-6) / (1 - d.p.clip(1e-6, 1 - 1e-6)))
    full.fit(d[cols].fillna(0), d.y)
    summary['coefficients'] = dict(zip(cols, map(float, full[-1].coef_[0])))
    OUT.mkdir(parents=True)
    d.drop(columns=['at']).to_csv(OUT / 'table.csv', index=False)
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    (OUT / 'manifest.json').write_text(json.dumps(dict(
        run_at=datetime.now(timezone.utc).isoformat(), protocol_sha256=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), seed=SEED, silent_days=SILENT_DAYS,
        min_rows=MIN_ROWS), indent=2), encoding='utf-8')
    g = summary['gate']
    print(json.dumps({k: summary[k] for k in ('rows', 'projects', 'positive_rate', 'with_comment', 'with_block_link')}, indent=2))
    print('GATE delta AUC', round(g['delta'], 4), [round(g['ci_low'], 4), round(g['ci_high'], 4)], 'projects',
          g['n_projects'], 'won', g['projects_won'], 'auc', round(g['auc_base'], 4), '->', round(g['auc_full'], 4))


if __name__ == '__main__':
    main()
