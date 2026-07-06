# LearnFlow — AI-Driven Learning Execution System

**[中文文档](README.md)**

LearnFlow is a personal learning execution app built on one core principle: **forced output loop**. Every learning step must pass AI review before the next step unlocks, ensuring knowledge is truly absorbed — not just "read through."

## Core Mechanism

LearnFlow is not a "course recommender" — it's a "learning executor." It solves the core problem: many people create study plans they never follow through on, or passively consume content without truly understanding it.

**Forced Output Loop:** Submit output → AI review (pass ≥70) → unlock next step. If the AI review fails, the user must revise and resubmit until it passes.

**Three Embedded Learning Methods:**

1. **Learning Ladder (5-level progression)** — Cognitive Awakening → Foundation Building → Practical Application → Deep Expansion → Systematic Output. Each level has clear pass criteria and common mistake alerts.
2. **Pareto Principle (80/20 Rule)** — Each week's content is tagged with "Core 20%," focusing on the knowledge that solves 80% of real-world problems.
3. **Feynman Technique + Socratic Questioning** — AI review doesn't just score — it uses Socratic follow-up questions to test depth of understanding, and the Feynman technique to detect whether the user is just stacking jargon.

## Skill Design Philosophy

LearnFlow's backend deeply embeds two core Skills, transforming learning methodologies from "documentation" into "executable code."

### Skill 1: Learning Plan Engine (learning-plan-engine)

**Design positioning:** Execution engine Skill — the user inputs a vague learning goal, and the Skill automatically outputs a daily executable learning plan.

**Embedded at:** `backend/app/services/plan_engine.py`

**3 embedded learning methods:**

| Method | Code Representation | Purpose |
|---|---|---|
| **Learning Ladder** | `LADDER_LEVELS` defines beginner/intermediate/advanced sets of 5-level progression, each with core_knowledge, common_mistakes, pass_criteria | Distributes total weeks proportionally across 5 levels, ensuring progressive difficulty |
| **Pareto Principle** | `CORE_20_TEMPLATES` defines core_20_focus for each learning goal (intro/systematic/practical/mastery/explore), tagged as "Core 20%" in generated content | Keeps weekly content focused on high-value knowledge, avoiding shallow breadth |
| **Signal in Noise** | LLM prompt requires 3-5 curated resources per week with type/level/duration/why, must include doc resources, videos prioritized from Bilibili | Filters truly time-worthy resources from the ocean of available content |

**Workflow:** User inputs topic, goal, level, and schedule via PlanWizard → `generate_learning_plan()` builds the ladder → LLM generates content in 4-week batches (avoiding JSON truncation) → falls back to `topic_library.py` presets when LLM is unavailable → outputs complete steps + milestones.

### Skill 2: Learning Output Reviewer (learning-output-reviewer)

**Design positioning:** Forced-loop Skill — after users submit learning output, AI acts as a strict mentor, blocking progression until the output passes review.

**Embedded at:** `backend/app/services/reviewer.py`

**3 embedded learning methods:**

| Method | Code Representation | Purpose |
|---|---|---|
| **Socratic Questioning** | Each review generates 1 deep-dive question (`socratic_question`), pushing users to think further rather than stay surface-level | Verifies genuine understanding vs. memorized terminology |
| **Feynman Technique** | `feynman_score` at 25% weight, detects `simple_language` (plain words), `has_analogy` (analogies used), `jargon_overuse` (term stacking) | Ensures users can "explain to a layperson," not just recite definitions |
| **Cheat Sheet Compression** | Auto-generates `cheat_sheet` suggestion upon passing, compressing core knowledge into a structured reference card | Facilitates long-term retention and quick review |

**Review dimensions & weights:** Depth of Understanding (30%) + Accuracy (25%) + Completeness (20%) + Original Expression (15%) + Practical Relevance (10%). ≥70 to pass and unlock next step; <70 returns feedback + 3 improvement suggestions, requiring revision and resubmission.

