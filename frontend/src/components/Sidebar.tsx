import { DiagnosticPanel, Panel } from "../panel";

interface SidebarProps {
  onLoadDiagnostics: (panel: DiagnosticPanel) => void;
  onLoadHistory: () => void;
  onSelectPanel: (panel: Panel) => void;
}

const diagnosticItems: { panel: DiagnosticPanel; label: string }[] = [
  { panel: "containers", label: "Docker" },
  { panel: "dockerStats", label: "Docker resources" },
  { panel: "pods", label: "Kubernetes" },
  { panel: "deployments", label: "Deployments" },
  { panel: "events", label: "Kubernetes events" },
  { panel: "storage", label: "Synology" },
  { panel: "alerts", label: "Alerts" },
  { panel: "targets", label: "Monitoring" },
  { panel: "pullRequests", label: "GitHub" },
  { panel: "radio", label: "Radio" },
  { panel: "backups", label: "Backups" },
  { panel: "security", label: "Security" },
];

export function Sidebar({ onLoadDiagnostics, onLoadHistory, onSelectPanel }: SidebarProps) {
  return <aside>
    <h1>ATLAS</h1>
    <p>Local HomeLab Assistant</p>
    <button onClick={() => onSelectPanel("overview")}>Overview</button>
    {diagnosticItems.slice(0, 2).map(({ panel, label }) =>
      <button key={panel} onClick={() => onLoadDiagnostics(panel)}>{label}</button>,
    )}
    <button onClick={() => onSelectPanel("dockerLogs")}>Docker logs</button>
    {diagnosticItems.slice(2, 5).map(({ panel, label }) =>
      <button key={panel} onClick={() => onLoadDiagnostics(panel)}>{label}</button>,
    )}
    <button onClick={() => onSelectPanel("podLogs")}>Kubernetes pod logs</button>
    {diagnosticItems.slice(5).map(({ panel, label }) =>
      <button key={panel} onClick={() => onLoadDiagnostics(panel)}>{label}</button>,
    )}
    <button onClick={() => onSelectPanel("automation")}>Automation</button>
    <button onClick={() => onSelectPanel("logs")}>Log analysis</button>
    <button onClick={() => onSelectPanel("incidents")}>Incidents</button>
    <button onClick={onLoadHistory}>History</button>
  </aside>;
}
