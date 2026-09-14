import { FormEvent } from "react";
import { ReadinessStatus, ServiceHealth } from "../api";

interface DashboardHeaderProps {
  apiKey: string;
  health: ServiceHealth[];
  isReady: boolean | null;
  readiness: ReadinessStatus | null;
  onApiKeyChange: (value: string) => void;
  onSaveApiKey: (event: FormEvent) => void;
}

export function DashboardHeader({
  apiKey,
  health,
  isReady,
  readiness,
  onApiKeyChange,
  onSaveApiKey,
}: DashboardHeaderProps) {
  const status = isReady === false ? "not ready" : isReady === true ? readiness?.status : "checking";
  const partiallyConfigured = isReady !== false && health.some((item) => item.status === "disabled");

  return <header>
    <span>System {status}{partiallyConfigured ? " (partially configured)" : ""}</span>
    <form onSubmit={onSaveApiKey}>
      <input
        type="password"
        value={apiKey}
        onChange={(event) => onApiKeyChange(event.target.value)}
        placeholder="API key (optional)"
        aria-label="Atlas API key"
        autoComplete="current-password"
      />
      <button>Save key</button>
    </form>
  </header>;
}
