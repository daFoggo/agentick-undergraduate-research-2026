# Sprint Risk Research

Research workspace for early prediction of issue non-completion within a sprint, using TAWOS as the primary dataset.

## Stack

- FastAPI application organized with `APIRouter` modules.
- PostgreSQL as the normalized, queryable research datastore.
- SQLAlchemy and Alembic for application-owned schema and migrations.
- Docker Compose for the API and PostgreSQL development environment.
- `pgloader` for the initial MySQL-to-PostgreSQL transfer of TAWOS.

The upstream TAWOS release is a MySQL dump. The MySQL instance is only an import/source adapter; application and research queries target PostgreSQL. Raw downloaded data stays under `data/raw/` and is deliberately excluded from Git.

## Start the API and PostgreSQL

1. Copy `.env.example` to `.env` and adjust local credentials if needed. The checked-in defaults are for local development only.
2. Start the database and API:

   ```powershell
   docker compose up --build -d
   ```

3. Open the interactive API docs at <http://localhost:8000/docs>.

The liveness endpoint is `/api/v1/health/live`; database readiness is `/api/v1/health/ready`.

## TAWOS data setup and PostgreSQL migration

Download TAWOS v1.1 from the [UCL Research Data Repository](https://doi.org/10.5522/04/21308124), read its terms of use, and place the archive at `data/raw/TAWOS-v1.1.sql.zip`. Extract `TAWOS.sql` to `data/raw/unpacked/TAWOS.sql`. The import/migration scripts do not download or commit the dataset.

Start PostgreSQL and an isolated MySQL source initialized from the dump:

```powershell
docker compose up -d db
docker compose --profile migration up -d source-mysql
```

Wait until `source-mysql` is healthy; the initial 4.3 GB SQL import can take several minutes. Then migrate and verify the row counts:

```powershell
.\scripts\migrate_tawos_to_postgres.ps1 -SourceContainer tawos-source-mysql
.\scripts\validate_tawos_migration.ps1 -SourceContainer tawos-source-mysql
```

The migration script refuses to load into a PostgreSQL `public` schema that already contains tables, to avoid accidental overwrite. Use a fresh local database for a repeat migration. The source DB is accessed with a read-only account by `pgloader` and is not exposed on a host port.

After validation, start/restart the API:

```powershell
docker compose up --build -d api
```

Key endpoints:

- `GET /api/v1/dataset/summary`
- `GET /api/v1/dataset/projects?limit=50&offset=0`

The migration preserves the upstream tables in PostgreSQL schema `tawos_raw`; application-owned research metadata is separated into the `research` schema and managed with Alembic. Migration validation currently compares exact row counts across all 13 upstream tables.

## Local tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Two-Tier System Architecture

The research combines a risk prediction model with an evidence-grounded alert agent. All quantitative results below are TAWOS v1.1 benchmarks; the system is not yet integrated into Agentick, so there is no live usage data.

1. **Tier 1: Risk model and alert controller (no LLM)**
   - Dynamic CatBoost scores open issues at the 50% sprint landmark (the pre-registered landmark; `midpoint` policy).
   - The main evaluation budget is `ceil(0.2 * n)` alerts per sprint of `n` issues. The fixed per-sprint cap `K = 2` is a value explored in the post-hoc policy replay (E1) and used to build the agent scenarios; it is not shown to be optimal.
2. **Tier 2: Grounded brief agent (`gemini-3.5-flash-lite`)**
   - Triggered only for issues selected by Tier 1; it does not produce probabilities or edit sprints.
   - Uses read-only tools (`get_issue_evidence`, `get_sprint_summary`) that only return as-of events from the same project.
   - Every claim cites an `event_id`; `EvidenceVerifier` blocks briefs with unknown event IDs, mismatched numbers or causal claims.

## Key Results

Forecasting (phase 4, 50% landmark, `ceil(0.2n)` budget): dynamic vs static recall 53.36% vs 44.46% (temporal, +8.90 pp, 95% CI [6.38, 11.70]) and 53.52% vs 43.56% (cross-project, +9.96 pp, CI [7.53, 12.82]). On issues still open at the landmark the gain shrinks to +2.59 / +2.03 pp, and the temporal gain over the business rule is not significant (+2.13 pp, CI [-0.33, 4.60]).

Agent technical evaluation (Protocol E3 v2, full 50-scenario suite, 1 repetition):

| Metric | A0 Template (no LLM) | A1 Single Narrator | A2 Bounded Tool Agent |
|---|---|---|---|
| Evidence Recall | 100.0% | 100.0% | 100.0% |
| Grounding Precision | 100.0% | 100.0% | 100.0% |
| Numeric Accuracy | 100.0% | 100.0% | 100.0% |
| Decision Accuracy | 100.0% | 98.0% | 98.0% |
| Average Tool Calls | 0.0 | 0.0 | 1.0 |
| Latency p50 / p95 | 0.00s / 0.00s | 1.67s / 2.07s | 2.67s / 17.34s |

All variants hit the ceiling on citation metrics (each scenario has 3 gold events), and the deterministic template matches or beats the LLM variants at zero cost. The result shows the evidence pipeline and verifier work across the five probe classes; it does not show that the LLM agent is more accurate than the template. A1 and A2 share one false alert (a MULE scenario expected to abstain).

Test suite: 68 tests. On 2026-10-08, 66 pass on a machine without the archival data files; the two failures (`test_agent_evaluation.py::test_evaluate_single_run_a0`, `test_agent_scenarios.py::test_load_dev_scenarios`) are `FileNotFoundError`s from the missing data.

## Research documents

- [Progress report / Thuyết minh báo cáo tiến độ](documents/Thuyet_minh_bao_cao_tien_do.md) (PDF alongside)
- [Final report / Báo cáo tổng kết đề tài](documents/Bao_cao_tong_ket_de_tai.docx)
- [Progress slides](slide-template/) (`main.pdf`, speaker notes in `script.md`)
- [Main Proposal / Đề cương nghiên cứu](documents/De_cuong_du_bao_som_rui_ro_sprint.md)
- [Results summary & slide outline](documents/Khung_trinh_bay_slide_va_tong_hop_ket_qua.md)
- [Phase 1 Protocol](documents/Protocol_pha_1_chot_bai_toan_va_thiet_ke_du_lieu.md)
- [Agent Extension Protocol E3 v2 report](artifacts/agent_extension/agent_v2/eval_report_full.md)
- [Deep Research on AI Agent Integration](documents/Deep_research_AI_agent_canh_bao_som.md)
- [Agent Research Progress](documents/Agent_research_progress.md)
