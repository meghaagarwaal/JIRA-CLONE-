import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "/api";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem("refresh_token");
      if (refresh) {
        try {
          const { data } = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refresh,
          });
          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return api(original);
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export interface User {
  id: string;
  name: string;
  email: string;
  avatar_url?: string;
  created_projects_count?: number;
  assigned_tickets_count?: number;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  project_key: string;
  owner_id: string;
  created_at: string;
  total_tickets: number;
  open_tickets: number;
  completed_tickets: number;
  member_count: number;
}

export interface UserBrief {
  id: string;
  name: string;
  email: string;
  avatar_url?: string;
}

export interface Ticket {
  id: string;
  ticket_key: string;
  ticket_number: number;
  title: string;
  description?: string;
  priority: string;
  status: string;
  story_points?: number;
  due_date?: string;
  project_id: string;
  project_key: string;
  project_name: string;
  reporter: UserBrief;
  assignee?: UserBrief;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: string;
  ticket_id: string;
  content: string;
  created_at: string;
  updated_at?: string;
  user_id: string;
  user_name: string;
  user_avatar?: string;
}

export interface Notification {
  id: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface Activity {
  id: string;
  user_id: string;
  user_name: string;
  ticket_id?: string;
  project_id?: string;
  action: string;
  created_at: string;
}

export interface DashboardData {
  stats: {
    my_tickets: number;
    completed_tickets: number;
    open_tickets: number;
    projects: number;
  };
  tickets_by_status: { status: string; count: number }[];
  weekly_progress: { day: string; completed: number; created: number }[];
}

export interface TicketListResponse {
  items: Ticket[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProjectDashboard {
  project: Project;
  recent_activity: Activity[];
}

export const authApi = {
  register: (data: { name: string; email: string; password: string }) =>
    api.post<User>("/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post<{ access_token: string; refresh_token: string }>("/auth/login", data),
  me: () => api.get<User>("/auth/me"),
};

export const projectsApi = {
  list: () => api.get<Project[]>("/projects"),
  get: (id: string) => api.get<Project>(`/projects/${id}`),
  dashboard: (id: string) => api.get<ProjectDashboard>(`/projects/${id}/dashboard`),
  create: (data: { name: string; description?: string; project_key: string }) =>
    api.post<Project>("/projects", data),
  update: (id: string, data: { name?: string; description?: string }) =>
    api.put<Project>(`/projects/${id}`, data),
  delete: (id: string) => api.delete(`/projects/${id}`),
};

export const ticketsApi = {
  list: (params?: Record<string, string | number>) =>
    api.get<TicketListResponse>("/tickets", { params }),
  byProject: (projectId: string) => api.get<Ticket[]>(`/tickets/project/${projectId}`),
  get: (id: string) => api.get<Ticket>(`/tickets/${id}`),
  create: (data: Record<string, unknown>) => api.post<Ticket>("/tickets", data),
  update: (id: string, data: Record<string, unknown>) => api.put<Ticket>(`/tickets/${id}`, data),
  delete: (id: string) => api.delete(`/tickets/${id}`),
};

export const commentsApi = {
  list: (ticketId: string) => api.get<Comment[]>(`/comments/ticket/${ticketId}`),
  create: (data: { ticket_id: string; content: string }) => api.post<Comment>("/comments", data),
  update: (id: string, content: string) => api.put<Comment>(`/comments/${id}`, { content }),
  delete: (id: string) => api.delete(`/comments/${id}`),
};

export const notificationsApi = {
  list: () => api.get<Notification[]>("/notifications"),
  markRead: (id: string) => api.patch<Notification>(`/notifications/${id}/read`),
};

export const dashboardApi = {
  get: () => api.get<DashboardData>("/dashboard"),
  activities: () => api.get<Activity[]>("/activities"),
};
