"""
Learning Output Reviewer - Skill 深度嵌入版
苏格拉底追问 + 费曼技巧 + 速查表压缩
"""
import json
import re
from ..config import settings, effective_model


def review_learning_output(
    step_title: str,
    step_content: str,
    user_output: str,
    step_type: str,
    test_question: str = "",
    test_answer_hint: str = "",
    ladder_level: str = "",
    ladder_name: str = "",
) -> dict:
    """
    评审用户的学习输出，深度嵌入三大学习方法。

    评审维度（融合费曼技巧）:
    1. 理解深度 (25%): 不是表面复述，有自己的理解
    2. 准确性 (20%): 概念和事实正确
    3. 完整性 (15%): 覆盖关键知识点
    4. 费曼表达 (25%): 用简单语言解释，避免术语堆砌
    5. 实践关联 (15%): 联系实际项目或例子

    返回:
    dict with: passed, score, feedback, suggestions,
               socratic_question (苏格拉底追问),
               feynman_score (费曼技巧评分),
               cheat_sheet (速查表建议)
    """
    # 基础质量检查
    min_length = 100
    if len(user_output.strip()) < min_length:
        return {
            "passed": False,
            "score": 20,
            "feedback": f"输出内容太短（{len(user_output.strip())}字）。请提供至少{min_length}字的实质性内容，用自己的话解释概念并举例说明。",
            "suggestions": [
                "展开每个概念，用自己的话详细解释",
                "添加具体的例子或类比",
                "将概念与你的项目实践联系起来",
            ],
            "socratic_question": "你能用最简单的话告诉我，这周学到的最核心的一个概念是什么吗？",
            "feynman_score": 0,
            "cheat_sheet": None,
        }

    # 检查复制粘贴（基础启发式）
    if step_content and _similarity(user_output, step_content) > 0.8:
        return {
            "passed": False,
            "score": 30,
            "feedback": "你的输出与原始材料高度相似。评审的目的是展示你的理解，而非复述材料。请用自己的话重新表达。",
            "suggestions": [
                "关掉参考资料，凭记忆重新写",
                "用你自己的例子，不要用资料里的",
                "尝试用费曼技巧——假装教一个完全不懂的人",
            ],
            "socratic_question": "如果不能用任何专业术语，你会怎么解释这个概念？",
            "feynman_score": 20,
            "cheat_sheet": None,
        }

    # AI 评审（如果 LLM API 可用）
    if settings.LLM_API_KEY:
        return _ai_review(
            step_title, step_content, user_output, step_type,
            test_question, test_answer_hint, ladder_level, ladder_name
        )

    # 降级：规则评审
    return _rule_based_review(
        step_title, step_content, user_output, step_type,
        test_question, ladder_level, ladder_name
    )


