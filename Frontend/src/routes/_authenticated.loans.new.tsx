import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { Loader2, ArrowLeft } from "lucide-react";
import { z } from "zod";
import { toast } from "sonner";
import { useCreateLoan } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ErrorBanner, apiErrorMessage } from "@/components/error-banner";

export const Route = createFileRoute("/_authenticated/loans/new")({
  ssr: false,
  validateSearch: (s: Record<string, unknown>) => ({
    farmer_id: typeof s.farmer_id === "string" ? s.farmer_id : undefined,
    season_id: typeof s.season_id === "string" ? s.season_id : undefined,
  }),
  component: CreateLoanPage,
});

const schema = z.object({
  farmer_id: z.string().uuid("Farmer ID required"),
  amount: z
    .string()
    .trim()
    .regex(/^\d+(\.\d{1,2})?$/, "Up to 2 decimal places")
    .refine((v) => Number(v) > 0, "Must be greater than 0"),
  season_id: z.string().trim().uuid("Invalid UUID").optional().or(z.literal("")),
});

function CreateLoanPage() {
  const { farmer_id, season_id } = Route.useSearch();
  const navigate = useNavigate();
  const create = useCreateLoan();
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [pageError, setPageError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPageError(null);
    const fd = new FormData(e.currentTarget);
    const parsed = schema.safeParse({
      farmer_id: fd.get("farmer_id"),
      amount: fd.get("amount"),
      season_id: fd.get("season_id") || undefined,
    });
    if (!parsed.success) {
      const next: Record<string, string> = {};
      for (const i of parsed.error.issues) next[i.path[0] as string] = i.message;
      setErrors(next);
      return;
    }
    setErrors({});
    try {
      const loan = await create.mutateAsync({
        farmer_id: parsed.data.farmer_id,
        amount: parsed.data.amount,
        season_id: parsed.data.season_id || null,
      });
      toast.success("Loan created");
      navigate({ to: "/loans/$loanId", params: { loanId: loan.id } });
    } catch (err) {
      setPageError(apiErrorMessage(err, "Failed to create loan."));
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <Link to="/dashboard" className="inline-flex items-center text-xs text-primary hover:underline">
        <ArrowLeft className="mr-1 h-3 w-3" /> Back
      </Link>
      <Card>
        <CardHeader>
          <CardTitle>Create loan</CardTitle>
          <CardDescription>Link a season ID for accurate AI risk scoring.</CardDescription>
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
            <Field label="Amount (KES)" name="amount" required placeholder="120000.00" error={errors.amount} />
            <Field
              label="Season ID"
              name="season_id"
              defaultValue={season_id ?? ""}
              placeholder="Optional but recommended"
              error={errors.season_id}
            />
            {pageError ? <ErrorBanner message={pageError} /> : null}
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => navigate({ to: "/dashboard" })}>
                Cancel
              </Button>
              <Button type="submit" disabled={create.isPending}>
                {create.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Create loan
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
  required,
  placeholder,
  error,
  defaultValue,
}: {
  label: string;
  name: string;
  required?: boolean;
  placeholder?: string;
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
        placeholder={placeholder}
        defaultValue={defaultValue}
        aria-invalid={!!error}
      />
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}
