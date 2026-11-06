"""Measure the diagnosis against an independent label (M13).

1. python scripts/post_briefs.py ...  with DUMP_INPUTS=artifacts/eval/inputs.jsonl   (what the model saw and answered)
2. python scripts/eval_diagnosis.py sheet artifacts/eval        -> label_sheet.md (no model output) and label_key.json
3. someone who has not seen the cards labels the sheet by eval/RUBRIC.md            -> artifacts/eval/labels.csv
   (columns id,primary,secondary,confidence,note; primary is a cause or none)
4. python scripts/eval_diagnosis.py score artifacts/eval [human.csv] -> results.json
   human.csv (same columns) is a second labeller on a subset; the score then also gives kappa between the two labellers.
"""
import csv
import json
import sys
from pathlib import Path

from research.eval_diagnosis import LABELS, kappa, model_cause, score, shuffled_ids


def load(folder):
    rows = [json.loads(line) for line in (folder / 'inputs.jsonl').read_text(encoding='utf-8').splitlines() if line]
    return {r['key']: r for r in rows}


def sheet(folder):
    by_key = load(folder)
    ids = shuffled_ids(by_key)
    (folder / 'label_key.json').write_text(json.dumps(ids, indent=1), encoding='utf-8')
    out = []
    for sid, key in ids.items():
        r = by_key[key]
        out.append(f"## {sid}\nTitle: {r['title'][:200]}\n"
                   f"Status: {r['status']}. No activity for {r['inactive']:.1f} days.\n")
        out += [f"- [{e['id']}] {e['kind']} {str(e['ts'])[:10]}: {e['text']}" for e in r['events']] or ['- (no events)']
        out.append('')
    (folder / 'label_sheet.md').write_text('\n'.join(out), encoding='utf-8')
    print(len(ids), 'alerts in', folder / 'label_sheet.md')


def read_labels(path):
    labels = {}
    for r in csv.DictReader(open(path, encoding='utf-8')):
        if r['primary'] not in LABELS or r['secondary'] not in LABELS + ('',):
            raise SystemExit(f"bad label in {path}: {r}")
        labels[r['id']] = r
    return labels


def run_score(folder, human=None):
    by_key, labels = load(folder), read_labels(folder / 'labels.csv')
    ids = json.loads((folder / 'label_key.json').read_text())
    missing = set(ids) - set(labels)
    if missing:
        raise SystemExit(f'{len(missing)} alerts have no label, e.g. {sorted(missing)[:3]}')
    rows = []
    for sid, key in ids.items():
        card = by_key[key]['card']
        rows.append(dict(id=sid, key=key, model=model_cause(card), model_all=[h['cause'] for h in card['hypotheses']],
                         label=labels[sid]['primary'], label2=labels[sid]['secondary']))
    result = score(rows)
    if human:
        h = read_labels(human)
        result['labellers'] = dict(n=len(h), kappa=kappa([(labels[i]['primary'], h[i]['primary']) for i in h]),
                                   agree=sum(labels[i]['primary'] == h[i]['primary'] for i in h) / len(h))
    (folder / 'results.json').write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(result, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    cmd, folder = sys.argv[1], Path(sys.argv[2])
    sheet(folder) if cmd == 'sheet' else run_score(folder, Path(sys.argv[3]) if len(sys.argv) > 3 else None)
