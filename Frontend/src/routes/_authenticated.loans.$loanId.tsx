import { createFileRoute, Link } from "@tanstack/react-router";
import { Loader2, Sparkles, Gauge } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import {
  transitionsForLoan,
  useLoan,
  useLoanRiskScore,
  useLoanTransition,
  useRunRiskAssessment,
  type LoanTransition,
} from "@/lib/queries";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { LoanStatusBadge, RiskLevelBadge } from "@/components/status-badge";
import { LoadingSteps } from "@/components/loading-steps";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { ErrorBanner, apiErrorMessage } from "@/components/error-banner";
import type { RiskAssessmentResult, RiskScore } from "@/lib/types";

export const Route = createFileRoute("/_authenticated/loans/$loanId")({
  ssr: false,
  component: LoanDetailPage,
});

function LoanDetailPage() {
  const { loanId } = Route.useParams();
  const { user } = useAuth();
  const canManage = user?.role === "admin" || user?.role === "sacco_admin";

  const { data, isLoading, error, refetch } = useLoan(loanId);
  const score = useLoanRiskScore(loanId, data?.season_id ?? null);
  const assess = useRunRiskAssessment(loanId);

  const [quickScore, setQuickScore] = useState<RiskScore | null>(null);
  const [assessment, setAssessment] = useState<RiskAssessmentResult | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading loan…</p>;
  if (error || !data) return <p className="text-sm text-destructive">Failed to load loan.</p>;

  async function runQuickScore() {
    setPageError(null);
    try {
      const result = await score.mutateAsync();
      setQuickScore(result);
    } catch (err) {
      setPageError(apiErrorMessage(err, "Risk calculation failed."));
    }
  }

  async function runFullAssessment() {
    setPageError(null);
    try {
      const result = await assess.mutateAsync();
      setAssessment(result);
    } catch (err) {
      setPageError(apiErrorMessage(err, "Risk assessment failed."));
    }
  }

  const actions = transitionsForLoan(data.status);

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Loan</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
            KES {data.amount}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Created {new Date(data.created_at).toLocaleString()}
          </p>
          <Link
            to="/farmers/$farmerId"
            params={{ farmerId: data.farmer_id }}
            className="mt-2 inline-block text-xs text-primary hover:underline"
          >
            ← Back to farmer
          </Link>
        </div>
        <LoanStatusBadge status={data.status} />
      </div>

      <ErrorBanner message={pageError} />

      {canManage && actions.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {actions.map((a) => (
            <TransitionButton
              key={a.action}
              loanId={loanId}
              action={a.action}
              label={a.label}
              variant={a.variant}
              onDone={refetch}
            />
          ))}
        </div>
      ) : null}

      <section className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Gauge className="h-4 w-4 text-primary" />
              Quick risk score
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {score.isPending ? (
              <LoadingSteps
                steps={[
                  "Calculating risk score…",
                  "Analyzing weather patterns…",
                  "Evaluating harvest timeline…",
                ]}
              />
            ) : quickScore ? (
              <RiskScoreCard score={quickScore.score} category={quickScore.category} />
            ) : typeof data.risk_score === "number" ? (
              <div className="space-y-2">
                <p className="text-4xl font-semibold text-foreground">{data.risk_score}</p>
                <p className="text-xs text-muted-foreground">Last stored score.</p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No risk score yet.</p>
            )}
            {canManage ? (
              <Button size="sm" variant="outline" disabled={score.isPending} onClick={runQuickScore}>
                {score.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Calculate
              </Button>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Sparkles className="h-4 w-4 text-primary" />
              Full AI assessment
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {assess.isPending ? (
              <LoadingSteps
                steps={[
                  "Calculating risk score…",
                  "Analyzing weather patterns…",
                  "Evaluating harvest timeline…",
                  "Generating AI explanation…",
                ]}
              />
            ) : assessment ? (
              <AssessmentBody result={assessment} />
            ) : (
              <p className="text-sm text-muted-foreground">
                Run the AI engine for a full breakdown and recommended action.
              </p>
            )}
            {canManage ? (
              <Button size="sm" disabled={assess.isPending} onClick={runFullAssessment}>
                {assess.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Run AI assessment
              </Button>
            ) : null}
          </CardContent>
        </Card>
      </section>
    </div>
  );
}

function RiskScoreCard({ score, category }: { score: number; category: "low" | "medium" | "high" }) {
  return (
    <div className="space-y-3">
      <div className="flex items-end gap-3">
        <p className="text-4xl font-semibold text-foreground">{score}</p>
        <RiskLevelBadge level={category} />
      </div>
      <Progress value={Math.min(100, Math.max(0, score))} />
      <p className="text-xs text-muted-foreground">Out of 100. Lower is safer.</p>
    </div>
  );
}

function TransitionButton({
  loanId,
  action,
  label,
  variant,
  onDone,
}: {
  loanId: string;
  action: LoanTransition;
  label: string;
  variant: "default" | "destructive" | "success";
  onDone: () => void;
}) {
  const mut = useLoanTransition(loanId, action);
  const isDestructive = variant === "destructive";

  async function execute() {
    try {
      await mut.mutateAsync();
      toast.success(`${label} succeeded.`);
      onDone();
    } catch (err) {
      toast.error(apiErrorMessage(err, "Transition failed."));
    }
  }

  const trigger = (
    <Button variant={variant} disabled={mut.isPending}>
      {mut.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
      {label}
    </Button>
  );

  if (isDestructive) {
    return (
      <ConfirmDialog
        title={`${label} this loan?`}
        description="This action changes the loan status and cannot be undone."
        confirmLabel={label}
        destructive
        onConfirm={execute}
        trigger={trigger}
      />
    );
  }

  return (
    <Button
      variant={variant}
      disabled={mut.isPending}
      onClick={execute}
    >
      {mut.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
      {label}
    </Button>
  );
}

function AssessmentBody({ result }: { result: RiskAssessmentResult }) {
  const { risk_assessment: r, analysis } = result;
  return (
    <div className="space-y-4">
      <RiskScoreCard score={r.score} category={r.risk_level} />

      <RiskBreakdownPanel
        weatherRisk={r.weather_risk}
        seasonRisk={r.season_risk}
        harvestRisk={r.harvest_risk}
        financialRisk={r.financial_risk}
        farmerRisk={r.farmer_risk}
      />

      <Accordion type="single" collapsible defaultValue="summary">
        <AccordionItem value="summary">
          <AccordionTrigger className="text-sm font-medium">AI explanation</AccordionTrigger>
          <AccordionContent className="space-y-2">
            <p className="text-sm font-medium text-foreground">{analysis.summary}</p>
            <p className="text-sm text-muted-foreground">{analysis.explanation}</p>
          </AccordionContent>
        </AccordionItem>
        {analysis.key_drivers?.length ? (
          <AccordionItem value="drivers">
            <AccordionTrigger className="text-sm font-medium">Key drivers</AccordionTrigger>
            <AccordionContent>
              <ul className="space-y-1">
                {analysis.key_drivers.map((d) => (
                  <li key={d} className="flex items-start gap-2 text-sm text-foreground">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                    {d}
                  </li>
                ))}
              </ul>
            </AccordionContent>
          </AccordionItem>
        ) : null}
      </Accordion>

      <div className="rounded-md border border-border bg-accent/40 p-3">
        <p className="text-xs font-medium uppercase tracking-wide text-accent-foreground">
          Recommended action
        </p>
        <p className="mt-1 text-sm text-foreground">{analysis.recommendation}</p>
        {r.action ? (
          <p className="mt-1 text-xs text-muted-foreground">System action: {r.action}</p>
        ) : null}
      </div>
    </div>
  );
}

function RiskBreakdownPanel({
  weatherRisk,
  seasonRisk,
  harvestRisk,
  financialRisk,
  farmerRisk,
}: {
  weatherRisk?: number;
  seasonRisk?: number;
  harvestRisk?: number;
  financialRisk?: number;
  farmerRisk?: number;
}) {
  const items: [string, number | undefined][] = [
    ["Weather", weatherRisk],
    ["Season", seasonRisk],
    ["Harvest", harvestRisk],
    ["Financial", financialRisk],
    ["Farmer", farmerRisk],
  ];
  const present = items.filter(([, v]) => typeof v === "number") as [string, number][];
  if (present.length === 0) return null;
  return (
    <div className="space-y-3">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        Risk breakdown
      </p>
      <div className="space-y-2">
        {present.map(([label, value]) => (
          <div key={label} className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">{label}</span>
              <span className="font-medium text-foreground">{value}</span>
            </div>
            <Progress value={Math.min(100, Math.max(0, value))} />
          </div>
        ))}
      </div>
    </div>
  );
}
