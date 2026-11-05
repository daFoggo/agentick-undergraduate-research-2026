"""Protocol E6: story-point estimation from similar past cases, no LLM. Locked in documents/Protocol_estimation_E6.md."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(os.environ.get('E6_OUT', 'artifacts/estimation_e6'))
PROTOCOL = Path('documents/Protocol_estimation_E6.md')
MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
QUERY_FRAC, K, MIN_CANDIDATES, MIN_PROJECT_ISSUES, SEED = .3, 20, 30, 500, 20261105
# smoke subset (amendment 1): E6_TOP largest projects, newest E6_CAP issues each, E6_MAXLEN tokens; 0 = full protocol
TOP, CAP, MAXLEN = (int(os.environ.get(k, d)) for k, d in (('E6_TOP', 0), ('E6_CAP', 0), ('E6_MAXLEN', 128)))
SQL = """select id, project_id, creation_date, resolution_date, story_point, title, description_text from tawos_raw.issue
where story_point > 0 and resolution_date is not null and creation_date is not null
and title_changed_after_estimation = 0 and description_changed_after_estimation = 0
and story_point_changed_after_estimation = 0 and length(coalesce(description_text,'')) > 50"""


def predict_project(df, emb, query_frac=QUERY_FRAC, k=K, min_candidates=MIN_CANDIDATES):
    """df sorted by creation_date, emb rows aligned. A query sees only issues resolved before it was created."""
    created, resolved = df.creation_date.to_numpy(), df.resolution_date.to_numpy()
    points = df.story_point.to_numpy(float)
    rows, skipped = [], 0
    for p in range(int(len(df) * (1 - query_frac)), len(df)):
        cand = np.flatnonzero((resolved < created[p]) & (np.arange(len(df)) != p))
        if len(cand) < min_candidates:
            skipped += 1  # protocol: dropped queries are counted, not silently lost
            continue
        vals = points[cand]
        near = vals[np.argsort(-(emb[cand] @ emb[p]), kind='stable')[:k]]
        rows.append(dict(query_pos=p, y=points[p], n_candidates=len(cand), m0=np.median(vals), m1=vals.mean(),
                         m2=np.median(near), lo0=np.quantile(vals, .1), hi0=np.quantile(vals, .9),
                         lo2=np.quantile(near, .1), hi2=np.quantile(near, .9)))
    out = pd.DataFrame(rows, columns=['query_pos', 'y', 'n_candidates', 'm0', 'm1', 'm2', 'lo0', 'hi0', 'lo2', 'hi2'])
    out.attrs['skipped'] = skipped
    return out


def summarize(out):
    res = {}
    for name, point, lo, hi in (('M0', 'm0', 'lo0', 'hi0'), ('M1', 'm1', 'lo0', 'hi0'), ('M2', 'm2', 'lo2', 'hi2')):
        err = (out[point] - out.y).abs()
        res[name] = dict(n=len(out), mae=float(err.mean()), mdae=float(err.median()),
                         mae_macro_project=float(err.groupby(out.project).mean().mean()),
                         coverage=float(((out.y >= out[lo]) & (out.y <= out[hi])).mean()),
                         width=float((out[hi] - out[lo]).mean()))
    return res


def bootstrap_delta(out, a='m2', b='m0'):
    diff = ((out[a] - out.y).abs() - (out[b] - out.y).abs()).groupby(out.project).mean()
    rng = np.random.default_rng(SEED)
    est = np.array([rng.choice(diff.to_numpy(), len(diff)).mean() for _ in range(2000)])
    return dict(n_projects=len(diff), delta=float(diff.mean()), ci_low=float(np.quantile(est, .025)),
                ci_high=float(np.quantile(est, .975)), projects_where_model_wins=int((diff < 0).sum()))


def embed(texts, batch=64):
    # transformers directly (sentence_transformers does not import in this env); mean pooling = this model's pooling
    import torch
    from transformers import AutoModel, AutoTokenizer
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    tok, net = AutoTokenizer.from_pretrained(MODEL), AutoModel.from_pretrained(MODEL).to(dev).eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), batch):
            enc = tok(texts[i:i + batch], padding=True, truncation=True, max_length=MAXLEN, return_tensors='pt').to(dev)
            h, m = net(**enc).last_hidden_state, enc.attention_mask.unsqueeze(-1)
            v = (h * m).sum(1) / m.sum(1)
            out.append(torch.nn.functional.normalize(v, dim=1).cpu().numpy())
    return np.concatenate(out)


def main():
    import psycopg
    if OUT.exists():
        raise SystemExit(f'{OUT} exists; protocol E6 results are not overwritten')
    with psycopg.connect(os.environ.get('RESEARCH_DATABASE_URL',
                                        'postgresql://tawos:tawos_local_dev@localhost:15990/tawos')) as con:
        data = pd.read_sql(SQL, con)
    for c in ('creation_date', 'resolution_date'):
        data[c] = pd.to_datetime(data[c], utc=True)
    keep = data.project_id.value_counts()
    keep = keep[keep >= MIN_PROJECT_ISSUES]
    keep = keep.head(TOP) if TOP else keep  # chosen by size only, never by outcome
    data = data[data.project_id.isin(keep.index)].sort_values(['project_id', 'creation_date', 'id'])
    if CAP:
        data = data.groupby('project_id').tail(CAP)
    data = data.reset_index(drop=True)
    emb = embed((data.title + ' ' + data.description_text).tolist())
    parts, skipped = [], {}
    for pid, g in data.groupby('project_id'):
        o = predict_project(g.reset_index(drop=True), emb[g.index.to_numpy()])
        skipped[str(pid)] = o.attrs['skipped']
        parts.append(o.assign(project=pid, issue_id=g.id.to_numpy()[o.query_pos.to_numpy()]))
    out = pd.concat(parts, ignore_index=True)
    summary = dict(models=summarize(out), m2_vs_m0=bootstrap_delta(out), m2_vs_m1=bootstrap_delta(out, 'm2', 'm1'),
                   eligible_issues=len(data), projects=int(data.project_id.nunique()), queries=len(out),
                   skipped_queries=skipped, skipped_total=sum(skipped.values()),
                   per_project={str(p): summarize(g) for p, g in out.groupby('project')})
    OUT.mkdir(parents=True)
    out.to_csv(OUT / 'queries.csv', index=False)
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    (OUT / 'manifest.json').write_text(json.dumps(dict(
        run_at=datetime.now(timezone.utc).isoformat(), protocol_sha256=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        amendments={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in PROTOCOL.parent.glob(f'{PROTOCOL.stem}_amendment*.md')},
        subset=dict(top=TOP, cap=CAP, max_tokens=MAXLEN),  # E6_TOP / E6_CAP / E6_MAXLEN: 0 = full protocol
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), model=MODEL, k=K, seed=SEED), indent=2),
        encoding='utf-8')
    print(json.dumps({k: summary[k] for k in ('eligible_issues', 'projects', 'queries', 'skipped_total', 'models',
                                              'm2_vs_m0', 'm2_vs_m1')}, indent=2))


if __name__ == '__main__':
    main()
