import { createFileRoute, Link } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useSeason, useSeasonTransition } from "@/lib/queries";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { SeasonStatusBadge } from "@/components/status-badge";
import { ConfirmDialog } from "@/components/confirm-dialog";
import { apiErrorMessage } from "@/components/error-banner";
import { AIRecommendationsSection } from "@/components/ai-recommendations-section";

export const Route = createFileRoute("/_authenticated/seasons/$seasonId")({
  ssr: false,
  component: SeasonDetailPage,
});

function SeasonDetailPage() {
  const { seasonId } = Route.useParams();
  const { user } = useAuth();
  const canManage = user?.role === "admin" || user?.role === "sacco_admin";

  const { data, isLoading, error, refetch } = useSeason(seasonId);
  const activate = useSeasonTransition(seasonId, "active");
  const harvest = useSeasonTransition(seasonId, "harvested");
  const fail = useSeasonTransition(seasonId, "failed");


  if (isLoading) return <p className="text-sm text-muted-foreground">Loading season…</p>;
  if (error || !data) return <p className="text-sm text-destructive">Failed to load season.</p>;

  async function run(mut: { mutateAsync: () => Promise<unknown> }, label: string) {
    try {
      await mut.mutateAsync();
      toast.success(`${label} succeeded.`);
      await refetch();
    } catch (err) {
      toast.error(apiErrorMessage(err, "Transition failed."));
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground">Season</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
            {data.crop_type}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Planted {data.planting_date} · Expected harvest {data.expected_harvest_date}
          </p>
          <Link
            to="/farms/$farmId"
            params={{ farmId: data.farm_id }}
            className="mt-2 inline-block text-xs text-primary hover:underline"
          >
            ← Back to farm
          </Link>
        </div>
        <SeasonStatusBadge status={data.status} />
      </div>

      {canManage ? (
        <div className="flex flex-wrap gap-2">
          {data.status === "planned" ? (
            <Button disabled={activate.isPending} onClick={() => run(activate, "Activate season")}>
              {activate.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Activate season
            </Button>
          ) : null}
          {data.status === "active" ? (
            <>
              <Button
                variant="success"
                disabled={harvest.isPending}
                onClick={() => run(harvest, "Mark harvested")}
              >
                {harvest.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Mark harvested
              </Button>
              <ConfirmDialog
                title="Mark this season as failed?"
                description="This permanently flags the season as failed and may impact loan risk scores."
                confirmLabel="Mark failed"
                destructive
                onConfirm={() => run(fail, "Mark failed")}
                trigger={
                  <Button variant="destructive" disabled={fail.isPending}>
                    {fail.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    Mark failed
                  </Button>
                }
              />
            </>
          ) : null}
        </div>
      ) : null}

      <AIRecommendationsSection seasonId={seasonId} canGenerate={canManage} />

    </div>
  );
}