**Dual-channel review:** AI review (full Socratic + Feynman + cheat sheet) when LLM API is available; rule-based review (heuristic scoring by word count, examples, personal reflection, structure) as fallback.

### Skill Collaboration Architecture

Beyond the two core Skills embedded in the backend, LearnFlow also includes two supporting Skills:

```
┌─────────────────────────────────────────────────┐
│              ai-learning-coach                    │
│   6 learning methods + 18 scenario variants      │
│   (Methodology source, not directly executable)   │
└───────────────┬─────────────────┬───────────────┘
                │ splits to       │ splits to
                ▼                 ▼
┌───────────────────────┐ ┌───────────────────────┐
│ learning-plan-engine  │ │learning-output-reviewer│
│ Plan generation       │ │ Output review          │
│ Ladder+Pareto+Signal  │ │ Socratic+Feynman+Sheet │
│ Code: plan_engine.py  │ │ Code: reviewer.py      │
└───────────┬───────────┘ └───────────┬───────────┘
            │ API                     │ API
            ▼                         ▼
┌─────────────────────────────────────────────────┐
│              ai-learning-engine                   │
│   Orchestration — chains plan gen + review loop   │
│   Calls POST /api/plans/wizard + POST /api/review │
│   Includes generate_plan.py CLI helper            │
└─────────────────────────────────────────────────┘
```

`ai-learning-coach` provides the methodology framework (6 learning methods), `ai-learning-engine` is the orchestration layer, and the two core Skills handle "plan generation" and "output review" respectively. Four layers collaborate to form a complete learning loop: Theory → Engine → API → User Interaction.

## Tech Stack

| Layer | Technology | Description |
|---|---|---|
| Frontend | Vue 3 + Vite + Element Plus | SPA, responsive PC/Mobile split layouts |
| State Management | Pinia | Lightweight state management |
| i18n | vue-i18n | Bilingual (zh-CN / en-US) |
| Backend | FastAPI | Python async web framework |
| Database | SQLite + SQLAlchemy | Zero-config local storage |
| LLM | OpenAI-compatible API | Supports any OpenAI-compatible endpoint (currently MiMo V2.5) |
| Notifications | Feishu / DingTalk / Desktop native / WeChat subscription | Multi-channel learning reminders |
| Scheduler | APScheduler | Daily reminder tasks |
| WeChat Mini Program | uni-app (Vue 3) | Cross-platform mini program, shared backend API |

## Project Structure

