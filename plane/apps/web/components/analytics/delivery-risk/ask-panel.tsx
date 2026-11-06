/**
 * Ask about delivery risk: one question, one answer. The risk service lets the model call read-only lookups over the
 * alerts, plans and decisions of the projects the user can see; it cannot change anything. The lookups behind the
 * answer are listed under it so a reader can see what it rests on.
 */
import { useState } from "react";
import { Button } from "@makeplane/propel/components/button";
import { useTranslation } from "@plane/i18n";
import AnalyticsSectionWrapper from "../analytics-section-wrapper";
import { askRisk } from "./risk-insights";
import type { TRiskAnswer } from "./risk-insights";

export function AskPanel() {
  const { t } = useTranslation();
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState<string | null>(null);
  const [result, setResult] = useState<TRiskAnswer | null>(null);
  const send = async () => {
    setBusy(true);
    setFailed(null);
    try {
      setResult(await askRisk(question.trim()));
    } catch (e) {
      setResult(null);
      setFailed((e as Error).message === "503" ? t("risk_insights.ask_off") : t("risk_insights.ask_failed"));
    } finally {
      setBusy(false);
    }
  };
  return (
    <AnalyticsSectionWrapper title={t("risk_insights.sec_ask")}>
      <div className="flex flex-col gap-3">
        <div className="flex gap-2">
          <input
            className="flex-1 rounded border border-subtle bg-surface-1 px-3 py-2 text-body-sm-regular text-primary"
            value={question}
            maxLength={500}
            placeholder={t("risk_insights.ask_placeholder")}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && question.trim().length >= 3 && !busy && void send()}
          />
          <Button
            type="button"
            stretch="auto"
            variant="primary"
            size="md"
            disabled={busy || question.trim().length < 3}
            onClick={() => void send()}
            label={busy ? t("risk_insights.ask_busy") : t("risk_insights.ask_send")}
          />
        </div>
        {failed && <p className="text-body-sm-regular text-danger-primary">{failed}</p>}
        {result && (
          <div className="flex flex-col gap-2">
            <p className="whitespace-pre-wrap text-body-sm-regular text-primary">{result.answer}</p>
            <p className="text-body-xs-regular text-tertiary">
              {t("risk_insights.ask_used")}: {result.tools.map((u) => u.name).join(", ") || "–"} · {result.cost_usd.toFixed(5)} USD
            </p>
          </div>
        )}
      </div>
    </AnalyticsSectionWrapper>
  );
}
