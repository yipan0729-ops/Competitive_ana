# 自动化竞品分析工具

基于设计文档实现的智能竞品分析工具，支持从主题自动发现竞品、爬取数据、AI分析并生成报告。

## 功能特点

✅ **智能数据源发现**: 输入主题自动搜索竞品和数据源  
✅ **三层爬取策略**: Firecrawl → Jina → Playwright 自动降级  
✅ **AI信息提取**: 自动提取产品信息、功能、价格、评价  
✅ **SWOT分析**: 自动生成竞品SWOT分析  
✅ **Markdown报告**: 自动生成完整分析报告  

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env`，填写必要的 API Key：

```bash
cp .env.example .env
```

必需配置：
- `OPENAI_API_KEY`: OpenAI API Key（必需）
- `SERPER_API_KEY`: Serper 搜索 API（推荐）或 Google Search API

可选配置：
- `FIRECRAWL_API_KEY`: Firecrawl API（提升爬取成功率）
- `GOOGLE_SEARCH_API_KEY`: Google Custom Search API
- `GOOGLE_SEARCH_ENGINE_ID`: Google 搜索引擎 ID

### 3. 初始化数据库

```bash
python main.py init-db
```

### 4. 开始分析

```bash
# 智能发现模式（推荐）
python main.py analyze "AI写作助手" --market 中国 --count 3

# 只发现不爬取（查看推荐的竞品和数据源）
python main.py analyze "在线协作工具" --no-crawl
```

## 使用示例

### 示例1：分析AI写作助手

```bash
python main.py analyze "AI写作助手" --count 3 --depth standard
```

输出：
- 自动发现 3 个竞品（如 Notion AI, Jasper, 讯飞星火）
- 爬取官网、评价等数据源
- 提取产品信息、功能、价格
- 生成 SWOT 分析
- 输出 Markdown 报告到 `reports/` 目录

### 示例2：深度分析

```bash
python main.py analyze "项目管理工具" --count 5 --depth deep --market 全球
```

## 项目结构

```
Competitive_ana/
├── src/
│   ├── config.py              # 配置管理
│   ├── database/              # 数据库模型
│   ├── discovery/             # 智能发现模块
│   │   ├── search_engine.py   # 搜索引擎集成
│   │   └── discoverer.py      # 竞品发现器
│   ├── crawler/               # 数据采集模块
│   │   └── url_crawler.py     # URL爬虫
│   ├── analysis/              # 分析模块
│   │   └── extractor.py       # 信息提取器
│   └── core/                  # 核心模块
│       └── analyzer.py        # 主分析器
├── data/                      # 原始数据
├── reports/                   # 分析报告
├── main.py                    # 命令行入口
└── requirements.txt           # 依赖列表
```

## 成本估算

基于免费 API 额度：
- **Serper API**: 2500次免费搜索
- **Jina Reader**: 完全免费
- **OpenAI GPT-4**: 按使用量付费

单次完整分析（3个竞品）：
- 搜索成本: $0.03-0.08
- 采集成本: $0（使用Jina）- $0.06（使用Firecrawl）
- 分析成本: $0.50
- **总计**: $0.55-0.65

## 技术栈

- **搜索**: Serper API / Google Search API
- **爬取**: Firecrawl / Jina Reader / Playwright
- **AI**: OpenAI GPT-4
- **数据库**: SQLite
- **语言**: Python 3.10+

## 常见问题

### Q: 必须配置哪些 API Key？
A: 最少需要 `OPENAI_API_KEY`（AI分析）和 `SERPER_API_KEY`（搜索）。

### Q: 如何提高爬取成功率？
A: 配置 `FIRECRAWL_API_KEY`，Firecrawl 能处理 JavaScript 渲染和反爬机制。

### Q: 搜索结果不准确怎么办？
A: 可以调整搜索深度参数 `--depth deep` 或者使用手动配置模式。

### Q: 支持哪些平台？
A: 官网、小红书、知乎、淘宝、京东、微信公众号、B站等10+平台。

## 开发计划

- [x] MVP核心功能
  - [x] 智能数据源发现
  - [x] 三层爬取策略
  - [x] AI信息提取
  - [x] SWOT生成
  - [x] Markdown报告
- [ ] 增强功能
  - [ ] 功能对比矩阵
  - [ ] 用户口碑分析
  - [ ] 价格对比可视化
- [ ] 监控功能
  - [ ] 定时监控
  - [ ] 变化检测
  - [ ] 预警通知
- [ ] Web界面
  - [ ] Streamlit UI
  - [ ] 报告管理
  - [ ] 可视化图表

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- 设计文档: `Design.md`
- 源代码参考: `source.md`
