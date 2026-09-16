import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { atlasApi } from "./api";
import { App } from "./main";

describe("App", () => {
  afterEach(cleanup);

  beforeEach(() => {
    sessionStorage.clear();
    vi.restoreAllMocks();
  });

  it("loads service health and readiness into the overview", async () => {
    vi.spyOn(atlasApi, "health").mockResolvedValue({
      status: "ok",
      services: [
        { name: "api", status: "healthy", detail: "" },
        { name: "GitHub", status: "disabled", detail: "Not configured" },
      ],
    });
    vi.spyOn(atlasApi, "ready").mockResolvedValue({ status: "ready", ollama: "available" });

    render(<App />);

    expect(await screen.findByText("System ready (partially configured)")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "api" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "GitHub" })).toBeTruthy();
  });

  it("stores a submitted API key for the current browser tab and reloads health", async () => {
    const health = vi.spyOn(atlasApi, "health").mockResolvedValue({
      status: "ok",
      services: [{ name: "api", status: "healthy", detail: "" }],
    });
    vi.spyOn(atlasApi, "ready").mockResolvedValue({ status: "ready", ollama: "available" });

    render(<App />);
    await screen.findByText("System ready");

    fireEvent.change(screen.getByLabelText("Atlas API key"), { target: { value: "session-key" } });
    fireEvent.click(screen.getByRole("button", { name: "Save key" }));

    await waitFor(() => expect(health).toHaveBeenCalledTimes(2));
    expect(sessionStorage.getItem("atlas-api-key")).toBe("session-key");
  });

  it("loads Docker inventory after selecting the diagnostic panel", async () => {
    vi.spyOn(atlasApi, "health").mockResolvedValue({
      status: "ok",
      services: [{ name: "api", status: "healthy", detail: "" }],
    });
    vi.spyOn(atlasApi, "ready").mockResolvedValue({ status: "ready", ollama: "available" });
    const containers = vi.spyOn(atlasApi, "containers").mockResolvedValue([
      { id: "atlas", status: "running" },
    ]);

    render(<App />);
    await screen.findByText("System ready");
    fireEvent.click(screen.getByRole("button", { name: "Docker" }));

    expect(await screen.findByRole("heading", { name: "Docker containers" })).toBeTruthy();
    expect(await screen.findByText(/"id": "atlas"/)).toBeTruthy();
    expect(containers).toHaveBeenCalledOnce();
  });

  it("switches between overview and interactive panels from the sidebar", async () => {
    vi.spyOn(atlasApi, "health").mockResolvedValue({
      status: "ok",
      services: [{ name: "api", status: "healthy", detail: "" }],
    });
    vi.spyOn(atlasApi, "ready").mockResolvedValue({ status: "ready", ollama: "available" });

    render(<App />);
    await screen.findByText("System ready");

    fireEvent.click(screen.getByRole("button", { name: "Automation" }));
    expect(screen.getByRole("heading", { name: "Observe-only remediation plan" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Log analysis" }));
    expect(screen.getByRole("heading", { name: "Local log analysis" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Incidents" }));
    expect(screen.getByRole("heading", { name: "Incident analysis" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Docker logs" }));
    expect(screen.getByRole("heading", { name: "Container logs" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Kubernetes pod logs" }));
    expect(screen.getByRole("heading", { name: "Kubernetes pod logs" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Overview" }));
    expect(screen.getByRole("heading", { name: "api" })).toBeTruthy();
  });

  it("loads container and pod logs from their dedicated panels", async () => {
    vi.spyOn(atlasApi, "health").mockResolvedValue({
      status: "ok",
      services: [{ name: "api", status: "healthy", detail: "" }],
    });
    vi.spyOn(atlasApi, "ready").mockResolvedValue({ status: "ready", ollama: "available" });
    const dockerLogs = vi.spyOn(atlasApi, "dockerLogs").mockResolvedValue({
      container: "atlas",
      tail: 200,
      logs: "container line",
    });
    const podLogs = vi.spyOn(atlasApi, "kubernetesPodLogs").mockResolvedValue({
      namespace: "default",
      pod: "atlas-api-0",
      tail: 200,
      logs: "pod line",
    });

    render(<App />);
    await screen.findByText("System ready");

    fireEvent.click(screen.getByRole("button", { name: "Docker logs" }));
    fireEvent.change(screen.getByLabelText("Container name or ID"), { target: { value: "atlas" } });
    fireEvent.click(screen.getByRole("button", { name: "Load logs" }));

    expect(await screen.findByText("atlas (last 200 lines)")).toBeTruthy();
    expect(screen.getByText("container line")).toBeTruthy();
    expect(dockerLogs).toHaveBeenCalledWith("atlas", 200);

    fireEvent.click(screen.getByRole("button", { name: "Kubernetes pod logs" }));
    fireEvent.change(screen.getByLabelText("Kubernetes pod name"), { target: { value: "atlas-api-0" } });
    fireEvent.click(screen.getByRole("button", { name: "Load logs" }));

    expect(await screen.findByText("default/atlas-api-0 (last 200 lines)")).toBeTruthy();
    expect(screen.getByText("pod line")).toBeTruthy();
    expect(podLogs).toHaveBeenCalledWith("default", "atlas-api-0", 200);
  });

  it("clears local history only after confirmation", async () => {
    vi.spyOn(atlasApi, "health").mockResolvedValue({
      status: "ok",
      services: [{ name: "api", status: "healthy", detail: "" }],
    });
    vi.spyOn(atlasApi, "ready").mockResolvedValue({ status: "ready", ollama: "available" });
    vi.spyOn(atlasApi, "history").mockResolvedValue([{
      id: 1,
      category: "chat",
      request: "Check Atlas",
      response: "{\"response\":\"healthy\"}",
      created_at: "2026-09-14T10:00:00Z",
    }]);
    const clearHistory = vi.spyOn(atlasApi, "clearHistory").mockResolvedValue({ deleted_entries: 1 });
    vi.spyOn(window, "confirm").mockReturnValue(true);

    render(<App />);
    await screen.findByText("System ready");
    fireEvent.click(screen.getByRole("button", { name: "History" }));
    expect(await screen.findByText("Check Atlas")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Clear local history" }));

    await waitFor(() => expect(clearHistory).toHaveBeenCalledOnce());
    expect(await screen.findByText("No local history yet.")).toBeTruthy();
  });

  it("shows a diagnostic API failure to the user", async () => {
    vi.spyOn(atlasApi, "health").mockResolvedValue({
      status: "ok",
      services: [{ name: "api", status: "healthy", detail: "" }],
    });
    vi.spyOn(atlasApi, "ready").mockResolvedValue({ status: "ready", ollama: "available" });
    vi.spyOn(atlasApi, "containers").mockRejectedValue(new Error("Docker socket is unavailable"));

    render(<App />);
    await screen.findByText("System ready");
    fireEvent.click(screen.getByRole("button", { name: "Docker" }));

    expect((await screen.findByRole("alert")).textContent).toContain("Docker socket is unavailable");
  });

  it("sends a chat message and displays its evidence", async () => {
    vi.spyOn(atlasApi, "health").mockResolvedValue({
      status: "ok",
      services: [{ name: "api", status: "healthy", detail: "" }],
    });
    vi.spyOn(atlasApi, "ready").mockResolvedValue({ status: "ready", ollama: "available" });
    const chat = vi.spyOn(atlasApi, "chat").mockResolvedValue({
      response: "The backend is healthy.",
      model: "llama3.2",
      evidence: ["Health endpoint returned ok."],
    });

    render(<App />);
    await screen.findByText("System ready");
    fireEvent.change(screen.getByLabelText("Ask Atlas"), { target: { value: "Is Atlas healthy?" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByText("The backend is healthy.")).toBeTruthy();
    expect(screen.getByText("Evidence: Health endpoint returned ok.")).toBeTruthy();
    expect(chat).toHaveBeenCalledWith("Is Atlas healthy?");
  });

  it("renders an observe-only automation plan with its required evidence", async () => {
    vi.spyOn(atlasApi, "health").mockResolvedValue({
      status: "ok",
      services: [{ name: "api", status: "healthy", detail: "" }],
    });
    vi.spyOn(atlasApi, "ready").mockResolvedValue({ status: "ready", ollama: "available" });
    const automationPlan = vi.spyOn(atlasApi, "automationPlan").mockResolvedValue({
      objective: "Investigate an unhealthy container",
      execution_mode: "observe-only",
      evidence_required: ["Inspect container status."],
      proposed_actions: ["Collect container logs."],
    });

    render(<App />);
    await screen.findByText("System ready");
    fireEvent.click(screen.getByRole("button", { name: "Automation" }));
    fireEvent.change(screen.getByLabelText("Automation objective"), {
      target: { value: "Investigate an unhealthy container" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Plan" }));

    expect(await screen.findByText("observe-only")).toBeTruthy();
    expect(screen.getByText("Evidence: Inspect container status.")).toBeTruthy();
    expect(screen.getByText("Actions: Collect container logs.")).toBeTruthy();
    expect(automationPlan).toHaveBeenCalledWith("Investigate an unhealthy container");
  });
});
