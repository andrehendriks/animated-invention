import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.config import get_settings
from app.dependencies import require_api_key
from app.models import AutomationPlan, AutomationPlanRequest, BackupStatus, ChatRequest, ChatResponse, DiagnosticItem, DockerContainerLogs, DockerContainerStats, HealthResponse, HistoryClearResponse, HistoryEntry, IncidentAnalysis, IncidentAnalysisRequest, KubernetesDeployment, KubernetesEvent, KubernetesPodLogs, LogAnalysis, LogAnalysisRequest, MonitoringAlert, MonitoringTarget, PullRequestSummary, RadioStatus, ReadinessResponse, SecurityFinding, StorageVolume
from app.agents.registry import get_agent_orchestrator
from app.services.command import CommandError
from app.services.docker_service import DockerService
from app.services.kubernetes_service import KubernetesService
from app.services.ollama_service import OllamaService
from app.services.synology_service import SynologyService
from app.services.monitoring_service import MonitoringService
from app.services.github_service import GitHubService
from app.services.radio_service import RadioService
from app.services.backup_service import BackupService
from app.services.security_service import SecurityService
from app.services.automation_service import AutomationService
from app.services.log_service import LogService
from app.services.incident_service import IncidentService
from app.services.history_service import HistoryService

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(require_api_key)])
public_router = APIRouter()


@public_router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        services=[
            DiagnosticItem(name="api", status="healthy"),
            DiagnosticItem(name="docker", status="configured" if settings.docker_enabled else "disabled"),
            DiagnosticItem(name="kubernetes", status="configured" if settings.kubernetes_enabled else "disabled"),
            DiagnosticItem(name="synology", status="configured" if settings.synology_enabled else "disabled"),
            DiagnosticItem(name="monitoring", status="configured" if settings.monitoring_enabled else "disabled"),
            DiagnosticItem(name="github", status="configured" if settings.github_enabled else "disabled"),
            DiagnosticItem(name="radio", status="configured" if settings.radio_enabled else "disabled"),
            DiagnosticItem(name="backup", status="configured" if settings.backup_enabled else "disabled"),
            DiagnosticItem(name="security", status="healthy"),
            DiagnosticItem(name="automation", status="observe-only"),
            DiagnosticItem(name="log-analysis", status="healthy"),
            DiagnosticItem(name="incident-analysis", status="healthy"),
        ],
    )


@public_router.get("/ready", response_model=ReadinessResponse)
async def ready() -> ReadinessResponse:
    try:
        await OllamaService().check_ready()
    except httpx.HTTPError as error:
        logger.warning("Atlas is not ready because Ollama is unavailable: %s", error)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama is unavailable",
        ) from error
    return ReadinessResponse(status="ready", ollama="available")


