"""
Learning Plan Engine - Skill 深度嵌入版
学习阶梯(5级) + 二八法则 + 噪音中找信号
"""
import json
import httpx
from datetime import date, timedelta
from ..config import settings
from .topic_library import get_topic_content, get_topic_resources


# 星期映射
DOW_MAP = {1: "周一", 2: "周二", 3: "周三", 4: "周四", 5: "周五", 6: "周六", 7: "周日"}

# 任务类型模板（中文）
STEP_TYPE_TEMPLATES = {
    "study": {
        "title_suffix": "系统学习",
        "duration": 60,
        "desc": "系统学习核心概念，配合精选资源",
    },
    "project": {
        "title_suffix": "动手实践",
        "duration": 90,
        "desc": "通过动手项目巩固所学知识",
    },
    "deep_project": {
        "title_suffix": "深度实战",
        "duration": 120,
        "desc": "深入完成综合性项目任务",
    },
    "output": {
        "title_suffix": "总结输出",
        "duration": 60,
        "desc": "用自己的话总结本周所学，通过AI评审",
    },
    "cheat_sheet": {
        "title_suffix": "速查表压缩",
        "duration": 45,
        "desc": "将本阶段所学压缩成一页速查表，便于长期记忆",
    },
    "test": {
        "title_suffix": "知识测试",
        "duration": 30,
        "desc": "完成本阶段知识测试，通过后方可解锁下一阶段",
    },
}

# ============================================================
# 学习阶梯（Skill 方法1）— 5级递进结构
# 每个等级包含：核心知识点、常见错误、过关标准
# ============================================================
LADDER_LEVELS = {
    "beginner": [
        {
            "level": 1,
            "name": "认知启蒙",
            "ratio": 0.15,
            "focus": "了解基本概念和术语，建立初步认知框架",
            "core_knowledge": "核心术语定义、基本概念、领域全貌",
            "common_mistakes": "混淆相似概念、跳过基础直接学高级内容",
            "pass_criteria": "能用自己的话解释该领域是什么、解决什么问题",
        },
        {
            "level": 2,
            "name": "基础构建",
            "ratio": 0.25,
            "focus": "掌握核心原理和基础技能，能完成简单任务",
            "core_knowledge": "核心原理、基础语法/API/工具、常见模式",
            "common_mistakes": "死记硬背不理解原理、忽视边界条件",
            "pass_criteria": "能独立完成入门级任务，不需要看教程",
        },
        {
            "level": 3,
            "name": "实践应用",
            "ratio": 0.30,
            "focus": "通过项目实战深化理解，掌握80%实际工作所需的核心技能",
            "core_knowledge": "项目实战、问题解决、最佳实践、调试技巧",
            "common_mistakes": "只跟教程不独立思考、遇到bug就放弃",
            "pass_criteria": "能独立完成一个中等复杂度的项目",
        },
        {
            "level": 4,
            "name": "深化拓展",
            "ratio": 0.20,
            "focus": "深入高级主题，理解底层原理和设计决策",
            "core_knowledge": "高级特性、性能优化、架构设计、底层原理",
            "common_mistakes": "过度优化、为了学而学不实用的内容",
            "pass_criteria": "能解释设计决策的trade-off，能做技术选型",
        },
        {
            "level": 5,
            "name": "体系输出",
            "ratio": 0.10,
            "focus": "构建完整知识体系，能够教学和指导他人",
            "core_knowledge": "知识体系化、前沿动态、跨领域联系、教学方法",
            "common_mistakes": "只输出不输入导致知识停滞",
            "pass_criteria": "能写教程/做分享/指导初学者",
        },
    ],
    "intermediate": [
        {
            "level": 1,
            "name": "查漏补缺",
            "ratio": 0.15,
            "focus": "识别并填补知识盲区，巩固薄弱环节",
            "core_knowledge": "知识盲区识别、基础回顾、概念辨析",
            "common_mistakes": "以为自己都会其实一知半解",
            "pass_criteria": "能系统地列出该领域的知识地图并标注掌握程度",
        },
        {
            "level": 2,
            "name": "核心深化",
            "ratio": 0.30,
            "focus": "深入核心20%的高级内容，解决80%的实际问题",
            "core_knowledge": "核心高级特性、复杂场景处理、性能优化",
            "common_mistakes": "广而不深，每个都懂一点但都不精",
            "pass_criteria": "能独立解决中等复杂度的实际问题",
        },
        {
            "level": 3,
            "name": "项目实战",
            "ratio": 0.30,
            "focus": "通过真实项目将知识转化为能力",
            "core_knowledge": "项目设计、工程实践、团队协作、代码质量",
            "common_mistakes": "追求完美不发布、忽视文档和测试",
            "pass_criteria": "完成至少一个可展示的完整项目",
        },
        {
            "level": 4,
            "name": "架构思维",
            "ratio": 0.15,
            "focus": "理解系统设计、技术选型和架构决策",
            "core_knowledge": "架构模式、设计原则、trade-off分析",
            "common_mistakes": "过度设计、忽视实际需求",
            "pass_criteria": "能做技术方案评审，能解释架构决策",
        },
        {
            "level": 5,
            "name": "知识输出",
            "ratio": 0.10,
            "focus": "将知识体系化并输出，达到能教他人的水平",
            "core_knowledge": "知识整理、教程编写、技术分享",
            "common_mistakes": "输出质量不高影响口碑",
            "pass_criteria": "发布高质量教程或技术文章",
        },
    ],
    "advanced": [
        {
            "level": 1,
            "name": "前沿追踪",
            "ratio": 0.15,
            "focus": "了解最新研究、工具和趋势",
            "core_knowledge": "前沿论文、新工具、行业动态",
            "common_mistakes": "追逐每一个新东西不加分辨",
            "pass_criteria": "能判断哪些新技术值得深入，哪些只是炒作",
        },
        {
            "level": 2,
            "name": "深度实践",
            "ratio": 0.30,
            "focus": "解决复杂问题，性能优化，底层调优",
            "core_knowledge": "性能分析、底层原理、疑难问题排查",
            "common_mistakes": "只看理论不动手",
            "pass_criteria": "能解决团队中最棘手的技术问题",
        },
        {
            "level": 3,
            "name": "架构设计",
            "ratio": 0.25,
            "focus": "系统架构设计，大规模系统经验",
            "core_knowledge": "分布式系统、高可用设计、可扩展架构",
            "common_mistakes": "过早优化、忽视业务需求",
            "pass_criteria": "能设计并实现一个中大规模系统",
        },
        {
            "level": 4,
            "name": "跨域整合",
            "ratio": 0.15,
            "focus": "跨领域知识整合，创新应用",
            "core_knowledge": "跨领域联系、创新方法论、技术迁移",
            "common_mistakes": "局限于单一领域思维",
            "pass_criteria": "能将其他领域的方法应用到本领域",
        },
        {
            "level": 5,
            "name": "专家输出",
            "ratio": 0.15,
            "focus": "成为领域专家，指导他人，建立影响力",
            "core_knowledge": "知识传承、社区贡献、行业影响力",
            "common_mistakes": "技术好但不善表达和分享",
            "pass_criteria": "在领域内建立一定影响力",
        },
    ],
}

