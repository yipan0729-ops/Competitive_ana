# 自动化竞品分析工具设计文档

## 1. 项目概述

### 1.1 项目背景

竞品分析是产品决策的重要环节，但传统方式存在以下痛点：
- **不知道竞品有哪些**：需要手动搜索，容易遗漏
- **不知道去哪找信息**：数据源分散在多个平台
- **数据收集耗时费力**：需要手动访问多个平台
- **信息缺乏结构化**：复制粘贴格式混乱
- **分析维度不全面**：容易遗漏关键信息
- **持续监控成本高**：难以实时追踪竞品动态

### 1.2 项目目标

基于已有的URL智能读取能力（Firecrawl + Jina + Playwright三层策略），构建一个自动化竞品分析工具，实现：
- **智能数据源发现**：用户输入主题，自动搜索并推荐竞品及数据源（NEW）
- **自动化数据采集**：批量抓取竞品官网、社交媒体、电商平台等多渠道信息
- **智能化信息解析**：利用AI提取关键特征、功能点、价格策略等结构化数据
- **系统化分析输出**：生成多维度竞品分析报告（SWOT、功能对比矩阵、用户口碑等）
- **持续性监控预警**：定期追踪竞品动态，发现重要变化自动通知

### 1.3 核心价值

- **效率提升**：从手动3-5天缩短至自动化30分钟
- **全面性**：多渠道、多维度、多竞品并行分析
- **实时性**：定时监控，及时发现竞品策略变化
- **智能化**：AI辅助洞察，减少人工分析工作量

---

## 2. 技术架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                      用户交互层                          │
│   [主题输入] [数据源推荐] [报告查看] [监控面板]          │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│                   业务编排层                             │
│  • 任务编排  • 定时调度  • 报告生成  • 配置管理         │
└────┬────────────────────────────────────────────────────┘
     │
┌────┴──────────────────────────────────────────────────┐
│           智能数据源发现层 (NEW)                       │
│  ┌──────────────┐    ┌──────────────┐                 │
│  │ 搜索引擎集成 │    │ LLM竞品提取  │                 │
│  └──────────────┘    └──────────────┘                 │
│  • Google/Bing       • 竞品识别                        │
│  • Serper API        • 链接分类                        │
│  • 垂直平台搜索      • 质量评分                        │
└────┬──────────────────────────────────────────────────┘
     │
┌────┴─────────────────┬──────────────────────────┐
│   数据采集层         │   AI分析层                │
│                      │                           │
│  ┌──────────────┐    │  ┌──────────────┐        │
│  │ URL爬虫模块  │    │  │ 信息提取模块 │        │
│  │ (三层策略)   │────┼─→│ (LLM解析)    │        │
│  └──────────────┘    │  └──────────────┘        │
│  • Firecrawl API     │  • 特征识别              │
│  • Jina Reader       │  • 结构化输出             │
│  • Playwright        │  • 情感分析               │
│                      │  • 对比分析               │
│  ┌──────────────┐    │                           │
│  │ 平台适配器   │    │  ┌──────────────┐        │
│  │ (识别+配置)  │    │  │ 报告生成模块 │        │
│  └──────────────┘    │  │ (模板引擎)   │        │
│  • 官网              │  └──────────────┘        │
│  • 小红书/知乎       │  • SWOT分析              │
│  • 淘宝/京东         │  • 功能矩阵               │
│  • 微信公众号        │  • 价格对比               │
│  • 抖音/B站          │  • 用户口碑               │
└──────────────────────┴──────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│                   数据存储层                             │
│  • 原始数据 (Markdown+图片)  • 分析结果 (JSON)          │
│  • 历史版本 • 变化记录 • 分析报告 • 搜索缓存            │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心技术栈

**数据源发现（NEW）**：
- Google Custom Search API - 高质量搜索结果
- Bing Search API - 性价比友好
- Serper API - 专业搜索API，结构化返回
- 垂直平台搜索（小红书、知乎、搜狗微信等）

**数据采集**：
- Firecrawl API (v2) - AI驱动的网页抓取
- Jina Reader - 免费的网页内容提取
- Playwright - 浏览器自动化（需要登录的场景）

**AI分析**：
- OpenAI GPT-4 / Claude / DeepSeek - 内容理解与分析
- LangChain - AI工作流编排
- 本地LLM（可选）- 降低成本

**数据处理**：
- Python 3.10+
- Pandas - 数据分析
- BeautifulSoup4 - HTML解析
- Regex - 文本提取
- FuzzyWuzzy - 模糊匹配（去重）

**任务调度**：
- APScheduler - 定时任务
- Celery（可选）- 分布式任务队列

**存储**：
- SQLite / PostgreSQL - 结构化数据
- 文件系统 - Markdown文档和图片
- Redis（可选）- 缓存和消息队列

**前端（可选）**：
- Streamlit - 快速原型
- Flask/FastAPI - Web后端
- Vue.js（后期）- 完整前端

---

## 3. 功能模块设计

### 3.0 智能数据源发现模块（前置模块）

#### 3.0.1 模块概述

**核心功能**：用户只需输入竞品调研主题（如"在线协作工具"、"AI写作助手"），系统自动搜索并推荐相关竞品及其数据源链接。

**解决的问题**：
- 用户不知道竞品有哪些
- 不知道去哪里找竞品信息
- 手动配置数据源太繁琐

**输入示例**：
```
主题：AI写作助手
目标市场：中国
竞品数量：3-5个
```

**输出示例**：
```python
{
    "topic": "AI写作助手",
    "competitors": [
        {
            "name": "Notion AI",
            "confidence": 0.95,
            "data_sources": [
                {"type": "官网", "url": "https://notion.so", "priority": 1},
                {"type": "产品介绍", "url": "https://notion.so/product/ai", "priority": 1},
                {"type": "定价", "url": "https://notion.so/pricing", "priority": 1},
                {"type": "小红书", "url": "https://xiaohongshu.com/search?keyword=Notion+AI", "priority": 2},
                {"type": "知乎评测", "url": "https://www.zhihu.com/search?q=Notion+AI", "priority": 2}
            ]
        },
        {
            "name": "Jasper AI",
            "confidence": 0.92,
            "data_sources": [...]
        }
    ],
    "suggested_keywords": ["AI写作", "智能文案", "内容生成"],
    "related_categories": ["办公软件", "内容营销工具"]
}
```

