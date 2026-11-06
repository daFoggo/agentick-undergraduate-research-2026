/**
 * Statistics of the sprint-risk alerts and the AI diagnosis. The risk service counts only the projects Plane lets
 * the signed-in user see, so nothing here filters by project.
 */
const RISK_API = "/risk/api/v1/insights";

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

export async function fetchRiskInsights<T>(path: string): Promise<T | null> {
  const response = await fetch(`${RISK_API}/${path}`, { credentials: "same-origin" });
  // Plane's web app answers with its HTML page when the /risk route is not deployed: no data, not an error
  if (response.ok && !response.headers.get("content-type")?.includes("application/json")) return null;
  if (!response.ok) throw new Error(String(response.status));
  return (await response.json()) as T;
}
