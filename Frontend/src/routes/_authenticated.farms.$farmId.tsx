import { createFileRoute, Link } from "@tanstack/react-router";
import { Plus } from "lucide-react";
import { useFarm } from "@/lib/queries";
import { useAuth } from "@/lib/auth-context";
import { CreateSeasonDialog } from "@/components/forms/create-season-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const Route = createFileRoute("/_authenticated/farms/$farmId")({
  ssr: false,
  component: FarmDetailPage,
});

function FarmDetailPage() {
  const { farmId } = Route.useParams();
  const { user } = useAuth();
  const { data, isLoading, error } = useFarm(farmId);

  const canManage = user?.role === "admin" || user?.role === "sacco_admin";

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading farm…</p>;
  if (error || !data) return <p className="text-sm text-destructive">Failed to load farm.</p>;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Farm</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
            {data.name}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {data.county} · {data.acreage} acres · {data.latitude.toFixed(4)},{" "}
            {data.longitude.toFixed(4)}
          </p>
          <Link
            to="/farmers/$farmerId"
            params={{ farmerId: data.farmer_id }}
            className="mt-2 inline-block text-xs text-primary hover:underline"
          >
            ← Back to farmer
          </Link>
        </div>
        {canManage ? (
          <CreateSeasonDialog
            farmId={farmId}
            trigger={
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Start season
              </Button>
            }
          />
        ) : null}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Seasons</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          A farm-level season list endpoint isn't in the integration guide. Open a season directly
          by ID, or start a new one with the button above.
        </CardContent>
      </Card>
    </div>
  );
}
