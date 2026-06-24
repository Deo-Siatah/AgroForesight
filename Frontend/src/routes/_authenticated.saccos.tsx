import { useState } from "react";
import { createFileRoute, Link, Outlet, useMatchRoute } from "@tanstack/react-router";
import { Building2, Plus } from "lucide-react";
import { useSaccos } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card } from "@/components/ui/card";
import { Pager, SearchInput, useDebounced } from "@/components/list-controls";

export const Route = createFileRoute("/_authenticated/saccos")({
  ssr: false,
  component: SaccosPage,
});

const PAGE_SIZE = 20;

function SaccosPage() {
  const matchRoute = useMatchRoute();
  const isChild = matchRoute({ to: "/saccos/new" }) || matchRoute({ to: "/saccos/$saccoId" });
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const debounced = useDebounced(search);
  const { data, isLoading, error } = useSaccos({
    offset: page * PAGE_SIZE,
    limit: PAGE_SIZE,
    search: debounced,
  });

  if (isChild) return <Outlet />;

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">SACCOs</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            All cooperative societies registered with Hifadhi.
          </p>
        </div>
        <Button asChild>
          <Link to="/saccos/new">
            <Plus className="mr-2 h-4 w-4" />
            New SACCO
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
          placeholder="Search by name or county…"
        />
      </div>

      <Card className="overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>County</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-12" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell colSpan={4}>
                    <div className="h-4 w-full animate-pulse rounded bg-muted" />
                  </TableCell>
                </TableRow>
              ))
            ) : error ? (
              <TableRow>
                <TableCell colSpan={4} className="text-sm text-destructive">
                  Failed to load SACCOs.
                </TableCell>
              </TableRow>
            ) : !data || data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4}>
                  <div className="flex flex-col items-center gap-2 py-10 text-center">
                    <Building2 className="h-8 w-8 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">No SACCOs found.</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              data.map((s) => (
                <TableRow key={s.id}>
                  <TableCell className="font-medium text-foreground">
                    <Link
                      to="/saccos/$saccoId"
                      params={{ saccoId: s.id }}
                      className="hover:underline"
                    >
                      {s.name}
                    </Link>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{s.county ?? "—"}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {new Date(s.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Button asChild variant="ghost" size="sm">
                      <Link to="/saccos/$saccoId" params={{ saccoId: s.id }}>
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
