/**
 * Monitoring page for the sprint-risk AI: what it flagged, why, what people decided, what it cost, and whether its
 * reasons are grounded in evidence. Numbers come from the risk service (see risk-insights.ts).
 */
import { observer } from "mobx-react";
import useSWR from "swr";
import { useTranslation } from "@plane/i18n";
import { useAnalytics } from "@/hooks/store/use-analytics";
import { useProject } from "@/hooks/store/use-project";
import AnalyticsWrapper from "../analytics-wrapper";
import AnalyticsSectionWrapper from "../analytics-section-wrapper";
import { fetchRiskInsights } from "./risk-insights";
import type { TRiskSummary } from "./risk-insights";
import { SprintPlans } from "./sprint-plans";

function Kpi(props: { label: string; value: string; hint?: string }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="text-body-xs-regular text-tertiary">{props.label}</div>
      <div className="text-h4-bold text-primary">{props.value}</div>
      {props.hint && <div className="text-body-xs-regular text-tertiary">{props.hint}</div>}
    </div>
  );
}

function Bars(props: { rows: { label: string; value: number }[]; empty: string }) {
  const max = Math.max(1, ...props.rows.map((r) => r.value));
  if (props.rows.length === 0) return <p className="text-body-sm-regular text-tertiary">{props.empty}</p>;
  return (
    <div className="flex flex-col gap-2">
      {props.rows.map((r) => (
        <div key={r.label} className="flex items-center gap-3 text-body-sm-regular">
          <div className="w-56 shrink-0 truncate text-secondary" title={r.label}>
            {r.label}
          </div>
          <div className="h-2 flex-1 rounded bg-layer-1">
            <div className="h-2 rounded bg-accent-primary" style={{ width: `${(r.value / max) * 100}%` }} />
          </div>
          <div className="w-10 text-right text-primary">{r.value}</div>
        </div>
      ))}
    </div>
  );
}

const pct = (n: number, d: number) => (d ? `${Math.round((n / d) * 100)}%` : "–");

