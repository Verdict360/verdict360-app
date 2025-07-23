# Legal Chatbot Platform - Project Structure

## Current Architecture (Aligned)

```
verdict360-app/
├── web/                      # SvelteKit Frontend (Port 5173)
│   ├── src/
│   │   ├── lib/components/   # Legal SaaS & chatbot components
│   │   ├── lib/services/     # API integration services
│   │   ├── routes/           # SvelteKit routes
│   │   └── app.html
│   ├── package.json
│   └── vite.config.ts
├── api-python/               # FastAPI Backend (Port 8000)
│   ├── app/
│   │   ├── api/v1/endpoints/ # REST API endpoints
│   │   ├── services/         # Core business logic
│   │   ├── models/           # Database models
│   │   └── main.py
│   └── requirements.txt
├── docker/                   # Infrastructure
│   ├── postgres/             # Database initialization
│   ├── keycloak/            # Authentication service
│   └── n8n/                 # Workflow automation
├── integrations/             # N8N Workflows & MCP Servers
│   ├── n8n-workflows/       # Legal automation workflows
│   └── mcp-servers/         # Legal software integrations
├── docker-compose.yml        # All services orchestration
├── CLAUDE.md                # Development context
├── PROJECT_SUMMARY.md       # Current status & roadmap
└── PROGRESS_TRACKING.md     # Task completion log
```

## Service Ports
- **SvelteKit Frontend**: http://localhost:5173
- **FastAPI Backend**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Keycloak**: http://localhost:8080
- **Redis**: localhost:6379
- **MinIO**: http://localhost:9000
- **N8N**: http://localhost:5678

## Technology Stack
- **Frontend**: SvelteKit + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python + PostgreSQL
- **Authentication**: Keycloak
- **Storage**: MinIO (S3-compatible)
- **Workflows**: N8N
- **Infrastructure**: Docker Compose