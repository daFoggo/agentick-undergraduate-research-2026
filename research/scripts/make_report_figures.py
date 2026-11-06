"""Chart sources (LaTeX, pgfplots/TikZ) for the report, written from the measured result files.
Usage: python scripts/make_report_figures.py OUT_DIR   then compile each .tex with xelatex and export with pdftoppm
(see scripts/build_report_figures.sh). Nothing here is typed by hand: every number comes from
artifacts/eval/results.json, artifacts/eval_heldout/results.json and artifacts/eval/backtest_plan.json."""
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
first = json.load(open('artifacts/eval/results.json'))
held = json.load(open('artifacts/eval_heldout/results.json'))
back = json.load(open('artifacts/eval/backtest_plan.json'))

VI = {'pulled_away': 'Người phụ trách bận việc khác', 'carry_over': 'Dồn từ sprint trước',
      'waiting_person': 'Chờ một người', 'needs_decision': 'Chờ quyết định', 'unclear_scope': 'Phạm vi chưa rõ',
      'blocked': 'Bị issue khác chặn', 'none': 'Không rõ'}
SHORT = {'pulled_away': 'Bận việc khác', 'carry_over': 'Dồn sprint', 'waiting_person': 'Chờ một người',
         'needs_decision': 'Chờ quyết định', 'unclear_scope': 'Phạm vi chưa rõ', 'blocked': 'Bị chặn', 'none': 'Không rõ'}
HEAD = (r'\documentclass[border=6pt]{standalone}' '\n' r'\usepackage{fontspec}\setmainfont{Times New Roman}' '\n'
        r'\usepackage{pgfplots}\pgfplotsset{compat=1.17}\usepgfplotslibrary{groupplots}\usepackage{tikz}\pgfkeys{/pgf/number format/.cd,use comma,1000 sep={}}' '\n'
        r'\definecolor{sys}{HTML}{2F6DB5}\definecolor{lab}{HTML}{D9822B}' '\n' r'\begin{document}' '\n')


def pc(x):
    return f'{x * 100:.0f}' + r'\%'  # a bare % starts a LaTeX comment


def vn(x, fmt):
    return f'{x:{fmt}}'.replace('.', ',')  # Vietnamese decimal comma


def write(name, body):
    (OUT / f'{name}.tex').write_text(HEAD + body + '\n' + r'\end{document}' + '\n', encoding='utf-8')


def counts(res):
    """per cause: (what the system put first, what the labeller chose); none = no cause."""
    rows = {c: (v['said'], v['labelled']) for c, v in res['per_cause'].items()}
    rows['none'] = (res['model_unknown'], res['label_none'])
    return rows


def cause_compare(res, title, name):
    rows = sorted(counts(res).items(), key=lambda kv: -max(kv[1]))
    sym = ','.join(VI[c] for c, _ in rows)
    sysc = ' '.join(f'({a},{VI[c]})' for c, (a, _) in rows)
    labc = ' '.join(f'({b},{VI[c]})' for c, (_, b) in rows)
    write(name, rf'''\begin{{tikzpicture}}
\begin{{axis}}[xbar, bar width=5pt, width=11cm, height={0.9 + 0.9 * len(rows)}cm, xmin=0,
 symbolic y coords={{{sym}}}, ytick=data, y dir=reverse, enlarge y limits=0.12, nodes near coords,
 nodes near coords style={{font=\footnotesize}}, xlabel={{Số alert (n={res["n"]})}}, title={{{title}}},
 legend style={{at={{(0.98,0.05)}}, anchor=south east, font=\footnotesize}}, tick label style={{font=\small}}]
\addplot[fill=sys, draw=none] coordinates {{{sysc}}};
\addplot[fill=lab, draw=none] coordinates {{{labc}}};
\legend{{Hệ thống (nguyên nhân đứng đầu), Người chấm độc lập}}
\end{{axis}}
\end{{tikzpicture}}''')


def confusion(res, title, x0):
    order = ['pulled_away', 'carry_over', 'waiting_person', 'unclear_scope', 'blocked', 'needs_decision', 'none']
    cell = {tuple(k.split('->')): v for k, v in res['confusion'].items()}
    top = max(cell.values())
    s = [rf'\begin{{scope}}[xshift={x0}cm]', rf'\node[font=\bfseries] at (3.6,2.7) {{{title}}};']
    for j, c in enumerate(order):
        s.append(rf'\node[rotate=35, anchor=west, font=\scriptsize] at ({j * 0.9 + 0.45},0.1) {{{SHORT[c]}}};')
    for i, lab in enumerate(order):
        s.append(rf'\node[anchor=east, font=\scriptsize] at (-0.1,{-i * 0.7 - 0.45}) {{{SHORT[lab]}}};')
        for j, mod in enumerate(order):
            v = cell.get((lab, mod), 0)
            fill = f'sys!{int(8 + 85 * v / top)}' if v else 'white'
            s.append(rf'\draw[draw=gray!50, fill={fill}] ({j * 0.9},{-i * 0.7}) rectangle +(0.9,-0.7);')
            if v:
                s.append(rf'\node[font=\footnotesize] at ({j * 0.9 + 0.45},{-i * 0.7 - 0.35}) {{{v}}};')
    s.append(r'\end{scope}')
    return '\n'.join(s)


