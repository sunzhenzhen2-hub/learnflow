# LearnFlow Product Requirements Document (PRD)

**[中文文档](PRD.md)**

**Version:** v0.1.0  
**Last Updated:** 2026-07-05  
**Status:** MVP Live

---

## 1. Product Overview

### 1.1 Product Positioning

LearnFlow is an **AI-driven learning execution system** designed for individual learners. It is not a "what to learn" recommendation tool — it is a "how to learn, how to persist" execution engine.

### 1.2 Core Problems Solved

| Problem | LearnFlow's Solution |
|---|---|
| Create study plans but can't stick to them | Daily push + forced unlock mechanism — can't advance without completing |
| Read many tutorials but don't truly understand | Forced output loop — every step requires submitted output and AI review |
| Don't know where to focus learning effort | Pareto Principle tags the core 20%, focusing on high-value content |
| Forget after learning, no systematization | 5-level Learning Ladder + cheat sheet compression + Feynman output |
| Inconsistent learning resource quality | Signal-in-noise filtering, 3-5 curated resources per week with rationale |

### 1.3 Target Users

Individual learners, especially developers self-studying programming, AI, and new technologies. Characteristics: capable of self-study but lacking system, prone to giving up midway or falling into "pseudo-learning" (consuming without practicing).

### 1.4 Product Differentiation

Fundamental difference from Coursera, Udemy, and other course platforms: LearnFlow does not provide courses — it **generates personalized learning execution plans and forces user output**. The core philosophy is "teaching is the best learning" — every step requires users to summarize in their own words, with AI playing the "strict mentor" role in review.

---

## 2. Core Features

### 2.1 Learning Plan Creation (PlanWizard)

**User Story:** As a learner, I want to create a complete learning plan through a simple wizard, instead of manually planning what to study every day of every week.

**Feature Description:**

4-step wizard creation flow:

1. **Choose Topic & Goal** — Enter learning topic (e.g., "Machine Learning"), select learning goal (Beginner Intro / Systematic Mastery / Project-Ready / Deep Mastery / Explore Frontier), optionally add focus area tags
2. **Assess Current Level** — Three-option card selection: Beginner (zero experience), Intermediate (some foundation), Advanced (experienced, seeking breakthrough)
3. **Schedule Learning Time** — Set weekly hours (3-30h slider), select study days (Mon-Sun multi-select), set start date
4. **Confirm & Create** — Preview plan summary, system calls LLM to generate full plan upon confirmation

**Plan Generation Logic (plan_engine.py):**

- Estimates total weeks based on user level and goal (Beginner 16 weeks, Intermediate 12 weeks, Advanced 8 weeks, adjustable by time)
- Builds 5-level Learning Ladder, distributing weeks proportionally: Cognitive Awakening (15%) → Foundation Building (25%) → Practical Application (30%) → Deep Expansion (20%) → Systematic Output (10%)
- Calls LLM to generate weekly content in batches (4 weeks per batch, avoiding JSON truncation)
- Generates per week: learning summary, core 20% content, 3-5 curated resources (including at least 1 document resource), practice tasks, test questions
- Falls back to topic_library.py preset content when LLM is unavailable

**Data Output:** One LearningPlan + N LearningSteps + M Milestones

### 2.2 Daily Learning Steps (LearningStep)

**User Story:** As a learner, I want to open the app every day and see what I should study today, with clear task guidance and supporting resources.

**Step Types:**

| Type | Description | Duration | Frequency |
|---|---|---|---|
| study (Systematic Learning) | Core concepts + supporting resources | 60min | 2-3x/week |
| project (Hands-on Practice) | Practice tasks based on weekly learning | 90min | 1x/week |
| deep_project (Deep Practice) | Comprehensive project tasks | 120min | 0-1x/week (5+ days) |
| output (Summary Output) | Summarize weekly learning in own words | 60min | 1x/week |
| cheat_sheet (Cheat Sheet Compression) | Compress stage learning into cheat sheet | 45min | Level transition weeks |
| test (Stage Test) | Must pass to unlock next level | 30min | As needed |

**Step Content Structure:**

Each step contains: title, learning content (200-300 word summary), core 20% tag (highlighted), curated resource list (video/document/article with platform, difficulty, duration, recommendation reason), practice task description.

**Resource Quality Requirements:**

- At least 1 doc-type document resource per week (official docs, technical specs, etc.)
- Video resources prioritize Bilibili
- Document resources prioritize official documentation
- URLs must be real and accessible
- Each resource tagged: type, title, url, platform, level (beginner/intermediate/advanced), duration, why

### 2.3 Forced Output Loop (Core Mechanism)

**User Story:** As a learner, I want to be "forced" to truly understand the material, rather than pretending I've learned it and skipping ahead.

**Flow:**

```
Step status: locked → available → in_progress → [submit output] → review_passed → completed
                                                          ↓
                                                    review_failed → [revise & resubmit] → review_passed
```

