import { createFileRoute, Link } from "@tanstack/react-router";
import { Plus, MapPin, Wallet } from "lucide-react";
import { useFarmerProfile } from "@/lib/queries";
import { useAuth } from "@/lib/auth-context";
import { CreateFarmDialog } from "@/components/forms/create-farm-dialog";
import { CreateLoanDialog } from "@/components/forms/create-loan-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoanStatusBadge } from "@/components/status-badge";

export const Route = createFileRoute("/_authenticated/farmers/$farmerId")({
  ssr: false,
  component: FarmerProfilePage,
});

function FarmerProfilePage() {
  const { farmerId } = Route.useParams();
  const { user } = useAuth();
  const { data, isLoading, error } = useFarmerProfile(farmerId);

  const canManage = user?.role === "admin" || user?.role === "sacco_admin";

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading farmer profile…</p>;
  }
  if (error || !data) {
    return <p className="text-sm text-destructive">Failed to load farmer.</p>;
  }

  const { farmer, farms, loans } = data;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Farmer</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
            {farmer.first_name} {farmer.last_name}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {farmer.phone}
            {farmer.national_id ? ` · ID ${farmer.national_id}` : ""}
          </p>
        </div>
        {canManage ? (
          <div className="flex gap-2">
            <CreateFarmDialog
              farmerId={farmerId}
              trigger={
                <Button variant="outline">
                  <Plus className="mr-2 h-4 w-4" /> Add farm
                </Button>
              }
            />
            <CreateLoanDialog
              farmerId={farmerId}
              trigger={
                <Button>
                  <Plus className="mr-2 h-4 w-4" /> Create loan
                </Button>
              }
            />
          </div>
        ) : null}
      </div>

      <section className="space-y-3">
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-primary" />
          <h2 className="text-lg font-semibold text-foreground">Farms</h2>
        </div>
        {farms.length === 0 ? (
          <EmptyCard text="No farms registered." />
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {farms.map((f) => (
              <Card key={f.id}>
                <CardContent className="space-y-2 p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <Link
                        to="/farms/$farmId"
                        params={{ farmId: f.id }}
                        className="font-medium text-foreground hover:underline"
                      >
                        {f.name}
                      </Link>
                      <p className="text-xs text-muted-foreground">{f.county}</p>
                    </div>
                    <p className="text-sm font-medium text-primary">{f.acreage} ac</p>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {f.latitude.toFixed(3)}, {f.longitude.toFixed(3)}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </section>

      <section className="space-y-3">
        <div className="flex items-center gap-2">
          <Wallet className="h-4 w-4 text-primary" />
          <h2 className="text-lg font-semibold text-foreground">Loans</h2>
        </div>
        {loans.length === 0 ? (
          <EmptyCard text="No loans yet." />
        ) : (
          <Card>
            <CardContent className="divide-y divide-border p-0">
              {loans.map((l) => (
                <Link
                  key={l.id}
                  to="/loans/$loanId"
                  params={{ loanId: l.id }}
                  className="flex items-center justify-between gap-4 px-5 py-3 transition-colors hover:bg-muted/50"
                >
                  <div>
                    <p className="font-medium text-foreground">KES {l.amount}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(l.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    {typeof l.risk_score === "number" ? (
                      <span className="text-sm text-muted-foreground">
                        Risk <span className="font-medium text-foreground">{l.risk_score}</span>
                      </span>
                    ) : (
                      <span className="text-xs text-muted-foreground">No risk score</span>
                    )}
                    <LoanStatusBadge status={l.status} />
                  </div>
                </Link>
              ))}
            </CardContent>
          </Card>
        )}
      </section>
    </div>
  );
}

function EmptyCard({ text }: { text: string }) {
  return (
    <Card>
      <CardContent className="p-6 text-center text-sm text-muted-foreground">{text}</CardContent>
    </Card>
  );
}

// Optional empty CardHeader/CardTitle exports to keep types happy when used elsewhere.
export { CardHeader, CardTitle };
