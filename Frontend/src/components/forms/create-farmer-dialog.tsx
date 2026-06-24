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
import { useCreateFarmer } from "@/lib/queries";

const phoneRe = /^\+?\d{7,20}$/;
const allZeros = /^\+?0+$/;
const digitsOnly = /^\d+$/;

const schema = z.object({
  first_name: z.string().trim().min(1).max(100),
  last_name: z.string().trim().min(1).max(100),
  phone: z
    .string()
    .trim()
    .regex(phoneRe, "Phone must be 7–20 digits, optional leading +")
    .refine((v) => !allZeros.test(v), "Phone cannot be all zeros"),
  national_id: z
    .string()
    .trim()
    .max(20)
    .regex(digitsOnly, "Digits only")
    .refine((v) => !/^0+$/.test(v), "Cannot be all zeros")
    .optional()
    .or(z.literal("")),
  login_email: z.string().trim().email().max(255),
  login_password: z.string().min(1),
});

export function CreateFarmerDialog({
  saccoId,
  trigger,
}: {
  saccoId: string;
  trigger: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const create = useCreateFarmer();

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setServerError(null);
    const fd = new FormData(e.currentTarget);
    const parsed = schema.safeParse({
      first_name: fd.get("first_name"),
      last_name: fd.get("last_name"),
      phone: fd.get("phone"),
      national_id: fd.get("national_id") || undefined,
      login_email: fd.get("login_email"),
      login_password: fd.get("login_password"),
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
        sacco_id: saccoId,
        first_name: parsed.data.first_name,
        last_name: parsed.data.last_name,
        phone: parsed.data.phone,
        national_id: parsed.data.national_id || null,
        login_email: parsed.data.login_email,
        login_password: parsed.data.login_password,
      });
      setOpen(false);
    } catch (err) {
      const ax = err as AxiosError<{ detail?: string }>;
      const status = ax.response?.status;
      setServerError(
        status === 409
          ? "Phone, national ID, or email is already in use."
          : (ax.response?.data?.detail ?? "Failed to register farmer."),
      );
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Register farmer</DialogTitle>
          <DialogDescription>
            Create a farmer record and their login credentials.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <div className="grid grid-cols-2 gap-3">
            <Field label="First name" name="first_name" required error={errors.first_name} />
            <Field label="Last name" name="last_name" required error={errors.last_name} />
          </div>
          <Field
            label="Phone"
            name="phone"
            required
            placeholder="+254712345678"
            error={errors.phone}
          />
          <Field label="National ID" name="national_id" error={errors.national_id} />
          <Field
            label="Login email"
            name="login_email"
            type="email"
            required
            error={errors.login_email}
          />
          <Field
            label="Login password"
            name="login_password"
            type="password"
            required
            error={errors.login_password}
          />
          {serverError ? <p className="text-sm text-destructive">{serverError}</p> : null}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={create.isPending}>
              {create.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Register
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
  placeholder,
}: {
  label: string;
  name: string;
  type?: string;
  required?: boolean;
  error?: string;
  placeholder?: string;
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={name}>
        {label} {required ? <span className="text-destructive">*</span> : null}
      </Label>
      <Input id={name} name={name} type={type} placeholder={placeholder} aria-invalid={!!error} />
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}
