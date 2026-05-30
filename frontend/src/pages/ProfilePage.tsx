import { useAuth } from "@/lib/auth";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getInitials } from "@/lib/utils";

export function ProfilePage() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-3xl font-bold">Profile</h1>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarFallback className="text-lg">{getInitials(user.name)}</AvatarFallback>
            </Avatar>
            <div>
              <CardTitle>{user.name}</CardTitle>
              <p className="text-muted-foreground">{user.email}</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg border p-4 text-center">
              <p className="text-3xl font-bold">{user.created_projects_count ?? 0}</p>
              <p className="text-sm text-muted-foreground">Created Projects</p>
            </div>
            <div className="rounded-lg border p-4 text-center">
              <p className="text-3xl font-bold">{user.assigned_tickets_count ?? 0}</p>
              <p className="text-sm text-muted-foreground">Assigned Tickets</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