@router.get("/docker/containers")
async def docker_containers() -> list[dict[str, str]]:
    if not get_settings().docker_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Docker integration is disabled")
    try:
        return await DockerService().list_containers()
    except CommandError as error:
        logger.warning("Docker diagnostics unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.get("/docker/stats", response_model=list[DockerContainerStats])
async def docker_stats() -> list[DockerContainerStats]:
    if not get_settings().docker_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Docker integration is disabled")
    try:
        return await DockerService().list_stats()
    except (CommandError, ValueError) as error:
        logger.warning("Docker resource diagnostics unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.get("/docker/containers/{container}/logs", response_model=DockerContainerLogs)
async def docker_logs(
    container: str = Path(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$"),
    tail: int = Query(default=200, ge=1, le=1000),
) -> DockerContainerLogs:
    if not get_settings().docker_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Docker integration is disabled")
    try:
        return await DockerService().get_logs(container, tail)
    except (CommandError, ValueError) as error:
        logger.warning("Docker log diagnostics unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.get("/kubernetes/pods")
async def kubernetes_pods() -> list[dict[str, str]]:
    if not get_settings().kubernetes_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Kubernetes integration is disabled")
    try:
        return await KubernetesService().list_pods()
    except (CommandError, ValueError) as error:
        logger.warning("Kubernetes diagnostics unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.get("/kubernetes/deployments", response_model=list[KubernetesDeployment])
async def kubernetes_deployments() -> list[KubernetesDeployment]:
    if not get_settings().kubernetes_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Kubernetes integration is disabled")
    try:
        return await KubernetesService().list_deployments()
    except (CommandError, ValueError) as error:
        logger.warning("Kubernetes deployment diagnostics unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.get("/kubernetes/events", response_model=list[KubernetesEvent])
async def kubernetes_events() -> list[KubernetesEvent]:
    if not get_settings().kubernetes_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Kubernetes integration is disabled")
    try:
        return await KubernetesService().list_recent_events()
    except (CommandError, ValueError) as error:
        logger.warning("Kubernetes event diagnostics unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.get("/kubernetes/namespaces/{namespace}/pods/{pod}/logs", response_model=KubernetesPodLogs)
async def kubernetes_pod_logs(
    namespace: str = Path(pattern=r"^[a-z0-9](?:[-a-z0-9]{0,61}[a-z0-9])?$"),
    pod: str = Path(pattern=r"^[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?$"),
    tail: int = Query(default=200, ge=1, le=1000),
) -> KubernetesPodLogs:
    if not get_settings().kubernetes_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Kubernetes integration is disabled")
    try:
        return await KubernetesService().get_pod_logs(namespace, pod, tail)
    except (CommandError, ValueError) as error:
        logger.warning("Kubernetes pod log diagnostics unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.get("/synology/storage", response_model=list[StorageVolume])
async def synology_storage() -> list[StorageVolume]:
    settings = get_settings()
    if not settings.synology_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Synology integration is disabled")
    try:
        return SynologyService(settings.synology_mounts).list_volumes()
    except (OSError, ValueError) as error:
        logger.warning("Synology diagnostics unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.get("/monitoring/alerts", response_model=list[MonitoringAlert])
async def monitoring_alerts() -> list[MonitoringAlert]:
    settings = get_settings()
    if not settings.monitoring_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Monitoring integration is disabled")
    try:
        return await MonitoringService(settings.prometheus_base_url).list_alerts()
    except (httpx.HTTPError, ValueError) as error:
        logger.warning("Monitoring alerts unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Prometheus is unavailable") from error


@router.get("/monitoring/targets", response_model=list[MonitoringTarget])
async def monitoring_targets() -> list[MonitoringTarget]:
    settings = get_settings()
    if not settings.monitoring_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Monitoring integration is disabled")
    try:
        return await MonitoringService(settings.prometheus_base_url).list_targets()
    except (httpx.HTTPError, ValueError) as error:
        logger.warning("Monitoring targets unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Prometheus is unavailable") from error


@router.get("/github/pull-requests", response_model=list[PullRequestSummary])
async def github_pull_requests() -> list[PullRequestSummary]:
    settings = get_settings()
    if not settings.github_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="GitHub integration is disabled")
    try:
        return await GitHubService(
            settings.github_repositories, settings.github_token
        ).list_open_pull_requests()
    except (httpx.HTTPError, ValueError) as error:
        logger.warning("GitHub diagnostics unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="GitHub is unavailable") from error


@router.get("/radio/status", response_model=RadioStatus)
async def radio_status() -> RadioStatus:
    settings = get_settings()
    if not settings.radio_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Radio integration is disabled")
    try:
        return await RadioService(
            settings.icecast_status_url, settings.liquidsoap_health_url
        ).get_status()
    except (httpx.HTTPError, ValueError) as error:
        logger.warning("Radio diagnostics unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Icecast is unavailable") from error


@router.get("/backups/status", response_model=BackupStatus)
async def backup_status() -> BackupStatus:
    settings = get_settings()
    if not settings.backup_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Backup integration is disabled")
    try:
        return BackupService(settings.backup_path).get_status()
    except (OSError, ValueError) as error:
        logger.warning("Backup diagnostics unavailable: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.get("/security/posture", response_model=list[SecurityFinding])
async def security_posture() -> list[SecurityFinding]:
    return SecurityService(get_settings()).assess()


@router.post("/automation/plans", response_model=AutomationPlan)
async def automation_plan(request: AutomationPlanRequest) -> AutomationPlan:
    return AutomationService().plan(request.objective)


@router.post("/logs/analyze", response_model=LogAnalysis)
async def analyze_logs(request: LogAnalysisRequest) -> LogAnalysis:
    return LogService().analyze(request.logs)


@router.post("/incidents/analyze", response_model=IncidentAnalysis)
async def analyze_incident(request: IncidentAnalysisRequest) -> IncidentAnalysis:
    evidence = await get_agent_orchestrator().collect(request.symptoms)
    analysis = IncidentService().analyze(request.symptoms, evidence)
    settings = get_settings()
    HistoryService(settings.database_path, settings.history_max_entries).record(
        "incident", request.symptoms, analysis.model_dump_json()
    )
    return analysis


@router.get("/history", response_model=list[HistoryEntry])
async def history(limit: int = Query(default=50, ge=1, le=100)) -> list[HistoryEntry]:
    settings = get_settings()
    return HistoryService(settings.database_path, settings.history_max_entries).list_entries(limit)


@router.delete("/history", response_model=HistoryClearResponse)
async def clear_history() -> HistoryClearResponse:
    settings = get_settings()
    deleted_entries = HistoryService(
        settings.database_path, settings.history_max_entries
    ).clear()
    return HistoryClearResponse(deleted_entries=deleted_entries)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    settings = get_settings()
    evidence = await get_agent_orchestrator().collect(request.message)
    try:
        context = request.message
        if evidence:
            context = f"User request: {request.message}\n\nCollected evidence:\n" + "\n".join(
                f"- {item}" for item in evidence
            )
        response = await OllamaService().chat(context)
    except httpx.HTTPError as error:
        logger.warning("Ollama chat failed: %s", error)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Ollama is unavailable") from error
    result = ChatResponse(response=response, model=settings.ollama_model, evidence=evidence)
    HistoryService(settings.database_path, settings.history_max_entries).record(
        "chat", request.message, result.model_dump_json()
    )
    return result
