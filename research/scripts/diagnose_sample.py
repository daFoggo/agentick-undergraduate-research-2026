"""Live check of the diagnosis on N random open sprint issues at 40% of their sprint (costs a few cents).
Usage: TAWOS_DSN=... python scripts/diagnose_sample.py [N]   (key from research/.env)"""
import json
import os
import sys

import psycopg

from app.services.diagnosis import diagnose
from app.services.openrouter_client import OpenRouterClient
from research.collectors import collect
from research.tawos_source import state_at

n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
client = OpenRouterClient(model='openai/gpt-6-luna', budget=.5)
with psycopg.connect(os.environ['TAWOS_DSN']) as c:
    cur = c.cursor()
    cur.execute("select i.id, i.issue_key, i.title, s.start_date + (s.end_date - s.start_date) * .4 from tawos_raw.issue i "
                "join tawos_raw.sprint s on s.id=i.sprint_id where s.end_date > s.start_date and "
                "s.end_date - s.start_date < interval '30 days' and exists (select 1 from tawos_raw.comment k where "
                "k.issue_id=i.id) and i.resolution_date > s.start_date + (s.end_date - s.start_date) * .4 "
                "order by random() limit %s", (n,))
    for issue_id, key, title, t in cur.fetchall():
        events = collect(c.cursor(), issue_id, t)
        status = state_at(c.cursor(), issue_id, t)['status']
        card, meta = diagnose(client, key, title or '', status, 3.0, events)
        print(f'\n== {key} {title[:70]} | events {len(events)} cost {meta["cost"]:.5f} error {meta["error"]}')
        print(json.dumps({k: card[k] for k in ('unknown', 'dropped', 'missing_info', 'action')}, ensure_ascii=False))
        for h in card['hypotheses']:
            print(' -', h['cause'], '|', h['reason'], '|', [e['id'] for e in h['evidence']])
print('\nspent USD', round(client.spent, 5))
