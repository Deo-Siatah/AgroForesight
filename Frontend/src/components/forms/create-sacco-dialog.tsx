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
import { useCreateSacco } from "@/lib/queries";

const schema = z.object({
  name: z.string().trim().min(1, "Name is required").max(255),
  county: z.string().trim().max(100).optional(),
  admin_email: z.string().trim().email("Invalid email").max(255),
  admin_password: z.string().min(1, "Password is required"),
});

export function CreateSaccoDialog({ trigger }: { trigger: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const create = useCreateSacco();

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setServerError(null);
    const fd = new FormData(e.currentTarget);
    const parsed = schema.safeParse({
      name: fd.get("name"),
      county: fd.get("county") || undefined,
      admin_email: fd.get("admin_email"),
      admin_password: fd.get("admin_password"),
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
        ...parsed.data,
        county: parsed.data.county ?? null,
      });
      setOpen(false);
    } catch (err) {
      const ax = err as AxiosError<{ detail?: string }>;
      setServerError(ax.response?.data?.detail ?? "Failed to create SACCO.");
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create SACCO</DialogTitle>
          <DialogDescription>
            Provision a new SACCO and its primary admin account.
          </DialogDescription>
        </DialogHeader>
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
          {serverError ? (
            <p className="text-sm text-destructive">{serverError}</p>
          ) : null}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={create.isPending}>
              {create.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Create
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
