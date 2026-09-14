frontend/

├── README.md
├── package.json
├── vite.config.ts
├── tsconfig.json
├── Dockerfile
│
├── public/
│   ├── favicon.ico
│   └── logo.png
│
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   │
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Chat.tsx
│   │   ├── Kubernetes.tsx
│   │   ├── Docker.tsx
│   │   ├── Synology.tsx
│   │   ├── Radio.tsx
│   │   ├── Monitoring.tsx
│   │   ├── GitHub.tsx
│   │   ├── Incidents.tsx
│   │   └── Settings.tsx
│   │
│   ├── components/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── StatusCard.tsx
│   │   ├── ChatWindow.tsx
│   │   ├── LogViewer.tsx
│   │   ├── PodTable.tsx
│   │   ├── RadioPlayer.tsx
│   │   └── AlertPanel.tsx
│   │
│   ├── layouts/
│   │   └── MainLayout.tsx
│   │
│   ├── services/
│   │   ├── api.ts
│   │   ├── chat.ts
│   │   ├── kubernetes.ts
│   │   ├── docker.ts
│   │   ├── synology.ts
│   │   └── github.ts
│   │
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── usePods.ts
│   │   └── useSystemStatus.ts
│   │
│   ├── types/
│   │   ├── chat.ts
│   │   ├── pod.ts
│   │   └── alert.ts
│   │
│   └── assets/
│
└── tests/