```
learnflow/
├── data/                           # SQLite database (gitignored)
│   └── learnflow.db
├── backend/
│   ├── .env                        # Environment variables (LLM API config, gitignored)
│   ├── requirements.txt            # Python dependencies
│   └── app/
│       ├── main.py                 # FastAPI entry, mount routers + static files
│       ├── config.py               # pydantic-settings configuration loader
│       ├── database.py             # SQLAlchemy engine + table migration
│       ├── models.py               # ORM models (5 tables)
│       ├── schemas.py              # Pydantic request/response schemas
│       ├── routers/                # API route layer
│       │   ├── auth.py             # WeChat login + dev login
│       │   ├── plans.py            # Learning plan CRUD + Wizard creation
│       │   ├── steps.py            # Learning step queries + state transitions
│       │   ├── review.py           # AI review (Socratic + Feynman + cheat sheet)
│       │   ├── reminders.py        # Learning reminder management
│       │   ├── achievements.py     # Achievement badge queries
│       │   ├── config.py           # LLM configuration read/write
│       │   └── profile.py          # Personal learning statistics
│       └── services/               # Business logic layer
│           ├── plan_engine.py      # Plan generation engine (Ladder + 80/20 + LLM)
│           ├── reviewer.py         # AI review service (Socratic + Feynman)
│           ├── topic_library.py    # Topic content library (React/Python/LLM presets)
│           ├── dashboard.py        # Dashboard data aggregation
│           ├── profile.py          # Personal profile statistics
│           ├── scheduler.py        # APScheduler timed reminders
│           ├── wx_notify.py        # WeChat subscription message service
│           └── notifiers/          # Multi-channel notifications (desktop/Feishu/DingTalk/WeChat)
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js              # Vite config + API proxy
    └── src/
        ├── main.js                 # Vue entry (Pinia + Router + Element Plus + i18n)
        ├── App.vue                 # Root component (device detection + layout switching)
        ├── router.js               # Router entry (loads routes by device type)
        ├── api/
        │   └── client.js           # Axios wrapper (8 API modules)
        ├── composables/
        │   └── useDevice.js        # Device detection composable (768px breakpoint)
        ├── i18n/
        │   ├── index.js            # vue-i18n configuration
        │   ├── zh-CN.js            # Chinese translations (216 lines)
        │   └── en-US.js            # English translations (216 lines)
        ├── layouts/
        │   ├── MobileLayout.vue    # Mobile: bottom 4-tab navigation
        │   └── PcLayout.vue        # PC: left sidebar + top bar
        ├── router/
        │   ├── mobile.js           # Mobile routes (4 pages, no admin)
        │   └── pc.js               # PC routes (4 pages + admin panel)
        ├── stores/
        │   └── plan.js             # Pinia plan state management
        └── views/
            ├── Dashboard.vue       # Home dashboard (progress, today's task, milestones)
            ├── PlanWizard.vue      # Plan creation wizard (4 steps)
            ├── LearningView.vue    # Main learning page (step list + detail + output submission)
            ├── ProfileView.vue     # Personal profile (stats + streak + achievements)
            ├── ReviewOutput.vue    # Review result page
            ├── Settings.vue        # Settings page (notification channels + plan management)
            ├── AdminView.vue       # Admin panel entry (PC only)
            └── admin/
                ├── LLMConfig.vue   # LLM API configuration
                ├── DingTalkConfig.vue  # DingTalk configuration
                └── FeishuConfig.vue    # Feishu configuration
└── miniapp/                        # WeChat Mini Program (uni-app Vue 3)
    ├── package.json
    ├── manifest.json               # uni-app config
    ├── pages.json                  # Page routes + TabBar
    ├── vite.config.js
    └── src/
        ├── App.vue                 # Root component (auto-login)
        ├── main.js                 # Vue entry
        ├── api/
        │   └── client.js           # uni.request wrapper (9 API modules)
        ├── utils/
        │   └── markdown.js         # Markdown parser (structured output)
        ├── components/
        │   ├── MarkdownViewer.vue  # Document rendering component
        │   ├── VideoPlayer.vue     # Video player (native video + external card)
        │   └── StepCard.vue        # Step card component
        ├── stores/
        │   └── plan.js             # Pinia state management
        └── pages/
            ├── dashboard/index.vue # Dashboard
            ├── learn/index.vue     # Learning page
            ├── wizard/index.vue    # Plan creation wizard
            ├── profile/index.vue   # Profile
            ├── review/index.vue    # AI review results
            └── settings/index.vue  # Settings
```

## Data Model

5 tables, SQLite storage, manual ALTER TABLE migration strategy:

| Table | Description | Key Fields |
|---|---|---|
| `learning_plans` | Learning plans | topic, goal, current_level, weekly_hours, total_weeks, status |
| `learning_steps` | Daily learning steps | step_type, content, resources(JSON), core_20_percent, ai_score, status |
| `milestones` | Stage milestones | week_num, title, check_task, status |
| `reminders` | Notification reminder configs | channel(feishu/dingtalk/windows), channel_config(JSON), enabled |
| `achievements` | Achievement badges | badge_key, title, rarity(common/rare/epic/legendary), unlocked_at |

**Step types (step_type):** study (systematic learning), project (hands-on practice), deep_project (deep practice), output (summary output), cheat_sheet (cheat sheet compression), test (stage test)