export const DeliveryRisk = observer(function DeliveryRisk() {
  const { t } = useTranslation();
  const { getPartialProjectById } = useProject();
  const { selectedProjects } = useAnalytics(); // the "All projects" filter of the Analytics header
  const query = selectedProjects.length ? `?${selectedProjects.map((id) => `project_ids=${id}`).join("&")}` : "";
  const { data, error, isLoading } = useSWR(`risk-insights-summary${query}`, () =>
    fetchRiskInsights<TRiskSummary>(`summary${query}`)
  );
  // "action_nudge_owner" -> its translation; an unknown key (a cause added later) shows as the raw key
  const label = (prefix: string, key: string) => {
    const k = `risk_insights.${prefix}_${key}`;
    const text = t(k);
    return text === k ? key : text;
  };

  if (isLoading) return <AnalyticsWrapper i18nTitle="risk_insights.title">…</AnalyticsWrapper>;
  if (error)
    return (
      <AnalyticsWrapper i18nTitle="risk_insights.title">
        <p className="text-body-sm-regular text-danger-primary">{t("risk_insights.error")}</p>
      </AnalyticsWrapper>
    );
  if (!data || data.alerts.total === 0)
    return (
      <AnalyticsWrapper i18nTitle="risk_insights.title">
        <p className="text-body-sm-regular text-tertiary">{t("risk_insights.empty")}</p>
      </AnalyticsWrapper>
    );

  const { alerts, ai } = data;
  const undiagnosed = data.causes.find((c) => c.cause === "undiagnosed")?.n ?? 0;
  const decided = alerts.approved + alerts.dismissed;
  const days = data.decisions_by_day;
  const maxDay = Math.max(1, ...days.map((d) => d.approve + d.reject + d.undo));
  const asRows = (m: Record<string, number>, prefix: string) =>
    Object.entries(m)
      .sort((a, b) => b[1] - a[1])
      .map(([k, v]) => ({ label: label(prefix, k), value: v }));

  return (
    <AnalyticsWrapper i18nTitle="risk_insights.title">
      <div className="flex flex-col gap-14">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-3 lg:grid-cols-6">
          <Kpi label={t("risk_insights.kpi_alerts")} value={String(alerts.total)} />
          <Kpi label={t("risk_insights.kpi_pending")} value={String(alerts.pending)} />
          <Kpi
            label={t("risk_insights.kpi_acceptance")}
            value={data.acceptance_rate === null ? "–" : `${Math.round(data.acceptance_rate * 100)}%`}
            hint={t("risk_insights.hint_decided", { count: alerts.approved, total: decided })}
          />
          <Kpi
            label={t("risk_insights.kpi_unknown")}
            value={pct(ai.unknown, ai.diagnosed)}
            hint={t("risk_insights.hint_checked", { count: ai.unknown, total: ai.diagnosed })}
          />
          <Kpi label={t("risk_insights.kpi_cost")} value={ai.cost_usd.toFixed(4)} />
          <Kpi label={t("risk_insights.kpi_failed")} value={String(ai.calls_failed)} />
        </div>

        <SprintPlans />

        <div className="grid grid-cols-1 gap-14 lg:grid-cols-2">
          <AnalyticsSectionWrapper title={t("risk_insights.sec_causes")}>
            <Bars
              rows={data.causes
                .filter((c) => c.cause !== "undiagnosed")
                .map((c) => ({
                  label: c.cause === "unknown" ? t("risk_insights.unknown") : label("cause", c.cause),
                  value: c.n,
                }))}
              empty={t("risk_insights.no_data")}
            />
            {undiagnosed > 0 && (
              <p className="mt-3 text-body-xs-regular text-tertiary">
                {t("risk_insights.not_checked_note", { count: undiagnosed })}
              </p>
            )}
          </AnalyticsSectionWrapper>

          <AnalyticsSectionWrapper title={t("risk_insights.sec_actions")}>
            <table className="w-full text-body-sm-regular">
              <thead className="text-left text-tertiary">
                <tr>
                  <th className="pb-2 font-medium">{t("risk_insights.col_action")}</th>
                  <th className="pb-2 text-right font-medium">{t("risk_insights.col_total")}</th>
                  <th className="pb-2 text-right font-medium">{t("risk_insights.col_approved")}</th>
                  <th className="pb-2 text-right font-medium">{t("risk_insights.col_dismissed")}</th>
                  <th className="pb-2 text-right font-medium">{t("risk_insights.col_pending")}</th>
                </tr>
              </thead>
              <tbody>
                {data.actions.map((a) => (
                  <tr key={a.action_type} className="border-t border-subtle">
                    <td className="py-2 text-secondary">{label("action", a.action_type)}</td>
                    <td className="py-2 text-right">{a.total}</td>
                    <td className="py-2 text-right">{a.approved}</td>
                    <td className="py-2 text-right">{a.dismissed}</td>
                    <td className="py-2 text-right">{a.pending}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-3 text-body-xs-regular text-tertiary">
              {t("risk_insights.undone")}: {data.undone}
            </p>
          </AnalyticsSectionWrapper>
        </div>

        <div className="grid grid-cols-1 gap-14 lg:grid-cols-2">
          <AnalyticsSectionWrapper title={t("risk_insights.sec_quality")}>
            <div className="mb-6 grid grid-cols-3 gap-6">
              <Kpi label={t("risk_insights.diagnosed")} value={String(ai.diagnosed)} />
              <Kpi
                label={t("risk_insights.kept")}
                value={String(ai.hypotheses_kept)}
                hint={pct(ai.hypotheses_kept, ai.hypotheses_kept + ai.hypotheses_dropped)}
              />
              <Kpi label={t("risk_insights.dropped")} value={String(ai.hypotheses_dropped)} />
            </div>
            <p className="mb-2 text-body-sm-medium text-secondary">{t("risk_insights.sec_evidence")}</p>
            <Bars rows={asRows(ai.evidence_kinds, "kind")} empty={t("risk_insights.no_data")} />
            <p className="mt-6 mb-2 text-body-sm-medium text-secondary">{t("risk_insights.sec_notes")}</p>
            <Bars rows={asRows(ai.notes, "note")} empty={t("risk_insights.no_data")} />
            <p className="mt-6 mb-2 text-body-sm-medium text-secondary">{t("risk_insights.models")}</p>
            <Bars
              rows={Object.entries(ai.models).map(([name, value]) => ({ label: name, value }))}
              empty={t("risk_insights.no_data")}
            />
          </AnalyticsSectionWrapper>

          <div className="flex flex-col gap-14">
            <AnalyticsSectionWrapper title={t("risk_insights.sec_time")}>
              {days.length === 0 ? (
                <p className="text-body-sm-regular text-tertiary">{t("risk_insights.no_data")}</p>
              ) : (
                <>
                  <div className="flex h-32 items-end gap-2">
                    {days.map((d) => (
                      <div
                        key={d.day}
                        className="flex flex-1 flex-col-reverse"
                        title={`${d.day}: ${d.approve} / ${d.reject} / ${d.undo}`}
                        style={{ height: `${((d.approve + d.reject + d.undo) / maxDay) * 100}%` }}
                      >
                        <div className="bg-success-primary" style={{ flex: d.approve }} />
                        <div className="bg-layer-3" style={{ flex: d.reject }} />
                        <div className="bg-warning-primary" style={{ flex: d.undo }} />
                      </div>
                    ))}
                  </div>
                  <div className="mt-2 flex gap-4 text-body-xs-regular text-tertiary">
                    <span className="text-success-primary">■ {t("risk_insights.approve")}</span>
                    <span>■ {t("risk_insights.reject")}</span>
                    <span className="text-warning-primary">■ {t("risk_insights.undo")}</span>
                    <span className="ml-auto">
                      {days[0].day} → {days[days.length - 1].day}
                    </span>
                  </div>
                </>
              )}
            </AnalyticsSectionWrapper>

            <AnalyticsSectionWrapper title={t("risk_insights.sec_projects")}>
              <table className="w-full text-body-sm-regular">
                <thead className="text-left text-tertiary">
                  <tr>
                    <th className="pb-2 font-medium" />
                    <th className="pb-2 text-right font-medium">{t("risk_insights.col_alerts")}</th>
                    <th className="pb-2 text-right font-medium">{t("risk_insights.col_pending")}</th>
                  </tr>
                </thead>
                <tbody>
                  {data.projects.map((p) => (
                    <tr key={p.project_id} className="border-t border-subtle">
                      <td className="py-2 text-secondary">{getPartialProjectById(p.project_id)?.name ?? p.project_id}</td>
                      <td className="py-2 text-right">{p.total}</td>
                      <td className="py-2 text-right">{p.pending}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </AnalyticsSectionWrapper>
          </div>
        </div>
      </div>
    </AnalyticsWrapper>
  );
});