def _ai_review(step_title, step_content, user_output, step_type,
               test_question, test_answer_hint, ladder_level, ladder_name):
    """
    使用 LLM API 进行中文评审。
    嵌入苏格拉底追问、费曼技巧评分、速查表建议。
    """
    import httpx

    test_context = ""
    if test_question:
        test_context = f"""

## 测试题目
{test_question}

## 答案要点参考
{test_answer_hint}

请同时评估用户对测试题的回答质量。"""

    ladder_context = ""
    if ladder_name:
        ladder_context = f"""

## 当前学习阶梯
等级: {ladder_level} - {ladder_name}
请根据该等级的过关标准来评估输出质量。"""

    prompt = f"""你是一位严格但公正的学习评审官，同时精通苏格拉底追问法和费曼技巧。

## 学习步骤
标题：{step_title}
类型：{step_type}
预期内容：{step_content[:500] if step_content else "无"}
{ladder_context}{test_context}

## 学生输出
{user_output}

## 评审标准（融合费曼技巧）
1. 理解深度（25%）：是否展示了深入理解，而非表面知识？
2. 准确性（20%）：概念和事实是否正确？
3. 完整性（15%）：是否覆盖了关键知识点？
4. 费曼表达（25%）：是否用简单语言解释？是否避免了术语堆砌？能否让外行听懂？
5. 实践关联（15%）：是否有实际例子或项目关联？

## 评分标准
- 90-100分：优秀，深入理解且能用简单语言讲清楚
- 70-89分：合格，基本理解正确
- 50-69分：不足，理解有偏差或只是在用术语糊弄
- 0-49分：需重做，未掌握核心内容

## 输出格式（仅JSON）
{{
    "score": <0-100的整数>,
    "passed": <score>=70时为true，否则为false>,
    "feedback": "<2-3句中文总体反馈，指出优点和不足>",
    "criteria_scores": {{
        "understanding": <0-100>,
        "accuracy": <0-100>,
        "completeness": <0-100>,
        "feynman": <0-100, 费曼技巧评分：用简单语言解释的能力>,
        "practical": <0-100>
    }},
    "suggestions": ["<具体改进建议1>", "<具体改进建议2>", "<具体改进建议3>"],
    "socratic_question": "<一个苏格拉底式追问问题，针对用户输出中的理解盲区或可以深挖的概念。这个问题应该让用户思考'为什么'或'如果...会怎样'。只问一个问题，要具体针对用户的输出内容。>",
    "feynman_analysis": {{
        "score": <0-100>,
        "simple_language": <是否使用了简单语言？true/false>,
        "has_analogy": <是否使用了类比？true/false>,
        "jargon_overuse": <是否过度使用术语？true/false>,
        "improvement": "<如何更好地用简单语言解释的建议>"
    }},
    "cheat_sheet_suggestion": "<如果用户输出质量>=70，给出一个速查表压缩建议：一句话总结+3个核心概念+1个例子。否则为null>"
}}
"""

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
                "model": effective_model(),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        review_data = json.loads(content)

        return {
            "passed": review_data.get("passed", review_data.get("score", 0) >= 70),
            "score": review_data.get("score", 50),
            "feedback": review_data.get("feedback", "评审完成。"),
            "suggestions": review_data.get("suggestions", []),
            "socratic_question": review_data.get("socratic_question", ""),
            "feynman_score": review_data.get("feynman_analysis", {}).get("score", 50),
            "feynman_analysis": review_data.get("feynman_analysis"),
            "cheat_sheet": review_data.get("cheat_sheet_suggestion"),
        }
    except Exception as e:
        print(f"AI review failed: {e}")
        return _rule_based_review(
            step_title, step_content, user_output, step_type,
            test_question, ladder_level, ladder_name
        )


