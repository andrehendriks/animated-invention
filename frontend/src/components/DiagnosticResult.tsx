import { DiagnosticPanel } from "../panel";

const titles: Record<DiagnosticPanel, string> = {
  containers: "Docker containers",
  dockerStats: "Docker resources",
  pods: "Kubernetes pods",
  deployments: "Kubernetes deployments",
  events: "Kubernetes events",
  storage: "Synology storage",
  alerts: "Prometheus alerts",
  targets: "Prometheus targets",
  pullRequests: "GitHub pull requests",
  radio: "Radio status",
  backups: "Backup status",
  security: "Security posture",
};

interface DiagnosticResultProps {
  loading: boolean;
  panel: DiagnosticPanel;
  result: unknown;
}

export function DiagnosticResult({ loading, panel, result }: DiagnosticResultProps) {
  return <>
    <h2>{titles[panel]}</h2>
    {loading ? <p>Loading diagnostics…</p> : <pre>{JSON.stringify(result, null, 2)}</pre>}
  </>;
}
