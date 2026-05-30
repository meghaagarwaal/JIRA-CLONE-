from pydantic import BaseModel


class DashboardStats(BaseModel):
    my_tickets: int
    completed_tickets: int
    open_tickets: int
    projects: int


class StatusChartItem(BaseModel):
    status: str
    count: int


class WeeklyProgressItem(BaseModel):
    day: str
    completed: int
    created: int


class DashboardResponse(BaseModel):
    stats: DashboardStats
    tickets_by_status: list[StatusChartItem]
    weekly_progress: list[WeeklyProgressItem]
