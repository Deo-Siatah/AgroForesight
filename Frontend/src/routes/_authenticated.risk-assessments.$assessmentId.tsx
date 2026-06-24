import { createFileRoute, Link } from "@tanstack/react-router";
import { useRiskAssessment } from "@/lib/queries";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RiskLevelBadge } from "@/components/status-badge";

export const Route = createFileRoute("/_authenticated/risk-assessments/$assessmentId")({
  ssr: false,
  component: RiskAssessmentDetailPage,
});

function RiskAssessmentDetailPage() {
  const { assessmentId } = Route.useParams();
  const { data, isLoading, error } = useRiskAssessment(assessmentId);

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading assessment…</p>;
  if (error || !data) return <p className="text-sm text-destructive">Failed to load assessment.</p>;

  const breakdown: [string, number | undefined][] = [
    ["Weather", data.weather_risk],
    ["Season", data.season_risk],
    ["Harvest", data.harvest_risk],
    ["Financial", data.financial_risk],
    ["Farmer", data.farmer_risk],
  ];
  const present = breakdown.filter(([, v]) => typeof v === "number");

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs uppercase tracking-wide text-muted-foreground">Risk assessment</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
          Score {data.score}
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {new Date(data.created_at).toLocaleString()}
        </p>
      </div>

      <div className="flex items-center gap-3">
        <RiskLevelBadge level={data.risk_level} />
        {data.action ? (
          <span className="text-sm text-muted-foreground">
            System action:{" "}
            <span className="font-medium text-foreground">{data.action}</span>
          </span>
        ) : null}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Linked loan</CardTitle>
        </CardHeader>
        <CardContent>
          <Link
            to="/loans/$loanId"
            params={{ loanId: data.loan_id }}
            className="font-mono text-sm text-primary hover:underline"
          >
            {data.loan_id}
          </Link>
        </CardContent>
      </Card>

      {present.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Risk breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
              {present.map(([label, value]) => (
                <div key={label} className="rounded-md border border-border bg-muted/30 p-3">
                  <p className="text-[10px] uppercase tracking-wide text-muted-foreground">
                    {label}
                  </p>
                  <p className="mt-1 text-lg font-semibold text-foreground">{value}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
