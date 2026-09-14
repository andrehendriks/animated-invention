import json
import re

from app.services.command import run_read_only_command
from app.models import KubernetesDeployment, KubernetesEvent, KubernetesPodLogs

NAMESPACE_PATTERN = re.compile(r"^[a-z0-9](?:[-a-z0-9]{0,61}[a-z0-9])?$")
POD_NAME_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?$")


class KubernetesService:
    async def list_pods(self) -> list[dict[str, str]]:
        result = await run_read_only_command(
            "kubectl", "get", "pods", "--all-namespaces", "-o", "json"
        )
        payload = json.loads(result.stdout)
        return [
            {
                "name": item["metadata"]["name"],
                "namespace": item["metadata"]["namespace"],
                "status": item.get("status", {}).get("phase", "Unknown"),
            }
            for item in payload.get("items", [])
        ]

    async def list_deployments(self) -> list[KubernetesDeployment]:
        result = await run_read_only_command(
            "kubectl", "get", "deployments", "--all-namespaces", "-o", "json"
        )
        payload = json.loads(result.stdout)
        deployments: list[KubernetesDeployment] = []
        for item in payload.get("items", []):
            desired = item.get("spec", {}).get("replicas", 1)
            available = item.get("status", {}).get("availableReplicas", 0)
            deployments.append(
                KubernetesDeployment(
                    name=item["metadata"]["name"],
                    namespace=item["metadata"]["namespace"],
                    desired_replicas=desired,
                    available_replicas=available,
                    status="healthy" if available >= desired else "degraded",
                )
            )
        return deployments

    async def list_recent_events(self, limit: int = 100) -> list[KubernetesEvent]:
        result = await run_read_only_command(
            "kubectl", "get", "events", "--all-namespaces", "--sort-by=.lastTimestamp", "-o", "json"
        )
        payload = json.loads(result.stdout)
        items = payload.get("items", [])[-limit:]
        return [
            KubernetesEvent(
                namespace=item["metadata"]["namespace"],
                involved_object=item.get("involvedObject", {}).get("name", "unknown"),
                type=item.get("type", "Normal"),
                reason=item.get("reason", "Unknown"),
                message=item.get("message", ""),
                timestamp=item.get("eventTime") or item.get("lastTimestamp") or item.get("metadata", {}).get("creationTimestamp"),
            )
            for item in items
        ]

    async def get_pod_logs(self, namespace: str, pod: str, tail: int) -> KubernetesPodLogs:
        if not NAMESPACE_PATTERN.fullmatch(namespace):
            raise ValueError("Kubernetes namespace has an invalid format")
        if not POD_NAME_PATTERN.fullmatch(pod):
            raise ValueError("Kubernetes pod name has an invalid format")
        result = await run_read_only_command(
            "kubectl", "logs", "--namespace", namespace, "--tail", str(tail), pod
        )
        logs = "\n".join(part for part in (result.stdout, result.stderr) if part)[-100_000:]
        return KubernetesPodLogs(namespace=namespace, pod=pod, tail=tail, logs=logs)
