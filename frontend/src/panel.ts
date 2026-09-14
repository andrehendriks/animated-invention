export type Panel =
  | "overview"
  | "containers"
  | "dockerStats"
  | "dockerLogs"
  | "pods"
  | "deployments"
  | "events"
  | "podLogs"
  | "storage"
  | "alerts"
  | "targets"
  | "pullRequests"
  | "radio"
  | "backups"
  | "security"
  | "automation"
  | "logs"
  | "incidents"
  | "history";

export type DiagnosticPanel = Exclude<
  Panel,
  "overview" | "automation" | "logs" | "incidents" | "dockerLogs" | "podLogs" | "history"
>;
