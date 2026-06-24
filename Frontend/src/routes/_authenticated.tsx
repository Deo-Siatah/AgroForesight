import { createFileRoute, Outlet, useNavigate, Link, useRouter } from "@tanstack/react-router";
import { useEffect } from "react";
import {
  Building2,
  History,
  LayoutDashboard,
  Loader2,
  LogOut,
  Plus,
  Sprout,
  UserPlus,
  MapPin,
  Sprout as SeasonIcon,
  Wallet,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth, type UserRole } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/_authenticated")({
  ssr: false,
  component: AuthenticatedLayout,
});

const ROLE_LABEL: Record<UserRole, string> = {
  admin: "System Admin",
  sacco_admin: "SACCO Admin",
  farmer: "Farmer",
  extension_officer: "Extension Officer",
};

function AuthenticatedLayout() {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      navigate({ to: "/login", replace: true });
    }
  }, [user, loading, navigate]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-5 w-5 animate-spin text-primary" />
      </div>
    );
  }

  function handleLogout() {
    logout();
    router.invalidate();
    navigate({ to: "/login", replace: true });
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-30 border-b border-border bg-card/80 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between gap-4 px-6">
          <Link to="/dashboard" className="flex items-center gap-2 text-primary">
            <Sprout className="h-5 w-5" />
            <span className="text-base font-semibold text-foreground">Hifadhi</span>
          </Link>

          <nav className="hidden items-center gap-1 md:flex">
            <NavLink to="/dashboard" icon={<LayoutDashboard className="h-4 w-4" />}>
              Dashboard
            </NavLink>
            {user.role === "admin" ? (
              <NavLink to="/saccos" icon={<Building2 className="h-4 w-4" />}>
                SACCOs
              </NavLink>
            ) : null}
            {(user.role === "admin" || user.role === "sacco_admin") && (
              <>
                <NavLink to="/farmers" icon={<UserPlus className="h-4 w-4" />}>
                  Farmers
                </NavLink>
                <NavLink to="/seasons" icon={<SeasonIcon className="h-4 w-4" />}>
                  Seasons
                </NavLink>
                <NavLink to="/loans" icon={<Wallet className="h-4 w-4" />}>
                  Loans
                </NavLink>
                <NavLink to="/risk-assessments" icon={<History className="h-4 w-4" />}>
                  Risk history
                </NavLink>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button size="sm" className="ml-1">
                      <Plus className="mr-1.5 h-4 w-4" />
                      New
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-48">
                    <DropdownMenuLabel>Create</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    {user.role === "admin" ? (
                      <DropdownMenuItem asChild>
                        <Link to="/saccos/new">
                          <Building2 className="mr-2 h-4 w-4" /> SACCO
                        </Link>
                      </DropdownMenuItem>
                    ) : null}
                    <DropdownMenuItem asChild>
                      <Link to="/farmers/new">
                        <UserPlus className="mr-2 h-4 w-4" /> Farmer
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/farms/new">
                        <MapPin className="mr-2 h-4 w-4" /> Farm
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/seasons/new">
                        <SeasonIcon className="mr-2 h-4 w-4" /> Season
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/loans/new">
                        <Wallet className="mr-2 h-4 w-4" /> Loan
                      </Link>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </>
            )}
          </nav>

          <div className="flex items-center gap-4">
            <div className="hidden text-right sm:block">
              <p className="text-sm font-medium text-foreground">{user.email}</p>
              <p className="text-xs text-muted-foreground">{ROLE_LABEL[user.role]}</p>
            </div>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              Sign out
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}

function NavLink({
  to,
  icon,
  children,
}: {
  to: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <Link
      to={to}
      className={cn(
        "inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground",
      )}
      activeProps={{ className: "bg-accent text-accent-foreground" }}
    >
      {icon}
      {children}
    </Link>
  );
}
