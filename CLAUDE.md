# CLAUDE.md - Project Context & Instructions

## 🏛️ PROJECT OVERVIEW

**Verdict360 AI Legal Chatbot Platform** - A comprehensive SaaS solution for South African law firms providing AI-powered client engagement through web chat widgets, voice calls, consultation booking, and legal knowledge integration.

### Key Business Metrics
- **Target Revenue**: R5,000-R10,000 monthly subscriptions
- **Market Size**: 81+ qualified SA law firms
- **ROI Potential**: 300-1,500% proven returns
- **Timeline**: 4-6 weeks to market-ready platform

## 📋 MANDATORY PROGRESS TRACKING

### ⚠️ CRITICAL INSTRUCTIONS FOR CLAUDE

**ALWAYS follow these steps when working on ANY task:**

1. **📖 READ PROJECT CONTEXT FIRST**
   ```bash
   - Read PROJECT_SUMMARY.md for current status
   - Read PROGRESS_TRACKING.md for completed tasks
   - Understand current implementation state before starting
   ```

2. **📝 CREATE TODO LIST**
   ```bash
   - Use TodoWrite tool at start of each session
   - Break complex tasks into specific, actionable items
   - Mark only ONE task as in_progress at a time
   ```

3. **✅ TRACK COMPLETION IMMEDIATELY**
   ```bash
   - Mark tasks completed as SOON as finished
   - Update PROGRESS_TRACKING.md with completion details
   - Never batch completions - update in real-time
   ```

4. **📊 REFERENCE PROJECT STATUS**
   ```bash
   - Always check current implementation percentages
   - Align new work with project priorities
   - Update PROJECT_SUMMARY.md if major progress made
   ```

### 🎯 CURRENT PROJECT PRIORITIES

**Phase 1: Voice Integration (Week 1-2) - 60% Complete**
- Implement Retell AI voice call integration
- Set up South African virtual phone numbers
- Connect voice transcription to consultation booking
- Test end-to-end voice consultation flow
- Integrate voice analytics with dashboard

**Phase 2: Dashboard Analytics (Week 2-3) - 40% Complete**
- Build conversation analytics pipeline
- Implement keyword extraction and trending
- Create conversion metric tracking
- Add voice call analytics and reporting
- Build law firm performance dashboards

**Phase 3: Calendar & Legal Knowledge (Week 3-4) - 30% Complete**
- Complete real-time calendar availability system
- Implement automated booking confirmation
- Add firm-specific legal knowledge management
- Integrate existing legal research tools
- Build legal content administration interface

## 🏗️ TECHNICAL ARCHITECTURE

### Backend (95% Complete)
- **Location**: `/api-python/` - FastAPI with legal processing APIs
- **Database**: PostgreSQL with chat, consultation, voice schemas
- **Vector Search**: ChromaDB with SA legal document embeddings
- **Authentication**: Keycloak with legal role-based access
- **Storage**: MinIO for legal documents
- **Compliance**: POPIA framework built-in

### Frontend (80% Complete)
- **Location**: `/web/` (renamed from web-sveltekit)
- **Framework**: SvelteKit with professional legal design system
- **Components**: Dashboard, chat interface, consultation forms
- **Widget**: Embeddable for law firm websites
- **Design**: Responsive with legal branding

### Infrastructure
- **Docker**: Full containerization with docker-compose
- **N8N**: Workflow automation for calendar/CRM integration
- **Redis**: Caching layer for performance
- **Keycloak**: Identity and access management

## 🔧 DEVELOPMENT GUIDELINES

### Code Standards
```bash
# Always run linting after changes
npm run lint        # Frontend linting
npm run typecheck   # TypeScript validation

# Test before committing
npm test           # Run test suites
```

### File Structure
```
verdict360-app/
├── CLAUDE.md                 # This file - project context
├── PROJECT_SUMMARY.md        # Current status & roadmap
├── PROGRESS_TRACKING.md      # Task completion log
├── api-python/              # FastAPI backend (95% complete)
├── web/                     # SvelteKit frontend (80% complete)
├── docker/                  # Container configurations
├── integrations/            # N8N workflows & CRM connections
└── mcp-servers/             # Legal document & analytics servers
```

### Git Workflow
```bash
# Standard commit format
git commit -m "type: description

- Specific change 1
- Specific change 2

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## 📚 CRITICAL FILES TO REFERENCE

### Always Read Before Starting Work:
1. **PROJECT_SUMMARY.md** - Current implementation status & roadmap
2. **PROGRESS_TRACKING.md** - Completed tasks & progress log
3. **ENV_SECURITY.md** - Security & POPIA compliance guidelines

### Update After Major Progress:
1. **PROGRESS_TRACKING.md** - Log all completed tasks
2. **PROJECT_SUMMARY.md** - Update completion percentages
3. **CLAUDE.md** - Modify priorities if needed

## 🎯 SUCCESS CRITERIA

### Technical Completion Checklist
- [ ] Voice calls functional with SA phone numbers
- [ ] Analytics dashboard with real conversation data
- [ ] Calendar booking working end-to-end
- [ ] Widget embeddable on law firm websites
- [ ] Legal knowledge management operational

### Business Readiness Checklist
- [ ] Demo environment for prospects
- [ ] Pricing/subscription system ready
- [ ] Multi-tenant deployment capability
- [ ] POPIA compliance documentation
- [ ] SA legal market entry preparation

## ⚡ QUICK START COMMANDS

### Development Environment
```bash
# Backend
cd api-python && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py

# Frontend  
cd web && npm install && npm run dev

# Full Stack
docker-compose up -d
```

### Common Tasks
```bash
# Run tests
cd web && npm test
cd api-python && python -m pytest

# Build production
cd web && npm run build
docker-compose -f docker-compose.yml up -d
```

## 🚨 IMPORTANT REMINDERS

1. **NEVER skip progress tracking** - Update PROGRESS_TRACKING.md after every completed task
2. **ALWAYS reference PROJECT_SUMMARY.md** - Understand current state before starting
3. **ONE task in_progress at a time** - Focus and complete before moving on
4. **Update completion percentages** - Keep PROJECT_SUMMARY.md accurate
5. **POPIA compliance first** - All voice/data handling must be compliant
6. **SA legal context** - All features must work for South African law firms

---

**Remember: This is a business-critical SaaS platform targeting R25,000+ MRR. Every task completed brings us closer to market deployment and revenue generation.**