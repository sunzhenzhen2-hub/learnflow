# LearnFlow — AI 驱动的学习执行系统

LearnFlow 是一个个人学习执行 APP，核心理念是**强制输出闭环**：每一步学习都必须通过 AI 评审才能解锁下一步，确保知识真正被吸收而非只是"看过"。

## 核心机制

LearnFlow 不是"课程推荐器"，而是"学习执行器"。它解决的核心问题是：很多人制定了学习计划却无法坚持执行，或者只是被动阅读而没有真正理解。

**强制输出链路：** 提交输出 → AI 评审（≥70分通过） → 解锁下一步。如果 AI 评审未通过，用户需要修订后重新提交，直到通过为止。

**三大学习方法嵌入：**

1. **学习阶梯（5级递进）** — 认知启蒙 → 基础构建 → 实践应用 → 深化拓展 → 体系输出，每个等级有明确的过关标准和常见错误提示
2. **二八法则** — 每周学习内容标注"核心20%"，聚焦能解决80%实际问题的关键知识
3. **费曼技巧 + 苏格拉底追问** — AI 评审不仅打分，还会用苏格拉底式追问检验理解深度，用费曼技巧检测是否只是术语堆砌

## 技术栈

| 层 | 技术 | 说明 |
|---|---|---|
| 前端 | Vue 3 + Vite + Element Plus | SPA，响应式 PC/移动端分离布局 |
| 状态管理 | Pinia | 轻量级状态管理 |
| 国际化 | vue-i18n | 中英双语（zh-CN / en-US） |
| 后端 | FastAPI | Python 异步 Web 框架 |
| 数据库 | SQLite + SQLAlchemy | 零配置本地存储 |
| LLM | OpenAI 兼容 API | 支持任意 OpenAI 兼容端点（当前配置 MiMo V2.5） |
| 通知 | 飞书 / 钉钉 / Windows Toast | 多渠道学习提醒 |
| 调度 | APScheduler | 每日定时提醒任务 |

## 项目结构

```
learnflow/
├── data/                           # SQLite 数据库（gitignored）
│   └── learnflow.db
├── backend/
│   ├── .env                        # 环境变量（LLM API 配置，gitignored）
│   ├── requirements.txt            # Python 依赖
│   └── app/
│       ├── main.py                 # FastAPI 入口，挂载路由 + 静态文件
│       ├── config.py               # pydantic-settings 配置加载
│       ├── database.py             # SQLAlchemy 引擎 + 表迁移
│       ├── models.py               # ORM 模型（5张表）
│       ├── schemas.py              # Pydantic 请求/响应模型
│       ├── routers/                # API 路由层
│       │   ├── plans.py            # 学习计划 CRUD + Wizard 创建
│       │   ├── steps.py            # 学习步骤查询 + 状态流转
│       │   ├── review.py           # AI 评审（苏格拉底 + 费曼 + 速查表）
│       │   ├── reminders.py        # 学习提醒管理
│       │   ├── achievements.py     # 成就徽章查询
│       │   ├── config.py           # LLM 配置读写
│       │   └── profile.py          # 个人学习统计
│       └── services/               # 业务逻辑层
│           ├── plan_engine.py      # 计划生成引擎（学习阶梯 + 二八法则 + LLM）
│           ├── reviewer.py         # AI 评审服务（苏格拉底追问 + 费曼检测）
│           ├── topic_library.py    # 主题内容库（React/Python/LLM 预设内容）
│           ├── dashboard.py        # 仪表盘数据聚合
│           ├── profile.py          # 个人档案统计
│           ├── scheduler.py        # APScheduler 定时提醒
│           └── notifiers/          # 多渠道通知（飞书/钉钉/Windows Toast）
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js              # Vite 配置 + API 代理
    └── src/
        ├── main.js                 # Vue 入口（Pinia + Router + Element Plus + i18n）
        ├── App.vue                 # 根组件（设备检测 + 布局切换）
        ├── router.js               # 路由入口（按设备类型加载路由）
        ├── api/
        │   └── client.js           # Axios 封装（8个 API 模块）
        ├── composables/
        │   └── useDevice.js        # 设备检测 composable（768px 断点）
        ├── i18n/
        │   ├── index.js            # vue-i18n 配置
        │   ├── zh-CN.js            # 中文翻译（216行）
        │   └── en-US.js            # 英文翻译（216行）
        ├── layouts/
        │   ├── MobileLayout.vue    # 移动端：底部4Tab导航
        │   └── PcLayout.vue        # PC端：左侧菜单 + 顶部栏
        ├── router/
        │   ├── mobile.js           # 移动端路由（4个页面，无管理后台）
        │   └── pc.js               # PC端路由（4个页面 + 管理后台）
        ├── stores/
        │   └── plan.js             # Pinia 计划状态管理
        └── views/
            ├── Dashboard.vue       # 首页仪表盘（进度、今日任务、里程碑）
            ├── PlanWizard.vue      # 计划创建向导（4步）
            ├── LearningView.vue    # 学习主页面（步骤列表 + 详情 + 输出提交）
            ├── ProfileView.vue     # 个人档案（统计 + 连续天数 + 成就）
            ├── ReviewOutput.vue    # 评审结果页
            ├── Settings.vue        # 设置页（通知渠道 + 计划管理）
            ├── AdminView.vue       # 管理后台入口（PC端专属）
            └── admin/
                ├── LLMConfig.vue   # LLM API 配置
                ├── DingTalkConfig.vue  # 钉钉配置
                └── FeishuConfig.vue    # 飞书配置
```