---

#### 3.0.2 实现策略

**策略一：搜索引擎API（主要方式）**

**支持的搜索引擎**：
1. **Google Custom Search API**
   - 优点：结果质量高，覆盖全面
   - 成本：100次免费/天，超出$5/1000次
   - 使用场景：海外产品、英文内容

2. **Bing Search API**
   - 优点：价格友好，中文支持好
   - 成本：1000次免费/月，超出$3/1000次
   - 使用场景：通用搜索

3. **Serper API**
   - 优点：专为爬虫设计，返回结构化数据
   - 成本：2500次免费，超出$5/1000次
   - 使用场景：批量搜索

4. **百度搜索（非官方API）**
   - 优点：中文内容最全
   - 成本：免费（需控制频率）
   - 使用场景：国内产品

**搜索策略**：

**阶段1：发现竞品**
```python
# 搜索查询构造
queries = [
    "{topic} 竞品",
    "{topic} 对比",
    "best {topic} alternatives",
    "{topic} vs",
    "{topic} 排行榜"
]

# 示例：AI写作助手
# → "AI写作助手 竞品"
# → "AI写作助手 对比"
# → "best AI writing assistant alternatives"
```

**阶段2：提取竞品名称**
```python
# 从搜索结果中提取竞品
# 方法1：解析标题和摘要
# 方法2：访问对比类文章，用LLM提取竞品列表

# LLM Prompt示例：
"""
从以下文章中提取所有提到的{topic}竞品名称。
只返回JSON数组格式：["竞品1", "竞品2", ...]

文章内容：
{search_result_content}
"""
```

**阶段3：搜索竞品数据源**

对每个竞品，自动搜索以下类型的链接：

```python
data_source_templates = {
    "官网": [
        "{competitor_name} 官网",
        "{competitor_name} official website"
    ],
    "产品介绍": [
        "{competitor_name} features",
        "{competitor_name} 功能介绍"
    ],
    "定价": [
        "{competitor_name} pricing",
        "{competitor_name} 价格"
    ],
    "用户评价": [
        "{competitor_name} 评价 site:xiaohongshu.com",
        "{competitor_name} 怎么样 site:zhihu.com",
        "{competitor_name} reviews"
    ],
    "电商": [
        "{competitor_name} site:taobao.com",
        "{competitor_name} site:jd.com"
    ],
    "社交媒体": [
        "{competitor_name} site:weixin.qq.com",
        "{competitor_name} 公众号"
    ]
}
```

**策略二：垂直平台搜索API（补充方式）**

**小红书搜索**：
```python
# 使用小红书搜索页面
url = f"https://www.xiaohongshu.com/search_result?keyword={competitor_name}"
# 提取笔记链接（前10-20篇）
```

**知乎搜索**：
```python
# 使用知乎搜索API（非官方）
url = f"https://www.zhihu.com/api/v4/search_v3?q={competitor_name}&t=content"
# 提取高赞回答和文章
```

**电商平台搜索**：
```python
# 淘宝商品搜索
# 京东商品搜索
# 拼多多商品搜索
# 提取销量靠前的商品详情页
```

**公众号搜索**（搜狗微信搜索）：
```python
url = f"https://weixin.sogou.com/weixin?type=2&query={competitor_name}"
# 提取相关公众号和文章
```

---

#### 3.0.3 链接质量评分与过滤

**评分维度**：

1. **相关性评分（0-1）**
   - 标题匹配度
   - 内容关键词密度
   - 域名可信度

2. **信息价值评分（0-1）**
   - 官方来源：1.0
   - 权威媒体：0.9
   - 用户评价平台：0.8
   - 个人博客：0.6

3. **时效性评分（0-1）**
   - 最近1个月：1.0
   - 最近3个月：0.9
   - 最近1年：0.7
   - 1年以上：0.5

**综合评分公式**：
```python
final_score = (
    relevance * 0.4 +
    value * 0.4 +
    freshness * 0.2
)
```

**过滤规则**：
- 去重（相同域名+路径）
- 屏蔽低质量站点（广告站、采集站）
- 过滤非中文内容（可选）
- 综合评分 < 0.6 的链接

---

#### 3.0.4 自动分类与优先级

**链接自动分类**：

使用规则+LLM混合方式：

**规则匹配**：
```python
url_patterns = {
    "官网首页": [r"^https?://[\w-]+\.(com|cn|io|ai)/?$"],
    "产品功能": [r"/features", r"/product", r"/functions"],
    "定价页面": [r"/pricing", r"/price", r"/plans"],
    "关于我们": [r"/about", r"/company"],
    "帮助文档": [r"/docs", r"/help", r"/support"],
    "博客": [r"/blog", r"/news"],
    "用户评价": [r"xiaohongshu\.com", r"zhihu\.com", r"douban\.com"],
    "电商": [r"taobao\.com", r"jd\.com", r"tmall\.com"],
    "社交媒体": [r"weixin\.qq\.com", r"weibo\.com"]
}
```

**LLM补充分类**（规则无法匹配时）：
```python
prompt = f"""
判断以下URL的内容类型，从以下选项中选择一个：
[官网首页, 产品功能, 定价页面, 用户评价, 电商, 博客文章, 帮助文档, 其他]

URL: {url}
页面标题: {title}

只返回分类名称。
"""
```

**优先级设定**：
```python
priority_map = {
    "官网首页": 1,
    "产品功能": 1,
    "定价页面": 1,
    "用户评价": 2,
    "电商": 2,
    "博客文章": 3,
    "帮助文档": 3,
    "其他": 4
}
```

---

#### 3.0.5 完整工作流程

