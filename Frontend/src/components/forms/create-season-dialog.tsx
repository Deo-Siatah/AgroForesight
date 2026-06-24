import { useState, type FormEvent, type ReactNode } from "react";
import { AxiosError } from "axios";
import { Loader2 } from "lucide-react";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCreateSeason } from "@/lib/queries";

const schema = z
  .object({
    crop_type: z.string().trim().min(1).max(100),
    planting_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "YYYY-MM-DD"),
    expected_harvest_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "YYYY-MM-DD"),
  })
  .refine((d) => d.expected_harvest_date > d.planting_date, {
    path: ["expected_harvest_date"],
    message: "Must be after planting date",
  });

export function CreateSeasonDialog({
  farmId,
  trigger,
}: {
  farmId: string;
  trigger: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const create = useCreateSeason();

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setServerError(null);
    const fd = new FormData(e.currentTarget);
    const parsed = schema.safeParse({
      crop_type: fd.get("crop_type"),
      planting_date: fd.get("planting_date"),
      expected_harvest_date: fd.get("expected_harvest_date"),
    });
    if (!parsed.success) {
      const next: Record<string, string> = {};
      for (const issue of parsed.error.issues) next[issue.path[0] as string] = issue.message;
      setErrors(next);
      return;
    }
    setErrors({});
    try {
      await create.mutateAsync({
        farm_id: farmId,
        crop_type: parsed.data.crop_type,
        planting_date: parsed.data.planting_date,
        expected_harvest_date: parsed.data.expected_harvest_date,
      });
      setOpen(false);
    } catch (err) {
      const ax = err as AxiosError<{ detail?: string }>;
      setServerError(ax.response?.data?.detail ?? "Failed to start season.");
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Start season</DialogTitle>
          <DialogDescription>
            Plan a new crop cycle. Starts as <em>planned</em>; activate when planting begins.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
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
          {serverError ? <p className="text-sm text-destructive">{serverError}</p> : null}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={create.isPending}>
              {create.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Start season
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function Field({
  label,
  name,
  type = "text",
  required,
  error,
}: {
  label: string;
  name: string;
  type?: string;
  required?: boolean;
  error?: string;
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={name}>
        {label} {required ? <span className="text-destructive">*</span> : null}
      </Label>
      <Input id={name} name={name} type={type} aria-invalid={!!error} />
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}
