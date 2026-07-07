# learning-plan-engine Skill

## 定位
执行引擎型 Skill - 用户输入模糊学习目标，自动输出每日可执行的学习计划。

## 嵌入的三大学习方法

| 方法 | 代码体现 | 作用 |
|------|---------|------|
| **学习阶梯** | LADDER_LEVELS 定义 beginner/intermediate/advanced 三套 5 级递进，每级含 core_knowledge/common_mistakes/pass_criteria | 总周数按比例分配到 5 级，难度递进 |
| **二八法则** | CORE_20_TEMPLATES 定义 core_20_focus，每周内容标注核心20% | 聚焦高价值知识，避免广而不深 |
| **噪音筛选** | LLM prompt 要求精选 3-5 个资源，标注 type/level/duration/why，视频优先B站 | 从海量信息中筛选真正值得投入时间的资源 |

## 核心输出字段规范

### doc_content（知识文档）
必须遵循的生成规范：

1. 提炼优先，不堆砌：doc_content 是 AI 从本周学习资源（视频+文章）中提炼核心知识点后生成的，不是简单引用链接或复制原文
2. 结构化 Markdown：## 和 ### 组织层级，- 列表、> 引用、代码块突出重点
3. 300-500 字：精炼但高质量，覆盖该周最核心的概念
4. 必须包含：
   - 该周的核心概念定义（1-2 句）
   - 关键代码示例或原理说明
   - 一个真实使用场景
   - 引用块标注核心提示或注意事项
5. 禁止：
   - 直接贴外部链接（资源 URL 不出现在 doc_content 中）
   - 用请访问xxx代替内容
   - 大段摘抄原文而不做提炼

### resources（资源列表）
- 每周精选 2-4 个：优先 B站视频 + 确有价值的文章
- 视频：必须可嵌入播放（B站 embed_url），需在加入计划前验证可播放性
- 文章：URL 需真实可访问，但内容不直接展示，全部提炼入 doc_content

### core_20_percent
- 1-2 句话
- 说明本周最重要的、能解决 80% 实际问题的知识点

## 视频可播放性验证
视频资源（B站）必须在加入计划前进行验证：
- 发送 HTTP HEAD 请求到 bilibili API 检查 BVID 是否存在
- 不可播放的视频不加入资源列表，并记录警告日志
- 验证失败的视频不影响计划生成，只从资源列表中剔除

## 工作流程
1. 用户输入 - PlanWizard（主题/目标/水平/时间）
2. generate_learning_plan() 构建 5 级阶梯
3. 按 4 周一批调用 LLM 生成内容（避免 JSON 截断）
4. LLM 不可用时回退到 topic_library.py 预设内容
5. 对所有 B站视频做可播放性验证
6. 输出完整的 steps + milestones
