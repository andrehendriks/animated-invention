import { FormEvent, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { atlasApi, AutomationPlan, ChatResult, DockerContainerLogs, HistoryEntry, IncidentAnalysis, KubernetesPodLogs, LogAnalysis, ReadinessStatus, ServiceHealth, setApiKey } from "./api";
import { DashboardHeader } from "./components/DashboardHeader";
import { DiagnosticResult } from "./components/DiagnosticResult";
import { Sidebar } from "./components/Sidebar";
import { DiagnosticPanel, Panel } from "./panel";
import "./styles.css";

export function App() {
  const [health, setHealth] = useState<ServiceHealth[]>([]);
  const [readiness, setReadiness] = useState<ReadinessStatus | null>(null);
  const [isReady, setIsReady] = useState<boolean | null>(null);
  const [apiKey, setApiKeyValue] = useState(() => sessionStorage.getItem("atlas-api-key") ?? "");
  const [panel, setPanel] = useState<Panel>("overview");
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState<ChatResult | null>(null);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [objective, setObjective] = useState("");
  const [plan, setPlan] = useState<AutomationPlan | null>(null);
  const [logs, setLogs] = useState("");
  const [logAnalysis, setLogAnalysis] = useState<LogAnalysis | null>(null);
  const [symptoms, setSymptoms] = useState("");
  const [incident, setIncident] = useState<IncidentAnalysis | null>(null);
  const [container, setContainer] = useState("");
  const [containerLogs, setContainerLogs] = useState<DockerContainerLogs | null>(null);
  const [podNamespace, setPodNamespace] = useState("default");
  const [pod, setPod] = useState("");
  const [podLogs, setPodLogs] = useState<KubernetesPodLogs | null>(null);
  const [historyEntries, setHistoryEntries] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    setApiKey(apiKey);
    atlasApi.health().then((data) => setHealth(data.services)).catch((err: Error) => setError(err.message));
    atlasApi.ready().then((data) => {
      setReadiness(data);
      setIsReady(true);
    }).catch(() => setIsReady(false));
  }, []);

  async function saveApiKey(event: FormEvent) {
    event.preventDefault();
    setApiKey(apiKey);
    if (apiKey) sessionStorage.setItem("atlas-api-key", apiKey);
    else sessionStorage.removeItem("atlas-api-key");
    setError("");
    try { setHealth((await atlasApi.health()).services); } catch (err) { setError((err as Error).message); }
  }

  async function submitChat(event: FormEvent) {
    event.preventDefault();
    if (!message.trim()) return;
    setLoading(true); setError("");
    try { setChat(await atlasApi.chat(message)); } catch (err) { setError((err as Error).message); }
    finally { setLoading(false); }
  }

  async function loadDiagnostics(target: DiagnosticPanel | "history") {
    setPanel(target); setLoading(true); setError(""); setResult(null);
    try {
      if (target === "history") {
        setHistoryEntries(await atlasApi.history());
        return;
      }
      setResult(target === "containers" ? await atlasApi.containers() :
        target === "dockerStats" ? await atlasApi.dockerStats() :
          target === "pods" ? await atlasApi.pods() :
          target === "deployments" ? await atlasApi.deployments() :
            target === "events" ? await atlasApi.kubernetesEvents() :
              target === "storage" ? await atlasApi.storage() :
            target === "alerts" ? await atlasApi.alerts() :
              target === "targets" ? await atlasApi.targets() :
                target === "pullRequests" ? await atlasApi.pullRequests() :
                  target === "radio" ? await atlasApi.radio() :
                    target === "backups" ? await atlasApi.backupStatus() : await atlasApi.securityPosture());
    }
    catch (err) { setError((err as Error).message); } finally { setLoading(false); }
  }

  async function createPlan(event: FormEvent) {
    event.preventDefault();
    if (!objective.trim()) return;
    setLoading(true); setError("");
    try { setPlan(await atlasApi.automationPlan(objective)); } catch (err) { setError((err as Error).message); }
    finally { setLoading(false); }
  }

  async function analyzeLogs(event: FormEvent) {
    event.preventDefault();
    if (!logs.trim()) return;
    setLoading(true); setError("");
    try { setLogAnalysis(await atlasApi.analyzeLogs(logs)); } catch (err) { setError((err as Error).message); }
    finally { setLoading(false); }
  }

  async function analyzeIncident(event: FormEvent) {
    event.preventDefault();
    if (!symptoms.trim()) return;
    setLoading(true); setError("");
    try { setIncident(await atlasApi.analyzeIncident(symptoms)); } catch (err) { setError((err as Error).message); }
    finally { setLoading(false); }
  }

  async function loadContainerLogs(event: FormEvent) {
    event.preventDefault();
    if (!container.trim()) return;
    setLoading(true); setError("");
    try { setContainerLogs(await atlasApi.dockerLogs(container, 200)); } catch (err) { setError((err as Error).message); }
    finally { setLoading(false); }
  }

  async function loadPodLogs(event: FormEvent) {
    event.preventDefault();
    if (!podNamespace.trim() || !pod.trim()) return;
    setLoading(true); setError("");
    try { setPodLogs(await atlasApi.kubernetesPodLogs(podNamespace, pod, 200)); } catch (err) { setError((err as Error).message); }
    finally { setLoading(false); }
  }

  async function clearHistory() {
    if (!window.confirm("Delete all local Atlas history? This cannot be undone.")) return;
    setLoading(true); setError("");
    try {
      await atlasApi.clearHistory();
      setHistoryEntries([]);
    } catch (err) { setError((err as Error).message); }
    finally { setLoading(false); }
  }

  return <main>
    <Sidebar onLoadDiagnostics={loadDiagnostics} onLoadHistory={() => loadDiagnostics("history")} onSelectPanel={setPanel} />
    <section>
      <DashboardHeader apiKey={apiKey} health={health} isReady={isReady} readiness={readiness}
        onApiKeyChange={setApiKeyValue} onSaveApiKey={saveApiKey} />
      {error && <div className="error" role="alert">{error}</div>}
      {panel === "overview" && <div className="cards">{health.map((item) =>
        <article key={item.name}><h2>{item.name}</h2><strong>{item.status}</strong></article>
      )}</div>}
      {panel === "automation" && <div className="chat"><h2>Observe-only remediation plan</h2>
        <form onSubmit={createPlan}><input value={objective} onChange={(event) => setObjective(event.target.value)}
          placeholder="Investigate an unhealthy container" aria-label="Automation objective" /><button disabled={loading}>Plan</button></form>
        {plan && <article><strong>{plan.execution_mode}</strong><p>Evidence: {plan.evidence_required.join(" ")}</p><p>Actions: {plan.proposed_actions.join(" ")}</p></article>}
      </div>}
      {panel === "logs" && <div className="chat"><h2>Local log analysis</h2>
        <form onSubmit={analyzeLogs}><textarea value={logs} onChange={(event) => setLogs(event.target.value)}
          placeholder="Paste raw logs here" aria-label="Raw logs" /><button disabled={loading}>Analyze</button></form>
        {logAnalysis && <article><p>{logAnalysis.executive_summary}</p><p>{logAnalysis.technical_summary}</p><pre>{JSON.stringify(logAnalysis.issues, null, 2)}</pre></article>}
      </div>}
      {panel === "incidents" && <div className="chat"><h2>Incident analysis</h2>
        <form onSubmit={analyzeIncident}><input value={symptoms} onChange={(event) => setSymptoms(event.target.value)}
          placeholder="Describe the observed symptoms" aria-label="Incident symptoms" /><button disabled={loading}>Analyze</button></form>
        {incident && <article><p><strong>Root cause:</strong> {incident.root_cause}</p><p><strong>Impact:</strong> {incident.impact}</p><p><strong>Confidence:</strong> {incident.confidence_percent}%</p><p><strong>Evidence:</strong> {incident.evidence.join(" ") || "None collected."}</p><p><strong>Remediation:</strong> {incident.remediation.join(" ")}</p></article>}
      </div>}
      {panel === "dockerLogs" && <div className="chat"><h2>Container logs</h2>
        <form onSubmit={loadContainerLogs}><input value={container} onChange={(event) => setContainer(event.target.value)}
          placeholder="Container name or ID" aria-label="Container name or ID" /><button disabled={loading}>Load logs</button></form>
        {containerLogs && <article><p>{containerLogs.container} (last {containerLogs.tail} lines)</p><pre>{containerLogs.logs}</pre></article>}
      </div>}
      {panel === "podLogs" && <div className="chat"><h2>Kubernetes pod logs</h2>
        <form onSubmit={loadPodLogs}><input value={podNamespace} onChange={(event) => setPodNamespace(event.target.value)}
          placeholder="Namespace" aria-label="Kubernetes namespace" /><input value={pod} onChange={(event) => setPod(event.target.value)}
          placeholder="Pod name" aria-label="Kubernetes pod name" /><button disabled={loading}>Load logs</button></form>
        {podLogs && <article><p>{podLogs.namespace}/{podLogs.pod} (last {podLogs.tail} lines)</p><pre>{podLogs.logs}</pre></article>}
      </div>}
      {panel === "history" && <><h2>Local history</h2>
        <button onClick={clearHistory} disabled={loading || historyEntries.length === 0}>Clear local history</button>
        {loading ? <p>Loading diagnostics…</p> : historyEntries.length === 0 ? <p>No local history yet.</p> :
          <div className="history">{historyEntries.map((entry) => <article key={entry.id}>
            <p><strong>{entry.category}</strong> <small>{new Date(entry.created_at).toLocaleString()}</small></p>
            <p><strong>Request:</strong> {entry.request}</p>
            <pre>{entry.response}</pre>
          </article>)}</div>}</>}
      {panel !== "overview" && panel !== "automation" && panel !== "logs" && panel !== "incidents" && panel !== "dockerLogs" && panel !== "podLogs" && panel !== "history" &&
        <DiagnosticResult loading={loading} panel={panel} result={result} />}
      <div className="chat"><h2>Ask Atlas</h2>
        <form onSubmit={submitChat}><input value={message} onChange={(event) => setMessage(event.target.value)}
          placeholder="Why is a container unhealthy?" aria-label="Ask Atlas" /><button disabled={loading}>Send</button></form>
        {chat && <article><p>{chat.response}</p>{chat.evidence.length > 0 && <small>Evidence: {chat.evidence.join(" ")}</small>}</article>}
      </div>
    </section>
  </main>;
}

const rootElement = document.getElementById("root");
if (rootElement) {
  createRoot(rootElement).render(<App />);
}
