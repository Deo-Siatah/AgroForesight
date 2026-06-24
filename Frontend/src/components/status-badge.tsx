import { cn } from "@/lib/utils";
import type { LoanStatus, RecommendationPriority, RiskLevel, SeasonStatus } from "@/lib/types";

/**
 * Brand rule: only greens, slate, and one neutral destructive tone.
 * No red/orange/yellow/purple/blue badges.
 */

const seasonStyles: Record<SeasonStatus, string> = {
  planned: "bg-muted text-foreground border-border",
  active: "bg-primary text-primary-foreground border-transparent",
  harvested: "bg-secondary text-secondary-foreground border-transparent",
  failed: "bg-destructive/10 text-destructive border-destructive/30",
};

const loanStyles: Record<LoanStatus, string> = {
  pending: "bg-muted text-foreground border-border",
  approved: "bg-accent text-accent-foreground border-transparent",
  disbursed: "bg-secondary/20 text-primary border-secondary/40",
  active: "bg-primary text-primary-foreground border-transparent",
  repaid: "bg-secondary text-secondary-foreground border-transparent",
  rejected: "bg-destructive/10 text-destructive border-destructive/30",
  defaulted: "bg-destructive/10 text-destructive border-destructive/30",
};

// Green-only priority palette per brand spec — exact hex values.
// High: #166534, Medium: #22C55E, Low: lighter green (#BBF7D0).
const priorityHex: Record<RecommendationPriority, { bg: string; fg: string; border: string }> = {
  high: { bg: "#166534", fg: "#FFFFFF", border: "#166534" },
  medium: { bg: "#22C55E", fg: "#052E16", border: "#22C55E" },
  low: { bg: "#BBF7D0", fg: "#14532D", border: "#86EFAC" },
};

const riskStyles: Record<RiskLevel, string> = {
  low: "bg-accent text-accent-foreground border-transparent",
  medium: "bg-secondary text-secondary-foreground border-transparent",
  high: "bg-primary text-primary-foreground border-transparent",
};

const base =
  "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize";

export function SeasonStatusBadge({ status }: { status: SeasonStatus }) {
  return <span className={cn(base, seasonStyles[status])}>{status}</span>;
}

export function LoanStatusBadge({ status }: { status: LoanStatus }) {
  return <span className={cn(base, loanStyles[status])}>{status}</span>;
}

export function RiskLevelBadge({ level }: { level: RiskLevel }) {
  return <span className={cn(base, riskStyles[level])}>{level} risk</span>;
}

export function PriorityBadge({ priority }: { priority: RecommendationPriority }) {
  const c = priorityHex[priority] ?? priorityHex.low;
  return (
    <span
      className={cn(base)}
      style={{ backgroundColor: c.bg, color: c.fg, borderColor: c.border }}
    >
      {priority} priority
    </span>
  );
}
