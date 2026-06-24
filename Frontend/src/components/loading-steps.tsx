import { Check, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

/**
 * Progressive loading indicator for AI endpoints (risk, recommendations).
 * Cycles through steps while the request is in flight so the UI never goes blank.
 */
export function LoadingSteps({
  steps,
  intervalMs = 1500,
  className,
}: {
  steps: string[];
  intervalMs?: number;
  className?: string;
}) {
  const [active, setActive] = useState(0);

  useEffect(() => {
    if (active >= steps.length - 1) return;
    const t = window.setTimeout(() => setActive((i) => Math.min(i + 1, steps.length - 1)), intervalMs);
    return () => window.clearTimeout(t);
  }, [active, steps.length, intervalMs]);

  return (
    <ol className={cn("space-y-2.5", className)}>
      {steps.map((step, i) => {
        const isActive = i === active;
        const isDone = i < active;
        return (
          <li key={step} className="flex items-center gap-3 text-sm">
            <span
              className={cn(
                "flex h-5 w-5 shrink-0 items-center justify-center rounded-full border",
                isDone && "border-primary bg-primary text-primary-foreground",
                isActive && "border-primary text-primary",
                !isDone && !isActive && "border-border text-muted-foreground",
              )}
            >
              {isDone ? (
                <Check className="h-3 w-3" />
              ) : isActive ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : (
                <span className="text-[10px]">{i + 1}</span>
              )}
            </span>
            <span
              className={cn(
                isDone && "text-foreground",
                isActive && "text-foreground font-medium",
                !isDone && !isActive && "text-muted-foreground",
              )}
            >
              {step}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