# ============================================================
# 二八法则（Skill 方法2）— 核心20%内容标记
# 每周内容中标注最重要的核心知识点
# ============================================================
CORE_20_TEMPLATES = {
    "beginner_intro": {
        "desc": "入门了解该领域的基本概念和术语",
        "week_factor": 0.6,
        "emphasis": "概念理解、术语掌握、基础认知",
        "project_ratio": 0.2,
        "core_20_focus": "最核心的概念和术语，能解释该领域是什么",
    },
    "systematic": {
        "desc": "系统性地掌握核心知识体系",
        "week_factor": 1.0,
        "emphasis": "知识体系构建、核心原理、系统思维",
        "project_ratio": 0.4,
        "core_20_focus": "核心原理和设计思想，能解释为什么这样设计",
    },
    "project_ready": {
        "desc": "能够独立完成实际项目",
        "week_factor": 1.2,
        "emphasis": "项目实战、工程实践、问题解决",
        "project_ratio": 0.6,
        "core_20_focus": "项目中最常用的技能和最佳实践",
    },
    "deep_mastery": {
        "desc": "达到能指导他人的专家水平",
        "week_factor": 1.5,
        "emphasis": "深度原理、架构设计、知识输出",
        "project_ratio": 0.5,
        "core_20_focus": "底层原理和trade-off，能解释给他人听",
    },
    "explore_expand": {
        "desc": "拓宽知识面，了解前沿动态",
        "week_factor": 0.5,
        "emphasis": "广度探索、前沿趋势、跨领域联系",
        "project_ratio": 0.3,
        "core_20_focus": "最值得投入时间的前沿方向",
    },
}


