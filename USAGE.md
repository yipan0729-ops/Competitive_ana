# 使用指南

## 目录
1. [环境准备](#环境准备)
2. [API配置](#api配置)
3. [快速开始](#快速开始)
4. [详细使用](#详细使用)
5. [故障排查](#故障排查)

---

## 环境准备

### 1. Python 环境

确保安装 Python 3.10 或更高版本：

```bash
python --version  # 应该显示 3.10 或更高
```

### 2. 安装依赖

```bash
# 进入项目目录
cd D:\Code\Competitive_ana

# 安装依赖
pip install -r requirements.txt

# 可选：安装 Playwright 浏览器（用于需要登录的场景）
playwright install chromium
```

---

## API配置

### 1. 创建配置文件

```bash
# 复制示例配置
copy .env.example .env

# 或者 Linux/Mac
cp .env.example .env
```

### 2. 必需的 API Key

编辑 `.env` 文件，填写以下 **必需** 的 API Key：

#### OpenAI API Key（必需）
用于 AI 信息提取和分析

```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

获取方式：https://platform.openai.com/api-keys

#### Serper API Key（推荐）
用于搜索竞品

```bash
SERPER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

获取方式：
1. 访问 https://serper.dev
2. 注册账号
3. 获取 API Key（有 2500 次免费额度）

### 3. 可选的 API Key

#### Firecrawl API Key（提升爬取成功率）

```bash
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

获取方式：https://firecrawl.dev

#### Google Search API（备选搜索引擎）

```bash
GOOGLE_SEARCH_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_SEARCH_ENGINE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

获取方式：
1. 访问 https://console.cloud.google.com
2. 启用 Custom Search API
3. 创建搜索引擎：https://programmablesearchengine.google.com

---

## 快速开始

### 1. 初始化数据库

```bash
python main.py init-db
```

输出示例：
```
✅ 数据库初始化完成
```

### 2. 第一次分析

```bash
python main.py analyze "AI写作助手" --count 2 --depth quick
```

这将：
- 自动搜索 AI写作助手 相关的竞品
- 发现 2 个竞品
- 爬取官网、评价等数据源
- 提取产品信息、功能、价格
- 生成 SWOT 分析
- 输出 Markdown 报告

### 3. 查看报告

报告会保存在 `reports/` 目录下：

```bash
# 查看最新报告
cd reports
dir /o-d  # Windows
ls -lt    # Linux/Mac
```

打开 `report.md` 查看完整分析报告。

---

## 详细使用

### 命令行参数

#### analyze 命令（智能发现模式）

```bash
python main.py analyze <主题> [选项]
```

**必需参数：**
- `<主题>`: 调研主题，如 "AI写作助手"、"项目管理工具"

**可选参数：**
- `--market <市场>`: 目标市场，默认 "中国"
- `--count <数量>`: 竞品数量，默认 3
- `--depth <深度>`: 搜索深度，可选 quick/standard/deep，默认 standard
- `--no-crawl`: 只发现不爬取，用于查看推荐的竞品

**示例：**

```bash
# 基础分析
python main.py analyze "在线协作工具"

# 深度分析（更多竞品）
python main.py analyze "AI绘画工具" --count 5 --depth deep

# 只发现不爬取（查看推荐）
python main.py analyze "视频编辑软件" --no-crawl

# 全球市场分析
python main.py analyze "CRM系统" --market 全球 --count 5
```

### 工作流程

```
用户输入主题
    ↓
阶段1: 智能数据源发现 (30-60秒)
├─ 搜索竞品相关信息
├─ LLM 提取竞品名称
└─ 为每个竞品搜索数据源
    ↓
阶段2: 数据采集 (1-3分钟)
├─ 爬取官网、评价等页面
├─ 保存 Markdown + 图片
└─ 计算内容哈希
    ↓
阶段3: AI信息提取 (2-5分钟)
├─ 提取产品信息
├─ 提取功能特征
├─ 提取价格策略
└─ 生成 SWOT 分析
    ↓
阶段4: 生成报告 (5-10秒)
├─ 渲染 Markdown 报告
├─ 保存 JSON 数据
└─ 输出报告路径
```

### 输出文件结构

```
reports/
└── AI写作助手_20260205_143025/
    ├── report.md          # Markdown 报告
    ├── data.json          # JSON 原始数据
    └── ...

data/
└── 20260205_143025_Notion_AI/
    ├── content.md         # 爬取内容
    ├── img_01.jpg         # 图片1
    ├── img_02.jpg         # 图片2
    └── ...
```

---

## 进阶使用

### Python API

```python
from src.core.analyzer import CompetitorAnalyzer
from src.database import init_db

# 初始化
init_db()
analyzer = CompetitorAnalyzer()

# 分析
result = analyzer.analyze_from_topic(
    topic="AI写作助手",
    market="中国",
    target_count=3,
    depth="standard",
    auto_crawl=True
)

# 查看结果
print(f"报告: {result['report_path']}")
print(f"竞品: {len(result['competitors'])} 个")
```

### 自定义配置

创建 `custom_config.yaml`:

```yaml
analysis:
  name: "自定义分析"
  date: "2026-02-05"

competitors:
  - name: "竞品A"
    sources:
      - type: "官网"
        urls: ["https://example.com"]
```

使用配置文件（待实现）:
```bash
python main.py analyze-config custom_config.yaml
```

---

## 故障排查

### 1. API Key 错误

**错误信息：**
```
❌ 缺少必要的环境变量: OPENAI_API_KEY
```

**解决方法：**
- 确认 `.env` 文件存在
- 检查 API Key 是否正确填写
- 不要在 API Key 两边加引号

### 2. 搜索失败

**错误信息：**
```
❌ Serper 搜索失败: 401 Unauthorized
```

**解决方法：**
- 检查 `SERPER_API_KEY` 是否正确
- 确认 API 额度是否用完
- 尝试使用 Google Search API（配置 `GOOGLE_SEARCH_API_KEY`）

### 3. 爬取失败

**错误信息：**
```
❌ 所有爬取策略都失败
```

**可能原因：**
- 网站有反爬机制
- 网络连接问题
- 需要登录

**解决方法：**
- 配置 `FIRECRAWL_API_KEY`（更强大的爬取能力）
- 检查网络连接
- 对于需要登录的网站，暂时跳过或使用其他数据源

### 4. LLM 提取失败

**错误信息：**
```
❌ LLM 调用失败: Rate limit exceeded
```

**解决方法：**
- OpenAI API 有速率限制
- 等待几分钟后重试
- 考虑升级 OpenAI 账户

### 5. 依赖安装失败

**错误信息：**
```
ERROR: Could not find a version that satisfies the requirement...
```

**解决方法：**
```bash
# 升级 pip
python -m pip install --upgrade pip

# 重新安装
pip install -r requirements.txt

# 如果还是失败，逐个安装核心依赖
pip install openai requests sqlalchemy
```

---

## 性能优化

### 1. 使用缓存

搜索结果会自动缓存 7 天，避免重复搜索：

```python
# 查看缓存命中
📦 使用缓存结果 (命中次数: 3)
```

### 2. 调整并发数

编辑 `.env`:

```bash
MAX_CONCURRENT_CRAWLS=5  # 同时爬取的URL数量
```

### 3. 降低成本

- 使用 `--depth quick` 快速模式
- 减少竞品数量 `--count 2`
- 使用免费的 Jina Reader（自动降级）

---

## 常见问题 FAQ

### Q: 需要多少钱？

**A:** 基于免费额度：
- Serper: 2500次免费搜索（足够数百次分析）
- Jina: 完全免费
- OpenAI: 按使用量付费

单次完整分析（3个竞品）约 $0.55-0.65

### Q: 分析需要多久？

**A:** 取决于竞品数量和搜索深度：
- Quick 模式：3-5 分钟（2个竞品）
- Standard 模式：5-10 分钟（3个竞品）
- Deep 模式：10-20 分钟（5个竞品）

### Q: 支持哪些语言？

**A:** 
- 界面：中文
- 内容：支持中英文自动识别
- 可通过 `--market` 参数指定目标市场

### Q: 能否分析竞争对手的具体数据？

**A:** 只能获取公开信息：
- 官网内容 ✅
- 公开评价 ✅
- 公开价格 ✅
- 私有数据 ❌
- 内部数据 ❌

### Q: 数据准确吗？

**A:** 
- 数据来源：公开网页，依赖信息质量
- AI提取：约85%准确率
- 建议：结合人工判断

---

## 更新日志

### v0.1.0 (2026-02-05)

✅ **核心功能**
- 智能数据源发现
- 三层爬取策略（Firecrawl/Jina/Playwright）
- AI信息提取（产品信息、功能、价格）
- SWOT自动生成
- Markdown报告生成

🚧 **计划中**
- Web界面
- 监控功能
- 对比矩阵可视化

---

## 支持与反馈

- 📝 问题反馈：在项目中创建 Issue
- 📖 详细文档：查看 `Design.md`
- 💡 功能建议：欢迎提出

---

*最后更新: 2026-02-05*
