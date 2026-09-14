from pydantic import BaseModel, Field


class DiagnosticItem(BaseModel):
    name: str
    status: str
    detail: str = ""


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10_000)


class ChatResponse(BaseModel):
    response: str
    model: str
    evidence: list[str] = []


class HealthResponse(BaseModel):
    status: str
    services: list[DiagnosticItem]


class ReadinessResponse(BaseModel):
    status: str
    ollama: str


class StorageVolume(BaseModel):
    name: str
    path: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    usage_percent: float


class MonitoringAlert(BaseModel):
    name: str
    state: str
    severity: str
    summary: str = ""
    active_at: str | None = None


class MonitoringTarget(BaseModel):
    job: str
    instance: str
    health: str
    last_error: str = ""


class PullRequestSummary(BaseModel):
    repository: str
    number: int
    title: str
    author: str
    url: str
    draft: bool


class RadioMount(BaseModel):
    name: str
    listeners: int
    bitrate_kbps: int | None = None
    title: str = ""
    listen_url: str = ""


class RadioStatus(BaseModel):
    icecast_healthy: bool
    liquidsoap_healthy: bool | None = None
    mounts: list[RadioMount]


class BackupStatus(BaseModel):
    path: str
    file_count: int
    total_bytes: int
    newest_backup: str | None = None
    newest_backup_at: str | None = None


class SecurityFinding(BaseModel):
    severity: str
    category: str
    message: str
    remediation: str


class AutomationPlanRequest(BaseModel):
    objective: str = Field(min_length=1, max_length=2_000)


class AutomationPlan(BaseModel):
    objective: str
    execution_mode: str = "observe-only"
    evidence_required: list[str]
    proposed_actions: list[str]


class LogAnalysisRequest(BaseModel):
    logs: str = Field(min_length=1, max_length=100_000)


class LogIssue(BaseModel):
    category: str
    count: int
    first_timestamp: str | None = None
    last_timestamp: str | None = None
    example: str


class LogAnalysis(BaseModel):
    lines_analyzed: int
    executive_summary: str
    technical_summary: str
    issues: list[LogIssue]


class KubernetesDeployment(BaseModel):
    name: str
    namespace: str
    desired_replicas: int
    available_replicas: int
    status: str


class KubernetesEvent(BaseModel):
    namespace: str
    involved_object: str
    type: str
    reason: str
    message: str
    timestamp: str | None = None


class KubernetesPodLogs(BaseModel):
    namespace: str
    pod: str
    tail: int
    logs: str


class IncidentAnalysisRequest(BaseModel):
    symptoms: str = Field(min_length=1, max_length=2_000)


class IncidentAnalysis(BaseModel):
    symptoms: str
    evidence: list[str]
    root_cause: str
    impact: str
    remediation: list[str]
    confidence_percent: int = Field(ge=0, le=100)


class HistoryEntry(BaseModel):
    id: int
    category: str
    request: str
    response: str
    created_at: str


class HistoryClearResponse(BaseModel):
    deleted_entries: int


class DockerContainerStats(BaseModel):
    name: str
    container_id: str
    cpu_percent: str
    memory_usage: str
    memory_percent: str
    network_io: str


class DockerContainerLogs(BaseModel):
    container: str
    tail: int
    logs: str