def generate_learning_plan(
    topic: str,
    goal: str,
    level: str,
    weekly_hours: float,
    preferred_days: list[int],
    start_date: date,
    focus_areas: list[str] = None,
) -> dict:
    """
    生成完整学习计划（学习阶梯 + 二八法则 + 噪音筛选）。

    流程：
    1. 根据用户水平获取5级学习阶梯
    2. 将总周数分配到5个等级
    3. 用二八法则标注每周核心20%内容
    4. 调用LLM生成精选资源（噪音中找信号）
    5. 为每个学习日生成具体任务
    6. 在阶段末尾插入速查表压缩环节
    """
    focus_areas = focus_areas or []
    goal_info = CORE_20_TEMPLATES.get(goal, CORE_20_TEMPLATES["systematic"])
    total_weeks = _estimate_weeks(level, weekly_hours, goal)
    ladder = _build_ladder(total_weeks, level)

    # 调用 LLM 生成学习内容和资源（如果 API 可用）
    llm_content = _llm_generate_content(topic, goal, level, total_weeks, ladder, focus_areas)

    steps = []
    current_date = start_date
    while current_date.isoweekday() not in preferred_days:
        current_date += timedelta(days=1)

    for week_num in range(1, total_weeks + 1):
        week_start = current_date + timedelta(weeks=week_num - 1)
        week_monday = week_start - timedelta(days=week_start.isoweekday() - 1)
        ladder_level = _get_ladder_for_week(week_num, ladder)

        # 获取 LLM 生成的本周内容
        week_llm = llm_content.get(str(week_num), {}) if llm_content else {}

        for idx, day in enumerate(sorted(preferred_days)):
            step_date = week_monday + timedelta(days=day - 1)
            step_type = _get_step_type(idx, len(preferred_days), week_num, ladder)
            template = STEP_TYPE_TEMPLATES[step_type]

            title = f"W{week_num}{DOW_MAP[day]} {topic} - {template['title_suffix']}"
            content = _generate_content(topic, step_type, week_num, ladder_level, level, week_llm, goal)

            # 资源和核心20%：优先用LLM生成，回退到主题内容库
            ladder_level_num = ladder_level.get("level", 1)
            topic_data = get_topic_content(topic, ladder_level_num)

            if step_type == "study":
                resources = week_llm.get("resources", [])
                if not resources:
                    resources = get_topic_resources(topic, ladder_level_num)
                resources = _enrich_and_validate_video_embed(resources)
                for r in resources:
                    if r.get("type") == "article":
                        r["synthesized"] = True
                core_20 = week_llm.get("core_20_percent", "")
                if not core_20 and topic_data:
                    core_20 = topic_data.get("core_20", "")
                doc_content = week_llm.get("doc_content", "")
                if not doc_content and topic_data:
                    doc_content = topic_data.get("doc_content", "")
                article_resources = [r for r in resources if r.get("type") == "article"]
                if article_resources:
                    ref_lines = ["> **引用来源**"]
                    for r in article_resources:
                        ref_lines.append("> - [" + r.get("title", "") + "](" + r.get("url", "") + ")")
                    ref_text = chr(10).join(ref_lines)
                    if doc_content and ref_text not in doc_content:
                        doc_content = doc_content.rstrip() + chr(10) + ref_text
            else:
                resources = []
                core_20 = ""

            test_questions = week_llm.get("test_questions", []) if step_type == "test" else []
            test_answer_hint = week_llm.get("test_answer_hint", "") if step_type == "test" else ""

            steps.append({
                "week_num": week_num,
                "day_of_week": day,
                "date": step_date,
                "step_type": step_type,
                "title": title,
                "content": content,
                "resources": resources,
                "core_20_percent": core_20,
                "test_questions": test_questions,
                "test_answer_hint": test_answer_hint,
                "duration_minutes": template["duration"],
                "ladder_level": ladder_level["level"],
                "ladder_name": ladder_level["name"],
            })

    milestones = _generate_milestones(topic, total_weeks, goal, ladder)

    return {
        "total_weeks": total_weeks,
        "steps": steps,
        "milestones": milestones,
        "ladder": ladder,
        "metadata": {
            "topic": topic,
            "goal": goal,
            "level": level,
            "weekly_hours": weekly_hours,
        },
    }


