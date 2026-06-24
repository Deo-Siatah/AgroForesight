import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { ArrowLeft, Loader2 } from "lucide-react";
import { z } from "zod";
import { toast } from "sonner";
import { useCreateSacco } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ErrorBanner, apiErrorMessage } from "@/components/error-banner";

export const Route = createFileRoute("/_authenticated/saccos/new")({
  ssr: false,
  component: CreateSaccoPage,
});

const schema = z.object({
  name: z.string().trim().min(1, "Name is required").max(255),
  county: z.string().trim().max(100).optional().or(z.literal("")),
  admin_email: z.string().trim().email("Invalid email").max(255),
  admin_password: z.string().min(8, "At least 8 characters"),
});

function CreateSaccoPage() {
  const navigate = useNavigate();
  const create = useCreateSacco();
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [pageError, setPageError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPageError(null);
    const fd = new FormData(e.currentTarget);
    const parsed = schema.safeParse({
      name: fd.get("name"),
      county: fd.get("county") || undefined,
      admin_email: fd.get("admin_email"),
      admin_password: fd.get("admin_password"),
    });
    if (!parsed.success) {
      const next: Record<string, string> = {};
      for (const i of parsed.error.issues) next[i.path[0] as string] = i.message;
      setErrors(next);
      return;
    }
    setErrors({});
    try {
      const sacco = await create.mutateAsync({
        name: parsed.data.name,
        county: parsed.data.county || null,
        admin_email: parsed.data.admin_email,
        admin_password: parsed.data.admin_password,
      });
      toast.success("SACCO created");
      navigate({ to: "/saccos/$saccoId", params: { saccoId: sacco.id } });
    } catch (err) {
      setPageError(apiErrorMessage(err, "Failed to create SACCO."));
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Link to="/saccos" className="inline-flex items-center text-xs text-primary hover:underline">
        <ArrowLeft className="mr-1 h-3 w-3" /> Back to SACCOs
      </Link>
      <Card>
        <CardHeader>
          <CardTitle>Create SACCO</CardTitle>
          <CardDescription>
            Provision a new SACCO and its primary admin account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4" noValidate>
            <Field label="SACCO name" name="name" required error={errors.name} />
            <Field label="County" name="county" error={errors.county} />
            <Field
              label="Admin email"
              name="admin_email"
              type="email"
              required
              error={errors.admin_email}
            />
            <Field
              label="Admin password"
              name="admin_password"
              type="password"
              required
              error={errors.admin_password}
            />
            {pageError ? <ErrorBanner message={pageError} /> : null}
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate({ to: "/saccos" })}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={create.isPending}>
                {create.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Create SACCO
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
