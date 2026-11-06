/**
 * Sprint plans: for a running sprint, how many open work items will probably not finish (from the earlier sprints of the
 * project) and which ones to move to the next cycle, each with its reason. A person picks the rows, then moves them in
 * one step; every move can be undone. The risk service lists only the plans of the projects the user can see.
 */
import { useState } from "react";
import { observer } from "mobx-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import useSWR from "swr";
import { Button } from "@makeplane/propel/components/button";
import { setToast } from "@plane/blocks/toast";
import { useTranslation } from "@plane/i18n";
import { useProject } from "@/hooks/store/use-project";
import AnalyticsSectionWrapper from "../analytics-section-wrapper";
import { fetchRiskPlans, postRiskPlan } from "./risk-insights";
import type { TRiskPlan } from "./risk-insights";

function PlanCard(props: { plan: TRiskPlan; workspaceSlug: string; onChange: (plan: TRiskPlan) => void }) {
  const { plan, workspaceSlug, onChange } = props;
  const { t } = useTranslation();
  const { getPartialProjectById } = useProject();
  const pending = plan.items.filter((i) => i.state === "pending");
  const decided = plan.items.filter((i) => i.state !== "pending");
  // rows ticked by the person; a pending row is ticked until they untick it
  const [unticked, setUnticked] = useState<Set<string>>(new Set());
  const [busy, setBusy] = useState(false);
  const chosen = pending.filter((i) => !unticked.has(i.work_item_id)).map((i) => i.work_item_id);
  const cause = (key: string | null) => {
    if (!key) return t("risk_insights.plan_no_reason");
    const k = `risk_insights.cause_${key}`;
    return t(k) === k ? key : t(k);
  };
  const run = async (action: "decision" | "undo", body: object) => {
    setBusy(true);
    try {
      const updated = await postRiskPlan(plan.id, action, body);
      onChange(updated);
      const refused = Object.keys(updated.errors).length;
      if (refused) setToast({ type: "error", title: t("risk_insights.sec_plans"), message: t("risk_insights.plan_refused", { count: refused }) });
    } catch {
      setToast({ type: "error", title: t("risk_insights.sec_plans"), message: t("risk_insights.plan_error") });
    } finally {
      setBusy(false);
    }
  };
  const toggle = (id: string) =>
    setUnticked((prev) => {
      const next = new Set(prev);
      if (!next.delete(id)) next.add(id);
      return next;
    });
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
            <th className="w-8 pb-2" />
            <th className="pb-2 font-medium">{t("risk_insights.col_issue")}</th>
            <th className="pb-2 font-medium">{t("risk_insights.col_reason")}</th>
            <th className="pb-2 text-right font-medium">{t("risk_insights.col_risk")}</th>
          </tr>
        </thead>
        <tbody>
          {plan.items.map((item) => (
            <tr key={item.work_item_id} className="border-t border-subtle align-top">
              <td className="py-2 pr-2">
                {item.state === "pending" ? (
                  <input
                    type="checkbox"
                    checked={!unticked.has(item.work_item_id)}
                    onChange={() => toggle(item.work_item_id)}
                    disabled={busy}
                    aria-label={item.issue_key}
                  />
                ) : null}
              </td>
              <td className="py-2 pr-3">
                <Link
                  href={`/${workspaceSlug}/projects/${plan.project_id}/issues/${item.work_item_id}`}
                  className="text-accent-primary"
                >
                  {item.issue_key}
                </Link>
                {item.state !== "pending" && (
                  <div className="text-body-xs-regular text-tertiary">
                    {t(`risk_insights.plan_state_${item.state}`)}
                  </div>
                )}
              </td>
              <td className="py-2 pr-3 text-secondary">
                {item.why === "follows" ? item.reason : `${cause(item.cause)}${item.reason ? `: ${item.reason}` : ""}`}
              </td>
              <td className="py-2 text-right">{item.score.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex gap-2">
        {pending.length > 0 && (
          <>
            <Button
              type="button"
              stretch="auto"
              variant="primary"
              size="md"
              disabled={busy || chosen.length === 0}
              onClick={() => run("decision", { decision: "approve", work_item_ids: chosen })}
              label={t("risk_insights.plan_approve", { count: chosen.length })}
            />
            <Button
              type="button"
              stretch="auto"
              variant="secondary"
              size="md"
              disabled={busy || chosen.length === 0}
              onClick={() => run("decision", { decision: "reject", work_item_ids: chosen })}
              label={t("risk_insights.plan_dismiss")}
            />
          </>
        )}
        {decided.length > 0 && (
          <Button
            type="button"
            stretch="auto"
            variant="secondary"
            size="md"
            disabled={busy}
            onClick={() => run("undo", { work_item_ids: decided.map((i) => i.work_item_id) })}
            label={t("risk_insights.plan_undo")}
          />
        )}
      </div>
    </div>
  );
}

export const SprintPlans = observer(function SprintPlans() {
  const { t } = useTranslation();
  const { workspaceSlug } = useParams();
  const { data, mutate } = useSWR("risk-plans", () => fetchRiskPlans());
  if (!data || data.length === 0 || !workspaceSlug) return null;
  return (
    <AnalyticsSectionWrapper title={t("risk_insights.sec_plans")}>
      <div className="flex flex-col gap-6">
        {data.map((plan) => (
          <PlanCard
            key={plan.id}
            plan={plan}
            workspaceSlug={workspaceSlug.toString()}
            onChange={(updated) => mutate(data.map((p) => (p.id === updated.id ? updated : p)), { revalidate: false })}
          />
        ))}
      </div>
    </AnalyticsSectionWrapper>
  );
});