**Step status flow:** locked → available → in_progress → review_passed → completed (review_failed requires resubmission)

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/wx-login` | WeChat mini program login (code → token) |
| POST | `/api/auth/dev-login` | Development login (no credentials) |
| GET | `/api/health` | Health check |
| GET | `/api/dashboard` | Dashboard aggregated data |
| GET | `/api/plans/` | Plan list |
| POST | `/api/plans/` | Create empty plan |
| POST | `/api/plans/wizard` | **Wizard creation** (calls plan_engine + LLM to generate full plan) |
| GET/DELETE | `/api/plans/{id}` | Plan detail / delete |
| GET | `/api/plans/{id}/steps` | Step list (supports week filter) |
| GET | `/api/plans/{id}/milestones` | Milestone list |
| GET | `/api/steps/today` | Today's step |
| GET | `/api/steps/{id}` | Step detail |
| POST | `/api/steps/{id}/start` | Start step |
| POST | `/api/steps/{id}/submit-output` | Submit learning output |
| POST | `/api/steps/{id}/complete` | Complete step |
| POST | `/api/review/{id}/review` | AI review |
| POST | `/api/review/{id}/review-retry` | Retry review |
| GET/POST | `/api/reminders/plan/{id}` | Reminder list / create |
| PUT/DELETE | `/api/reminders/{id}` | Toggle / delete reminder |
| GET | `/api/achievements/plan/{id}` | Achievement list |
| GET/PUT | `/api/llm-config` | LLM config read / update |
| GET | `/api/profile/` | Personal profile statistics |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+

### Backend

```bash
cd learnflow/backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure LLM API (optional, falls back to topic library if not configured)
cp .env.example .env
# Edit .env file with your API config:
# LLM_API_BASE=https://your-api-endpoint/v1
# LLM_API_KEY=your-key
# LLM_MODEL=your-model

# Start server (port 8001)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend

```bash
cd learnflow/frontend

# Install dependencies
npm install

# Start dev server (port 5173, auto-proxies /api → localhost:8001)
npm run dev
```

### Production Deployment

```bash
# Build frontend
cd frontend && npm run build

# FastAPI automatically serves frontend/dist/ as static files
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

After building, only the backend needs to run. Visit `http://localhost:8001` to use the full application.

### WeChat Mini Program

```bash
cd learnflow/miniapp

# Install dependencies
npm install

# Dev mode (H5, browser debugging)
npm run dev:h5

# Build WeChat mini program
npm run build:mp-weixin
# Output to dist/build/mp-weixin/
# Import this directory into WeChat Developer Tools
```

Mini program configuration:

1. Set `WX_APPID` and `WX_SECRET` in `backend/.env`
2. Create a subscription message template in WeChat MP console, copy the template ID to `WX_TEMPLATE_ID`
3. Update `wxTemplateId` in `miniapp/src/pages/settings/index.vue` with the actual template ID

## Cross-Platform Deployment

LearnFlow supports Windows, macOS, and Linux. All core dependencies are cross-platform compatible. Below are the platform-specific differences.

### Platform Comparison

| Component | Windows | macOS | Linux |
|---|---|---|---|
| Python deps | All universal | All universal | All universal |
| Desktop notifications | `win11toast` (optional) + PowerShell fallback | `osascript` (built-in) | `notify-send` (requires libnotify) |
| Feishu notifications | `lark-cli.cmd` | `lark-cli` | `lark-cli` |
| DingTalk notifications | `dws.exe` | `dws` | `dws` |
| Process management | `python -m uvicorn ...` | `python -m uvicorn ...` | `python -m uvicorn ...` |

### Windows Additional Dependencies

```powershell
# Desktop notifications (optional, falls back to PowerShell native notifications if not installed)
pip install win11toast==0.9
```

### macOS Additional Configuration