def _estimate_weeks(level: str, weekly_hours: float, goal: str = "systematic") -> int:
    """根据水平、可用时间和学习目标估算总周数。"""
    base_weeks = {"beginner": 16, "intermediate": 12, "advanced": 8}.get(level, 16)
    goal_factor = CORE_20_TEMPLATES.get(goal, CORE_20_TEMPLATES["systematic"])["week_factor"]
    base_weeks = int(base_weeks * goal_factor)
    if weekly_hours >= 20:
        return max(int(base_weeks * 0.6), 4)
    elif weekly_hours >= 15:
        return max(int(base_weeks * 0.75), 6)
    elif weekly_hours <= 5:
        return min(int(base_weeks * 1.5), 24)
    return base_weeks


def _build_ladder(total_weeks: int, level: str) -> list[dict]:
    """
    构建5级学习阶梯，将总周数分配到各等级。
    每个等级包含：名称、核心知识、常见错误、过关标准。
    """
    ladder_template = LADDER_LEVELS.get(level, LADDER_LEVELS["beginner"])
    ladder = []
    current_week = 1

    for i, tmpl in enumerate(ladder_template):
        if i < len(ladder_template) - 1:
            end_week = max(current_week + 1, int(total_weeks * tmpl["ratio"]))
        else:
            end_week = total_weeks

        ladder.append({
            "level": tmpl["level"],
            "name": tmpl["name"],
            "start_week": current_week,
            "end_week": end_week,
            "focus": tmpl["focus"],
            "core_knowledge": tmpl["core_knowledge"],
            "common_mistakes": tmpl["common_mistakes"],
            "pass_criteria": tmpl["pass_criteria"],
        })
        current_week = end_week + 1

    return ladder


def _get_ladder_for_week(week_num: int, ladder: list[dict]) -> dict:
    """获取某周对应的学习阶梯等级。"""
    for level in ladder:
        if level["start_week"] <= week_num <= level["end_week"]:
            return level
    return ladder[-1]


def _get_step_type(day_index: int, total_days: int, week_num: int, ladder: list[dict]) -> str:
    """
    根据学习日序号决定任务类型。
    在阶梯等级过渡周插入速查表压缩和测试。
    """
    # 检查是否是阶梯等级过渡周的最后一天
    current_ladder = _get_ladder_for_week(week_num, ladder)
    is_transition_week = (week_num == current_ladder["end_week"])

    if is_transition_week and day_index == total_days - 1:
        return "cheat_sheet"

    if total_days <= 3:
        type_map = {0: "study", 1: "project", 2: "output"}
    elif total_days <= 4:
        type_map = {0: "study", 1: "study", 2: "project", 3: "output"}
    else:
        type_map = {0: "study", 1: "study", 2: "project", 3: "deep_project", 4: "output"}
    return type_map.get(day_index, "study")


