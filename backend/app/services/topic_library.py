"""
主题内容库 - 为常见学习主题提供预设的高质量学习内容和资源。
当 LLM API 不可用时，使用这些预设内容作为回退。
"""

TOPIC_LIBRARY = {
    "react": {
        "keywords": ["react", "reactjs", "react.js", "前端"],
        "levels": {
            1: {
                "name": "认知启蒙",
                "study_content": """React 是什么？
React 是 Facebook 开发的一个用于构建用户界面的 JavaScript 库。它的核心理念是「声明式」和「组件化」。

核心概念：
1. **JSX 语法** - 在 JavaScript 中写 HTML 的语法糖。例如：
   ```jsx
   const element = <h1>Hello, React!</h1>;
   ```
   它实际上会被编译成 React.createElement() 调用。

2. **组件** - UI 的最小可复用单元。有两种写法：
   ```jsx
   // 函数组件（推荐）
   function Welcome({ name }) {
     return <h1>Hello, {name}</h1>;
   }
   ```

3. **Props** - 父组件向子组件传递数据的方式，类似 HTML 属性。

4. **State** - 组件内部的响应式数据，用 useState 管理：
   ```jsx
   const [count, setCount] = useState(0);
   ```

5. **虚拟 DOM** - React 用 JavaScript 对象描述 UI 结构，只在数据变化时更新变化的部分，而不是整个页面。

动手试一试：
访问 https://react.dev/learn 的在线沙箱，试着写一个 Hello World 组件。""",
                "core_20": "JSX 语法 + 函数组件 + useState + Props 传递，掌握这 4 个就能写出基本的 React 页面",
                "project_task": """创建一个简单的「个人名片」组件：
1. 创建一个 ProfileCard 组件，展示姓名、职位、一句话介绍
2. 使用 Props 传入数据
3. 用一个按钮和 useState 实现「关注/取消关注」切换
4. 在父组件中渲染 3 张不同的名片

完成标准：页面能正常显示 3 张名片，点击关注按钮状态能正确切换。""",
                "doc_content": "## React 入门核心概念\n\nReact 是 Facebook 开发的 UI 库，核心理念是**声明式**和**组件化**。\n\n### JSX 语法\nJSX 让你在 JavaScript 中写类似 HTML 的代码：\n```jsx\nconst element = <h1>Hello, React!</h1>;\n```\n\n### 函数组件\n组件是 UI 的最小复用单元：\n```jsx\nfunction Welcome({ name }) {\n  return <h1>Hello, {name}</h1>;\n}\n```\n\n### Props 与 State\n- **Props**: 父组件向子组件传数据，类似 HTML 属性\n- **State**: 组件内部的响应式数据，用 `useState` 管理\n\n### 虚拟 DOM\nReact 用 JS 对象描述 UI，只在数据变化时更新变化部分，性能优异。\n\n> 动手试试：访问 react.dev/learn 的在线沙箱写一个 Hello World",
                "resources": [
                    {"type": "video", "title": "React 零基础入门到实战", "url": "https://www.bilibili.com/video/BV1wy4y1D7JT", "embed_url": "https://player.bilibili.com/player.html?bvid=BV1wy4y1D7JT&high_quality=1&danmaku=0", "platform": "B站", "level": "入门", "duration": "120分钟", "why": "系统入门课程，从环境搭建到项目实战"},
                    {"type": "video", "title": "10分钟学会 React", "url": "https://www.bilibili.com/video/BV1hm4y1v7oW", "embed_url": "https://player.bilibili.com/player.html?bvid=BV1hm4y1v7oW&high_quality=1&danmaku=0", "platform": "B站", "level": "入门", "duration": "10分钟", "why": "短视频快速了解 React 全貌"},
                ],
            },
            2: {
                "name": "基础构建",
                "study_content": """React 基础技能进阶：

1. **事件处理**
   ```jsx
   function Button() {
     const handleClick = () => alert('Clicked!');
     return <button onClick={handleClick}>点我</button>;
   }
   ```
   注意：传参要用箭头函数包裹，不能直接调用。

2. **条件渲染** - 三种方式：
   - 三元表达式：`{isLoggedIn ? <Dashboard /> : <Login />}`
   - && 短路：`{hasMessages && <MessageList />}`
   - 提前 return

3. **列表渲染**
   ```jsx
   const items = todos.map(todo =>
     <li key={todo.id}>{todo.text}</li>
   );
   ```
   key 必须唯一且稳定，不要用数组索引。

4. **useEffect** - 处理副作用（API 请求、订阅、定时器）
   ```jsx
   useEffect(() => {
     // 组件挂载或依赖变化时执行
     fetchData();
     return () => cleanup(); // 清理函数
   }, [dependency]);
   ```

5. **表单处理** - 受控组件模式：
   ```jsx
   const [text, setText] = useState('');
   <input value={text} onChange={e => setText(e.target.value)} />
   ```""",
                "core_20": "useEffect 的依赖数组机制 + 条件渲染 + 列表渲染的 key 原理，这三个解决了 80% 的日常开发问题",
                "project_task": """创建一个「待办事项」应用：
1. 输入框 + 添加按钮，能新增待办
2. 列表展示所有待办，支持勾选完成
3. 显示未完成数量
4. 用 localStorage 保存数据（useEffect 监听变化）
5. 支持删除功能

完成标准：刷新页面后数据不丢失，所有增删改功能正常。""",
                "doc_content": "## React Hooks 与表单处理\n\n### useEffect 副作用\n处理 API 请求、订阅、定时器等副作用：\n```jsx\nuseEffect(() => {\n  fetchData();\n  return () => cleanup(); // 清理函数\n}, [dependency]); // 依赖数组\n```\n- **空数组 `[]`**: 只在挂载时执行一次\n- **有依赖**: 依赖变化时重新执行\n- **无数组**: 每次渲染都执行\n\n### 条件渲染\n```jsx\n{isLoggedIn ? <Dashboard /> : <Login />}\n{hasMessages && <MessageList />}\n```\n\n### 列表渲染\n```jsx\nconst items = todos.map(todo =>\n  <li key={todo.id}>{todo.text}</li>\n);\n```\n> key 必须唯一且稳定，不要用数组索引\n\n### 受控组件表单\n```jsx\nconst [text, setText] = useState('');\n<input value={text} onChange={e => setText(e.target.value)} />\n```",
                "resources": [
                    {"type": "video", "title": "React Hooks 完全指南", "url": "https://www.bilibili.com/video/BV1gD4y1m7V3", "embed_url": "https://player.bilibili.com/player.html?bvid=BV1gD4y1m7V3&high_quality=1&danmaku=0", "platform": "B站", "level": "入门", "duration": "45分钟", "why": "全面讲解 useState、useEffect 等核心 Hooks"},
                ],
            },
            3: {
                "name": "实践应用",
                "study_content": """React 实战核心技能：

1. **自定义 Hook** - 复用状态逻辑
   ```jsx
   function useLocalStorage(key, initial) {
     const [value, setValue] = useState(
       () => JSON.parse(localStorage.getItem(key)) ?? initial
     );
     useEffect(() => {
       localStorage.setItem(key, JSON.stringify(value));
     }, [key, value]);
     return [value, setValue];
   }
   ```

2. **React Router** - 页面路由
   ```jsx
   import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
   // 声明式导航 + 路由配置
   ```

3. **状态管理选择**
   - 简单场景：useState + Props 传递
   - 跨组件共享：useContext + useReducer
   - 复杂场景：Zustand（推荐）或 Redux Toolkit

4. **数据请求** - 推荐用 React Query / TanStack Query
   ```jsx
   const { data, isLoading } = useQuery(['todos'], fetchTodos);
   ```
   自动处理缓存、重试、后台更新。

5. **性能优化**
   - React.memo 避免不必要的重渲染
   - useMemo 缓存计算结果
   - useCallback 缓存函数引用
   - 代码分割：React.lazy + Suspense""",
                "core_20": "自定义 Hook 模式 + React Router 路由配置 + Zustand/Context 状态管理，这三项覆盖了 80% 的实际项目需求",
                "project_task": """创建一个「电影搜索」应用：
1. 使用 React Router 实现首页/搜索/详情页三个页面
2. 调用 TMDB API（https://api.themoviedb.org）搜索电影
3. 用 React Query 管理 API 请求（加载态、错误态、缓存）
4. 用 Zustand 管理用户收藏夹（跨页面共享）
5. 点击电影卡片跳转到详情页

完成标准：能搜索电影、查看详情、添加收藏，刷新后收藏数据保留。""",
                "doc_content": "## React 实战：路由、状态管理与性能优化\n\n### 自定义 Hook\n复用状态逻辑的最佳方式：\n```jsx\nfunction useLocalStorage(key, initial) {\n  const [value, setValue] = useState(\n    () => JSON.parse(localStorage.getItem(key)) ?? initial\n  );\n  useEffect(() => {\n    localStorage.setItem(key, JSON.stringify(value));\n  }, [key, value]);\n  return [value, setValue];\n}\n```\n\n### React Router 路由\n```jsx\nimport { BrowserRouter, Routes, Route, Link } from 'react-router-dom';\n```\n声明式导航 + 路由配置，支持嵌套路由和动态参数。\n\n### 状态管理选型\n- **简单场景**: useState + Props 传递\n- **跨组件共享**: useContext + useReducer\n- **复杂场景**: Zustand（推荐，比 Redux 简单 10 倍）\n\n### 性能优化\n- `React.memo` 避免不必要重渲染\n- `useMemo` 缓存计算结果\n- `useCallback` 缓存函数引用\n- `React.lazy + Suspense` 代码分割\n\n> TanStack Query 自动处理 API 缓存、重试、后台更新",
                "resources": [
                    {"type": "video", "title": "React Router v6 路由实战", "url": "https://www.bilibili.com/video/BV1QY411N7pV", "embed_url": "https://player.bilibili.com/player.html?bvid=BV1QY411N7pV&high_quality=1&danmaku=0", "platform": "B站", "level": "进阶", "duration": "40分钟", "why": "系统讲解路由配置与嵌套路由"},
                    {"type": "article", "title": "自定义 Hook 模式大全", "url": "https://usehooks.com/", "platform": "useHooks.com", "level": "进阶", "duration": "25分钟", "why": "大量可复用的自定义 Hook 示例"},
                ],
            },
        },
    },
    "python": {
        "keywords": ["python", "py", "python3"],
        "levels": {
            1: {
                "name": "认知启蒙",
                "study_content": """Python 入门核心：

1. **变量和数据类型**
   ```python
   name = "Alice"      # 字符串
   age = 25            # 整数
   height = 1.68       # 浮点数
   is_student = True   # 布尔值
   scores = [90, 85]   # 列表
   info = {"name": "Alice", "age": 25}  # 字典
   ```

2. **控制流程**
   ```python
   # 条件判断
   if age >= 18:
       print("成年人")
   elif age >= 12:
       print("青少年")
   else:
       print("儿童")

   # 循环
   for i in range(5):
       print(i)
   ```

3. **函数**
   ```python
   def greet(name, greeting="你好"):
       return f"{greeting}, {name}!"
   
   print(greet("小明"))  # 你好, 小明!
   ```

4. **列表操作**（最常用）
   ```python
   fruits = ["苹果", "香蕉", "橙子"]
   fruits.append("葡萄")     # 添加
   fruits.remove("香蕉")     # 删除
   print(fruits[0])          # 索引访问
   print(len(fruits))        # 长度
   ```""",
                "core_20": "变量赋值 + if/for + 函数定义 + 列表/字典操作，这四块能写出 80% 的基础程序",
                "project_task": """创建一个「学生成绩管理器」命令行程序：
1. 用字典存储学生姓名和成绩
2. 实现添加学生、录入成绩、查看排名功能
3. 计算平均分、最高分、最低分
4. 支持按成绩排序显示

完成标准：程序能正常运行，所有功能无 bug。""",
                "doc_content": "## Python 入门核心\n\n### 变量与数据类型\n```python\nname = \"Alice\"      # 字符串\nage = 25            # 整数\nheight = 1.68       # 浮点数\nscores = [90, 85]   # 列表\ninfo = {\"name\": \"Alice\", \"age\": 25}  # 字典\n```\n\n### 控制流程\n```python\nif age >= 18:\n    print(\"成年人\")\n\nfor i in range(5):\n    print(i)\n```\n\n### 函数定义\n```python\ndef greet(name, greeting=\"你好\"):\n    return f\"{greeting}, {name}!\"\n```\n\n### 列表操作（最常用）\n```python\nfruits = [\"苹果\", \"香蕉\", \"橙子\"]\nfruits.append(\"葡萄\")     # 添加\nfruits.remove(\"香蕉\")     # 删除\nprint(fruits[0])          # 索引\nprint(len(fruits))        # 长度\n```\n\n> 掌握这四块就能写出 80% 的基础程序",
                "resources": [
                    {"type": "video", "title": "Python 零基础入门", "url": "https://www.bilibili.com/video/BV1wD4y1o7AS", "embed_url": "https://player.bilibili.com/player.html?bvid=BV1wD4y1o7AS&high_quality=1&danmaku=0", "platform": "B站", "level": "入门", "duration": "30分钟", "why": "短视频快速了解 Python 基础"},
                ],
            },
            2: {
                "name": "基础构建",
                "study_content": """Python 基础进阶：

1. **文件操作**
   ```python
   with open("data.txt", "r", encoding="utf-8") as f:
       content = f.read()
   # with 语句自动处理文件关闭
   ```

2. **异常处理**
   ```python
   try:
       result = 10 / 0
   except ZeroDivisionError as e:
       print(f"错误: {e}")
   finally:
       print("清理资源")
   ```

3. **面向对象**
   ```python
   class Student:
       def __init__(self, name, age):
           self.name = name
           self.age = age
       
       def introduce(self):
           return f"我叫{self.name}，{self.age}岁"
   ```

4. **列表推导式**（Python 特色）
   ```python
   squares = [x**2 for x in range(10)]
   evens = [x for x in range(20) if x % 2 == 0]
   ```

5. **模块和包**
   ```python
   import json
   from datetime import datetime, timedelta
   from pathlib import Path
   ```""",
                "core_20": "文件读写 + 异常处理 + 类的基本使用 + 列表推导式，这些是从脚本到项目的桥梁",
                "project_task": """创建一个「日记本」应用：
1. 用类封装日记的增删改查
2. 数据保存到 JSON 文件
3. 支持按日期搜索和关键词搜索
4. 统计写日记的天数和频率

完成标准：程序能持久化存储，重启后数据不丢失。""",
                "doc_content": "## Python 基础进阶\n\n### 文件操作\n```python\nwith open(\"data.txt\", \"r\", encoding=\"utf-8\") as f:\n    content = f.read()\n# with 语句自动处理文件关闭\n```\n\n### 异常处理\n```python\ntry:\n    result = 10 / 0\nexcept ZeroDivisionError as e:\n    print(f\"错误: {e}\")\nfinally:\n    print(\"清理资源\")\n```\n\n### 面向对象\n```python\nclass Student:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    def introduce(self):\n        return f\"我叫{self.name}，{self.age}岁\"\n```\n\n### 列表推导式（Python 特色）\n```python\nsquares = [x**2 for x in range(10)]\nevens = [x for x in range(20) if x % 2 == 0]\n```\n\n### 模块导入\n```python\nimport json\nfrom datetime import datetime\nfrom pathlib import Path\n```\n\n> 文件读写 + 异常处理 + 类 + 推导式 = 从脚本到项目的桥梁",
                "resources": [
                    {"type": "video", "title": "Python 进阶编程技巧", "url": "https://www.bilibili.com/video/BV1c4411e77t", "embed_url": "https://player.bilibili.com/player.html?bvid=BV1c4411e77t&high_quality=1&danmaku=0", "platform": "B站", "level": "进阶", "duration": "50分钟", "why": "面向对象与文件操作实战讲解"},
                ],
            },
        },
    },
    "llm": {
        "keywords": ["llm", "大模型", "大语言模型", "language model", "rag", "prompt"],
        "levels": {
            1: {
                "name": "认知启蒙",
                "study_content": """LLM（大语言模型）入门：

1. **什么是 LLM？**
   LLM 是基于 Transformer 架构的大规模神经网络，通过在海量文本上训练，学会了理解和生成自然语言。
   代表：GPT-4、Claude、通义千问、文心一言。

2. **核心原理（简化版）**
   - **Token 化** - 把文本切成小块（token），"你好"可能是 1-2 个 token
   - **注意力机制** - 模型理解每个词和其他词的关系
   - **自回归生成** - 一个字一个字地预测下一个 token

3. **Prompt Engineering（提示工程）**
   核心技巧：
   - **角色设定**：「你是一位资深 Python 工程师」
   - **明确输出格式**：「用 JSON 格式返回」
   - **Few-shot 示例**：给 2-3 个例子让模型学习模式
   - **思维链**：「请一步步思考」

4. **API 调用基础**
   ```python
   import openai
   response = openai.chat.completions.create(
       model="gpt-4o-mini",
       messages=[
           {"role": "system", "content": "你是助手"},
           {"role": "user", "content": "解释 Transformer"}
       ]
   )
   ```

5. **应用场景**
   - 文本生成/摘要/翻译
   - 代码生成/调试
   - 知识问答
   - 数据分析""",
                "core_20": "Prompt Engineering 的 4 个核心技巧 + API 调用方法，掌握这两点就能用 LLM 解决 80% 的任务",
                "project_task": """创建一个「智能翻译助手」：
1. 用 OpenAI/兼容 API 实现中英文互译
2. 支持 3 种风格：正式、口语、学术
3. 添加术语表功能（特定词汇的固定翻译）
4. 实现批量翻译（一次翻译多段文本）

完成标准：翻译质量优于机器直译，能保持上下文连贯性。""",
                "doc_content": "## LLM 大语言模型入门\n\nLLM 是基于 **Transformer** 架构的大规模神经网络，通过在海量文本上训练，学会理解和生成自然语言。代表：GPT-4、Claude、通义千问、文心一言。\n\n### 核心原理（简化版）\n- **Token 化**：把文本切成小块，`你好` 可能是 1-2 个 token\n- **注意力机制**：模型理解每个词和其他词的关系\n- **自回归生成**：逐字预测下一个 token\n\n### Prompt Engineering 四大技巧\n1. **角色设定**：`你是一位资深 Python 工程师`\n2. **明确输出格式**：`用 JSON 格式返回`\n3. **Few-shot 示例**：给 2-3 个例子让模型学习模式\n4. **思维链**：`请一步步思考`\n\n### API 调用示例\n```python\nimport openai\nresponse = openai.chat.completions.create(\n    model=\"gpt-4o-mini\",\n    messages=[\n        {\"role\": \"system\", \"content\": \"你是助手\"},\n        {\"role\": \"user\", \"content\": \"解释 Transformer\"}\n    ]\n)\n```\n\n> 掌握 Prompt 技巧 + API 调用 = 用 LLM 解决 80% 的任务",
                "resources": [
                    {"type": "video", "title": "LLM 入门：从零理解大模型", "url": "https://www.bilibili.com/video/BV1ug4y1t7aH", "embed_url": "https://player.bilibili.com/player.html?bvid=BV1ug4y1t7aH&high_quality=1&danmaku=0", "platform": "B站", "level": "入门", "duration": "45分钟", "why": "通俗易懂的 LLM 原理讲解"},
                ],
            },
            2: {
                "name": "基础构建",
                "study_content": """LLM 应用开发进阶：

1. **RAG（检索增强生成）**
   核心思路：先检索相关文档，再让 LLM 基于文档回答
   ```
   用户问题 → 向量检索 → 相关文档 → LLM 生成答案
   ```
   工具链：LangChain/LlamaIndex + 向量数据库（Chroma/Pinecone）

2. **Function Calling**
   让 LLM 调用外部工具：
   ```python
   tools = [{
       "type": "function",
       "function": {
           "name": "get_weather",
           "description": "获取天气信息",
           "parameters": {...}
       }
   }]
   ```

3. **对话记忆管理**
   - 滑动窗口：只保留最近 N 轮对话
   - 摘要压缩：用 LLM 压缩历史对话
   - Token 限制：按 token 数量裁剪

4. **Embedding 和向量搜索**
   ```python
   from openai import OpenAI
   embedding = client.embeddings.create(
       input="文本内容", model="text-embedding-3-small"
   )
   ```

5. **流式输出**
   ```python
   stream = client.chat.completions.create(
       stream=True, ...
   )
   for chunk in stream:
       print(chunk.choices[0].delta.content, end="")
   ```""",
                "core_20": "RAG 检索增强生成 + Function Calling + 流式输出，这三个是当前 LLM 应用开发的核心模式",
                "project_task": """创建一个「知识库问答」系统：
1. 上传 PDF/Markdown 文档，自动分块
2. 用 Embedding 生成向量，存入 Chroma
3. 用户提问时检索相关文档片段
4. 将检索结果作为上下文传给 LLM 生成答案
5. 支持流式输出和对话历史

完成标准：能基于上传的文档准确回答问题，不编造内容。""",
                "doc_content": "## LLM 应用开发进阶\n\n### RAG 检索增强生成\n核心思路：先检索相关文档，再让 LLM 基于文档回答。\n```\n用户问题 -> 向量检索 -> 相关文档 -> LLM 生成答案\n```\n工具链：LangChain/LlamaIndex + 向量数据库（Chroma/Pinecone）\n\n### Function Calling\n让 LLM 调用外部工具：\n```python\ntools = [{\n    \"type\": \"function\",\n    \"function\": {\n        \"name\": \"get_weather\",\n        \"description\": \"获取天气信息\",\n        \"parameters\": {...}\n    }\n}]\n```\n\n### 对话记忆管理\n- **滑动窗口**：只保留最近 N 轮对话\n- **摘要压缩**：用 LLM 压缩历史对话\n- **Token 限制**：按 token 数量裁剪\n\n### Embedding 与向量搜索\n```python\nembedding = client.embeddings.create(\n    input=\"文本内容\", model=\"text-embedding-3-small\"\n)\n```\n\n### 流式输出\n```python\nstream = client.chat.completions.create(stream=True, ...)\nfor chunk in stream:\n    print(chunk.choices[0].delta.content, end=\"\")\n```\n\n> RAG + Function Calling + 流式输出 = 当前 LLM 应用开发三大核心模式",
                "resources": [
                    {"type": "video", "title": "RAG 大模型知识库实战", "url": "https://www.bilibili.com/video/BV1xN4y1v7gG", "embed_url": "https://player.bilibili.com/player.html?bvid=BV1xN4y1v7gG&high_quality=1&danmaku=0", "platform": "B站", "level": "进阶", "duration": "45分钟", "why": "从零搭建 RAG 知识库问答系统，含完整代码演示"},
                ],
            },
        },
    },
}


def get_topic_content(topic: str, ladder_level: int) -> dict:
    """
    根据主题和阶梯等级获取预设内容。
    返回: {"study_content", "core_20", "project_task", "resources"} 或 None
    """
    topic_lower = topic.lower().strip()

    # 精确匹配
    if topic_lower in TOPIC_LIBRARY:
        level_data = TOPIC_LIBRARY[topic_lower]["levels"].get(ladder_level)
        return level_data

    # 关键词匹配
    for key, data in TOPIC_LIBRARY.items():
        if any(kw in topic_lower for kw in data["keywords"]):
            level_data = data["levels"].get(ladder_level)
            return level_data

    return None


def get_topic_resources(topic: str, ladder_level: int) -> list:
    """获取主题相关的预设资源列表。"""
    content = get_topic_content(topic, ladder_level)
    if content:
        return content.get("resources", [])
    return []
