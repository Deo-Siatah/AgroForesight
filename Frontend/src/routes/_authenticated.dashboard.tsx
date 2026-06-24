import { createFileRoute, Link } from "@tanstack/react-router";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Building2, ArrowRight, History, UserCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  PortfolioRiskOverview,
  RecentRecommendations,
  RecentRiskAssessments,
} from "@/components/dashboard-widgets";
import { GlobalGenerateRecommendation } from "@/components/global-generate-recommendation";

export const Route = createFileRoute("/_authenticated/dashboard")({
  ssr: false,
  component: DashboardPage,
});

function DashboardPage() {
  const { user } = useAuth();
  if (!user) return null;

  const scopeLabel =
    user.role === "admin"
      ? "All SACCOs"
      : user.role === "sacco_admin"
        ? "Your SACCO"
        : user.role === "farmer"
          ? "Personal account"
          : "—";

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Welcome back</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Signed in as <span className="font-medium text-foreground">{user.email}</span>
          </p>
        </div>
        <Badge className="bg-accent text-accent-foreground">{scopeLabel}</Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {user.role === "admin" ? (
          <ActionCard
            icon={<Building2 className="h-5 w-5" />}
            title="SACCOs"
            description="Create and manage cooperative lending societies."
            to="/saccos"
            cta="Manage SACCOs"
          />
        ) : null}

        {user.role === "sacco_admin" && user.sacco_id ? (
          <ActionCard
            icon={<Building2 className="h-5 w-5" />}
            title="Your SACCO"
            description="View members, register farmers, manage portfolio."
            to="/saccos/$saccoId"
            params={{ saccoId: user.sacco_id }}
            cta="Open SACCO"
          />
        ) : null}

        {user.role === "farmer" && user.farmer_id ? (
          <ActionCard
            icon={<UserCircle className="h-5 w-5" />}
            title="Your profile"
            description="See your farms, seasons, and loans."
            to="/farmers/$farmerId"
            params={{ farmerId: user.farmer_id }}
            cta="View profile"
          />
        ) : null}

        {(user.role === "admin" || user.role === "sacco_admin") && (
          <ActionCard
            icon={<History className="h-5 w-5" />}
            title="Risk history"
            description="Browse historical AI risk assessments."
            to="/risk-assessments"
            cta="Open history"
          />
        )}
      </div>

      {(user.role === "admin" || user.role === "sacco_admin") && (
        <div className="space-y-6">
          <GlobalGenerateRecommendation />
          <PortfolioRiskOverview />
          <div className="grid gap-6 lg:grid-cols-2">
            <RecentRecommendations />
            <RecentRiskAssessments />
          </div>
        </div>
      )}



      <Card>
        <CardHeader>
          <CardTitle>API base</CardTitle>
          <CardDescription>
            Override at build time with <code className="rounded bg-muted px-1.5 py-0.5 text-xs">VITE_API_BASE</code>.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <code className="text-xs text-muted-foreground">
            {import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000/api/v1"}
          </code>
        </CardContent>
      </Card>
    </div>
  );
}

function ActionCard({
  icon,
  title,
  description,
  to,
  params,
  cta,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  to: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  params?: any;
  cta: string;
}) {
  return (
    <Card>
      <CardContent className="space-y-4 p-5">
        <div className="flex items-center gap-2">
          <div className="rounded-md bg-accent p-2 text-accent-foreground">{icon}</div>
          <p className="font-medium text-foreground">{title}</p>
        </div>
        <p className="text-sm text-muted-foreground">{description}</p>
        <Button asChild variant="outline" size="sm">
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          <Link to={to as any} params={params}>
            {cta}
            <ArrowRight className="ml-1 h-4 w-4" />
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