def _generate_content(topic, step_type, week_num, ladder_level, level, week_llm=None, goal="systematic"):
    """生成中文学习内容，嵌入学习阶梯和二八法则。"""

    level_name = ladder_level["name"]
    focus = ladder_level["focus"]
    core_knowledge = ladder_level.get("core_knowledge", "")
    common_mistakes = ladder_level.get("common_mistakes", "")
    pass_criteria = ladder_level.get("pass_criteria", "")
    ladder_level_num = ladder_level.get("level", 1)

    goal_info = CORE_20_TEMPLATES.get(goal, CORE_20_TEMPLATES["systematic"])
    core_20_focus = goal_info.get("core_20_focus", "")

    # 尝试从主题内容库获取预设内容
    topic_data = get_topic_content(topic, ladder_level_num)

    if step_type == "study":
        llm_summary = week_llm.get("study_summary", "") if week_llm else ""
        core_20 = week_llm.get("core_20_percent", "") if week_llm else ""

        content = f"[阶梯等级: {level_name}] {focus}\n\n"

        if llm_summary:
            if core_20:
                content += f"[核心20%] {core_20}\n\n"
            content += llm_summary
        elif topic_data:
            # 使用主题内容库的预设内容
            topic_core_20 = core_20 or topic_data.get("core_20", "")
            if topic_core_20:
                content += f"[核心20%] {topic_core_20}\n\n"
            content += topic_data.get("study_content", "")
            content += f"\n\n过关标准: {pass_criteria}"
        else:
            content += (
                f"本周学习要点:\n"
                f"1. 掌握核心知识: {core_knowledge}\n"
                f"2. 避免常见错误: {common_mistakes}\n"
                f"3. 过关标准: {pass_criteria}\n"
                f"4. 聚焦重点: {core_20_focus}"
            )
        return content

    elif step_type == "project":
        llm_project = week_llm.get("project_task", "") if week_llm else ""
        if llm_project:
            return f"[{level_name}] 实践任务\n\n{llm_project}"
        elif topic_data and topic_data.get("project_task"):
            return f"[{level_name}] 实践任务\n\n{topic_data['project_task']}"
        return (
            f"[{level_name}] 动手实践\n\n"
            f"1. 回顾学习笔记（15分钟）\n"
            f"2. 完成本周实践任务（60分钟）\n"
            f"3. 记录遇到的问题和解决方案\n"
            f"4. 检查是否达到过关标准: {pass_criteria}"
        )

    elif step_type == "deep_project":
        return (
            f"[{level_name}] 深度实战\n\n"
            f"1. 继续推进项目实现（90分钟）\n"
            f"2. 测试和调试\n"
            f"3. 记录学习心得\n"
            f"4. 思考: 这周学到的最核心的20%是什么？"
        )

    elif step_type == "output":
        return (
            f"[{level_name}] 总结输出\n\n"
            f"1. 撰写本周学习总结（30分钟）\n"
            f"2. 用自己的话解释核心概念（费曼技巧）\n"
            f"3. 提交AI评审（必须通过70分才能进入下周）\n"
            f"4. 过关标准: {pass_criteria}"
        )

    elif step_type == "cheat_sheet":
        return (
            f"[{level_name}] 速查表压缩\n\n"
            f"将本阶段所学压缩成一页速查表:\n"
            f"1. 一句话定义本阶段核心内容（30字以内）\n"
            f"2. 最重要的3-5个核心概念（每个一句话）\n"
            f"3. 一个真实场景的例子\n"
            f"4. 最常见的3个错误及避免方法\n"
            f"5. 实操检查清单\n"
            f"6. 3道自测题（附答案）\n\n"
            f"本阶段核心知识: {core_knowledge}\n"
            f"常见错误: {common_mistakes}\n"
            f"过关标准: {pass_criteria}"
        )

    elif step_type == "test":
        return f"[{level_name}] 阶段测试\n\n完成测试题，通过后方可解锁下一阶梯等级。"

    return f"学习{topic} - 第{week_num}周"


def _generate_milestones(topic, total_weeks, goal, ladder):
    """生成中文里程碑，基于学习阶梯等级。"""
    goal_info = CORE_20_TEMPLATES.get(goal, CORE_20_TEMPLATES["systematic"])
    goal_desc = goal_info["desc"]
    milestones = []

    # 为每个阶梯等级生成里程碑
    for level in ladder:
        if level["level"] <= 3:  # 前3个等级生成里程碑
            milestones.append({
                "week_num": level["end_week"],
                "title": f"{level['name']} - {topic}",
                "description": f"达成: {level['pass_criteria']}",
                "check_task": f"验证: {level['pass_criteria']}。注意避免: {level['common_mistakes']}",
            })

    # 最终里程碑
    milestones.append({
        "week_num": total_weeks,
        "title": f"目标达成 - {topic}体系化",
        "description": f"达成学习目标: {goal_desc}",
        "check_task": f"用费曼技巧向他人完整讲解{topic}的核心内容",
    })

    return milestones