## 数据模型

5 张表，SQLite 存储，手动 ALTER TABLE 迁移策略：

| 表 | 说明 | 关键字段 |
|---|---|---|
| `learning_plans` | 学习计划 | topic, goal, current_level, weekly_hours, total_weeks, status |
| `learning_steps` | 每日学习步骤 | step_type, content, resources(JSON), core_20_percent, ai_score, status |
| `milestones` | 阶段里程碑 | week_num, title, check_task, status |
| `reminders` | 通知提醒配置 | channel(feishu/dingtalk/windows), channel_config(JSON), enabled |
| `achievements` | 成就徽章 | badge_key, title, rarity(common/rare/epic/legendary), unlocked_at |

**步骤类型（step_type）：** study（系统学习）、project（动手实践）、deep_project（深度实战）、output（总结输出）、cheat_sheet（速查表压缩）、test（阶段测试）

**步骤状态流转：** locked → available → in_progress → review_passed → completed（review_failed 需重新提交）

## API 端点

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查 |
| GET | `/api/dashboard` | 仪表盘聚合数据 |
| GET | `/api/plans/` | 计划列表 |
| POST | `/api/plans/` | 创建空计划 |
| POST | `/api/plans/wizard` | **向导创建**（调用 plan_engine + LLM 生成完整计划） |
| GET/DELETE | `/api/plans/{id}` | 计划详情/删除 |
| GET | `/api/plans/{id}/steps` | 步骤列表（支持 week 过滤） |
| GET | `/api/plans/{id}/milestones` | 里程碑列表 |
| GET | `/api/steps/today` | 今日步骤 |
| GET | `/api/steps/{id}` | 步骤详情 |
| POST | `/api/steps/{id}/start` | 开始步骤 |
| POST | `/api/steps/{id}/submit-output` | 提交学习输出 |
| POST | `/api/steps/{id}/complete` | 完成步骤 |
| POST | `/api/review/{id}/review` | AI 评审 |
| POST | `/api/review/{id}/review-retry` | 重新评审 |
| GET/POST | `/api/reminders/plan/{id}` | 提醒列表/创建 |
| PUT/DELETE | `/api/reminders/{id}` | 切换/删除提醒 |
| GET | `/api/achievements/plan/{id}` | 成就列表 |
| GET/PUT | `/api/llm-config` | LLM 配置读取/更新 |
| GET | `/api/profile/` | 个人档案统计 |

## 快速启动

### 环境要求

- Python 3.10+
- Node.js 18+

### 后端

```bash
cd learnflow/backend

# 安装依赖（国内用户建议加 -i https://pypi.tuna.tsinghua.edu.cn/simple）
pip install -r requirements.txt

# 配置 LLM API（可选，不配置则使用主题内容库回退）
# 编辑 .env 文件：
# LLM_API_BASE=https://your-api-endpoint/v1
# LLM_API_KEY=your-key
# LLM_MODEL=your-model

# 启动服务（端口 8001）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 前端

```bash
cd learnflow/frontend

# 安装依赖
npm install

# 启动开发服务器（端口 5173，自动代理 /api → localhost:8001）
npm run dev
```

### 生产部署

```bash
# 构建前端
cd frontend && npm run build

# FastAPI 自动服务 frontend/dist/ 静态文件
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

构建后只需启动后端，访问 `http://localhost:8001` 即可使用完整应用。

## LLM 集成

LearnFlow 使用 LLM 完成两个核心功能：

1. **计划内容生成**（`plan_engine.py`）— 按 4 周为一批调用 LLM 生成学习内容、资源推荐、实践任务和测试题。为避免 JSON 截断，采用分批生成策略。
2. **AI 评审**（`reviewer.py`）— 对用户提交的学习输出进行评分，嵌入苏格拉底追问（检验理解深度）、费曼技巧（检测术语堆砌，25%权重）和速查表生成。

支持任何 OpenAI 兼容 API。当 LLM 不可用时，自动回退到 `topic_library.py` 中的预设内容（React 3级、Python 2级、LLM 2级）。

## 通知渠道

| 渠道 | 实现方式 | 状态 |
|---|---|---|
| Windows Toast | `win11toast` 原生通知 | 默认启用 |
| 飞书（Lark） | `lark-cli` CLI 工具 | 需配置 App ID/Secret |
| 钉钉 | `dws` CLI 工具 | 需配置 App Key/Secret |

## 许可证

MIT License
