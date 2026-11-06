/**
 * Home: sprint-risk alerts nobody has decided on yet, highest score first. It reads the risk service, which lists
 * only the projects Plane lets the signed-in user see; with no alerts, or no risk service, nothing is rendered.
 */
import Link from "next/link";
import useSWR from "swr";
import { useTranslation } from "@plane/i18n";
import { fetchRiskInsights } from "@/components/analytics/delivery-risk/risk-insights";
import type { TRiskPending } from "@/components/analytics/delivery-risk/risk-insights";

export function RiskPendingWidget(props: { workspaceSlug: string }) {
  const { workspaceSlug } = props;
  const { t } = useTranslation();
  const { data } = useSWR("risk-insights-pending", () => fetchRiskInsights<TRiskPending[]>("pending?limit=8"));
  if (!data || data.length === 0) return null;
  const action = (a: string) => {
    const key = `risk_insights.action_${a}`;
    const text = t(key);
    return text === key ? a : text;
  };
  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-body-md-medium text-secondary">{t("risk_insights.home_title")}</h2>
        <Link href={`/${workspaceSlug}/analytics/delivery-risk`} className="text-body-xs-regular text-accent-primary">
          {t("risk_insights.home_more")}
        </Link>
      </div>
      <div className="flex flex-col gap-1">
        {data.map((a) => (
          <Link
            key={a.work_item_id}
            href={`/${workspaceSlug}/projects/${a.project_id}/issues/${a.work_item_id}`}
            className="flex flex-col gap-0.5 rounded-md px-3 py-2 hover:bg-layer-1"
          >
            <div className="flex items-center gap-2 text-body-sm-medium text-primary">
              <span>{a.issue_key}</span>
              <span className="text-body-xs-regular text-tertiary">
                {a.rank}/{a.size} · {a.score.toFixed(2)} · {action(a.action_type)}
              </span>
            </div>
            <div className="truncate text-body-xs-regular text-tertiary">
              {a.cause_label
                ? `${a.cause_label}${a.reason ? `: ${a.reason}` : ""}`
                : t(a.diagnosed ? "risk_insights.unknown" : "risk_insights.undiagnosed")}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
