import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { Trash2, Send } from "lucide-react";
import { ticketsApi, commentsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PRIORITIES, STATUSES, priorityColors, statusColors, cn, getInitials } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toaster";

export function TicketDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [comment, setComment] = useState("");

  const { data: ticket, isLoading } = useQuery({
    queryKey: ["ticket", id],
    queryFn: () => ticketsApi.get(id!).then((r) => r.data),
    enabled: !!id,
  });

  const { data: comments = [] } = useQuery({
    queryKey: ["comments", id],
    queryFn: () => commentsApi.list(id!).then((r) => r.data),
    enabled: !!id,
  });

  const updateMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => ticketsApi.update(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ticket", id] });
      toast({ title: "Ticket updated" });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => ticketsApi.delete(id!),
    onSuccess: () => {
      toast({ title: "Ticket deleted" });
      navigate("/tickets");
    },
  });

  const commentMutation = useMutation({
    mutationFn: () => commentsApi.create({ ticket_id: id!, content: comment }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["comments", id] });
      setComment("");
      toast({ title: "Comment added" });
    },
  });

  const deleteCommentMutation = useMutation({
    mutationFn: (commentId: string) => commentsApi.delete(commentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["comments", id] }),
  });

  if (isLoading) return <div className="text-muted-foreground">Loading...</div>;
  if (!ticket) return <div>Ticket not found</div>;

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-2 space-y-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="font-mono text-muted-foreground">{ticket.ticket_key}</span>
            <Badge className={priorityColors[ticket.priority as keyof typeof priorityColors]}>
              {ticket.priority}
            </Badge>
            <Badge className={statusColors[ticket.status as keyof typeof statusColors]}>
              {ticket.status}
            </Badge>
          </div>
          <h1 className="text-2xl font-bold">{ticket.title}</h1>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm whitespace-pre-wrap">{ticket.description || "No description"}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Comments ({comments.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {comments.length === 0 ? (
              <p className="text-sm text-muted-foreground">No comments yet</p>
            ) : (
              comments.map((c) => (
                <div key={c.id} className="flex gap-3">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback>{getInitials(c.user_name)}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{c.user_name}</span>
                      <span className="text-xs text-muted-foreground">
                        {format(new Date(c.created_at), "MMM d, yyyy h:mm a")}
                      </span>
                      {c.user_id === user?.id && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 ml-auto"
                          onClick={() => deleteCommentMutation.mutate(c.id)}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                    <p className="text-sm mt-1">{c.content}</p>
                  </div>
                </div>
              ))
            )}
            <div className="flex gap-2">
              <Input
                placeholder="Add a comment..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && comment && commentMutation.mutate()}
              />
              <Button size="icon" disabled={!comment} onClick={() => commentMutation.mutate()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div>
              <p className="text-muted-foreground mb-1">Status</p>
              <select
                className="w-full h-9 rounded-md border border-input bg-background px-2 text-sm"
                value={ticket.status}
                onChange={(e) => updateMutation.mutate({ status: e.target.value })}
              >
                {STATUSES.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <div>
              <p className="text-muted-foreground mb-1">Priority</p>
              <select
                className="w-full h-9 rounded-md border border-input bg-background px-2 text-sm"
                value={ticket.priority}
                onChange={(e) => updateMutation.mutate({ priority: e.target.value })}
              >
                {PRIORITIES.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div>
              <p className="text-muted-foreground">Reporter</p>
              <p className="font-medium">{ticket.reporter.name}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Assignee</p>
              <p className="font-medium">{ticket.assignee?.name || "Unassigned"}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Project</p>
              <p className="font-medium">{ticket.project_name}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Created</p>
              <p>{format(new Date(ticket.created_at), "MMM d, yyyy")}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Updated</p>
              <p>{format(new Date(ticket.updated_at), "MMM d, yyyy")}</p>
            </div>
          </CardContent>
        </Card>

        <Button
          variant="destructive"
          className="w-full"
          onClick={() => {
            if (confirm("Delete this ticket?")) deleteMutation.mutate();
          }}
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Delete Ticket
        </Button>
      </div>
    </div>
  );
}
