import { createFileRoute } from "@tanstack/react-router";
import { Plus } from "lucide-react";
import { useSacco } from "@/lib/queries";
import { CreateFarmerDialog } from "@/components/forms/create-farmer-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const Route = createFileRoute("/_authenticated/saccos/$saccoId")({
  ssr: false,
  component: SaccoDetailPage,
});

function SaccoDetailPage() {
  const { saccoId } = Route.useParams();
  const { data, isLoading, error } = useSacco(saccoId);

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-muted-foreground">SACCO</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-foreground">
            {isLoading ? "Loading…" : (data?.name ?? "Unknown")}
          </h1>
          {data?.county ? (
            <p className="mt-1 text-sm text-muted-foreground">{data.county} County</p>
          ) : null}
        </div>
        <CreateFarmerDialog
          saccoId={saccoId}
          trigger={
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Register farmer
            </Button>
          }
        />
      </div>

      {error ? (
        <p className="text-sm text-destructive">Failed to load SACCO.</p>
      ) : null}

      <div className="grid gap-4 md:grid-cols-3">
        <SummaryCard label="SACCO ID" value={data?.id ?? "—"} mono />
        <SummaryCard label="County" value={data?.county ?? "—"} />
        <SummaryCard
          label="Created"
          value={data ? new Date(data.created_at).toLocaleDateString() : "—"}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Farmers</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          A SACCO-level farmer roster endpoint isn't documented in the guide.
          Open a farmer directly by ID, or register one with the button above.
        </CardContent>
      </Card>
    </div>
  );
}

function SummaryCard({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <Card>
      <CardContent className="space-y-1 p-5">
        <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
        <p
          className={
            mono
              ? "truncate font-mono text-sm text-foreground"
              : "text-base font-medium text-foreground"
          }
        >
          {value}
        </p>
      </CardContent>
    </Card>
  );
}
