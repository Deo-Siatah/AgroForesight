import { Link } from "@tanstack/react-router";
import { useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PriorityBadge, RiskLevelBadge } from "@/components/status-badge";
import { useRecentRecommendations, useRiskAssessments } from "@/lib/queries";
import { AlertCircle, Sparkles, ShieldCheck } from "lucide-react";

export function PortfolioRiskOverview() {
  const { data, isLoading, error } = useRiskAssessments(0, 100);

  const stats = useMemo(() => {
    if (!data || data.length === 0) return null;
    const latestByLoan = new Map<string, (typeof data)[number]>();
    for (const a of data) {
      const prev = latestByLoan.get(a.loan_id);
      if (!prev || new Date(a.created_at) > new Date(prev.created_at)) {
        latestByLoan.set(a.loan_id, a);
      }
    }
    const list = [...latestByLoan.values()];
    const avg = list.reduce((s, a) => s + a.score, 0) / list.length;
    return {
      avg: Math.round(avg),
      high: list.filter((a) => a.risk_level === "high").length,
      medium: list.filter((a) => a.risk_level === "medium").length,
      low: list.filter((a) => a.risk_level === "low").length,
      total: list.length,
    };
  }, [data]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-primary" />
          <CardTitle>Portfolio risk overview</CardTitle>
        </div>
        <CardDescription>
          Aggregated from latest AI risk assessments per loan.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <SkeletonGrid />
        ) : error || !stats ? (
          <EmptyState
            icon={<AlertCircle className="h-4 w-4" />}
            label={error ? "Failed to load assessments." : "No assessments yet."}
          />
        ) : (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <Metric label="Avg. risk score" value={stats.avg} suffix="/100" />
            <Metric label="High risk" value={stats.high} tone="primary" />
            <Metric label="Medium risk" value={stats.medium} tone="secondary" />
            <Metric label="Low risk" value={stats.low} tone="accent" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function RecentRecommendations() {
  const { data, isLoading } = useRecentRecommendations(5);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <CardTitle>Recent AI recommendations</CardTitle>
        </div>
        <CardDescription>Latest insights generated for active seasons.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          <SkeletonList />
        ) : !data || data.length === 0 ? (
          <EmptyState label="No recommendations yet." />
        ) : (
          data.map((r) => (
            <Link
              key={r.id}
              to="/seasons/$seasonId"
              params={{ seasonId: r.season_id }}
              className="flex items-start justify-between gap-3 rounded-lg border bg-card p-3 transition-colors hover:bg-accent"
            >
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-foreground">{r.title}</p>
                <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">
                  {r.recommendation_text}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {new Date(r.created_at).toLocaleDateString()}
                </p>
              </div>
              <PriorityBadge priority={r.priority} />
            </Link>
          ))
        )}
      </CardContent>
    </Card>
  );
}

export function RecentRiskAssessments() {
  const { data, isLoading, error } = useRiskAssessments(0, 5);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-primary" />
          <CardTitle>Recent risk assessments</CardTitle>
        </div>
        <CardDescription>Most recent AI-powered loan evaluations.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          <SkeletonList />
        ) : error ? (
          <EmptyState label="Failed to load assessments." />
        ) : !data || data.length === 0 ? (
          <EmptyState label="No assessments yet." />
        ) : (
          data.slice(0, 5).map((a) => (
            <Link
              key={a.id}
              to="/risk-assessments/$assessmentId"
              params={{ assessmentId: a.id }}
              className="flex items-center justify-between gap-3 rounded-lg border bg-card p-3 transition-colors hover:bg-accent"
            >
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-foreground">
                  Loan <span className="font-mono text-xs">{a.loan_id.slice(0, 8)}…</span>
                </p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  {a.action ?? "Review recommended"}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {new Date(a.created_at).toLocaleString()}
                </p>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className="text-sm font-semibold text-foreground">{a.score}</span>
                <RiskLevelBadge level={a.risk_level} />
              </div>
            </Link>
          ))
        )}
      </CardContent>
    </Card>
  );
}

function Metric({
  label,
  value,
  suffix,
  tone = "default",
}: {
  label: string;
  value: number;
  suffix?: string;
  tone?: "default" | "primary" | "secondary" | "accent";
}) {
  const toneClass = {
    default: "text-foreground",
    primary: "text-primary",
    secondary: "text-secondary-foreground",
    accent: "text-accent-foreground",
  }[tone];
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className={`mt-1 text-2xl font-semibold ${toneClass}`}>
        {value}
        {suffix ? <span className="ml-0.5 text-sm text-muted-foreground">{suffix}</span> : null}
      </p>
    </div>
  );
}

function SkeletonGrid() {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="h-20 animate-pulse rounded-lg bg-muted" />
      ))}
    </div>
  );
}

function SkeletonList() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="h-16 animate-pulse rounded-lg bg-muted" />
      ))}
    </div>
  );
}

function EmptyState({ icon, label }: { icon?: React.ReactNode; label: string }) {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-dashed bg-muted/30 p-6 text-sm text-muted-foreground">
      {icon}
      <span>{label}</span>
    </div>
  );
}