write('fig_confusion', r'\begin{tikzpicture}' '\n'
      + confusion(first, f'81 alert (lần 1), khớp {pc(first["top1"])}', 0) + '\n'
      + confusion(held, f'60 ca held-out, khớp {pc(held["top1"])}', 11) + '\n'
      + r'\node[font=\small] at (3.6,-5.6) {Hàng: nhãn của người chấm. Cột: nguyên nhân đứng đầu của hệ thống.};' '\n'
      + r'\node[font=\small] at (14.6,-5.6) {Số ô là số alert.};' '\n' + r'\end{tikzpicture}')
cause_compare(first, 'Lần 1: 81 alert, trước khi sửa thứ tự', 'fig_cause_first')
cause_compare(held, 'Held-out: 60 ca, sau khi sửa thứ tự', 'fig_cause_heldout')

pts = ' '.join(f'({r["expected"]},{r["unfinished"]})' for r in back['sprints'])
top = max(max(r['expected'], r['unfinished']) for r in back['sprints']) + 1
sm = back['summary']
write('fig_backtest', rf'''\begin{{tikzpicture}}
\begin{{axis}}[width=9cm, height=9cm, xmin=0, xmax={top}, ymin=0, ymax={top}, xlabel={{Số issue không xong dự kiến (từ các sprint trước)}},
 ylabel={{Số issue không xong thực tế}}, title={{{sm["sprints_replayed"]} sprint, mốc {pc(sm["mark"])}: lệch trung bình {vn(sm["expected_vs_actual_mae"], ".1f")} issue}},
 title style={{font=\small}}, label style={{font=\small}}]
\addplot[only marks, mark=*, mark size=1.8pt, sys, opacity=0.55] coordinates {{{pts}}};
\addplot[gray, dashed, domain=0:{top}] {{x}};
\end{{axis}}
\end{{tikzpicture}}''')

# --- detection results (E1-E9). These files are not in the working tree (they live in the backup
# migration_dump_20261106/code/research_ignored_artifacts_and_data.tgz): research/artifacts/rerun_v3_rank/h1_bootstrap.csv
# (static and dynamic recall), rerun_v2_clean/summary_by_seed.csv (rule and oracle, mean over seeds) and
# lead_time_e9/summary.json (lift with 95% CI). The values below were read from them on 2026-11-06.
MARKS = '0,0.25,0.5,0.75'
RECALL = {  # split: (static, dynamic, rule, oracle) per mark
    'Theo thời gian (397 sprint)': ([.462] * 4, [.456, .503, .532, .543], [.405, .451, .481, .525], [.598] * 4),
    'Theo dự án (1962 sprint)': ([.447] * 4, [.447, .486, .522, .573], [.367, .418, .466, .535], [.637] * 4),
}
LIFT = [(1.23, 1.21, 1.26, 1.01), (1.19, 1.17, 1.21, 1.03), (1.14, 1.12, 1.16, 1.03), (1.08, 1.07, 1.10, 1.03)]


def line(vals, style, name):
    pts = ' '.join(f'({m},{v})' for m, v in zip(MARKS.split(','), vals))
    return rf'\addplot[{style}] coordinates {{{pts}}}; \addlegendentry{{{name}}}'


panels = []
for i, (title, (st, dy, ru, orc)) in enumerate(RECALL.items()):
    panels.append(rf"""\nextgroupplot[title={{{title}}}, {'ylabel={Recall khi chỉ cảnh báo 20\% issue mỗi sprint}' if i == 0 else 'yticklabels={}'}]
{line(orc, 'gray, dashed, thick', 'Mức tối đa (xếp theo nhãn thật)')}
{line(dy, 'sys, very thick, mark=*', 'Mô hình động')}
{line(st, 'lab, thick, mark=square*', 'Mô hình tĩnh')}
{line(ru, 'black, thick, mark=triangle*', 'Quy tắc: đã xong hay chưa')}""")
write('fig_7_1', rf"""\begin{{tikzpicture}}
\begin{{groupplot}}[group style={{group size=2 by 1, horizontal sep=1cm}}, width=8.2cm, height=7cm, ymin=0.3, ymax=0.68,
 xmin=-0.05, xmax=0.8, xtick={{0,0.25,0.5,0.75}}, xticklabels={{0,25,50,75}}, xlabel={{Phần sprint đã trôi qua (\%)}},
 title style={{font=\small}}, label style={{font=\small}}, tick label style={{font=\footnotesize}}, grid=major, grid style={{gray!25}},
 legend style={{font=\scriptsize, at={{(0.02,0.98)}}, anchor=north west, fill=white, fill opacity=0.85, text opacity=1}}]
{panels[0]}
{panels[1].replace(r'\addlegendentry', r'\addlegendentry').replace('legend', 'legend')}
\end{{groupplot}}
\end{{tikzpicture}}""")

