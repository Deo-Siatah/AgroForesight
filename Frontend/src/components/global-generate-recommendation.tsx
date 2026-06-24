import { useEffect, useMemo, useState } from "react";
import { Link } from "@tanstack/react-router";
import { Sparkles, ArrowRight, X } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useGenerateRecommendation, useSeasons } from "@/lib/queries";
import { apiErrorMessage } from "@/components/error-banner";
import {
  RecommendationGeneratingState,
} from "@/components/ai-recommendations-section";
import { PriorityBadge } from "@/components/status-badge";
import type { Recommendation } from "@/lib/types";

const STORAGE_KEY = "hifadhi.pinned-recommendations";

function loadPinned(): Recommendation[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Recommendation[]) : [];
  } catch {
    return [];
  }
}

function savePinned(items: Recommendation[]) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch {
    /* ignore quota */
  }
}

export function GlobalGenerateRecommendation() {
  const { data: seasons, isLoading } = useSeasons({ limit: 50 });
  const eligible = useMemo(
    () => (seasons ?? []).filter((s) => s.status === "active" || s.status === "planned"),
    [seasons],
  );
  const [seasonId, setSeasonId] = useState<string>("");
  const [pinned, setPinned] = useState<Recommendation[]>([]);
  const [open, setOpen] = useState<Recommendation | null>(null);

  useEffect(() => {
    setPinned(loadPinned());
  }, []);

  const generate = useGenerateRecommendation(seasonId);

  async function onGenerate() {
    if (!seasonId) {
      toast.error("Select a season first.");
      return;
    }
    try {
      const rec = await generate.mutateAsync();
      const next = [rec, ...pinned.filter((r) => r.id !== rec.id)];
      setPinned(next);
      savePinned(next);
      setOpen(rec);
      toast.success("Recommendation generated.");
    } catch (err) {
      toast.error(apiErrorMessage(err, "Failed to generate recommendation."));
    }
  }

  function dismiss(id: string) {
    const next = pinned.filter((r) => r.id !== id);
    setPinned(next);
    savePinned(next);
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <CardTitle>Generate AI recommendation</CardTitle>
        </div>
        <CardDescription>
          Pick a planned or active season and generate an AI-powered recommendation.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col gap-2 sm:flex-row">
          <Select value={seasonId} onValueChange={setSeasonId} disabled={isLoading}>
            <SelectTrigger className="sm:flex-1">
              <SelectValue
                placeholder={
                  isLoading
                    ? "Loading seasons…"
                    : eligible.length === 0
                      ? "No eligible seasons"
                      : "Select a season"
                }
              />
            </SelectTrigger>
            <SelectContent>
              {eligible.map((s) => (
                <SelectItem key={s.id} value={s.id}>
                  {s.crop_type} · {s.status} · planted {s.planting_date}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button onClick={onGenerate} disabled={!seasonId || generate.isPending}>
            <Sparkles className="mr-2 h-4 w-4" />
            Generate
          </Button>
        </div>

        {generate.isPending ? <RecommendationGeneratingState /> : null}

        {pinned.length > 0 ? (
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">
              Pinned recommendations
            </p>
            <div className="grid gap-2 sm:grid-cols-2">
              {pinned.map((r) => (
                <PinnedRecommendationCard
                  key={r.id}
                  recommendation={r}
                  onOpen={() => setOpen(r)}
                  onDismiss={() => dismiss(r.id)}
                />
              ))}
            </div>
          </div>
        ) : null}
      </CardContent>

      <RecommendationDetailDialog
        recommendation={open}
        onOpenChange={(o) => !o && setOpen(null)}
      />
    </Card>
  );
}

function PinnedRecommendationCard({
  recommendation: r,
  onOpen,
  onDismiss,
}: {
  recommendation: Recommendation;
  onOpen: () => void;
  onDismiss: () => void;
}) {
  return (
    <div className="group relative rounded-lg border bg-card p-3 transition-colors hover:bg-accent">
      <button
        type="button"
        onClick={onOpen}
        className="block w-full text-left"
        aria-label={`Open recommendation: ${r.title}`}
      >
        <div className="flex items-start justify-between gap-2 pr-6">
          <p className="truncate text-sm font-medium text-foreground">{r.title}</p>
          <PriorityBadge priority={r.priority} />
        </div>
        <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
          {r.recommendation_text}
        </p>
        <p className="mt-1 text-[11px] text-muted-foreground">
          {new Date(r.created_at).toLocaleString()}
        </p>
      </button>
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          onDismiss();
        }}
        aria-label="Dismiss recommendation"
        className="absolute right-2 top-2 rounded-md p-1 text-muted-foreground opacity-70 hover:bg-background hover:text-foreground hover:opacity-100"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}

function RecommendationDetailDialog({
  recommendation: r,
  onOpenChange,
}: {
  recommendation: Recommendation | null;
  onOpenChange: (open: boolean) => void;
}) {
  return (
    <Dialog open={!!r} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        {r ? (
          <>
            <DialogHeader>
              <div className="flex items-start justify-between gap-3">
                <DialogTitle>{r.title}</DialogTitle>
                <PriorityBadge priority={r.priority} />
              </div>
              <DialogDescription>
                Generated {new Date(r.created_at).toLocaleString()}
              </DialogDescription>
            </DialogHeader>
            <div className="max-h-[60vh] overflow-y-auto whitespace-pre-line text-sm text-foreground">
              {r.recommendation_text}
            </div>
            <div className="flex justify-end">
              <Button asChild variant="outline" size="sm">
                <Link to="/seasons/$seasonId" params={{ seasonId: r.season_id }}>
                  Open season
                  <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