```
用户输入主题
    ↓
【阶段1：竞品发现】
1. 构造多种搜索查询
2. 调用搜索引擎API
3. 提取搜索结果（标题+摘要+URL）
4. 访问对比类文章，LLM提取竞品列表
5. 竞品去重和置信度评分
    ↓
【阶段2：数据源搜索】
6. 对每个竞品，构造数据源搜索查询
7. 并行搜索多种数据源类型
8. 补充垂直平台搜索
    ↓
【阶段3：链接质量评估】
9. 相关性评分
10. 信息价值评分
11. 时效性评分
12. 综合过滤
    ↓
【阶段4：分类与排序】
13. 自动分类（官网/评价/电商等）
14. 设置优先级
15. 按评分排序
    ↓
【阶段5：用户确认】
16. 展示推荐结果
17. 用户选择/调整
18. 保存为采集配置
    ↓
交给数据采集模块执行
```

---

#### 3.0.6 用户交互界面

**输入表单**：
```
┌─────────────────────────────────────────┐
│  智能数据源发现                          │
├─────────────────────────────────────────┤
│  调研主题: [AI写作助手______________]    │
│  目标市场: [中国 ▼]                      │
│  竞品数量: [3-5个 ▼]                     │
│  数据源类型: ☑ 官网 ☑ 评价 ☑ 电商       │
│  搜索深度: ◉ 快速  ○ 标准  ○ 深度       │
│                                          │
│  [开始搜索]                              │
└─────────────────────────────────────────┘
```

**推荐结果展示**：
```
┌─────────────────────────────────────────────────────┐
│ 找到 5 个竞品，共 42 个数据源                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ✓ Notion AI                          置信度: 95%   │
│   ├─ [官网] https://notion.so              评分:9.2 │
│   ├─ [定价] https://notion.so/pricing      评分:9.0 │
│   ├─ [小红书] 8篇笔记                      评分:8.5 │
│   └─ [知乎] 12篇评测                       评分:8.3 │
│   [ 查看全部 10 个数据源 ▼ ]                        │
│                                                      │
│ ✓ Jasper AI                          置信度: 92%   │
│   ├─ [官网] https://jasper.ai              评分:9.1 │
│   ├─ [定价] https://jasper.ai/pricing     评分:8.9 │
│   └─ ...                                            │
│                                                      │
│ □ ChatGPT                            置信度: 88%   │
│   (已排除：不完全匹配主题)                           │
│                                                      │
├─────────────────────────────────────────────────────┤
│ [调整选择] [保存配置] [直接开始分析]                │
└─────────────────────────────────────────────────────┘
```

---

#### 3.0.7 API设计

**POST /api/discover/search**
```python
# 请求
{
    "topic": "AI写作助手",
    "market": "中国",
    "competitor_count": "3-5",
    "source_types": ["官网", "评价", "电商"],
    "depth": "standard"  # quick/standard/deep
}

# 响应
{
    "task_id": "disc_123456",
    "status": "processing",
    "progress": 0,
    "estimated_time": 60  # 秒
}
```

**GET /api/discover/status/{task_id}**
```python
# 响应
{
    "status": "completed",
    "progress": 100,
    "competitors_found": 5,
    "data_sources_found": 42,
    "result": {
        "competitors": [...],
        "search_metadata": {
            "total_searches": 25,
            "api_calls": 15,
            "time_elapsed": 58
        }
    }
}
```

**POST /api/discover/confirm**
```python
# 用户确认后，保存为采集配置
{
    "task_id": "disc_123456",
    "selected_competitors": ["Notion AI", "Jasper AI"],
    "selected_sources": {
        "Notion AI": ["url1", "url2"],
        "Jasper AI": ["url3", "url4"]
    },
    "save_as_config": True
}

# 响应：生成采集配置ID
{
    "config_id": "cfg_789012",
    "config_path": "/configs/AI写作助手_20260205.yaml"
}
```

---

#### 3.0.8 成本分析

**搜索API成本**（单次发现任务）：

假设：发现5个竞品，每个竞品搜索6种数据源

- **Google Search API**: 15次搜索 × $0 (免费额度内) = $0
- **Bing Search API**: 15次搜索 × $0 (免费额度内) = $0
- **Serper API**: 15次搜索 × $0.002 = $0.03
- **LLM解析**（提取竞品+分类链接）: 约$0.05

**单次成本**: $0.03-0.08
**月度成本**（10次发现任务）: $0.30-0.80

**优化方案**：
- 优先使用免费API（Google/Bing每日免费额度）
- 缓存热门主题的搜索结果（7天）
- 批量LLM调用

---

#### 3.0.9 示例Prompt

**竞品提取Prompt**：
```
你是一位专业的市场研究分析师。请从以下文章中提取所有提到的{topic}相关产品/工具的名称。

文章标题：{title}
文章内容：
{content}

要求：
1. 只提取明确提到的产品名称，不要臆测
2. 排除通用名词（如"AI工具"、"软件"）
3. 每个产品给出置信度评分（0-1）
4. 按照JSON格式输出

输出格式：
{
    "competitors": [
        {"name": "产品名", "confidence": 0.95, "reason": "文中明确提到为AI写作工具"},
        {"name": "产品名2", "confidence": 0.80, "reason": "推测可能相关"}
    ]
}
```

**链接分类Prompt**：
```
判断以下URL和页面标题属于什么类型的内容。

URL: {url}
标题: {title}
摘要: {description}

请从以下类别中选择一个：
- 官网首页：公司/产品官方主页
- 产品功能：功能介绍、特性列表
- 定价页面：价格方案、套餐
- 用户评价：用户评论、使用体验
- 电商页面：淘宝、京东等电商平台
- 博客文章：新闻、博客、教程
- 帮助文档：使用文档、FAQ
- 其他

只返回分类名称，不要解释。
```

---

#### 3.0.10 技术实现要点

**1. 搜索引擎集成**

```python
# 使用 Serper API 示例
import requests

def search_with_serper(query, num=10):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "num": num,
        "gl": "cn",  # 地区
        "hl": "zh-cn"  # 语言
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

**2. 并发搜索**

```python
from concurrent.futures import ThreadPoolExecutor

