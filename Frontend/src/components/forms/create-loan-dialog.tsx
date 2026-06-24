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
import { useCreateLoan } from "@/lib/queries";

const schema = z.object({
  amount: z
    .string()
    .trim()
    .regex(/^\d+(\.\d{1,2})?$/, "Up to 2 decimal places")
    .refine((v) => Number(v) > 0, "Must be greater than 0"),
  season_id: z.string().trim().uuid("Invalid UUID").optional().or(z.literal("")),
});

export function CreateLoanDialog({
  farmerId,
  trigger,
}: {
  farmerId: string;
  trigger: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const create = useCreateLoan();

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setServerError(null);
    const fd = new FormData(e.currentTarget);
    const parsed = schema.safeParse({
      amount: fd.get("amount"),
      season_id: fd.get("season_id") || undefined,
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
        amount: parsed.data.amount,
        season_id: parsed.data.season_id || null,
      });
      setOpen(false);
    } catch (err) {
      const ax = err as AxiosError<{ detail?: string }>;
      setServerError(ax.response?.data?.detail ?? "Failed to create loan.");
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create loan</DialogTitle>
          <DialogDescription>
            Link a season ID for accurate AI risk scoring.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <Field
            label="Amount (KES)"
            name="amount"
            required
            placeholder="120000.00"
            error={errors.amount}
          />
          <Field
            label="Season ID"
            name="season_id"
            placeholder="Optional but recommended"
            error={errors.season_id}
          />
          {serverError ? <p className="text-sm text-destructive">{serverError}</p> : null}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={create.isPending}>
              {create.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Create loan
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
  required,
  placeholder,
  error,
}: {
  label: string;
  name: string;
  required?: boolean;
  placeholder?: string;
  error?: string;
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={name}>
        {label} {required ? <span className="text-destructive">*</span> : null}
      </Label>
      <Input id={name} name={name} placeholder={placeholder} aria-invalid={!!error} />
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}
