"""Publish, for every TAWOS work item in the given Plane projects, the finished cases most similar to it (E6 method M2).

A case is a same-project issue with a story point that was resolved before this issue was created, so nothing from the
future is shown. The card shows how the 20 nearest cases split into small / medium / large (relative to the project's own
story-point scale) and the 3 closest as examples. Each example is imported into a Plane project "Past cases" so the link
opens inside Plane. No point estimate: the E6 smoke run did not meet the lock-in rule for one
(documents/Protocol_estimation_E6_amendment1.md).
Usage: PLANE_API_KEY=... RISK_INGEST_TOKEN=... python scripts/publish_cases.py ISP DCP   (PYTHONPATH=. from research/)
"""
import json
import os
import sys
import urllib.error
import urllib.request

import numpy as np
import pandas as pd
import psycopg

from research.estimate_cases import K, SQL, embed
from tawos_text import to_html

BASE = os.environ.get('PLANE_URL', 'http://localhost:31080/api/v1/workspaces/ript')
RISK_URL = os.environ.get('RISK_URL', 'http://localhost:31081/api/v1/cases')
SLUG = BASE.rstrip('/').rsplit('/', 1)[-1]
POOL = 1000  # newest eligible cases per project; keeps CPU embedding to minutes (smoke setting, amendment 1)
SHOWN = 3
HISTORY = ('Past cases', 'PCA')  # Plane project names allow no special characters
SOURCE = 'tawos-history'


def plane(path, body=None, method=None):
    req = urllib.request.Request(BASE + path, method=method or ('POST' if body else 'GET'),
                                 data=json.dumps(body).encode() if body else None,
                                 headers={'X-API-Key': os.environ['PLANE_API_KEY'], 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f'{path} -> {e.code} {e.read()[:300]}')


def work_items(project, source='tawos'):
    out, cursor = [], None
    while True:
        page = plane(f'/projects/{project}/work-items/?per_page=100' + (f'&cursor={cursor}' if cursor else ''))
        out += [w for w in page['results'] if w.get('external_source') == source]
        if not page['next_page_results']:
            return out
        cursor = page['next_cursor']


def size_of(points, every):
    small, large = np.quantile(every, [.33, .8])
    if np.ptp(every) == 0:  # every case has the same points: nothing is small or large next to the others
        return 'medium'
    return 'small' if points <= small else 'large' if points > large else 'medium'


def history_paths(cases):
    """Plane page path of each case (tawos id -> '/slug/browse/PCA-n/'), creating the missing ones as Done items."""
    projects = {p['identifier']: p['id'] for p in plane('/projects/')['results']}
    pid = projects.get(HISTORY[1]) or plane('/projects/', {'name': HISTORY[0], 'identifier': HISTORY[1]})['id']
    done = next(s['id'] for s in plane(f'/projects/{pid}/states/')['results'] if s['name'] == 'Done')
    have = {w['external_id']: w['sequence_id'] for w in work_items(pid, SOURCE)}
    for c in cases.values():
        if str(c['id']) in have:
            continue
        w = plane(f'/projects/{pid}/work-items/', {
            'name': f"[{c['key']}] {c['title']}"[:255], 'state': done, 'external_source': SOURCE,
            'external_id': str(c['id']),
            'description_html': to_html(c['text'], c['key'])})
        have[str(c['id'])] = w['sequence_id']
    return {int(i): f'/{SLUG}/browse/{HISTORY[1]}-{n}/' for i, n in have.items()}


def main(identifiers):
    projects = {p['identifier']: p['id'] for p in plane('/projects/')['results']}
    items = [(projects[i], w) for i in identifiers for w in work_items(projects[i])]
    ids = [int(w['external_id']) for _, w in items]
    with psycopg.connect(os.environ.get('RESEARCH_DATABASE_URL',
                                        'postgresql://tawos:tawos_local_dev@localhost:15990/tawos')) as con:
        q = pd.read_sql("select id, project_id, creation_date, title, description_text from tawos_raw.issue "
                        "where id = any(%s)", con, params=(ids,)).set_index('id')
        pool = pd.read_sql(SQL, con)
        meta = pd.read_sql("select id, issue_key, in_progress_minutes from tawos_raw.issue where id = any(%s)", con,
                           params=(pool.id.tolist(),)).set_index('id')
    for c in ('creation_date', 'resolution_date'):
        pool[c] = pd.to_datetime(pool[c], utc=True)
    q['creation_date'] = pd.to_datetime(q.creation_date, utc=True)
    pool['issue_key'] = pool.id.map(meta.issue_key)
    pool['days'] = pool.id.map(meta.in_progress_minutes).map(lambda m: round(m / 1440, 1) if m and m > 0 else None)
    pool = pool.sort_values('creation_date').groupby('project_id').tail(POOL).reset_index(drop=True)
    text = lambda d: (d.title + ' ' + d.description_text.fillna('')).tolist()
    pool_emb = embed(text(pool))
    q_emb = dict(zip(q.index, embed(text(q))))
    drafts, shown = [], {}
    for pid, w in items:
        row = q.loc[int(w['external_id'])]
        ok = ((pool.project_id == row.project_id) & (pool.resolution_date < row.creation_date) &
              (pool.id != int(w['external_id']))).to_numpy()
        cand = np.flatnonzero(ok)
        if len(cand) < K:
            continue
        sims = pool_emb[cand] @ q_emb[row.name]
        top = cand[np.argsort(-sims, kind='stable')[:K]]
        points, every = pool.story_point.to_numpy(float), pool.story_point.to_numpy(float)[cand]
        sizes = [size_of(p, every) for p in points[top]]
        for i in top[:SHOWN]:
            shown[int(pool.id[i])] = dict(id=int(pool.id[i]), key=pool.issue_key[i], title=pool.title[i],
                                          text=pool.description_text[i] or '')
        drafts.append(dict(work_item_id=w['id'], project_id=pid, project_size=len(every),
                           sizes={s: sizes.count(s) for s in ('small', 'medium', 'large')},
                           cases=[dict(id=int(pool.id[i]), key=pool.issue_key[i], title=pool.title[i][:120],
                                       size=size_of(points[i], every),
                                       days=None if pd.isna(pool.days[i]) else float(pool.days[i])) for i in top[:SHOWN]]))
    paths = history_paths(shown)
    published = [{**d, 'cases': [{k: v for k, v in c.items() if k != 'id'} | {'path': paths[c['id']]}
                                 for c in d['cases']]} for d in drafts]
    req = urllib.request.Request(RISK_URL, method='PUT', data=json.dumps(published).encode(),
                                 headers={'Authorization': f"Bearer {os.environ['RISK_INGEST_TOKEN']}",
                                          'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        print('risk service stored', json.load(r)['stored'], 'of', len(items), 'work items;', len(shown),
              'past cases in Plane')


if __name__ == '__main__':
    main(sys.argv[1:])