1. User clicks "Start Learning," step status changes from available to in_progress
2. After learning, user clicks "Submit Output," summarizing what they learned in their own words
3. System calls AI review service (reviewer.py), scoring 0-100
4. ≥70: Pass — automatically unlocks next step, generates achievements/milestone checks
5. <70: Fail — shows feedback and improvement suggestions, user must revise and resubmit

**AI Review Three Methods:**

1. **Socratic Questioning** — Every review includes 1 deep-dive question, testing whether the user truly understands (not just remembers)
2. **Feynman Technique Detection** — 25% weight of total score, detects whether the user is just stacking jargon without genuine understanding. If jargon stacking is detected, requires the user to re-explain "as if teaching a 10-year-old"
3. **Cheat Sheet Generation** — Auto-generates a knowledge cheat sheet for the step upon passing, facilitating long-term memory and review

### 2.4 Learning Ladder (5-Level Progression)

**User Story:** As a learner, I want a clear progression path, knowing what stage I'm at and what level I need to reach next.

**5-Level Structure:**

| Level | Name | Ratio | Core Focus | Pass Criteria |
|---|---|---|---|---|
| 1 | Cognitive Awakening | 15% | Basic concepts and terminology | Can explain what the field is in own words |
| 2 | Foundation Building | 25% | Core principles and basic skills | Can independently complete beginner-level tasks |
| 3 | Practical Application | 30% | Project practice and best practices | Can independently complete medium-complexity projects |
| 4 | Deep Expansion | 20% | Advanced features and underlying principles | Can explain trade-offs in design decisions |
| 5 | Systematic Output | 10% | Knowledge systematization and teaching | Can write tutorials or guide beginners |

Each level contains: core knowledge points, common mistakes, pass criteria. Level transition weeks automatically insert cheat sheet compression and stage test segments.

### 2.5 Dashboard

**User Story:** As a learner, I want to see at a glance what to do today, my overall progress, and recent achievements.

**Display Content:**

- Active plan card: progress bar, statistics (streak days, completed steps, current week)
- Today's task card: step type tag, duration, core 20% highlight, "Start Learning" button
- Upcoming steps list
- Milestones list (with week number markers)
- Achievement badge display (graded by rarity: Common/Rare/Epic/Legendary)

### 2.6 Personal Profile

**User Story:** As a learner, I want to review my learning journey, seeing quantified growth and progress.

**Display Content:**

- 4-grid statistics: total plans, completed steps, total hours, total achievements
- Learning streak card
- Plan progress list (with progress bars, click to enter learning)
- Recent completion activity (with AI review scores)

### 2.7 Notification Reminders

**User Story:** As a learner, I want to receive reminders at my study time every day so I don't forget to learn.

**Supported Channels:**

| Channel | Implementation | Trigger |
|---|---|---|
| Windows Toast | win11toast native notifications | Daily 8:00 scheduled task |
| Feishu (Lark) | lark-cli | Configurable reminder time |
| DingTalk | dws CLI | Configurable reminder time |

Each channel can be independently enabled/disabled with configurable reminder times and test-send support.

### 2.8 LLM Configuration Management

**User Story:** As a user, I want to configure the LLM API directly within the app without editing files.

**Feature:** PC admin panel provides LLM configuration form (API Base URL, API Key, Model Name). Changes take effect immediately at runtime and persist to .env file. API Key is masked in responses (only returns has_key: true/false), and empty values on update preserve the existing key.

### 2.9 Skill Design Philosophy — Turning Learning Methodology into Executable Code

LearnFlow's competitive advantage lies not in UI or feature count, but in deeply embedding 6 validated learning methodologies into the backend engine — transforming "methods written in documents" into "automatically executing code."

**Design Philosophy:** Adopts "execution engine" Skill design — user inputs a goal, system automatically outputs a complete plan, rather than requiring users to manually select tools and methods.

#### Skill 1: Learning Plan Engine (learning-plan-engine)

Transforms vague "I want to learn machine learning" into daily executable learning plans. Embeds 3 learning methods:

- **Learning Ladder** — `LADDER_LEVELS` in code defines beginner/intermediate/advanced sets of 5-level progression. Each level contains core knowledge points, common mistakes, pass criteria. The system automatically distributes total weeks across 5 levels (15%/25%/30%/20%/10%), inserting cheat sheet compression and stage tests at transition weeks.
- **Pareto Principle** — `CORE_20_TEMPLATES` defines core focus directions for 5 learning goals. Tags "Core 20%" when generating weekly content, letting users clearly know which knowledge deserves deep study and which only needs surface understanding.
- **Signal in Noise** — LLM prompt mandates 3-5 curated resources per week, must include document-type resources, videos prioritized from Bilibili, each resource tagged with difficulty, time estimate, and recommendation reason. Filters truly high-signal content from the ocean of learning resources.

#### Skill 2: Learning Output Reviewer (learning-output-reviewer)

Acts as a strict mentor, ensuring users truly understand rather than pretending to have learned. Embeds 3 learning methods:

