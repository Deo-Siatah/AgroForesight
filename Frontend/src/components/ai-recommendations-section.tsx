import { useState } from "react";
import { ChevronDown, ChevronUp, Plus, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { PriorityBadge } from "@/components/status-badge";
import { LoadingSteps } from "@/components/loading-steps";
import { apiErrorMessage } from "@/components/error-banner";
import {
  useGenerateRecommendation,
  useSeasonRecommendations,
} from "@/lib/queries";
import type { Recommendation } from "@/lib/types";
import { cn } from "@/lib/utils";

const STEPS = [
  "Generating recommendation…",
  "Analyzing farm…",
  "Checking weather…",
  "Evaluating crop conditions…",
];

export function AIRecommendationsSection({
  seasonId,
  canGenerate,
}: {
  seasonId: string;
  canGenerate: boolean;
}) {
  const recs = useSeasonRecommendations(seasonId);
  const generate = useGenerateRecommendation(seasonId);

  async function onGenerate() {
    try {
      await generate.mutateAsync();
      toast.success("Recommendation generated.");
    } catch (err) {
      toast.error(apiErrorMessage(err, "Failed to generate recommendation."));
    }
  }

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <h2 className="text-lg font-semibold text-foreground">AI recommendations</h2>
        </div>
        {canGenerate ? (
          <Button
            size="sm"
            variant="outline"
            disabled={generate.isPending}
            onClick={onGenerate}
          >
            <Plus className="mr-2 h-4 w-4" />
            Generate recommendation
          </Button>
        ) : null}
      </div>

      {generate.isPending ? <RecommendationGeneratingState /> : null}

      {recs.isLoading ? (
        <RecommendationSkeletonList />
      ) : recs.data && recs.data.length > 0 ? (
        <div className="space-y-3">
          {recs.data.map((r) => (
            <RecommendationCard key={r.id} recommendation={r} />
          ))}
        </div>
      ) : !generate.isPending ? (
        <Card>
          <CardContent className="p-6 text-center text-sm text-muted-foreground">
            No recommendations generated yet.
          </CardContent>
        </Card>
      ) : null}
    </section>
  );
}

export function RecommendationCard({ recommendation: r }: { recommendation: Recommendation }) {
  const [open, setOpen] = useState(false);
  const text = r.recommendation_text ?? "";
  const isLong = text.length > 220;
  const preview = isLong && !open ? text.slice(0, 220) + "…" : text;

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between space-y-0 gap-3">
        <CardTitle className="text-base">{r.title}</CardTitle>
        <PriorityBadge priority={r.priority} />
      </CardHeader>
      <CardContent className="space-y-3">
        <p className={cn("whitespace-pre-line text-sm text-foreground")}>{preview}</p>
        {isLong ? (
          <Button
            size="sm"
            variant="ghost"
            className="h-7 px-2 text-xs"
            onClick={() => setOpen((v) => !v)}
            aria-expanded={open}
          >
            {open ? (
              <>
                <ChevronUp className="mr-1 h-3.5 w-3.5" /> Hide details
              </>
            ) : (
              <>
                <ChevronDown className="mr-1 h-3.5 w-3.5" /> Show details
              </>
            )}
          </Button>
        ) : null}
        <p className="text-xs text-muted-foreground">
          Generated {new Date(r.created_at).toLocaleString()}
        </p>
      </CardContent>
    </Card>
  );
}

export function RecommendationGeneratingState() {
  return (
    <Card>
      <CardContent className="space-y-4 p-5">
        <div className="space-y-2">
          <p className="text-sm font-medium text-foreground">Generating recommendation…</p>
          <Progress value={66} className="h-1.5" />
        </div>
        <LoadingSteps steps={STEPS} />
        <RecommendationSkeletonList compact />
      </CardContent>
    </Card>
  );
}

export function RecommendationSkeletonList({ compact = false }: { compact?: boolean }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: compact ? 1 : 2 }).map((_, i) => (
        <div key={i} className="space-y-2 rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-40" />
            <Skeleton className="h-5 w-24 rounded-full" />
          </div>
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-5/6" />
          <Skeleton className="h-3 w-2/3" />
        </div>
      ))}
    </div>
  );
}
