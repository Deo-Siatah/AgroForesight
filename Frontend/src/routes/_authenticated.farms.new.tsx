import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { Loader2, ArrowLeft } from "lucide-react";
import { z } from "zod";
import { toast } from "sonner";
import { useCreateFarm } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ErrorBanner, apiErrorMessage } from "@/components/error-banner";
import { MapPicker, isInKenya } from "@/components/map-picker";

export const Route = createFileRoute("/_authenticated/farms/new")({
  ssr: false,
  validateSearch: (s: Record<string, unknown>) => ({
    farmer_id: typeof s.farmer_id === "string" ? s.farmer_id : undefined,
  }),
  component: CreateFarmPage,
});

const schema = z.object({
  farmer_id: z.string().uuid("Farmer ID required"),
  name: z.string().trim().min(1).max(255),
  county: z.string().trim().min(1).max(100),
  acreage: z
    .string()
    .trim()
    .regex(/^\d+(\.\d{1,2})?$/, "Up to 2 decimal places")
    .refine((v) => Number(v) > 0, "Must be greater than 0"),
  latitude: z.coerce.number().min(-5, "Lat -5 to 5").max(5, "Lat -5 to 5"),
  longitude: z.coerce.number().min(33.5, "Lng 33.5 to 42").max(42, "Lng 33.5 to 42"),
});

function CreateFarmPage() {
  const { farmer_id } = Route.useSearch();
  const navigate = useNavigate();
  const create = useCreateFarm();
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [pageError, setPageError] = useState<string | null>(null);
  const [latitude, setLatitude] = useState<number | undefined>();
  const [longitude, setLongitude] = useState<number | undefined>();

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPageError(null);
    const fd = new FormData(e.currentTarget);
    const parsed = schema.safeParse({
      farmer_id: fd.get("farmer_id"),
      name: fd.get("name"),
      county: fd.get("county"),
      acreage: fd.get("acreage"),
      latitude: fd.get("latitude"),
      longitude: fd.get("longitude"),
    });
    if (!parsed.success) {
      const next: Record<string, string> = {};
      for (const i of parsed.error.issues) next[i.path[0] as string] = i.message;
      setErrors(next);
      return;
    }
    if (!isInKenya(parsed.data.latitude, parsed.data.longitude)) {
      setErrors({ latitude: "Pin must fall inside Kenya's bounding box." });
      return;
    }
    setErrors({});
    try {
      const farm = await create.mutateAsync(parsed.data);
      toast.success("Farm created");
      navigate({ to: "/farms/$farmId", params: { farmId: farm.id } });
    } catch (err) {
      setPageError(apiErrorMessage(err, "Failed to create farm."));
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Link to="/dashboard" className="inline-flex items-center text-xs text-primary hover:underline">
        <ArrowLeft className="mr-1 h-3 w-3" /> Back
      </Link>
      <Card>
        <CardHeader>
          <CardTitle>Add farm</CardTitle>
          <CardDescription>Register a GPS-validated parcel within Kenya.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4" noValidate>
            <Field
              label="Farmer ID"
              name="farmer_id"
              required
              defaultValue={farmer_id ?? ""}
              error={errors.farmer_id}
            />
            <Field label="Farm name" name="name" required error={errors.name} />
            <div className="grid grid-cols-2 gap-3">
              <Field label="County" name="county" required error={errors.county} />
              <Field label="Acreage" name="acreage" required placeholder="2.50" error={errors.acreage} />
            </div>

            <div className="space-y-2">
              <Label>Farm location</Label>
              <MapPicker
                latitude={latitude}
                longitude={longitude}
                onChange={(lat, lng) => {
                  setLatitude(lat);
                  setLongitude(lng);
                }}
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
                value={latitude ?? ""}
                onChange={(v) => setLatitude(v === "" ? undefined : Number(v))}
                error={errors.latitude}
              />
              <Field
                label="Longitude"
                name="longitude"
                type="number"
                step="0.0001"
                required
                placeholder="36.10"
                value={longitude ?? ""}
                onChange={(v) => setLongitude(v === "" ? undefined : Number(v))}
                error={errors.longitude}
              />
            </div>
            {pageError ? <ErrorBanner message={pageError} /> : null}
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => navigate({ to: "/dashboard" })}>
                Cancel
              </Button>
              <Button type="submit" disabled={create.isPending}>
                {create.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Add farm
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
  placeholder,
  step,
  defaultValue,
  value,
  onChange,
}: {
  label: string;
  name: string;
  type?: string;
  required?: boolean;
  error?: string;
  placeholder?: string;
  step?: string;
  defaultValue?: string;
  value?: string | number;
  onChange?: (value: string) => void;
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
        defaultValue={defaultValue}
        value={value}
        onChange={onChange ? (e) => onChange(e.target.value) : undefined}
        aria-invalid={!!error}
      />
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}
