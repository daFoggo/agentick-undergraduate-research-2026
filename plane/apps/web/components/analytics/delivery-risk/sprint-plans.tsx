/**
 * Sprint plans: for a running sprint, how many open work items will probably not finish (from the earlier sprints of the
 * project) and which ones to move to the next cycle, each with its reason. The risk service lists only the plans of the
 * projects the signed-in user can see.
 */
import { observer } from "mobx-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import useSWR from "swr";
import { useTranslation } from "@plane/i18n";
import { useProject } from "@/hooks/store/use-project";
import AnalyticsSectionWrapper from "../analytics-section-wrapper";
import { fetchRiskPlans } from "./risk-insights";
import type { TRiskPlan } from "./risk-insights";

function PlanCard(props: { plan: TRiskPlan; workspaceSlug: string }) {
  const { plan, workspaceSlug } = props;
  const { t } = useTranslation();
  const { getPartialProjectById } = useProject();
  const cause = (key: string | null) => {
    if (!key) return t("risk_insights.plan_no_reason");
    const k = `risk_insights.cause_${key}`;
    return t(k) === k ? key : t(k);
  };
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-subtle p-4">
      <div>
        <div className="text-body-md-medium text-primary">
          {t("risk_insights.plan_headline", { name: plan.sprint_name, budget: plan.budget, open: plan.open_count })}
        </div>
        <div className="mt-1 text-body-xs-regular text-tertiary">
          {t("risk_insights.plan_basis", {
            sprints: plan.history_sprints,
            share: Math.round(plan.unfinished_share * 100),
            mark: Math.round(plan.mark * 100),
          })}
          {getPartialProjectById(plan.project_id)?.name ? ` · ${getPartialProjectById(plan.project_id)?.name}` : ""}
        </div>
      </div>
      <p className="text-body-sm-regular text-secondary">{t("risk_insights.plan_move", { count: plan.items.length })}</p>
      <table className="w-full text-body-sm-regular">
        <thead className="text-left text-tertiary">
          <tr>
            <th className="pb-2 font-medium">{t("risk_insights.col_issue")}</th>
            <th className="pb-2 font-medium">{t("risk_insights.col_reason")}</th>
            <th className="pb-2 text-right font-medium">{t("risk_insights.col_risk")}</th>
          </tr>
        </thead>
        <tbody>
          {plan.items.map((item) => (
            <tr key={item.work_item_id} className="border-t border-subtle align-top">
              <td className="py-2 pr-3">
                <Link
                  href={`/${workspaceSlug}/projects/${plan.project_id}/issues/${item.work_item_id}`}
                  className="text-accent-primary"
                >
                  {item.issue_key}
                </Link>
              </td>
              <td className="py-2 pr-3 text-secondary">
                {item.why === "follows" ? item.reason : `${cause(item.cause)}${item.reason ? `: ${item.reason}` : ""}`}
              </td>
              <td className="py-2 text-right">{item.score.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export const SprintPlans = observer(function SprintPlans() {
  const { t } = useTranslation();
  const { workspaceSlug } = useParams();
  const { data } = useSWR("risk-plans", () => fetchRiskPlans());
  if (!data || data.length === 0 || !workspaceSlug) return null;
  return (
    <AnalyticsSectionWrapper title={t("risk_insights.sec_plans")}>
      <div className="flex flex-col gap-6">
        {data.map((plan) => (
          <PlanCard key={plan.id} plan={plan} workspaceSlug={workspaceSlug.toString()} />
        ))}
      </div>
    </AnalyticsSectionWrapper>
  );
});
