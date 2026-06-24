import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { Loader2, ArrowLeft } from "lucide-react";
import { z } from "zod";
import { toast } from "sonner";
import { useCreateFarmer } from "@/lib/queries";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PasswordInput } from "@/components/ui/password-input";
import { ErrorBanner, apiErrorMessage } from "@/components/error-banner";

export const Route = createFileRoute("/_authenticated/farmers/new")({
  ssr: false,
  validateSearch: (s: Record<string, unknown>) => ({
    sacco_id: typeof s.sacco_id === "string" ? s.sacco_id : undefined,
  }),
  component: RegisterFarmerPage,
});

const phoneRe = /^\+?\d{7,20}$/;
const schema = z.object({
  sacco_id: z.string().uuid("Sacco ID required"),
  first_name: z.string().trim().min(1).max(100),
  last_name: z.string().trim().min(1).max(100),
  phone: z
    .string()
    .trim()
    .regex(phoneRe, "Phone must be 7–20 digits, optional leading +")
    .refine((v) => !/^\+?0+$/.test(v), "Phone cannot be all zeros"),
  national_id: z.string().trim().max(20).optional().or(z.literal("")),
  login_email: z.string().trim().email().max(255),
  login_password: z.string().min(1),
});

function RegisterFarmerPage() {
  const { user } = useAuth();
  const search = Route.useSearch();
  const navigate = useNavigate();
  const create = useCreateFarmer();
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [pageError, setPageError] = useState<string | null>(null);

  const defaultSaccoId = search.sacco_id ?? user?.sacco_id ?? "";
  const canChooseSacco = user?.role === "admin";

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPageError(null);
    const fd = new FormData(e.currentTarget);
    const parsed = schema.safeParse({
      sacco_id: canChooseSacco ? fd.get("sacco_id") : defaultSaccoId,
      first_name: fd.get("first_name"),
      last_name: fd.get("last_name"),
      phone: fd.get("phone"),
      national_id: fd.get("national_id") || undefined,
      login_email: fd.get("login_email"),
      login_password: fd.get("login_password"),
    });
    if (!parsed.success) {
      const next: Record<string, string> = {};
      for (const i of parsed.error.issues) next[i.path[0] as string] = i.message;
      setErrors(next);
      return;
    }
    setErrors({});
    try {
      const farmer = await create.mutateAsync({
        sacco_id: parsed.data.sacco_id,
        first_name: parsed.data.first_name,
        last_name: parsed.data.last_name,
        phone: parsed.data.phone,
        national_id: parsed.data.national_id || null,
        login_email: parsed.data.login_email,
        login_password: parsed.data.login_password,
      });
      toast.success("Farmer registered");
      navigate({ to: "/farmers/$farmerId", params: { farmerId: farmer.id } });
    } catch (err) {
      setPageError(apiErrorMessage(err, "Failed to register farmer."));
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Link to="/dashboard" className="inline-flex items-center text-xs text-primary hover:underline">
        <ArrowLeft className="mr-1 h-3 w-3" /> Back to dashboard
      </Link>
      <Card>
        <CardHeader>
          <CardTitle>Register farmer</CardTitle>
          <CardDescription>Create a farmer record and their login credentials.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4" noValidate>
            {canChooseSacco && (
              <Field
                label="SACCO ID"
                name="sacco_id"
                required
                defaultValue={defaultSaccoId}
                error={errors.sacco_id}
              />
            )}
            <div className="grid grid-cols-2 gap-3">
              <Field label="First name" name="first_name" required error={errors.first_name} />
              <Field label="Last name" name="last_name" required error={errors.last_name} />
            </div>
            <Field label="Phone" name="phone" required placeholder="+254712345678" error={errors.phone} />
            <Field label="National ID" name="national_id" error={errors.national_id} />
            <Field label="Login email" name="login_email" type="email" required error={errors.login_email} />
            <Field
              label="Login password"
              name="login_password"
              type="password"
              required
              error={errors.login_password}
            />
            {pageError ? <ErrorBanner message={pageError} /> : null}
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => navigate({ to: "/dashboard" })}>
                Cancel
              </Button>
              <Button type="submit" disabled={create.isPending}>
                {create.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Register
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
  defaultValue,
  readOnly,
}: {
  label: string;
  name: string;
  type?: string;
  required?: boolean;
  error?: string;
  placeholder?: string;
  defaultValue?: string;
  readOnly?: boolean;
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={name}>
        {label} {required ? <span className="text-destructive">*</span> : null}
      </Label>
      {type === "password" ? (
        <PasswordInput
          id={name}
          name={name}
          placeholder={placeholder}
          defaultValue={defaultValue}
          aria-invalid={!!error}
        />
      ) : (
        <Input
          id={name}
          name={name}
          type={type}
          placeholder={placeholder}
          defaultValue={defaultValue}
          readOnly={readOnly}
          aria-invalid={!!error}
        />
      )}
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}
