export interface ServiceHealth {
  name: string;
  status: string;
  detail: string;
}

export interface ChatResult {
  response: string;
  model: string;
  evidence: string[];
}

export interface ReadinessStatus {
  status: string;
  ollama: string;
}

const baseUrl = import.meta.env.VITE_API_URL ?? "/api";
let apiKey = "";

export function setApiKey(value: string): void {
  apiKey = value;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(apiKey ? { "X-API-Key": apiKey } : {}),
      ...init?.headers,
    },
    ...init,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const atlasApi = {
  health: () => request<{ status: string; services: ServiceHealth[] }>("/health"),
  ready: () => request<ReadinessStatus>("/ready"),
  containers: () => request<Record<string, string>[]>("/docker/containers"),
  dockerStats: () => request<DockerContainerStats[]>("/docker/stats"),
  dockerLogs: (container: string, tail: number) =>
    request<DockerContainerLogs>(`/docker/containers/${encodeURIComponent(container)}/logs?tail=${tail}`),
  pods: () => request<{ name: string; namespace: string; status: string }[]>("/kubernetes/pods"),
  deployments: () => request<KubernetesDeployment[]>("/kubernetes/deployments"),
  kubernetesEvents: () => request<KubernetesEvent[]>("/kubernetes/events"),
  kubernetesPodLogs: (namespace: string, pod: string, tail: number) =>
    request<KubernetesPodLogs>(`/kubernetes/namespaces/${encodeURIComponent(namespace)}/pods/${encodeURIComponent(pod)}/logs?tail=${tail}`),
  history: () => request<HistoryEntry[]>("/history"),
  clearHistory: () => request<HistoryClearResponse>("/history", { method: "DELETE" }),
  storage: () => request<StorageVolume[]>("/synology/storage"),
  alerts: () => request<MonitoringAlert[]>("/monitoring/alerts"),
  targets: () => request<MonitoringTarget[]>("/monitoring/targets"),
  pullRequests: () => request<PullRequestSummary[]>("/github/pull-requests"),
  radio: () => request<RadioStatus>("/radio/status"),
  backupStatus: () => request<BackupStatus>("/backups/status"),
  securityPosture: () => request<SecurityFinding[]>("/security/posture"),
  automationPlan: (objective: string) =>
    request<AutomationPlan>("/automation/plans", { method: "POST", body: JSON.stringify({ objective }) }),
  analyzeLogs: (logs: string) =>
    request<LogAnalysis>("/logs/analyze", { method: "POST", body: JSON.stringify({ logs }) }),
  analyzeIncident: (symptoms: string) =>
    request<IncidentAnalysis>("/incidents/analyze", { method: "POST", body: JSON.stringify({ symptoms }) }),
  chat: (message: string) =>
    request<ChatResult>("/chat", { method: "POST", body: JSON.stringify({ message }) }),
};

export interface StorageVolume {
  name: string;
  path: string;
  total_bytes: number;
  used_bytes: number;
  free_bytes: number;
  usage_percent: number;
}

export interface KubernetesDeployment {
  name: string;
  namespace: string;
  desired_replicas: number;
  available_replicas: number;
  status: string;
}

export interface DockerContainerStats {
  name: string;
  container_id: string;
  cpu_percent: string;
  memory_usage: string;
  memory_percent: string;
  network_io: string;
}

export interface DockerContainerLogs {
  container: string;
  tail: number;
  logs: string;
}

export interface KubernetesEvent {
  namespace: string;
  involved_object: string;
  type: string;
  reason: string;
  message: string;
  timestamp: string | null;
}

export interface KubernetesPodLogs {
  namespace: string;
  pod: string;
  tail: number;
  logs: string;
}

export interface HistoryEntry {
  id: number;
  category: string;
  request: string;
  response: string;
  created_at: string;
}

export interface HistoryClearResponse {
  deleted_entries: number;
}

export interface MonitoringAlert {
  name: string;
  state: string;
  severity: string;
  summary: string;
  active_at: string | null;
}

export interface MonitoringTarget {
  job: string;
  instance: string;
  health: string;
  last_error: string;
}

export interface PullRequestSummary {
  repository: string;
  number: number;
  title: string;
  author: string;
  url: string;
  draft: boolean;
}

export interface RadioStatus {
  icecast_healthy: boolean;
  liquidsoap_healthy: boolean | null;
  mounts: RadioMount[];
}

export interface RadioMount {
  name: string;
  listeners: number;
  bitrate_kbps: number | null;
  title: string;
  listen_url: string;
}

export interface BackupStatus {
  path: string;
  file_count: number;
  total_bytes: number;
  newest_backup: string | null;
  newest_backup_at: string | null;
}

export interface SecurityFinding {
  severity: string;
  category: string;
  message: string;
  remediation: string;
}

export interface AutomationPlan {
  objective: string;
  execution_mode: string;
  evidence_required: string[];
  proposed_actions: string[];
}

export interface LogAnalysis {
  lines_analyzed: number;
  executive_summary: string;
  technical_summary: string;
  issues: LogIssue[];
}

export interface LogIssue {
  category: string;
  count: number;
  first_timestamp: string | null;
  last_timestamp: string | null;
  example: string;
}

export interface IncidentAnalysis {
  symptoms: string;
  evidence: string[];
  root_cause: string;
  impact: string;
  remediation: string[];
  confidence_percent: number;
}