def discover_competitors(topic, max_workers=5):
    queries = generate_queries(topic)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(search_with_serper, queries)
    
    # 合并结果
    all_results = []
    for result in results:
        all_results.extend(result.get('organic', []))
    
    return all_results
```

**3. LLM提取竞品**

```python
def extract_competitors_with_llm(content, topic):
    prompt = f"""
    从以下内容中提取{topic}的竞品名称...
    {content}
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)
```

**4. 去重与合并**

```python
def deduplicate_competitors(competitors_list):
    # 使用模糊匹配去重（考虑大小写、空格、别名）
    from fuzzywuzzy import fuzz
    
    unique = []
    for comp in competitors_list:
        is_duplicate = False
        for existing in unique:
            similarity = fuzz.ratio(comp['name'].lower(), existing['name'].lower())
            if similarity > 85:  # 相似度阈值
                # 合并置信度
                existing['confidence'] = max(existing['confidence'], comp['confidence'])
                is_duplicate = True
                break
        if not is_duplicate:
            unique.append(comp)
    
    return unique
```

---

### 3.1 数据采集模块

#### 3.1.1 URL采集器（复用已有能力）

**核心功能**：
- 平台自动识别（官网、小红书、知乎、淘宝、京东、微信公众号等）
- 三层策略自动降级采集
- 图片本地化存储
- Markdown格式保存

**输入**：
```python
{
    "urls": [
        "https://example.com/product",
        "https://xiaohongshu.com/xxx",
        "https://mp.weixin.qq.com/s/xxx"
    ],
    "competitor_name": "竞品A",
    "category": "官网/社媒/电商/内容平台"
}
```

**输出**：
```python
{
    "success": True,
    "data": {
        "competitor": "竞品A",
        "source": "官网",
        "raw_content": "content.md",
        "images": ["img_01.jpg", "img_02.jpg"],
        "metadata": {
            "title": "产品介绍",
            "url": "https://example.com/product",
            "crawl_time": "2026-02-05 10:30:00",
            "platform": "官网",
            "content_length": 5000
        }
    }
}
```

#### 3.1.2 批量采集器

**核心功能**：
- 支持竞品配置文件（YAML/JSON）
- 多竞品并行采集
- 失败重试机制
- 采集进度可视化

**配置文件示例**：
```yaml
analysis:
  name: "在线教育产品竞品分析"
  date: "2026-02-05"
  
competitors:
  - name: "竞品A"
    sources:
      - type: "官网"
        urls: 
          - "https://competitor-a.com"
          - "https://competitor-a.com/features"
          - "https://competitor-a.com/pricing"
      - type: "小红书"
        urls:
          - "https://xiaohongshu.com/user/xxx"
        keywords: ["竞品A", "使用体验"]
      - type: "淘宝"
        urls:
          - "https://item.taobao.com/xxx.htm"
        
  - name: "竞品B"
    sources:
      - type: "官网"
        urls: ["https://competitor-b.com"]
      - type: "知乎"
        keywords: ["竞品B评价"]
```

#### 3.1.3 监控采集器

**核心功能**：
- 定时采集（每日/每周）
- 内容变化检测（diff算法）
- 关键指标追踪（价格、功能更新、用户评分）
- 异常预警通知

---

### 3.2 AI解析模块

#### 3.2.1 信息提取器

**核心能力**：利用LLM从原始内容中提取结构化信息

**提取维度**：

**1. 产品基础信息**
```python
{
    "product_name": "产品名称",
    "company": "公司名称",
    "tagline": "产品定位/slogan",
    "target_users": ["目标用户群1", "目标用户群2"],
    "founding_year": "2020",
    "team_size": "50-200人",
    "funding": "B轮"
}
```

**2. 功能特征矩阵**
```python
{
    "core_features": [
        {
            "name": "功能名称",
            "description": "功能描述",
            "category": "基础功能/核心功能/高级功能",
            "unique": True/False  # 是否差异化功能
        }
    ],
    "feature_count": {
        "basic": 10,
        "advanced": 5,
        "unique": 3
    }
}
```

**3. 价格策略**
```python
{
    "pricing_model": "订阅制/买断制/免费+增值",
    "price_tiers": [
        {
            "name": "免费版",
            "price": 0,
            "features": ["功能1", "功能2"],
            "limitations": ["限制用户数", "限制存储"]
        },
        {
            "name": "专业版",
            "price": 99,
            "billing_cycle": "月付/年付",
            "features": ["所有基础功能", "高级功能A"]
        }
    ],
    "trial": {
        "available": True,
        "duration": "14天"
    }
}
```

**4. 用户评价分析**
```python
{
    "sentiment": {
        "positive": 0.65,
        "neutral": 0.25,
        "negative": 0.10
    },
    "rating": 4.5,
    "review_count": 1200,
    "key_praise": ["优点1", "优点2", "优点3"],
    "key_complaints": ["缺点1", "缺点2"],
    "common_keywords": ["易用", "功能强大", "价格贵"]
}
```

**5. 营销策略**
```python
{
    "channels": ["微信公众号", "小红书", "知乎"],
    "content_types": ["教程", "案例", "活动"],
    "posting_frequency": "每周3篇",
    "engagement": {
        "avg_likes": 500,
        "avg_comments": 50
    },
    "key_messages": ["核心卖点1", "核心卖点2"]
}
```

**实现方式**：
- 使用结构化Prompt引导LLM输出JSON
- 多轮对话补充缺失信息
- 置信度评分（高/中/低）

**Prompt模板示例**：
```
你是一位专业的产品分析师。请从以下内容中提取竞品的产品信息。

内容：
{content}

请按照以下JSON格式输出：
{
    "product_name": "...",
    "company": "...",
    "core_features": [...],
    ...
}

注意：
1. 如果信息缺失，字段值设为null
2. 对于不确定的信息，在confidence字段标注"低"
3. 提取时保持客观，避免主观评价
```

#### 3.2.2 对比分析器

**核心能力**：多竞品横向对比

**对比维度**：

**1. 功能对比矩阵**
```
| 功能模块      | 我方产品 | 竞品A | 竞品B | 竞品C |
|--------------|---------|-------|-------|-------|
| 基础功能1     | ✅ 完善 | ✅ 完善 | ✅ 基础 | ❌    |
| 高级功能2     | ✅ 独有 | ❌    | ✅ 基础 | ✅ 完善 |
| 差异化功能3   | ✅      | ❌    | ❌    | ❌    |
```

**2. 价格竞争力分析**
```python
{
    "price_positioning": {
        "our_product": {"min": 0, "max": 299, "avg": 149},
        "competitor_a": {"min": 0, "max": 399, "avg": 199},
        "competitor_b": {"min": 99, "max": 499, "avg": 299}
    },
    "value_score": {  # 性价比评分
        "our_product": 8.5,
        "competitor_a": 7.8,
        "competitor_b": 7.2
    }
}
```

**3. 用户口碑对比**
```python
{
    "rating_comparison": {
        "our_product": 4.6,
        "competitor_a": 4.5,
        "competitor_b": 4.2
    },
    "satisfaction_dimensions": {
        "易用性": {"我方": 4.7, "竞品A": 4.5, "竞品B": 4.0},
        "功能性": {"我方": 4.5, "竞品A": 4.6, "竞品B": 4.5},
        "性价比": {"我方": 4.6, "竞品A": 4.3, "竞品B": 3.8}
    }
}
```

#### 3.2.3 SWOT分析器

**核心能力**：针对每个竞品生成SWOT分析

**输出结构**：
```python
{
    "competitor": "竞品A",
    "swot": {
        "strengths": [
            {
                "point": "品牌知名度高",
                "evidence": "市场占有率30%，行业第一",
                "impact": "高"
            },
            {
                "point": "功能完善",
                "evidence": "支持50+种集成",
                "impact": "中"
            }
        ],
        "weaknesses": [
            {
                "point": "价格偏高",
                "evidence": "比行业平均高40%",
                "impact": "高"
            }
        ],
        "opportunities": [
            {
                "point": "市场增长快",
                "context": "行业年增长率25%",
                "action": "建议加大市场投入"
            }
        ],
        "threats": [
            {
                "point": "新兴竞品进入",
                "context": "3家创业公司获得融资",
                "action": "关注技术创新趋势"
            }
        ]
    },
    "overall_assessment": "竞品A处于市场领先地位，但价格策略可能成为突破口",
    "strategic_suggestions": [
        "建议1：差异化定价策略",
        "建议2：强化性价比宣传"
    ]
}
```

---

### 3.3 报告生成模块

#### 3.3.1 报告模板

**标准竞品分析报告结构**：

```markdown
# 竞品分析报告

**分析时间**: 2026-02-05
**分析人**: 自动生成
**竞品数量**: 3个

---

## 一、执行摘要

- 市场概况：...
- 主要发现：...
- 核心建议：...

---

## 二、竞品概览

### 2.1 竞品基本信息

| 竞品 | 公司 | 产品定位 | 目标用户 | 发展阶段 |
|------|------|---------|---------|---------|
| 竞品A | ... | ... | ... | ... |
| 竞品B | ... | ... | ... | ... |

### 2.2 市场定位图

[定位矩阵图：价格-功能维度]

---

## 三、功能对比分析

### 3.1 功能对比矩阵

[详细功能对比表]

### 3.2 功能差异分析

- **我方优势功能**: ...
- **竞品独有功能**: ...
- **功能空白区**: ...

---

## 四、价格策略分析

### 4.1 价格体系对比

[价格对比表]

### 4.2 性价比分析

[图表：价格-价值散点图]

---

## 五、用户口碑分析

### 5.1 用户满意度

[评分对比图]

### 5.2 用户评价关键词

[词云图]

### 5.3 优缺点总结

**优点TOP3**: ...
**痛点TOP3**: ...

---

## 六、营销策略分析

### 6.1 内容营销

- 渠道布局：...
- 内容策略：...
- 投放频率：...

### 6.2 获客策略

- 免费试用：...
- 推荐奖励：...
- 合作伙伴：...

---

## 七、SWOT分析

### 7.1 竞品A SWOT

[详细SWOT]

### 7.2 竞品B SWOT

[详细SWOT]

---

## 八、竞争态势总结

### 8.1 威胁等级评估

| 竞品 | 威胁等级 | 理由 |
|------|---------|------|
| 竞品A | 高 | ... |
| 竞品B | 中 | ... |

### 8.2 竞争格局预测

...

---

## 九、战略建议

### 9.1 产品策略

1. ...
2. ...

### 9.2 定价策略

1. ...
2. ...

### 9.3 营销策略

1. ...
2. ...

---

## 附录

- 数据来源
- 采集时间
- 原始数据链接
```

#### 3.3.2 多格式导出

支持格式：
- **Markdown** - 默认格式，便于版本控制
- **PDF** - 正式报告分享
- **Excel** - 数据表格导出
- **HTML** - 在线查看
- **PPT** - 汇报演示（Markdown转PPT）

---

### 3.4 监控预警模块

#### 3.4.1 定时监控

**监控维度**：
- 价格变动（涨价/降价/促销）
- 功能更新（新功能上线/功能下线）
- 用户评分变化（评分上升/下降）
- 内容发布（新文章/新视频/新活动）
- 市场动态（融资/收购/重大新闻）

**监控频率**：
- 高优先级：每日监控
- 中优先级：每周监控
- 低优先级：每月监控

#### 3.4.2 变化检测

**检测算法**：
- 文本diff：检测内容变化
- 价格跟踪：记录历史价格曲线
- 评分监控：追踪评分趋势
- 关键词变化：识别新增/删除的关键卖点

**变化日志**：
```python
{
    "competitor": "竞品A",
    "change_type": "价格调整",
    "change_date": "2026-02-05",
    "before": "专业版 ¥199/月",
    "after": "专业版 ¥149/月（限时优惠）",
    "impact": "高",
    "suggestion": "建议关注竞品降价策略，评估是否跟进"
}
```

#### 3.4.3 预警通知

**通知渠道**：
- 邮件通知
- 企业微信/钉钉机器人
- Slack/Discord
- 站内消息

**预警规则**：
```yaml
alerts:
  - name: "价格战预警"
    condition: "竞品降价幅度 > 20%"
    severity: "高"
    notify: ["email", "wechat"]
    
  - name: "重大功能更新"
    condition: "新增核心功能"
    severity: "中"
    notify: ["email"]
    
  - name: "口碑危机"
    condition: "评分下降 > 0.5分"
    severity: "高"
    notify: ["email", "wechat"]
```

---

## 4. 数据流设计

### 4.1 完整分析流程（含智能发现）

**方式一：智能发现模式（推荐）**

```
用户输入调研主题
    ↓
【数据源发现阶段】
1. 构造搜索查询（竞品发现）
2. 调用搜索引擎API（Google/Bing/Serper）
3. 提取搜索结果，访问对比类文章
4. LLM提取竞品列表（去重+置信度评分）
    ↓
5. 对每个竞品搜索数据源
   - 官网（首页、功能、定价）
   - 用户评价（小红书、知乎）
   - 电商（淘宝、京东）
   - 社交媒体（公众号、微博）
6. 链接质量评分与过滤
7. 自动分类与优先级排序
    ↓
8. 展示推荐结果供用户确认
9. 生成采集配置文件
    ↓
【数据采集阶段】
10. 解析竞品列表和数据源
11. 批量采集多个URL（并行）
12. 保存原始内容（Markdown + 图片）
    ↓
【数据清洗阶段】
13. 去除噪音（广告、导航等）
14. 内容分类（产品介绍/评价/价格）
    ↓
【AI解析阶段】
15. 信息提取（结构化字段）
16. 对比分析（多竞品横向）
17. SWOT生成
    ↓
【报告生成阶段】
18. 填充报告模板
19. 生成图表（功能矩阵、价格对比等）
20. 导出多格式报告
    ↓
【结果输出】
- 完整分析报告
- 数据看板
- 历史对比
```

**方式二：手动配置模式（传统）**

```
用户输入竞品配置文件
    ↓
【数据采集阶段】
1. 解析竞品列表和数据源
2. 批量采集多个URL（并行）
3. 保存原始内容（Markdown + 图片）
    ↓
【后续流程同上】
...
```

### 4.2 监控流程

```
定时任务触发
    ↓
1. 读取监控配置
2. 采集最新数据
3. 与历史数据对比
    ↓
【发现变化】
4. 记录变化日志
5. 评估影响等级
6. 触发预警通知
    ↓
【无变化】
7. 更新检查时间
8. 进入下次等待
```

---

## 5. 数据库设计

### 5.1 核心数据表

**发现任务表 (discovery_tasks)** ✨NEW
```sql
CREATE TABLE discovery_tasks (
    id INTEGER PRIMARY KEY,
    topic TEXT NOT NULL,
    market TEXT,
    target_count INTEGER,
    search_depth TEXT,  -- quick/standard/deep
    status TEXT DEFAULT 'pending',  -- pending/processing/completed/failed
    progress INTEGER DEFAULT 0,
    competitors_found INTEGER DEFAULT 0,
    sources_found INTEGER DEFAULT 0,
    result_data JSON,  -- 发现结果
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

**搜索缓存表 (search_cache)** ✨NEW
```sql
CREATE TABLE search_cache (
    id INTEGER PRIMARY KEY,
    query TEXT NOT NULL UNIQUE,
    search_engine TEXT,  -- google/bing/serper
    results JSON,
    cached_at TIMESTAMP,
    expires_at TIMESTAMP,
    hit_count INTEGER DEFAULT 0
);
CREATE INDEX idx_search_query ON search_cache(query);
CREATE INDEX idx_search_expires ON search_cache(expires_at);
```

**竞品表 (competitors)**
```sql
CREATE TABLE competitors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    company TEXT,
    website TEXT,
    category TEXT,
    discovery_task_id INTEGER,  -- 来自哪个发现任务
    confidence REAL,  -- 置信度评分
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (discovery_task_id) REFERENCES discovery_tasks(id)
);
```

**数据源表 (data_sources)**
```sql
CREATE TABLE data_sources (
    id INTEGER PRIMARY KEY,
    competitor_id INTEGER,
    source_type TEXT,  -- 官网/小红书/淘宝等
    url TEXT,
    priority INTEGER,  -- 优先级
    quality_score REAL,  -- 质量评分
    auto_discovered BOOLEAN DEFAULT FALSE,  -- 是否自动发现
    status TEXT DEFAULT 'active',
    last_crawl_time TIMESTAMP,
    FOREIGN KEY (competitor_id) REFERENCES competitors(id)
);
```

**原始内容表 (raw_contents)**
```sql
CREATE TABLE raw_contents (
    id INTEGER PRIMARY KEY,
    source_id INTEGER,
    content_path TEXT,  -- Markdown文件路径
    content_hash TEXT,  -- 内容哈希，用于检测变化
    crawl_time TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (source_id) REFERENCES data_sources(id)
);
```

**解析结果表 (parsed_data)**
```sql
CREATE TABLE parsed_data (
    id INTEGER PRIMARY KEY,
    raw_content_id INTEGER,
    data_type TEXT,  -- product_info/features/pricing/reviews
    extracted_data JSON,
    confidence REAL,
    parsed_at TIMESTAMP,
    FOREIGN KEY (raw_content_id) REFERENCES raw_contents(id)
);
```

**分析报告表 (analysis_reports)**
```sql
CREATE TABLE analysis_reports (
    id INTEGER PRIMARY KEY,
    report_name TEXT,
    report_type TEXT,  -- full/feature_compare/price_compare
    competitors JSON,  -- 包含的竞品列表
    report_path TEXT,
    created_at TIMESTAMP
);
```

**变化日志表 (change_logs)**
```sql
CREATE TABLE change_logs (
    id INTEGER PRIMARY KEY,
    competitor_id INTEGER,
    change_type TEXT,
    field_name TEXT,
    old_value TEXT,
    new_value TEXT,
    impact_level TEXT,  -- 高/中/低
    detected_at TIMESTAMP,
    notified BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (competitor_id) REFERENCES competitors(id)
);
```

---

## 6. API设计

### 6.1 核心API接口

#### 6.1.1 采集相关

**POST /api/crawl/single**
- 功能：采集单个URL
- 参数：`{"url": "...", "competitor": "...", "source_type": "..."}`
- 返回：采集结果和保存路径

**POST /api/crawl/batch**
- 功能：批量采集
- 参数：竞品配置文件
- 返回：任务ID和进度查询接口

**GET /api/crawl/status/{task_id}**
- 功能：查询采集进度
- 返回：完成数量、失败数量、当前状态

#### 6.1.2 分析相关

**POST /api/analyze/extract**
- 功能：从原始内容提取信息
- 参数：`{"content_id": 123, "extract_fields": ["features", "pricing"]}`
- 返回：结构化数据

**POST /api/analyze/compare**
- 功能：多竞品对比
- 参数：`{"competitor_ids": [1,2,3], "dimensions": ["features", "pricing"]}`
- 返回：对比矩阵

**POST /api/analyze/swot**
- 功能：生成SWOT分析
- 参数：`{"competitor_id": 1}`
- 返回：SWOT结构化数据

#### 6.1.3 报告相关

**POST /api/report/generate**
- 功能：生成完整报告
- 参数：`{"competitor_ids": [1,2,3], "template": "standard", "format": "markdown"}`
- 返回：报告ID和下载链接

**GET /api/report/{report_id}**
- 功能：查看报告
- 返回：报告内容

**GET /api/report/export/{report_id}?format=pdf**
- 功能：导出报告
- 返回：文件下载

#### 6.1.4 监控相关

**POST /api/monitor/create**
- 功能：创建监控任务
- 参数：监控配置（竞品、频率、预警规则）
- 返回：监控任务ID

**GET /api/monitor/changes**
- 功能：查询变化日志
- 参数：`{"competitor_id": 1, "days": 7}`
- 返回：变化列表

**GET /api/monitor/dashboard**
- 功能：监控面板数据
- 返回：所有监控任务状态、最新变化

---

## 7. 实施计划

### 7.1 开发阶段

**Phase 1: MVP核心功能（2周）**
- [x] 复用现有URL采集能力
- [ ] **智能数据源发现模块（NEW）**
  - [ ] 搜索引擎API集成
  - [ ] LLM竞品提取
  - [ ] 链接质量评分
- [ ] 实现批量采集配置
- [ ] 集成LLM进行基础信息提取
- [ ] 实现简单的对比分析
- [ ] 生成Markdown报告

**Phase 2: 增强分析能力（2周）**
- [ ] 完善信息提取维度（功能/价格/评价）
- [ ] 实现SWOT自动生成
- [ ] 添加功能对比矩阵
- [ ] 用户口碑情感分析
- [ ] 图表可视化

**Phase 3: 监控与自动化（1周）**
- [ ] 定时监控调度
- [ ] 变化检测算法
- [ ] 预警通知系统
- [ ] 历史数据对比

**Phase 4: 产品化（1周）**
- [ ] Web界面（Streamlit）
- [ ] 配置管理界面
- [ ] 报告管理和导出
- [ ] 监控面板

### 7.2 技术验证

**已验证**：
- ✅ URL采集三层策略（Firecrawl + Jina + Playwright）
- ✅ 图片本地化保存
- ✅ Markdown格式输出

**待验证**：
- **搜索API覆盖率**（能否找到足够的竞品和数据源）
- **LLM竞品识别准确率**（去重和置信度评分效果）
- LLM结构化提取准确率
- 批量采集性能（10+竞品并行）
- 变化检测算法效果
- 成本控制（API调用费用）

---

## 8. 成本分析

### 8.1 API成本

**数据源发现成本（NEW）**：
- Google Search API: 100次/天免费，超出$5/1000次
- Bing Search API: 1000次/月免费，超出$3/1000次
- Serper API: 2500次免费，超出$5/1000次
- LLM竞品提取：约$0.02-0.05/次

**数据采集成本**：
- Firecrawl: 免费500页/月（超出后约$0.02/页）
- Jina: 完全免费
- Playwright: 免费（本地运行）

**AI分析成本**（以GPT-4为例）：
- 信息提取：约$0.01-0.03/竞品/维度
- SWOT生成：约$0.05/竞品
- 报告生成：约$0.10/报告

**单次完整分析成本估算**（智能发现模式，3个竞品）：
- **数据源发现**：$0.03-0.08（搜索+LLM提取）
- 采集：$0-0.06（取决于页面数）
- 分析：约$0.50
- **总计：约$0.55-0.65**

**单次完整分析成本估算**（手动配置模式，3个竞品）：
- 采集：$0-0.06（取决于页面数）
- 分析：约$0.50
- **总计：约$0.50-0.56**

**月度成本估算**（智能发现10个竞品 + 监控）：
- 数据源发现：$0.30-0.80/月（10次发现任务）
- 每周采集更新：$2-4/月
- 月度深度分析：$5-10/月
- **总计：约$7.30-14.80/月**

### 8.2 成本优化方案

1. **优先使用免费方案**：
   - 搜索：优先Google/Bing免费额度
   - 采集：Jina优先，Firecrawl作为备选
2. **搜索缓存策略**：热门主题缓存7天，避免重复搜索
3. **内容缓存策略**：相同内容避免重复分析
4. **增量更新**：只分析变化部分
5. **本地LLM**：低价值分析用本地模型（DeepSeek/Llama）
6. **批量处理**：合并API调用，减少请求次数

---

## 9. 风险与应对

### 9.1 技术风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| 搜索API限额不足 | 中 | 中 | 多API轮换，搜索结果缓存 |
| LLM竞品识别错误 | 中 | 中 | 用户确认环节，置信度评分 |
| 反爬虫限制 | 高 | 中 | 三层策略降级，增加代理池 |
| LLM提取不准确 | 中 | 中 | 人工校验+反馈优化Prompt |
| 成本超预算 | 低 | 低 | 使用免费方案+本地模型+缓存 |
| 数据存储增长快 | 低 | 低 | 定期清理+压缩存储 |

### 9.2 合规风险

- **数据抓取合规**：遵守robots.txt，尊重网站ToS
- **隐私保护**：只采集公开信息，不收集用户隐私
- **商业使用**：仅用于内部分析，不公开传播竞品数据

---

## 10. 未来规划

### 10.1 短期优化（3个月内）

- [ ] **优化智能发现**：支持更多搜索引擎、提升准确率
- [ ] 支持更多平台（LinkedIn、Twitter、GitHub等）
- [ ] AI分析模型微调（提升准确率）
- [ ] 增加预测功能（价格趋势预测、功能路线图推测）
- [ ] 团队协作功能（多人标注、评论）

### 10.2 中期扩展（6个月内）

- [ ] 行业知识库（行业报告、趋势分析）
- [ ] 自动化推荐（基于分析结果推荐策略）
- [ ] 数据API开放（供其他系统调用）
- [ ] 移动端支持

### 10.3 长期愿景

- [ ] 竞品情报社区（用户分享分析报告）
- [ ] 多行业覆盖（SaaS、电商、教育、金融等）
- [ ] 实时预警（分钟级监控）
- [ ] AI策略顾问（自动生成应对策略）

---

## 11. 总结

### 11.1 核心优势

1. **零配置启动**：输入主题即可自动发现竞品和数据源（NEW）
2. **复用已有能力**：基于成熟的URL采集技术，快速启动
3. **全自动化流程**：从竞品发现到报告生成，最小化人工介入
4. **低成本方案**：优先免费工具，月度成本<$15
5. **实时监控能力**：持续追踪竞品动态，及时预警
6. **AI赋能分析**：深度洞察，超越人工分析效率

### 11.2 关键指标

- **效率提升**：从3-5天缩短至30分钟（含竞品发现）
- **覆盖广度**：支持10+平台数据源
- **自动化程度**：智能发现竞品准确率>80%
- **分析深度**：8大维度结构化分析
- **更新频率**：支持每日监控
- **成本控制**：月度<$15（含发现+监控10竞品）

### 11.3 成功标准

- MVP版本2周内上线（含智能发现模块）
- 竞品发现准确率>80%
- 单次分析准确率>85%
- 用户满意度>4.0/5.0
- 月度使用成本<$20
- 覆盖3+主流行业场景
- 月度使用成本<$20
- 覆盖3+主流行业场景

---

## 附录A：智能发现功能使用示例

### 示例1：AI写作助手竞品分析

**用户输入**：
```python
{
    "topic": "AI写作助手",
    "market": "中国",
    "competitor_count": "3-5",
    "source_types": ["官网", "评价", "电商"],
    "depth": "standard"
}
```

**系统自动执行**：

1. **竞品发现阶段**（约20秒）
   - 搜索查询："AI写作助手 竞品"、"AI写作助手 对比"、"best AI writing assistant"
   - 找到对比文章：《2026年最佳AI写作工具推荐》
   - LLM提取竞品：Notion AI、Jasper、Copy.ai、讯飞星火、秘塔写作猫

2. **数据源搜索阶段**（约30秒）
   - 对每个竞品并行搜索：
     - 官网首页、功能页、定价页
     - 小红书评价（前10篇）
     - 知乎讨论（前5篇）
     - 淘宝/京东商品页

3. **质量评分与排序**（约5秒）
   - 链接去重、评分、分类
   - 按优先级排序

**系统输出**（约55秒完成）：
```
找到 5 个竞品，共 48 个高质量数据源

✓ Notion AI (置信度: 95%)
  - [官网] https://notion.so (评分: 9.2)
  - [功能] https://notion.so/product/ai (评分: 9.0)
  - [定价] https://notion.so/pricing (评分: 9.0)
  - [小红书] 12篇笔记 (评分: 8.5)
  - [知乎] 8篇评测 (评分: 8.3)

✓ Jasper AI (置信度: 92%)
  - [官网] https://jasper.ai (评分: 9.1)
  - ...

✓ 讯飞星火 (置信度: 88%)
  - ...

[用户确认] → [开始采集分析] → [30分钟后得到完整报告]
```

### 示例2：在线协作工具竞品监控

**场景**：已经通过智能发现建立了竞品库，现在设置持续监控

**配置**：
```yaml
monitor:
  competitors: ["Notion", "飞书", "语雀"]
  frequency: "daily"
  alert_on:
    - price_change: ">10%"
    - new_feature: true
    - rating_change: ">0.3"
```

**自动运行**：
- 每天早上9点自动采集最新数据
- 对比昨日数据，检测变化
- 发现重要变化自动发送通知

**预警示例**：
```
🚨 竞品动态预警

竞品：Notion
变化类型：价格调整
时间：2026-02-05 09:15

详情：
- 专业版价格从 $10/月 降至 $8/月 (-20%)
- 企业版保持不变
- 影响评估：高

建议：关注竞品降价策略，评估是否跟进
```

---

## 附录B：API调用示例代码

### Python SDK 使用示例

```python
from competitive_analyzer import CompetitorAnalyzer

# 初始化
analyzer = CompetitorAnalyzer(
    firecrawl_key="your_key",
    serper_key="your_key",
    openai_key="your_key"
)

# 方式1：智能发现模式
result = analyzer.discover_and_analyze(
    topic="AI写作助手",
    market="中国",
    auto_start=True  # 自动开始分析
)

print(f"找到 {len(result.competitors)} 个竞品")
print(f"报告已生成: {result.report_path}")

# 方式2：手动配置模式
result = analyzer.analyze_from_config(
    config_file="competitors.yaml"
)

# 方式3：监控模式
analyzer.create_monitor(
    competitors=["Notion", "飞书"],
    frequency="daily",
    alert_webhook="https://your-webhook.com"
)
```

---

**文档版本**: v1.1 (新增智能发现模块)  
**最后更新**: 2026-02-05  
**作者**: AI设计  
**状态**: 待评审
