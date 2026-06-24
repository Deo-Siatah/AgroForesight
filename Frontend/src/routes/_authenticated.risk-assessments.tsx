import { createFileRoute, Link } from "@tanstack/react-router";
import { useRiskAssessments } from "@/lib/queries";
import { Card } from "@/components/ui/card";
import { RiskLevelBadge } from "@/components/status-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export const Route = createFileRoute("/_authenticated/risk-assessments")({
  ssr: false,
  component: RiskHistoryPage,
});

function RiskHistoryPage() {
  const { data, isLoading, error } = useRiskAssessments();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Risk history</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Historical AI risk assessments across loans.
        </p>
      </div>

      <Card className="overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Loan</TableHead>
              <TableHead>Score</TableHead>
              <TableHead>Level</TableHead>
              <TableHead>Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell colSpan={5}>
                    <div className="h-4 w-full animate-pulse rounded bg-muted" />
                  </TableCell>
                </TableRow>
              ))
            ) : error ? (
              <TableRow>
                <TableCell colSpan={5} className="text-sm text-destructive">
                  Failed to load assessments.
                </TableCell>
              </TableRow>
            ) : !data || data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="py-10 text-center text-sm text-muted-foreground">
                  No assessments yet.
                </TableCell>
              </TableRow>
            ) : (
              data.map((a) => (
                <TableRow key={a.id}>
                  <TableCell className="text-muted-foreground">
                    {new Date(a.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Link
                      to="/loans/$loanId"
                      params={{ loanId: a.loan_id }}
                      className="font-mono text-xs text-primary hover:underline"
                    >
                      {a.loan_id.slice(0, 8)}…
                    </Link>
                  </TableCell>
                  <TableCell className="font-medium text-foreground">{a.score}</TableCell>
                  <TableCell>
                    <RiskLevelBadge level={a.risk_level} />
                  </TableCell>
                  <TableCell>
                    <Link
                      to="/risk-assessments/$assessmentId"
                      params={{ assessmentId: a.id }}
                      className="text-xs text-primary hover:underline"
                    >
                      {a.action ?? "View"}
                    </Link>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
