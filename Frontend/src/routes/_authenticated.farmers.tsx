import { useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { Plus, Users } from "lucide-react";
import { useFarmers } from "@/lib/queries";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Pager, SearchInput, useDebounced } from "@/components/list-controls";

export const Route = createFileRoute("/_authenticated/farmers")({
  ssr: false,
  component: FarmersPage,
});

const PAGE_SIZE = 20;

function FarmersPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const debounced = useDebounced(search);
  const { data, isLoading, error } = useFarmers({
    offset: page * PAGE_SIZE,
    limit: PAGE_SIZE,
    search: debounced,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Farmers</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            All farmers registered in the system.
          </p>
        </div>
        <Button asChild>
          <Link to="/farmers/new">
            <Plus className="mr-2 h-4 w-4" /> Register farmer
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
          placeholder="Search by name, phone or national ID…"
        />
      </div>

      <Card className="overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Phone</TableHead>
              <TableHead>National ID</TableHead>
              <TableHead>Joined</TableHead>
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
                  Failed to load farmers.
                </TableCell>
              </TableRow>
            ) : !data || data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5}>
                  <div className="flex flex-col items-center gap-2 py-10 text-center">
                    <Users className="h-8 w-8 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">No farmers found.</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              data.map((f) => (
                <TableRow key={f.id}>
                  <TableCell className="font-medium text-foreground">
                    <Link
                      to="/farmers/$farmerId"
                      params={{ farmerId: f.id }}
                      className="hover:underline"
                    >
                      {f.first_name} {f.last_name}
                    </Link>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{f.phone}</TableCell>
                  <TableCell className="text-muted-foreground">{f.national_id ?? "—"}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {new Date(f.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Button asChild variant="ghost" size="sm">
                      <Link to="/farmers/$farmerId" params={{ farmerId: f.id }}>
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
