import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { Plus, Filter } from "lucide-react";
import { ticketsApi, projectsApi } from "@/lib/api";
import { PRIORITIES, STATUSES, priorityColors, statusColors, cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toaster";

export function TicketsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [showFilters, setShowFilters] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const search = searchParams.get("search") || "";
  const status = searchParams.get("status") || "";
  const priority = searchParams.get("priority") || "";
  const project_id = searchParams.get("project_id") || "";
  const page = Number(searchParams.get("page") || "1");

  const [newTicket, setNewTicket] = useState({
    title: "",
    description: "",
    priority: "Medium",
    status: "Backlog",
    project_id: "",
  });

  const { data, isLoading } = useQuery({
    queryKey: ["tickets", search, status, priority, project_id, page],
    queryFn: () =>
      ticketsApi
        .list({
          search: search || undefined,
          status: status || undefined,
          priority: priority || undefined,
          project_id: project_id || undefined,
          page,
        })
        .then((r) => r.data),
  });

  const { data: projects = [] } = useQuery({
    queryKey: ["projects"],
    queryFn: () => projectsApi.list().then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: () => ticketsApi.create(newTicket),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tickets"] });
      setShowCreate(false);
      setNewTicket({ title: "", description: "", priority: "Medium", status: "Backlog", project_id: "" });
      toast({ title: "Ticket created" });
    },
    onError: () => toast({ title: "Failed to create ticket", variant: "destructive" }),
  });

  const updateFilter = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams);
    if (value) params.set(key, value);
    else params.delete(key);
    params.set("page", "1");
    setSearchParams(params);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Tickets</h1>
          <p className="text-muted-foreground">{data?.total ?? 0} tickets found</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
          <Button onClick={() => setShowCreate(!showCreate)}>
            <Plus className="h-4 w-4 mr-2" />
            New Ticket
          </Button>
        </div>
      </div>

      <div className="flex gap-2">
        <Input
          placeholder="Search tickets..."
          value={search}
          onChange={(e) => updateFilter("search", e.target.value)}
          className="max-w-sm"
        />
      </div>

      {showFilters && (
        <Card>
          <CardContent className="pt-6 grid gap-4 sm:grid-cols-3">
            <div className="space-y-2">
              <Label>Status</Label>
              <select
                className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                value={status}
                onChange={(e) => updateFilter("status", e.target.value)}
              >
                <option value="">All</option>
                {STATUSES.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label>Priority</Label>
              <select
                className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                value={priority}
                onChange={(e) => updateFilter("priority", e.target.value)}
              >
                <option value="">All</option>
                {PRIORITIES.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label>Project</Label>
              <select
                className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                value={project_id}
                onChange={(e) => updateFilter("project_id", e.target.value)}
              >
                <option value="">All</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
          </CardContent>
        </Card>
      )}

      {showCreate && (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2 sm:col-span-2">
                <Label>Title</Label>
                <Input value={newTicket.title} onChange={(e) => setNewTicket({ ...newTicket, title: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>Project</Label>
                <select
                  className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                  value={newTicket.project_id}
                  onChange={(e) => setNewTicket({ ...newTicket, project_id: e.target.value })}
                >
                  <option value="">Select project</option>
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label>Priority</Label>
                <select
                  className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                  value={newTicket.priority}
                  onChange={(e) => setNewTicket({ ...newTicket, priority: e.target.value })}
                >
                  {PRIORITIES.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
            </div>
            <Button
              onClick={() => createMutation.mutate()}
              disabled={!newTicket.title || !newTicket.project_id || createMutation.isPending}
            >
              Create Ticket
            </Button>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="text-muted-foreground">Loading tickets...</div>
      ) : (data?.items.length ?? 0) === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">No tickets found</CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {data?.items.map((t) => (
            <Link key={t.id} to={`/tickets/${t.id}`}>
              <Card className="hover:border-primary/50 transition-colors">
                <CardContent className="py-4 flex items-center gap-4">
                  <span className="font-mono text-sm text-muted-foreground w-24 shrink-0">{t.ticket_key}</span>
                  <span className="flex-1 font-medium truncate">{t.title}</span>
                  <Badge className={cn("shrink-0", priorityColors[t.priority as keyof typeof priorityColors])}>
                    {t.priority}
                  </Badge>
                  <Badge className={cn("shrink-0 hidden sm:inline-flex", statusColors[t.status as keyof typeof statusColors])}>
                    {t.status}
                  </Badge>
                  <span className="text-sm text-muted-foreground hidden md:block">{t.project_name}</span>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {data && data.total > data.page_size && (
        <div className="flex justify-center gap-2">
          <Button
            variant="outline"
            disabled={page <= 1}
            onClick={() => updateFilter("page", String(page - 1))}
          >
            Previous
          </Button>
          <span className="flex items-center text-sm text-muted-foreground">
            Page {page} of {Math.ceil(data.total / data.page_size)}
          </span>
          <Button
            variant="outline"
            disabled={page >= Math.ceil(data.total / data.page_size)}
            onClick={() => updateFilter("page", String(page + 1))}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
