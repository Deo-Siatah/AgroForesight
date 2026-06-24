import { useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Plus, Wallet } from "lucide-react";
import { useLoans } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { LoanStatusBadge } from "@/components/status-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Pager, SearchInput, useDebounced } from "@/components/list-controls";
import type { LoanStatus } from "@/lib/types";

export const Route = createFileRoute("/_authenticated/loans")({
  ssr: false,
  component: LoansPage,
});

const PAGE_SIZE = 20;
const STATUSES: LoanStatus[] = [
  "pending",
  "approved",
  "rejected",
  "disbursed",
  "active",
  "repaid",
  "defaulted",
];

function LoansPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<LoanStatus | "all">("all");
  const [page, setPage] = useState(0);
  const debounced = useDebounced(search);
  const { data, isLoading, error } = useLoans({
    offset: page * PAGE_SIZE,
    limit: PAGE_SIZE,
    search: debounced,
    status: status === "all" ? undefined : status,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Loans</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            All loan applications and their current state.
          </p>
        </div>
        <Button asChild>
          <Link to="/loans/new">
            <Plus className="mr-2 h-4 w-4" /> Create loan
          </Link>
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <SearchInput
          value={search}
          onChange={(v) => {
            setPage(0);
            setSearch(v);
          }}
          placeholder="Search by loan or farmer ID…"
        />
        <Select
          value={status}
          onValueChange={(v) => {
            setPage(0);
            setStatus(v as LoanStatus | "all");
          }}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            {STATUSES.map((s) => (
              <SelectItem key={s} value={s} className="capitalize">
                {s}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Card className="overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Loan ID</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Risk score</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-12" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell colSpan={6}>
                    <div className="h-4 w-full animate-pulse rounded bg-muted" />
                  </TableCell>
                </TableRow>
              ))
            ) : error ? (
              <TableRow>
                <TableCell colSpan={6} className="text-sm text-destructive">
                  Failed to load loans.
                </TableCell>
              </TableRow>
            ) : !data || data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6}>
                  <div className="flex flex-col items-center gap-2 py-10 text-center">
                    <Wallet className="h-8 w-8 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">No loans found.</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              data.map((l) => (
                <TableRow key={l.id}>
                  <TableCell className="font-mono text-xs text-foreground">
                    <Link
                      to="/loans/$loanId"
                      params={{ loanId: l.id }}
                      className="hover:underline"
                    >
                      {l.id.slice(0, 8)}…
                    </Link>
                  </TableCell>
                  <TableCell className="font-medium text-foreground">
                    KES {Number(l.amount).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <LoanStatusBadge status={l.status} />
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {l.risk_score ?? "—"}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {new Date(l.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Button asChild variant="ghost" size="sm">
                      <Link to="/loans/$loanId" params={{ loanId: l.id }}>
                        Open
                      </Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
        <Pager page={page} pageSize={PAGE_SIZE} count={data?.length ?? 0} onPage={setPage} />
      </Card>
    </div>
  );
}
