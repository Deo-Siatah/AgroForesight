import { createFileRoute, Link } from "@tanstack/react-router";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Building2, ArrowRight, History, MapPin, Sprout, Wallet } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  PortfolioRiskOverview,
  RecentRecommendations,
  RecentRiskAssessments,
} from "@/components/dashboard-widgets";
import { GlobalGenerateRecommendation } from "@/components/global-generate-recommendation";
import { useFarmerProfile } from "@/lib/queries";
import { LoanStatusBadge, SeasonStatusBadge } from "@/components/status-badge";

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
          <FarmerDashboard farmerId={user.farmer_id} />
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

function FarmerDashboard({ farmerId }: { farmerId: string }) {
  const { data, isLoading } = useFarmerProfile(farmerId);

  if (isLoading) {
    return <div className="col-span-3 h-32 animate-pulse rounded-lg bg-muted" />;
  }

  const farms = data?.farms ?? [];
  const loans = data?.loans ?? [];
  const activeLoans = loans.filter((l) => l.status === "active" || l.status === "disbursed");
  const pendingLoans = loans.filter((l) => l.status === "pending");

  return (
    <div className="col-span-full space-y-6">
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="rounded-md bg-accent p-2 text-accent-foreground">
              <MapPin className="h-5 w-5" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-foreground">{farms.length}</p>
              <p className="text-sm text-muted-foreground">Farm{farms.length !== 1 ? "s" : ""}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="rounded-md bg-accent p-2 text-accent-foreground">
              <Wallet className="h-5 w-5" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-foreground">{activeLoans.length}</p>
              <p className="text-sm text-muted-foreground">Active loan{activeLoans.length !== 1 ? "s" : ""}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="rounded-md bg-accent p-2 text-accent-foreground">
              <Sprout className="h-5 w-5" />
            </div>
            <div>
              <p className="text-2xl font-semibold text-foreground">{pendingLoans.length}</p>
              <p className="text-sm text-muted-foreground">Pending loan{pendingLoans.length !== 1 ? "s" : ""}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {farms.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Your farms</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {farms.map((farm) => (
              <div key={farm.id} className="flex items-center justify-between rounded-md border p-3">
                <div>
                  <p className="text-sm font-medium text-foreground">{farm.name}</p>
                  <p className="text-xs text-muted-foreground">{farm.county} · {farm.acreage} acres</p>
                </div>
                <Button asChild variant="ghost" size="sm">
                  <Link to="/farms/$farmId" params={{ farmId: farm.id }}>
                    View <ArrowRight className="ml-1 h-3 w-3" />
                  </Link>
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {loans.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Your loans</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {loans.map((loan) => (
              <div key={loan.id} className="flex items-center justify-between rounded-md border p-3">
                <div>
                  <p className="text-sm font-medium text-foreground">KES {Number(loan.amount).toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground">{new Date(loan.created_at).toLocaleDateString()}</p>
                </div>
                <div className="flex items-center gap-2">
                  <LoanStatusBadge status={loan.status} />
                  <Button asChild variant="ghost" size="sm">
                    <Link to="/loans/$loanId" params={{ loanId: loan.id }}>
                      View <ArrowRight className="ml-1 h-3 w-3" />
                    </Link>
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
