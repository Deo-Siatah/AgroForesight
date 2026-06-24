import { useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Plus, Sprout } from "lucide-react";
import { useSeasons } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { SeasonStatusBadge } from "@/components/status-badge";
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
import type { SeasonStatus } from "@/lib/types";

export const Route = createFileRoute("/_authenticated/seasons")({
  ssr: false,
  component: SeasonsPage,
});

const PAGE_SIZE = 20;
const STATUSES: SeasonStatus[] = ["planned", "active", "harvested", "failed"];

function SeasonsPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<SeasonStatus | "all">("all");
  const [page, setPage] = useState(0);
  const debounced = useDebounced(search);
  const { data, isLoading, error } = useSeasons({
    offset: page * PAGE_SIZE,
    limit: PAGE_SIZE,
    search: debounced,
    status: status === "all" ? undefined : status,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Seasons</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            All crop seasons across registered farms.
          </p>
        </div>
        <Button asChild>
          <Link to="/seasons/new">
            <Plus className="mr-2 h-4 w-4" /> Start season
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
          placeholder="Search by crop type…"
        />
        <Select
          value={status}
          onValueChange={(v) => {
            setPage(0);
            setStatus(v as SeasonStatus | "all");
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
              <TableHead>Crop</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Planted</TableHead>
              <TableHead>Expected harvest</TableHead>
              <TableHead className="w-12" />
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
                  Failed to load seasons.
                </TableCell>
              </TableRow>
            ) : !data || data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5}>
                  <div className="flex flex-col items-center gap-2 py-10 text-center">
                    <Sprout className="h-8 w-8 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">No seasons found.</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              data.map((s) => (
                <TableRow key={s.id}>
                  <TableCell className="font-medium text-foreground">
                    <Link
                      to="/seasons/$seasonId"
                      params={{ seasonId: s.id }}
                      className="hover:underline"
                    >
                      {s.crop_type}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <SeasonStatusBadge status={s.status} />
                  </TableCell>
                  <TableCell className="text-muted-foreground">{s.planting_date}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {s.expected_harvest_date}
                  </TableCell>
                  <TableCell>
                    <Button asChild variant="ghost" size="sm">
                      <Link to="/seasons/$seasonId" params={{ seasonId: s.id }}>
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
