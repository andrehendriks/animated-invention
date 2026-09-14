import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DashboardHeader } from "./DashboardHeader";
import { DiagnosticResult } from "./DiagnosticResult";
import { Sidebar } from "./Sidebar";

describe("Sidebar", () => {
  it("keeps diagnostic and interactive navigation available", () => {
    const onLoadDiagnostics = vi.fn();
    const onLoadHistory = vi.fn();
    const onSelectPanel = vi.fn();

    render(<Sidebar
      onLoadDiagnostics={onLoadDiagnostics}
      onLoadHistory={onLoadHistory}
      onSelectPanel={onSelectPanel}
    />);

    fireEvent.click(screen.getByRole("button", { name: "Docker resources" }));
    fireEvent.click(screen.getByRole("button", { name: "History" }));
    fireEvent.click(screen.getByRole("button", { name: "Log analysis" }));

    expect(onLoadDiagnostics).toHaveBeenCalledWith("dockerStats");
    expect(onLoadHistory).toHaveBeenCalledOnce();
    expect(onSelectPanel).toHaveBeenCalledWith("logs");
  });
});

describe("DashboardHeader", () => {
  it("reports a partially configured ready system and saves the entered key", () => {
    const onApiKeyChange = vi.fn();
    const onSaveApiKey = vi.fn((event) => event.preventDefault());

    render(<DashboardHeader
      apiKey=""
      health={[{ name: "GitHub", status: "disabled", detail: "Not configured" }]}
      isReady={true}
      readiness={{ status: "ready", ollama: "available" }}
      onApiKeyChange={onApiKeyChange}
      onSaveApiKey={onSaveApiKey}
    />);

    fireEvent.change(screen.getByLabelText("Atlas API key"), { target: { value: "test-key" } });
    fireEvent.click(screen.getByRole("button", { name: "Save key" }));

    expect(screen.getByText("System ready (partially configured)")).toBeTruthy();
    expect(onApiKeyChange).toHaveBeenCalledWith("test-key");
    expect(onSaveApiKey).toHaveBeenCalledOnce();
  });
});

describe("DiagnosticResult", () => {
  it("renders a human-readable panel title and serialized response", () => {
    render(<DiagnosticResult loading={false} panel="targets" result={[{ health: "up" }]} />);

    expect(screen.getByRole("heading", { name: "Prometheus targets" })).toBeTruthy();
    expect(screen.getByText(/"health": "up"/)).toBeTruthy();
  });
});
