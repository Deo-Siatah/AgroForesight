import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { Loader2, ArrowLeft } from "lucide-react";
import { z } from "zod";
import { toast } from "sonner";
import { useCreateSeason } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ErrorBanner, apiErrorMessage } from "@/components/error-banner";

export const Route = createFileRoute("/_authenticated/seasons/new")({
  ssr: false,
  validateSearch: (s: Record<string, unknown>) => ({
    farm_id: typeof s.farm_id === "string" ? s.farm_id : undefined,
  }),
  component: StartSeasonPage,
});

const schema = z
  .object({
    farm_id: z.string().uuid("Farm ID required"),
    crop_type: z.string().trim().min(1).max(100),
    planting_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "YYYY-MM-DD"),
    expected_harvest_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "YYYY-MM-DD"),
  })
  .refine((d) => d.expected_harvest_date > d.planting_date, {
    path: ["expected_harvest_date"],
    message: "Must be after planting date",
  });

function StartSeasonPage() {
  const { farm_id } = Route.useSearch();
  const navigate = useNavigate();
  const create = useCreateSeason();
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [pageError, setPageError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPageError(null);
    const fd = new FormData(e.currentTarget);
    const parsed = schema.safeParse({
      farm_id: fd.get("farm_id"),
      crop_type: fd.get("crop_type"),
      planting_date: fd.get("planting_date"),
      expected_harvest_date: fd.get("expected_harvest_date"),
    });
    if (!parsed.success) {
      const next: Record<string, string> = {};
      for (const i of parsed.error.issues) next[i.path[0] as string] = i.message;
      setErrors(next);
      return;
    }
    setErrors({});
    try {
      const season = await create.mutateAsync(parsed.data);
      toast.success("Season started");
      navigate({ to: "/seasons/$seasonId", params: { seasonId: season.id } });
    } catch (err) {
      setPageError(apiErrorMessage(err, "Failed to start season."));
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Link to="/dashboard" className="inline-flex items-center text-xs text-primary hover:underline">
        <ArrowLeft className="mr-1 h-3 w-3" /> Back
      </Link>
      <Card>
        <CardHeader>
          <CardTitle>Start season</CardTitle>
          <CardDescription>
            Plan a new crop cycle. Starts as <em>planned</em>; activate when planting begins.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4" noValidate>
            <Field label="Farm ID" name="farm_id" required defaultValue={farm_id ?? ""} error={errors.farm_id} />
            <Field label="Crop type" name="crop_type" required error={errors.crop_type} />
            <div className="grid grid-cols-2 gap-3">
              <Field
                label="Planting date"
                name="planting_date"
                type="date"
                required
                error={errors.planting_date}
              />
              <Field
                label="Expected harvest"
                name="expected_harvest_date"
                type="date"
                required
                error={errors.expected_harvest_date}
              />
            </div>
            {pageError ? <ErrorBanner message={pageError} /> : null}
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => navigate({ to: "/dashboard" })}>
                Cancel
              </Button>
              <Button type="submit" disabled={create.isPending}>
                {create.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Start season
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

function Field({
  label,
  name,
  type = "text",
  required,
  error,
  defaultValue,
}: {
  label: string;
  name: string;
  type?: string;
  required?: boolean;
  error?: string;
  defaultValue?: string;
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={name}>
        {label} {required ? <span className="text-destructive">*</span> : null}
      </Label>
      <Input
        id={name}
        name={name}
        type={type}
        defaultValue={defaultValue}
        aria-invalid={!!error}
      />
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}