def _llm_generate_content(topic, goal, level, total_weeks, ladder, focus_areas):
    """
    调用外部 LLM 分批生成每周学习内容和资源推荐。
    每批4周，避免输出超出模型token限制导致JSON截断。
    嵌入学习阶梯结构 + 二八法则核心标注 + 噪音筛选资源。
    """
    if not settings.LLM_API_KEY:
        print("[LLM] No API key, skipping LLM generation")
        return {}

    goal_info = CORE_20_TEMPLATES.get(goal, CORE_20_TEMPLATES["systematic"])
    goal_desc = goal_info["desc"]
    goal_emphasis = goal_info["emphasis"]
    core_20_focus = goal_info["core_20_focus"]

    ladder_desc = "\n".join([
        f"  等级{lv['level']} {lv['name']}(W{lv['start_week']}-W{lv['end_week']}): "
        f"核心知识={lv['core_knowledge']}, "
        f"常见错误={lv['common_mistakes']}, "
        f"过关标准={lv['pass_criteria']}"
        for lv in ladder
    ])

    focus_str = "、".join(focus_areas) if focus_areas else "无特定方向"

    # 分批生成，每批4周
    all_results = {}
    batch_size = 4
    batches = [(i, min(i + batch_size - 1, total_weeks))
               for i in range(1, total_weeks + 1, batch_size)]

    for batch_start, batch_end in batches:
        week_keys = ", ".join([f'"{w}"' for w in range(batch_start, batch_end + 1)])
        batch_result = _llm_generate_batch(
            topic, goal_desc, goal_emphasis, level,
            ladder_desc, focus_str, batch_start, batch_end, week_keys
        )
        if batch_result:
            all_results.update(batch_result)

    print(f"[LLM] total generated: {len(all_results)}/{total_weeks} weeks")
    return all_results


def _enrich_and_validate_video_embed(resources: list) -> list:
    """
    为视频资源添加 embed_url，同时验证可播放性。
    不可播放的视频（B站已删除/下线/私密）从列表中移除并记录警告。
    遵循 skill 规范：所有加入计划视频必须可嵌入播放。
    """
    import re
    enriched = []
    validated = []
    for r in resources:
        r = dict(r)
        url = r.get("url", "")
        rtype = r.get("type", "")
        
        # 验证所有资源 URL
        if url and not _validate_url(url):
            print(f"[WARN] 资源 URL 不可访问，已跳过: {url}")
            continue
        
        if rtype != "video":
            enriched.append(r)
            continue
        m = re.search(r"bilibili\.com/video/(BV[\w]+)", url)
        if not m:
            enriched.append(r)
            continue
        bvid = m.group(1)
        if not settings.LLM_API_KEY:
            r["embed_url"] = f"https://player.bilibili.com/player.html?bvid={bvid}&high_quality=1&danmaku=0"
            enriched.append(r)
            continue
        if _validate_bilibili_video(bvid):
            r["embed_url"] = f"https://player.bilibili.com/player.html?bvid={bvid}&high_quality=1&danmaku=0"
            enriched.append(r)
        else:
            print(f"[WARN] B站视频不可播放，已跳过: {url}")
    return enriched


def _validate_bilibili_video(bvid: str) -> bool:
    """通过 bilibili API 验证 BVID 是否存在且可播放。"""
    try:
        resp = httpx.get(
            "https://api.bilibili.com/x/web-interface/view",
            params={"bvid": bvid},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
        )
        data = resp.json()
        if data.get("code") == 0:
            aid = data.get("data", {}).get("aid", 0)
            return aid > 0
        return False
    except Exception as e:
        return False


def _validate_url(url: str) -> bool:
    """验证 URL 是否可访问。跳过 Google Developers 等已知不可访问的域名。"""
    # 已知在中国不可访问或超时的域名
    blocked_domains = [
        "developers.google.com",
        "google.dev",
        "cloud.google.com",
        "medium.com",
        "github.com",  # 可能需要代理
        "stackoverflow.com",
        "reddit.com",
    ]
    
    url_lower = url.lower()
    for domain in blocked_domains:
        if domain in url_lower:
            print(f"[WARN] 跳过不可访问的域名: {url}")
            return False
    
    try:
        resp = httpx.head(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5, follow_redirects=True)
        return resp.status_code < 400
    except Exception:
        return False