def _rule_based_review(step_title, step_content, user_output, step_type,
                       test_question, ladder_level="", ladder_name=""):
    """
    规则评审（LLM API 不可用时的降级方案）。
    嵌入费曼技巧检测和苏格拉底追问。
    """
    score = 50
    suggestions = []
    feynman_score = 50

    # 长度加分
    if len(user_output) > 300:
        score += 10
    if len(user_output) > 500:
        score += 10

    # 有例子
    example_patterns = [
        r"例如", r"比如", r"举个例子", r"举例", r"以.*为例",
        r"example", r"for instance", r"such as", r"e\.g\.",
    ]
    has_examples = any(re.search(p, user_output, re.IGNORECASE) for p in example_patterns)
    if has_examples:
        score += 15
        feynman_score += 10
    else:
        suggestions.append("尝试添加具体的例子或类比来阐述你的理解")

    # 有个人思考
    reflection_patterns = [
        r"我觉得", r"我认为", r"我的理解", r"我理解", r"总结", r"体会",
        r"我发现", r"我学到", r"关键", r"核心",
        r"I think", r"I understand", r"In my opinion", r"key",
    ]
    has_reflection = any(re.search(p, user_output, re.IGNORECASE) for p in reflection_patterns)
    if has_reflection:
        score += 10
        feynman_score += 5
    else:
        suggestions.append("加入个人思考——你觉得哪些内容最有价值？为什么？")

    # 有结构
    if "\n\n" in user_output or "\n-" in user_output or "\n1." in user_output or "\n*" in user_output:
        score += 5
    else:
        suggestions.append("用段落或列表组织你的输出，让结构更清晰")

    # 关联实践
    project_patterns = [
        r"项目", r"代码", r"实现", r"应用", r"实践", r"开发",
        r"project", r"code", r"implement", r"build",
    ]
    has_project = any(re.search(p, user_output, re.IGNORECASE) for p in project_patterns)
    if has_project:
        score += 10
        feynman_score += 10
    else:
        suggestions.append("将学习内容与你的实际项目或工作场景联系起来")

    # 费曼技巧检测：检查是否使用了过多术语而没有解释
    jargon_patterns = [
        r"架构", r"范式", r"抽象", r"封装", r"多态", r"继承",
        r"分布式", r"微服务", r"容器化", r"编排",
        r"architecture", r"paradigm", r"abstraction", r"polymorphism",
    ]
    jargon_count = sum(1 for p in jargon_patterns if re.search(p, user_output, re.IGNORECASE))

    # 如果有术语但没有解释，扣分
    if jargon_count > 3 and not has_examples:
        feynman_score -= 20
        suggestions.append("费曼技巧：你使用了较多术语但没有用简单语言解释。尝试用类比或日常语言重新表达")
    elif jargon_count > 0 and has_examples:
        feynman_score += 5

    feynman_score = max(0, min(100, feynman_score))
    score = min(score, 100)
    passed = score >= 70

    # 生成苏格拉底追问问题
    socratic_question = _generate_socratic_question(user_output, step_type, ladder_name)

    # 生成速查表建议（如果通过）
    cheat_sheet = None
    if passed:
        cheat_sheet = _generate_cheat_sheet_suggestion(step_title, user_output)

    if passed:
        feedback = f"你的输出得分 {score}/100（费曼评分 {feynman_score}/100）。不错！你展示了对核心概念的基本理解。"
    else:
        feedback = f"你的输出得分 {score}/100（费曼评分 {feynman_score}/100）。还需要更深入——尝试更详细地解释概念，并加入自己的思考和例子。"

    if not suggestions:
        suggestions = ["继续保持！", "尝试将不同概念之间建立联系"]

    return {
        "passed": passed,
        "score": score,
        "feedback": feedback,
        "suggestions": suggestions[:3],
        "socratic_question": socratic_question,
        "feynman_score": feynman_score,
        "cheat_sheet": cheat_sheet,
    }


def _generate_socratic_question(user_output: str, step_type: str, ladder_name: str) -> str:
    """
    基于用户输出生成苏格拉底追问问题。
    规则版：根据内容类型和关键词选择追问方向。
    """
    # 检测用户输出中的关键主题
    if re.search(r"概念|定义|是什么", user_output):
        return "你能举一个这个概念在实际项目中的应用场景吗？如果不用这个概念，会遇到什么问题？"
    elif re.search(r"步骤|流程|过程", user_output):
        return "如果跳过其中某个步骤会怎样？哪个步骤是最关键的，为什么？"
    elif re.search(r"优点|好处|优势", user_output):
        return "这个方案有什么局限性或trade-off？在什么场景下它反而不适用？"
    elif re.search(r"项目|代码|实现", user_output):
        return "如果要把这个项目的规模扩大10倍，你当前的方案还能work吗？需要做哪些改变？"
    elif re.search(r"比较|对比|区别", user_output):
        return "在什么情况下你会选择另一个方案？选择的依据是什么？"
    else:
        return "你能用最简单的语言（像对一个12岁小孩讲）重新解释你学到的最核心的概念吗？"


def _generate_cheat_sheet_suggestion(step_title: str, user_output: str) -> str:
    """
    基于用户输出生成速查表压缩建议。
    规则版：提取关键信息组成速查表。
    """
    # 提取前100字作为一句话总结
    summary = user_output[:100].replace("\n", " ").strip()
    if len(user_output) > 100:
        summary += "..."

    return (
        f"速查表建议:\n"
        f"一句话总结: {summary}\n"
        f"核心概念: 从你的输出中提取3-5个关键概念\n"
        f"常见错误: 回顾你遇到的问题和解决方案\n"
        f"实操清单: 列出做之前需要检查的要点"
    )


