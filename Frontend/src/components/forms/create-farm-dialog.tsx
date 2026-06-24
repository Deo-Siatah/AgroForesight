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
import { useCreateFarm } from "@/lib/queries";

const schema = z.object({
  name: z.string().trim().min(1).max(255),
  county: z.string().trim().min(1).max(100),
  acreage: z
    .string()
    .trim()
    .regex(/^\d+(\.\d{1,2})?$/, "Up to 2 decimal places")
    .refine((v) => Number(v) > 0, "Must be greater than 0"),
  latitude: z.coerce
    .number()
    .min(-5, "Latitude must be within Kenya (-5 to 5)")
    .max(5, "Latitude must be within Kenya (-5 to 5)"),
  longitude: z.coerce
    .number()
    .min(33.5, "Longitude must be within Kenya (33.5 to 42)")
    .max(42, "Longitude must be within Kenya (33.5 to 42)"),
});

export function CreateFarmDialog({
  farmerId,
  trigger,
}: {
  farmerId: string;
  trigger: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const create = useCreateFarm();

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setServerError(null);
    const fd = new FormData(e.currentTarget);
    const parsed = schema.safeParse({
      name: fd.get("name"),
      county: fd.get("county"),
      acreage: fd.get("acreage"),
      latitude: fd.get("latitude"),
      longitude: fd.get("longitude"),
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
        farmer_id: farmerId,
        name: parsed.data.name,
        county: parsed.data.county,
        acreage: parsed.data.acreage,
        latitude: parsed.data.latitude,
        longitude: parsed.data.longitude,
      });
      setOpen(false);
    } catch (err) {
      const ax = err as AxiosError<{ detail?: string }>;
      setServerError(ax.response?.data?.detail ?? "Failed to create farm.");
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add farm</DialogTitle>
          <DialogDescription>
            Register a GPS-validated parcel within Kenya's bounding box.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <Field label="Farm name" name="name" required error={errors.name} />
          <div className="grid grid-cols-2 gap-3">
            <Field label="County" name="county" required error={errors.county} />
            <Field
              label="Acreage"
              name="acreage"
              required
              placeholder="2.50"
              error={errors.acreage}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Field
              label="Latitude"
              name="latitude"
              type="number"
              step="0.0001"
              required
              placeholder="-0.30"
              error={errors.latitude}
            />
            <Field
              label="Longitude"
              name="longitude"
              type="number"
              step="0.0001"
              required
              placeholder="36.10"
              error={errors.longitude}
            />
          </div>
          <p className="text-xs text-muted-foreground">
            Kenya bounding box: lat −5 to 5, lng 33.5 to 42.
          </p>
          {serverError ? <p className="text-sm text-destructive">{serverError}</p> : null}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={create.isPending}>
              {create.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Add farm
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
  placeholder,
  step,
  error,
}: {
  label: string;
  name: string;
  type?: string;
  required?: boolean;
  placeholder?: string;
  step?: string;
  error?: string;
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
        step={step}
        placeholder={placeholder}
        aria-invalid={!!error}
      />
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}
