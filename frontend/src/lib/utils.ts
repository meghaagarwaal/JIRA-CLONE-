import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getInitials(name: string) {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export const PRIORITIES = ["Low", "Medium", "High", "Critical"] as const;
export const STATUSES = ["Backlog", "Todo", "In Progress", "In Review", "Done"] as const;

export type Priority = (typeof PRIORITIES)[number];
export type TicketStatus = (typeof STATUSES)[number];

export const priorityColors: Record<Priority, string> = {
  Low: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
  Medium: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  High: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  Critical: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export const statusColors: Record<TicketStatus, string> = {
  Backlog: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
  Todo: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300",
  "In Progress": "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  "In Review": "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  Done: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
};