```bash
# Desktop notifications: built-in osascript works out of the box, no extra install needed
# For richer notifications (clickable, actionable), optionally install terminal-notifier:
brew install terminal-notifier

# Feishu/DingTalk: ensure the CLI tools are in PATH, or specify paths in .env
# LARK_CLI_PATH=/usr/local/bin/lark-cli
# DWS_CLI_PATH=/usr/local/bin/dws
```

### Linux Additional Configuration

```bash
# Desktop notifications (most desktop distros ship libnotify pre-installed)
# Debian/Ubuntu:
sudo apt install libnotify-bin
# Fedora/RHEL:
sudo dnf install libnotify
# Arch:
sudo pacman -S libnotify

# Headless servers (no desktop): desktop notifications unavailable, use Feishu/DingTalk channels instead

# Feishu/DingTalk: ensure the CLI tools are in PATH, or specify paths in .env
```

### Environment Variable Configuration

Copy `backend/.env.example` to `backend/.env` and fill in values per the comments:

```bash
cp backend/.env.example backend/.env
```

Key configuration variables:

| Variable | Description | Required |
|---|---|---|
| `LLM_API_BASE` | OpenAI-compatible API endpoint URL | No (uses presets if empty) |
| `LLM_API_KEY` | API key | No |
| `LLM_MODEL` | Model name | No |
| `LARK_CLI_PATH` | Feishu CLI path (overrides default search) | No |
| `DWS_CLI_PATH` | DingTalk CLI path (overrides default search) | No |
| `WX_APPID` | WeChat Mini Program AppID | Required for mini program |
| `WX_SECRET` | WeChat Mini Program Secret | Required for mini program |
| `WX_TEMPLATE_ID` | WeChat subscription message template ID | Optional (needed for subscription messages) |

### Docker Deployment (Optional)

```dockerfile
FROM python:3.12-slim
WORKDIR /app

# Install Node.js for frontend build
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*

# Install backend dependencies
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Build frontend
COPY frontend/ frontend/
RUN cd frontend && npm install && npm run build

# Copy backend code
COPY backend/ backend/

EXPOSE 8001
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

```bash
docker build -t learnflow .
docker run -p 8001:8001 -v $(pwd)/data:/app/data learnflow
```

## LLM Integration

LearnFlow uses LLM for two core functions:

1. **Plan Content Generation** (`plan_engine.py`) — Calls LLM in 4-week batches to generate learning content, resource recommendations, practice tasks, and test questions. Batch processing prevents JSON truncation.
2. **AI Review** (`reviewer.py`) — Scores user-submitted learning output, embedding Socratic questioning (tests depth of understanding), Feynman technique (detects jargon stacking, 25% weight), and cheat sheet generation.

Supports any OpenAI-compatible API. When LLM is unavailable, automatically falls back to preset content in `topic_library.py` (React 3 levels, Python 2 levels, LLM 2 levels).

## Notification Channels

| Channel | Implementation | Platform | Status |
|---|---|---|---|
| Desktop (desktop) | Platform-native APIs | Windows / macOS / Linux | Auto-detected |
| Windows Toast | `win11toast` + PowerShell fallback | Windows 10/11 | Requires win11toast (optional) |
| macOS Notification | `osascript` (built-in) / `terminal-notifier` (optional) | macOS 10.15+ | Built-in, no install needed |
| Linux Notification | `notify-send` (libnotify) / `zenity` (fallback) | Desktop Linux | Requires libnotify-bin |
| Feishu (Lark) | `lark-cli` CLI tool | All platforms | Requires App ID/Secret |
| DingTalk | `dws` CLI tool | All platforms | Requires App Key/Secret |
| WeChat Subscription | WeChat API + wx_notify.py | WeChat Mini Program | Requires WX_APPID/WX_SECRET/template ID |

The desktop notification channel accepts both `desktop` (recommended) and `windows` (backward-compatible) as the channel name. The system automatically detects the current platform and uses the appropriate notification API.

## License

MIT License
