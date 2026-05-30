import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { LayoutGrid, Settings, Ticket } from "lucide-react";
import { projectsApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data, isLoading } = useQuery({
    queryKey: ["project-dashboard", id],
    queryFn: () => projectsApi.dashboard(id!).then((r) => r.data),
    enabled: !!id,
  });

  if (isLoading) return <div className="text-muted-foreground">Loading...</div>;
  if (!data) return <div>Project not found</div>;

  const { project, recent_activity } = data;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono bg-muted px-2 py-1 rounded">{project.project_key}</span>
          </div>
          <h1 className="text-3xl font-bold">{project.name}</h1>
          <p className="text-muted-foreground">{project.description}</p>
        </div>
        <div className="flex gap-2">
          <Link to={`/projects/${id}/board`}>
            <Button variant="outline">
              <LayoutGrid className="h-4 w-4 mr-2" />
              Kanban Board
            </Button>
          </Link>
          <Link to={`/projects/${id}/settings`}>
            <Button variant="outline">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Total Tickets", value: project.total_tickets },
          { label: "Open Tickets", value: project.open_tickets },
          { label: "Completed", value: project.completed_tickets },
          { label: "Team Members", value: project.member_count },
        ].map(({ label, value }) => (
          <Card key={label}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">{label}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Ticket className="h-5 w-5" />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          {recent_activity.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">No activity yet</p>
          ) : (
            <div className="space-y-3">
              {recent_activity.map((a) => (
                <div key={a.id} className="flex items-start gap-3 text-sm border-b last:border-0 pb-3">
                  <div className="h-2 w-2 rounded-full bg-primary mt-2" />
                  <div>
                    <p>{a.action}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(a.created_at), { addSuffix: true })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
