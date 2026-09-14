scripts/

├── README.md
│
├── bootstrap/
│   ├── bootstrap.sh
│   ├── bootstrap.ps1
│   ├── initialize_repo.sh
│   └── create_structure.sh
│
├── install/
│   ├── install_backend.sh
│   ├── install_frontend.sh
│   ├── install_ollama.sh
│   ├── install_postgres.sh
│   ├── install_monitoring.sh
│   └── install_all.sh
│
├── deploy/
│   ├── deploy_local.sh
│   ├── deploy_docker.sh
│   ├── deploy_kubernetes.sh
│   ├── deploy_dev.sh
│   ├── deploy_test.sh
│   └── deploy_prod.sh
│
├── backup/
│   ├── backup_database.sh
│   ├── backup_configs.sh
│   ├── backup_volumes.sh
│   ├── backup_atlas.sh
│   └── verify_backup.sh
│
├── restore/
│   ├── restore_database.sh
│   ├── restore_configs.sh
│   ├── restore_volumes.sh
│   └── restore_atlas.sh
│
├── maintenance/
│   ├── cleanup_logs.sh
│   ├── cleanup_images.sh
│   ├── update_dependencies.sh
│   ├── rotate_logs.sh
│   └── healthcheck.sh
│
├── diagnostics/
│   ├── check_kubernetes.sh
│   ├── check_docker.sh
│   ├── check_synology.sh
│   ├── check_ollama.sh
│   ├── check_storage.sh
│   └── full_diagnostics.sh
│
├── agents/
│   ├── agent_status.sh
│   ├── restart_agents.sh
│   └── verify_agents.sh
│
├── radio/
│   ├── restart_icecast.sh
│   ├── restart_liquidsoap.sh
│   ├── check_stream.sh
│   ├── verify_music_mount.sh
│   └── collect_radio_logs.sh
│
├── monitoring/
│   ├── export_metrics.sh
│   ├── grafana_backup.sh
│   └── prometheus_backup.sh
│
├── github/
│   ├── release.sh
│   ├── changelog.sh
│   └── sync_docs.sh
│
└── windows/
    ├── deploy.ps1
    ├── backup.ps1
    ├── restore.ps1
    └── diagnostics.ps1