from functools import lru_cache
import os


class Settings:
    """Application settings sourced from the environment."""

    app_name = os.getenv("ATLAS_APP_NAME", "Project Atlas")
    environment = os.getenv("ATLAS_ENVIRONMENT", "development")
    auth_enabled = os.getenv("ATLAS_AUTH_ENABLED", "false").lower() == "true"
    api_key = os.getenv("ATLAS_API_KEY", "")
    ollama_base_url = os.getenv("ATLAS_OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("ATLAS_OLLAMA_MODEL", "llama3.2")
    ollama_request_timeout_seconds = int(os.getenv("ATLAS_OLLAMA_REQUEST_TIMEOUT_SECONDS", "180"))
    docker_enabled = os.getenv("ATLAS_DOCKER_ENABLED", "true").lower() == "true"
    kubernetes_enabled = os.getenv("ATLAS_KUBERNETES_ENABLED", "true").lower() == "true"
    synology_enabled = os.getenv("ATLAS_SYNOLOGY_ENABLED", "false").lower() == "true"
    monitoring_enabled = os.getenv("ATLAS_MONITORING_ENABLED", "false").lower() == "true"
    prometheus_base_url = os.getenv("ATLAS_PROMETHEUS_BASE_URL", "http://localhost:9090")
    github_enabled = os.getenv("ATLAS_GITHUB_ENABLED", "false").lower() == "true"
    github_token = os.getenv("ATLAS_GITHUB_TOKEN", "")
    radio_enabled = os.getenv("ATLAS_RADIO_ENABLED", "false").lower() == "true"
    icecast_status_url = os.getenv("ATLAS_ICECAST_STATUS_URL", "http://localhost:8000/status-json.xsl")
    liquidsoap_health_url = os.getenv("ATLAS_LIQUIDSOAP_HEALTH_URL", "")
    backup_enabled = os.getenv("ATLAS_BACKUP_ENABLED", "false").lower() == "true"
    backup_path = os.getenv("ATLAS_BACKUP_PATH", "/mnt/atlas-backups")
    database_path = os.getenv("ATLAS_DATABASE_PATH", "/data/atlas.db")
    history_max_entries = int(os.getenv("ATLAS_HISTORY_MAX_ENTRIES", "1000"))

    @property
    def allowed_origins(self) -> list[str]:
        value = os.getenv("ATLAS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8080")
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @property
    def synology_mounts(self) -> dict[str, str]:
        """Return configured logical storage names and their local mount paths."""
        mounts: dict[str, str] = {}
        for item in os.getenv("ATLAS_SYNOLOGY_MOUNTS", "").split(","):
            if not item.strip():
                continue
            name, separator, path = item.partition("=")
            if not separator or not name.strip() or not path.strip():
                raise ValueError("ATLAS_SYNOLOGY_MOUNTS entries must use name=/absolute/path")
            mounts[name.strip()] = path.strip()
        return mounts

    @property
    def github_repositories(self) -> list[str]:
        repositories = [item.strip() for item in os.getenv("ATLAS_GITHUB_REPOSITORIES", "").split(",") if item.strip()]
        if any(repository.count("/") != 1 for repository in repositories):
            raise ValueError("ATLAS_GITHUB_REPOSITORIES entries must use owner/repository")
        return repositories


@lru_cache
def get_settings() -> Settings:
    return Settings()
