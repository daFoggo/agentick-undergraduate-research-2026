# Sprint Risk — Early Warning System

| Folder | Content |
|---|---|
| [backend/](backend/) | New backend (in progress) |
| [frontend/](frontend/) | New frontend (in progress) |
| [experiment/](experiment/) | New experiments |
| [research/](research/) | Previous research work: `research` package (training/evaluation/agent), prototype FastAPI app, artifacts, reports, paper, slides, tests. See [research/README.md](research/README.md). |

Run the old code from inside `research/` (relative paths such as `artifacts/`, `data/raw/` are resolved from there):

```bash
cd research
python -m pytest
docker compose up --build -d
```