- **Socratic Questioning** — Every review includes 1 deep-dive question, pressing users on "why" and "what if it weren't so," testing depth of understanding rather than memorization.
- **Feynman Technique** — 25% weight of total score. Detects whether users explain in simple language (`simple_language`), use analogies (`has_analogy`), or stack jargon (`jargon_overuse`). If jargon stacking is detected, requires re-explanation "as if teaching a 10-year-old."
- **Cheat Sheet Compression** — Auto-generates structured cheat sheet suggestion upon passing, compressing core knowledge into one page for long-term memory and quick review.

Review uses 5-dimension weighted scoring: Depth of Understanding (30%) + Accuracy (25%) + Completeness (20%) + Original Expression (15%) + Practical Relevance (10%). ≥70 to unlock next step, <70 returns 3 improvement suggestions. Falls back to rule-based review when LLM is unavailable.

#### Four-Layer Skill Collaboration

```
Methodology Source  ai-learning-coach (6 learning methods + 18 scenario variants)
                        ↓ splits to          ↓ splits to
Core Skills         learning-plan-engine    learning-output-reviewer
                    (Ladder+Pareto+Signal)   (Socratic+Feynman+Sheet)
                        ↓ API                  ↓ API
Orchestration Layer  ai-learning-engine (chains plan generation + review loop)
                        ↓
User Interaction     LearnFlow APP (Dashboard → Wizard → Learn → Output → Review)
```

4 Skills with clear division of labor: `ai-learning-coach` provides the methodology framework, two core Skills embed in backend engines for "plan generation" and "output review," `ai-learning-engine` serves as the orchestration layer chaining the complete learning loop.

---

## 3. Non-Functional Requirements

### 3.1 Performance

- Plan creation (including LLM generation): ~2-3 minutes for a 16-week plan (batch generation, 4 weeks per batch)
- Step query: < 200ms
- AI review: < 30 seconds
- Dashboard load: < 500ms

### 3.2 Compatibility

- **PC:** Chrome, Edge, Firefox latest, width ≥ 768px
- **Mobile:** iOS Safari, Android Chrome, width < 768px
- Device detection: 768px breakpoint, different routes and layouts for mobile and PC

### 3.3 Data Security

- All data stored in local SQLite, not uploaded to cloud
- LLM API Key stored in .env file, masked in API responses
- Both .env and database files are gitignored

### 3.4 Internationalization

- Supports Chinese (zh-CN) and English (en-US) bilingual
- All UI copy managed through vue-i18n
- LLM-generated content defaults to Chinese

---

## 4. Technical Constraints

### 4.1 Known Limitations

- **SQLite concurrency:** Single-file database, does not support high-concurrency writes. Suitable for personal use, not multi-user
- **LLM dependency:** Plan generation and AI review depend on external LLM API. Falls back to preset content when unavailable (currently covers React, Python, LLM — 3 topics)
- **No user authentication:** Single-user design, no login/registration mechanism
- **Manual migration:** Database schema changes via manual ALTER TABLE, no ORM auto-migration tool
- **Windows-only notifications:** Windows Toast notifications only support Windows systems

### 4.2 Deployment Constraints

- Backend defaults to port 8001 (8000 may be occupied by other services)
- uvicorn --reload may leave stale processes on Windows, requires manual cleanup before deployment
- MiMo V2.5 model name is case-sensitive, must use lowercase `mimo-v2.5`

---

## 5. Milestone Roadmap

### v0.1.0 (Current) — MVP Core Features

- [x] Plan creation wizard (4 steps)
- [x] 5-level Learning Ladder + Pareto Principle
- [x] LLM-driven plan content generation
- [x] Forced output loop (AI review ≥70 to unlock)
- [x] Socratic questioning + Feynman technique + cheat sheet
- [x] Topic content library fallback (React/Python/LLM)
- [x] Dashboard + personal profile
- [x] PC/Mobile responsive layout
- [x] Bilingual (Chinese/English)
- [x] Windows Toast notifications
- [x] Achievement badge system

### v0.2.0 — Resource & Content Enhancement

- [ ] In-app Markdown rendering for document resources
- [ ] LLM-generated concise knowledge cards (replacing external links)
- [ ] More topic library presets (Vue, TypeScript, Go, Rust, etc.)
- [ ] Automatic resource link validity detection
- [ ] Learning plan export (Markdown / PDF)

### v0.3.0 — Social & Collaboration

- [ ] Study groups (multi-user shared plans)
- [ ] Learning check-in sharing
- [ ] Feynman output peer review
- [ ] Leaderboards

### v1.0.0 — Platform

- [ ] Multi-user authentication system
- [ ] Cloud data sync
- [ ] Learning plan template marketplace
- [ ] Learning data analytics reports
- [ ] Open API (third-party integrations)

---

## 6. Key Metrics

| Metric | Definition | Target |
|---|---|---|
| Daily Completion Rate | Days with ≥1 completed step / total days | ≥ 80% |
| Output Pass Rate | Proportion of AI reviews passed on first attempt (≥70) | 60-80% |
| Plan Completion Rate | Proportion of fully completed learning plans | ≥ 50% |
| Average Review Score | Average AI review score across all outputs | 75-85 |
| Learning Streak | Longest consecutive daily learning streak | Continuously growing |