def grade_test_questions(
    test_questions: list,
    answers: list,
) -> dict:
    """
    对结构化测试题进行评分。
    
    Args:
        test_questions: 测试题列表，[{"type":"choice"|"true_false"|"short","question":"...","options":[...],"correct":"A","keywords":[...]}]
        answers: 用户答案列表，[{"question_index":0,"answer":"A"}]
    
    Returns:
        {
            "passed": bool,
            "score": float,        # 0-100
            "total": int,
            "correct": int,
            "results": [            # 每题详情
                {
                    "index": int,
                    "type": str,
                    "question": str,
                    "user_answer": str,
                    "correct_answer": str,
                    "correct": bool,
                    "score": float,   # 本题得分
                }
            ],
            "feedback": str,
            "suggestions": list[str],
        }
    """
    if not test_questions or not answers:
        return {
            "passed": False,
            "score": 0,
            "total": len(test_questions) if test_questions else 0,
            "correct": 0,
            "results": [],
            "feedback": "未找到测试题或答案。",
            "suggestions": ["请确保已加载测试题目并填写答案。"],
        }
    
    # 转换为 dict 方便查询
    answer_map = {a["question_index"]: a["answer"] for a in answers}
    
    results = []
    correct_count = 0
    
    for i, q in enumerate(test_questions):
        qtype = q.get("type", "short")
        user_ans = answer_map.get(i, "").strip()
        correct_ans = ""
        is_correct = False
        q_score = 0
        
        if qtype == "choice":
            correct_ans = q.get("correct", "").upper().strip()
            is_correct = user_ans.upper() == correct_ans
            q_score = 100 if is_correct else 0
            
        elif qtype == "true_false":
            correct_ans = str(q.get("correct", "")).lower().strip()
            is_correct = user_ans.lower() == correct_ans
            q_score = 100 if is_correct else 0
            
        elif qtype == "short":
            correct_ans = q.get("keywords", [])
            # 关键词匹配：答到1个关键词得40%，2个得70%，3个以上得100%
            if not user_ans:
                q_score = 0
            else:
                kw_match = sum(1 for kw in correct_ans if kw in user_ans)
                if kw_match == 0:
                    q_score = 0
                elif kw_match == 1:
                    q_score = 40
                elif kw_match == 2:
                    q_score = 70
                else:
                    q_score = 100
            is_correct = q_score >= 70  # 简答题 70 分以上算对
            correct_ans = str(correct_ans)
        
        if is_correct:
            correct_count += 1
        
        results.append({
            "index": i,
            "type": qtype,
            "question": q.get("question", ""),
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "correct": is_correct,
            "score": q_score,
        })
    
    total = len(test_questions)
    score = round(sum(r["score"] for r in results) / total) if total > 0 else 0
    passed = score >= 70
    
    # 生成反馈
    correct_ans_list = [r["correct_answer"] for r in results]
    
    return {
        "passed": passed,
        "score": score,
        "total": total,
        "correct": correct_count,
        "results": results,
        "feedback": f"得分 {score}/100（答对 {correct_count}/{total} 题）{'\u2705 通过' if passed else '\u274c 未通过'}",
        "suggestions": _build_test_suggestions(results, test_questions),
    }


def _build_test_suggestions(results: list, test_questions: list) -> list:
    suggestions = []
    for r in results:
        if r["correct"]:
            continue
        qtype = r["type"]
        q_idx = r["index"]
        q = test_questions[q_idx] if q_idx < len(test_questions) else {}
        
        if qtype == "choice":
            suggestions.append(f"第{q_idx+1}题选错了。正确答案：{r['correct_answer']}。请回顾相关知识点。")
        elif qtype == "true_false":
            suggestions.append(f"第{q_idx+1}题判断错误。正确答案：{r['correct_answer']}。")
        elif qtype == "short":
            kw = q.get("keywords", [])
            suggestions.append(f"第{q_idx+1}题参考答案关键词：{kw}。请补充相关内容。")
    
    if not suggestions:
        suggestions.append("全部答对，继续保持！")
    
    return suggestions[:3]


def _similarity(text1: str, text2: str) -> float:
    """简单的词重叠相似度。"""
    # 中文按字符分割，英文按单词
    chars1 = set(text1.lower())
    chars2 = set(text2.lower())
    if not chars1 or not chars2:
        return 0.0
    intersection = chars1 & chars2
    union = chars1 | chars2
    return len(intersection) / len(union)
