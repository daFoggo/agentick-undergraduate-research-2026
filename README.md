# Sprint-risk diagnosis assistant

Tells a team which sprint issues are at risk, why (with evidence from the issue's real context), and what to do; a
person approves every action in Plane. Problem, architecture and module plan: [intent.md](intent.md).

| Folder | Content |
|---|---|
| [research/](research/) | Offline pipeline on TAWOS: risk scoring, context collectors, diagnosis, publishing to Plane |
| [agentick-backend/](agentick-backend/) | FastAPI service next to Plane: alerts, diagnoses, approve / dismiss / undo |
| [plane/](plane/) | Plane fork (`feat/risk-service`) with the risk card and the `/risk` proxy |
| [scripts/](scripts/) | `stack.sh`: start / stop the whole local stack |

Run and test: [CLAUDE.md](CLAUDE.md).
