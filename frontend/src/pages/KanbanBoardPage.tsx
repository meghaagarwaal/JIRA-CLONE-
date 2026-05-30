import { useMemo } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
  useDroppable,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { SortableContext, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { useState } from "react";
import { ticketsApi, type Ticket } from "@/lib/api";
import { STATUSES, priorityColors, cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function TicketCard({ ticket }: { ticket: Ticket }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: ticket.id,
    data: { ticket, status: ticket.status },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <Link to={`/tickets/${ticket.id}`}>
        <Card className="cursor-grab active:cursor-grabbing hover:border-primary/50 transition-colors mb-2">
          <CardContent className="p-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-muted-foreground">{ticket.ticket_key}</span>
              <Badge className={cn("text-xs", priorityColors[ticket.priority as keyof typeof priorityColors])}>
                {ticket.priority}
              </Badge>
            </div>
            <p className="text-sm font-medium line-clamp-2">{ticket.title}</p>
            {ticket.assignee && (
              <p className="text-xs text-muted-foreground">{ticket.assignee.name}</p>
            )}
          </CardContent>
        </Card>
      </Link>
    </div>
  );
}

function KanbanColumn({ status, tickets }: { status: string; tickets: Ticket[] }) {
  const { setNodeRef, isOver } = useDroppable({ id: status, data: { status } });
  const ids = tickets.map((t) => t.id);

  return (
    <div ref={setNodeRef} className="flex-shrink-0 w-72">
      <Card className={cn("h-full transition-colors", isOver && "border-primary")}>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center justify-between">
            {status}
            <span className="text-muted-foreground font-normal">{tickets.length}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="min-h-[200px]">
          <SortableContext items={ids} strategy={verticalListSortingStrategy}>
            {tickets.map((t) => (
              <TicketCard key={t.id} ticket={t} />
            ))}
          </SortableContext>
        </CardContent>
      </Card>
    </div>
  );
}

export function KanbanBoardPage() {
  const { id: projectId } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [activeTicket, setActiveTicket] = useState<Ticket | null>(null);

  const { data: tickets = [], isLoading } = useQuery({
    queryKey: ["project-tickets", projectId],
    queryFn: () => ticketsApi.byProject(projectId!).then((r) => r.data),
    enabled: !!projectId,
  });

  const updateMutation = useMutation({
    mutationFn: ({ ticketId, status }: { ticketId: string; status: string }) =>
      ticketsApi.update(ticketId, { status }),
    onMutate: async ({ ticketId, status }) => {
      await queryClient.cancelQueries({ queryKey: ["project-tickets", projectId] });
      const previous = queryClient.getQueryData<Ticket[]>(["project-tickets", projectId]);
      queryClient.setQueryData<Ticket[]>(["project-tickets", projectId], (old) =>
        old?.map((t) => (t.id === ticketId ? { ...t, status } : t)) ?? []
      );
      return { previous };
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["project-tickets", projectId], context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["project-tickets", projectId] });
    },
  });

  const columns = useMemo(() => {
    const grouped: Record<string, Ticket[]> = {};
    STATUSES.forEach((s) => (grouped[s] = []));
    tickets.forEach((t) => {
      if (grouped[t.status]) grouped[t.status].push(t);
    });
    return grouped;
  }, [tickets]);

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 8 } }));

  const handleDragStart = (event: DragStartEvent) => {
    const ticket = tickets.find((t) => t.id === event.active.id);
    if (ticket) setActiveTicket(ticket);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveTicket(null);
    const { active, over } = event;
    if (!over) return;

    const ticketId = active.id as string;
    const ticket = tickets.find((t) => t.id === ticketId);
    if (!ticket) return;

    let newStatus = over.data.current?.status as string | undefined;
    if (!newStatus && STATUSES.includes(over.id as typeof STATUSES[number])) {
      newStatus = over.id as string;
    }
    if (!newStatus) {
      const overTicket = tickets.find((t) => t.id === over.id);
      if (overTicket) newStatus = overTicket.status;
    }

    if (newStatus && newStatus !== ticket.status) {
      updateMutation.mutate({ ticketId, status: newStatus });
    }
  };

  if (isLoading) return <div className="text-muted-foreground">Loading board...</div>;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-3xl font-bold">Kanban Board</h1>
        <p className="text-muted-foreground">Drag tickets between columns to update status</p>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-4 overflow-x-auto pb-4">
          {STATUSES.map((status) => (
            <div key={status} id={status} data-status={status}>
              <KanbanColumn status={status} tickets={columns[status] || []} />
            </div>
          ))}
        </div>
        <DragOverlay>
          {activeTicket ? (
            <Card className="w-72 opacity-90 shadow-xl">
              <CardContent className="p-3">
                <span className="text-xs font-mono">{activeTicket.ticket_key}</span>
                <p className="text-sm font-medium mt-1">{activeTicket.title}</p>
              </CardContent>
            </Card>
          ) : null}
        </DragOverlay>
      </DndContext>
    </div>
  );
}