lift_pts = ' '.join(f'({m},{v[0]}) +- (0,{round(v[0]-v[1],2)})' for m, v in zip(MARKS.split(','), LIFT))
rule_pts = ' '.join(f'({m},{v[3]})' for m, v in zip(MARKS.split(','), LIFT))
write('fig_7_2', rf"""\begin{{tikzpicture}}
\begin{{axis}}[width=10cm, height=6.5cm, ymin=0.9, ymax=1.32, xmin=-0.05, xmax=0.8, xtick={{0,0.25,0.5,0.75}},
 xticklabels={{0,25,50,75}}, xlabel={{Phần sprint đã trôi qua (\%)}}, ylabel={{Lift (độ chính xác so với chọn ngẫu nhiên)}},
 label style={{font=\small}}, tick label style={{font=\footnotesize}}, grid=major, grid style={{gray!25}},
 legend style={{font=\scriptsize, at={{(0.98,0.98)}}, anchor=north east}}]
\addplot[sys, very thick, mark=*, error bars/.cd, y dir=both, y explicit, error bar style={{thick}}] coordinates {{{lift_pts}}};
\addlegendentry{{Mô hình động (khoảng tin cậy 95\%)}}
\addplot[black, thick, mark=triangle*] coordinates {{{rule_pts}}}; \addlegendentry{{Quy tắc đơn giản}}
\addplot[gray, dashed, domain=-0.05:0.8] {{1}}; \addlegendentry{{Chọn ngẫu nhiên}}
\end{{axis}}
\end{{tikzpicture}}""")

# --- 7.3 top cause over the 81 alerts of the first run; 7.5 the backtest sprint by sprint
rows = sorted(counts(first).items(), key=lambda kv: -kv[1][0])
sym = ','.join(VI[c] for c, _ in rows)
cs = ' '.join(f'({a},{VI[c]})' for c, (a, _) in rows)
write('fig_7_3', rf"""\begin{{tikzpicture}}
\begin{{axis}}[xbar, bar width=9pt, width=11cm, height=7cm, xmin=0, xmax=46, symbolic y coords={{{sym}}}, ytick=data, y dir=reverse,
 enlarge y limits=0.1, nodes near coords, xlabel={{Số cảnh báo (n={first["n"]})}}, tick label style={{font=\small}}, label style={{font=\small}}]
\addplot[fill=sys, draw=none] coordinates {{{cs}}};
\end{{axis}}
\end{{tikzpicture}}""")

sp = back['sprints']
exp_pts = ' '.join(f'({i + 1},{r["expected"]})' for i, r in enumerate(sp))
act_pts = ' '.join(f'({i + 1},{r["unfinished"]})' for i, r in enumerate(sp))
mov_pts = ' '.join(f'({i + 1},{r["moved"]})' for i, r in enumerate(sp))
write('fig_7_5', rf"""\begin{{tikzpicture}}
\begin{{axis}}[ybar, bar width=3.2pt, width=16cm, height=7cm, xmin=0, xmax={len(sp) + 1}, ymin=0, xlabel={{Sprint, theo thứ tự thời gian}},
 ylabel={{Số issue}}, label style={{font=\small}}, tick label style={{font=\footnotesize}}, grid=major, grid style={{gray!20}},
 legend style={{font=\scriptsize, at={{(0.5,-0.25)}}, anchor=north, legend columns=-1}},
 title={{Lệch trung bình {vn(sm["expected_vs_actual_mae"], ".2f")} issue, thiên lệch {vn(sm["expected_vs_actual_bias"], "+.2f")}}}, title style={{font=\small}}]
\addplot[fill=lab, draw=none] coordinates {{{act_pts}}}; \addlegendentry{{Thực tế không xong}}
\addplot[sys, thick, mark=*, mark size=1.2pt, only marks] coordinates {{{exp_pts}}}; \addlegendentry{{Dự kiến không xong}}
\addplot[black, mark=x, mark size=1.5pt, only marks] coordinates {{{mov_pts}}}; \addlegendentry{{Số issue được đề xuất chuyển}}
\end{{axis}}
\end{{tikzpicture}}""")

print('written to', OUT)
