"""Held-out cases for the diagnosis check (M13): ranked open issues that did NOT raise an alert, never seen when the
diagnosis was tuned. Writes the same inputs.jsonl that post_briefs.py dumps, so eval_diagnosis.py sheet/score work on it.
Usage: TAWOS_DSN=... OPENROUTER_API_KEY=... python scripts/eval_heldout.py scores.csv out_folder [N] [exclude.jsonl]
"""
import json
import os
import sys
from pathlib import Path

import pandas as pd
import psycopg

from app.services.diagnosis import diagnose
from app.services.openrouter_client import OpenRouterClient
from research.collectors import collect

scores, out = pd.read_csv(sys.argv[1]), Path(sys.argv[2])
n = int(sys.argv[3]) if len(sys.argv) > 3 else 60
seen = set()
if len(sys.argv) > 4:  # issues already evaluated stay out
    seen = {json.loads(line)['key'].split('@')[0] for line in Path(sys.argv[4]).read_text(encoding='utf-8').splitlines()}
pool = scores[(scores['rank'].notna()) & (scores['alert'] == False)]  # noqa: E712 (a pandas mask)
snap = pd.read_parquet('data/processed/snapshots.parquet').set_index(['landmark', 'sprint_id', 'issue_id'])
client = OpenRouterClient(model='openai/gpt-6-luna', budget=.5)
out.mkdir(parents=True, exist_ok=True)
done = 0
with psycopg.connect(os.environ['TAWOS_DSN']) as c, open(out / 'inputs.jsonl', 'w', encoding='utf-8') as f:
    for _, r in pool.sample(frac=1, random_state=20261106).iterrows():
        if done == n:
            break
        cur = c.cursor()
        cur.execute('select issue_key, title from tawos_raw.issue where id=%s', (int(r['issue_id']),))
        key, title = cur.fetchone()
        if key in seen:
            continue
        seen.add(key)
        row = snap.loc[(float(r['mark']), int(r['sprint_id']), int(r['issue_id']))]
        cutoff = row['prediction_at']
        events = collect(c.cursor(), int(r['issue_id']), cutoff)
        inactive = float(row['dynamic_inactive_days'])
        card, meta = diagnose(client, key, title or '', row['dynamic_status'], inactive, events)
        f.write(json.dumps(dict(key=f"{key}@{int(r['sprint_id'])}@{r['mark']}", title=title or '',
                                status=row['dynamic_status'], inactive=inactive, events=events, card=card),
                           default=str, ensure_ascii=False) + '\n')
        done += 1
print(done, 'cases, spent USD', round(client.spent, 5))