def _llm_generate_batch(topic, goal_desc, goal_emphasis, level,
                         ladder_desc, focus_str, batch_start, batch_end, week_keys):
    """Generate learning content for a batch of weeks via LLM."""
    week_range = f"第{batch_start}-{batch_end}周"
    prompt = f"""你是学习课程设计专家，精通"学习阶梯"、"二八法则"和"噪音中找信号"三大学习方法。

## 学习主题
{topic}

## 学习目标
{goal_desc}

## 学习重点
{goal_emphasis}

## 当前水平
{level}

## 5级学习阶梯
{ladder_desc}

## 重点方向
{focus_str}

## 本次生成范围
{week_range}（共{batch_end - batch_start + 1}周）

## 二八法则要求
每周内容必须明确标注"核心20%"——即该周最重要的、能解决80%实际问题的知识点。

## 噪音中找信号要求
资源推荐必须精挑细选，每个资源标注:
- 适合什么水平
- 难度（入门/进阶/高级）
- 预计耗时
- 为什么值得看（最大优点）

请为以下周生成内容，用JSON格式返回，key为周数:
[{week_keys}]

每个周的格式:
{{
  "周数": {{
    "study_summary": "本周学习内容的中文摘要（200-300字，覆盖核心知识点）",
    "core_20_percent": "本周最核心的20%内容（1-2句话，能解决80%问题的关键知识）",
    "doc_content": "## 标题\\n本周核心知识文档（300-500字）。必须从本周文章资源和视频简介中提炼核心知识点，禁止直接引用URL或堆砌原文。必须包含：核心概念定义、关键代码示例、真实使用场景、>核心提示引用块。禁止出现外部链接。",
    "resources": [
      # article 类型的 url 为 LLM 参考，LLM 须提炼其核心内容入 doc_content 并标注引用来源
      {{
        "type": "doc",
        "title": "官方文档名称（必须是真实存在的文档链接）",
        "url": "https://官方文档真实URL",
        "platform": "平台名",
        "level": "入门/进阶/高级",
        "duration": "预计耗时",
        "why": "为什么值得看"
      }},
      {{
        "type": "video",
        "title": "B站视频标题（优先B站视频）",
        "url": "https://www.bilibili.com/video/BVxxxxx",
        "platform": "B站",
        "level": "入门/进阶/高级",
        "duration": "预计耗时",
        "why": "为什么值得看"
      }}
    ],
    "project_task": "本周实践任务描述（中文，具体可执行）",
    "test_questions": [
      {{"type": "choice", "question": "选择题：XXX？", "options": ["A. XXX", "B. XXX", "C. XXX", "D. XXX"], "correct": "A"}},
      {{"type": "true_false", "question": "判断题：XXX", "correct": "true"}},
      {{"type": "short", "question": "简答题：XXX", "keywords": ["关键词1", "关键词2"]}}
    ]
  }}
}}

要求:
1. 所有内容使用中文
2. test_questions 数组必须包含17道题：10道choice + 5道true_false + 2道short
3. **doc_content 是核心**：必须从本周推荐的文章资源、视频简介中提炼核心知识点，生成300-500字的精炼Markdown文档。禁止直接引用URL、不做提炼堆砌原文。包含：核心概念定义、关键代码示例、真实使用场景、>核心提示引用块。资源URL不出现在doc_content中。
4. resources 每周精选2-4个：视频优先B站（提供真实BV号），文章提供真实URL（内容已提炼入doc_content，无需doc类型资源）
5. URL必须是真实存在的、可访问的链接，不要编造URL
6. 每周明确标注核心20%内容
7. 内容难度按5级学习阶梯递进
8. 实践任务要具体、可执行
9. 紧扣学习目标: {goal_desc}
10. test_questions 每周期必须生成：10道选择题 + 5道判断题 + 2道简答题（共17题），选择题/判断题必须提供正确答案

只返回JSON，不要其他文字。"""

    headers = {"Content-Type": "application/json"}
    if settings.LLM_API_KEY.startswith("tp-"):
        headers["api-key"] = settings.LLM_API_KEY
    else:
        headers["Authorization"] = f"Bearer {settings.LLM_API_KEY}"

    try:
        response = httpx.post(
            f"{settings.LLM_API_BASE}/chat/completions",
            headers=headers,
            json={
                "model": settings.LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            timeout=60,  # 增加超时时间
        )
        response.raise_for_status()
        result = response.json()
        msg = result["choices"][0]["message"]
        # 优先使用 content 字段，如果为空则尝试 reasoning_content
        raw_content = msg.get("content", "")
        if not raw_content and msg.get("reasoning_content"):
            raw_content = msg.get("reasoning_content", "")
        
        # 尝试提取 JSON
        import re
        m = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if m:
            batch_data = json.loads(m.group())
            print(f"[LLM] batch {week_range}: {len(batch_data)} weeks generated")
            return batch_data
        else:
            print(f"[LLM] batch {week_range}: no JSON found, content: {raw_content[:100]}")
            return None
    except httpx.TimeoutException:
        print(f"[LLM] batch {week_range} timeout")
        return None
    except Exception as e:
        print(f"[LLM] batch {week_range} failed: {e}")
        return None
