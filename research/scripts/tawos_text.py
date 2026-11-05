"""TAWOS description_text -> readable Plane HTML. The dump lost line breaks (they became runs of spaces), so runs of
3+ spaces are treated as paragraph breaks; Jira's doubled quotes are collapsed."""
import html
import re


def to_html(text, key, limit=3000):
    t = (text or '').strip()
    t = re.sub(r'"{2,}', '"', t).strip('"').strip()[:limit]
    paras = [p.strip() for p in re.split(r'\s{3,}|\n+', t) if p.strip()]
    body = ''.join(f'<p>{html.escape(p)}</p>' for p in paras) or '<p><em>(Không có mô tả)</em></p>'
    return body + f'<p><em>Nguồn: bộ dữ liệu TAWOS, issue {html.escape(key)}.</em></p>'
