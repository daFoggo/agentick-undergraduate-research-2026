/**
 * Statistics of the sprint-risk alerts and the AI diagnosis, and the sprint plans. The risk service counts only the
 * projects Plane lets the signed-in user see, so nothing here filters by project.
 */
const RISK_API = "/risk/api/v1";

type TCounts = { total: number; pending: number; approved: number; dismissed: number };

export type TRiskSummary = {
  alerts: TCounts;
  acceptance_rate: number | null;
  undone: number;
  causes: { cause: string; n: number }[];
  actions: (TCounts & { action_type: string })[];
  ai: {
    diagnosed: number;
    unknown: number;
    hypotheses_kept: number;
    hypotheses_dropped: number;
    notes: Record<string, number>;
    evidence_kinds: Record<string, number>;
    cost_usd: number;
    calls_failed: number;
    models: Record<string, number>;
  };
  projects: (TCounts & { project_id: string })[];
  decisions_by_day: { day: string; approve: number; reject: number; undo: number }[];
};

export type TRiskPending = {
  work_item_id: string;
  project_id: string;
  issue_key: string;
  score: number;
  rank: number;
  size: number;
  action_type: string;
  diagnosed: boolean;
  cause_label: string | null;
  reason: string | null;
};

export type TRiskPlanItem = {
  work_item_id: string;
  issue_key: string;
  score: number;
  why: "risk" | "follows";
  cause: string | null;
  reason: string | null;
  state: "pending" | "applied" | "dismissed";
};

export type TRiskPlan = {
  id: string;
  project_id: string;
  cycle_id: string;
  next_cycle_id: string;
  sprint_name: string;
  mark: number;
  open_count: number;
  history_sprints: number;
  unfinished_share: number;
  expected_unfinished: number;
  budget: number;
  items: TRiskPlanItem[];
  errors: Record<string, string>; // items the last request could not move, with Plane's answer
};

async function getRisk<T>(path: string): Promise<T | null> {
  const response = await fetch(`${RISK_API}/${path}`, { credentials: "same-origin" });
  // Plane's web app answers with its HTML page when the /risk route is not deployed: no data, not an error
  if (response.ok && !response.headers.get("content-type")?.includes("application/json")) return null;
  if (!response.ok) throw new Error(String(response.status));
  return (await response.json()) as T;
}

export const fetchRiskInsights = <T>(path: string) => getRisk<T>(`insights/${path}`);
export const fetchRiskPlans = () => getRisk<TRiskPlan[]>("plans");

// decision: approve moves the chosen items in Plane, reject dismisses them; undo reverses what was decided
export async function postRiskPlan(planId: string, action: "decision" | "undo", body: object): Promise<TRiskPlan> {
  const response = await fetch(`${RISK_API}/plans/${planId}/${action}`, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(String(response.status));
  return (await response.json()) as TRiskPlan;
}

export type TRiskAnswer = {
  answer: string;
  tools: { name: string; arguments: Record<string, unknown>; ok: boolean }[]; // every lookup the answer rests on
  cost_usd: number;
  unverified: boolean;
};

export async function askRisk(question: string): Promise<TRiskAnswer> {
  const response = await fetch(`${RISK_API}/assistant/ask`, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) throw new Error(String(response.status));
  return (await response.json()) as TRiskAnswer;
}
