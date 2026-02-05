# 项目文件清单

## 📁 完整文件列表

### 根目录
```
Competitive_ana/
├── main.py                      ⭐ 命令行入口
├── test_setup.py                ⭐ 环境检测脚本
├── requirements.txt             ⭐ Python依赖
├── .env.example                 ⭐ 环境变量模板
├── .gitignore                   ⭐ Git忽略配置
│
├── README.md                    📖 项目说明
├── USAGE.md                     📖 详细使用指南
├── PROJECT_SUMMARY.md           📖 项目总结
├── Design.md                    📖 设计文档
├── source.md                    📖 参考文档
└── base.md                      📖 原始素材
```

### src/ 源代码目录
```
src/
├── __init__.py                  # 包初始化
├── config.py                    ⭐ 配置管理
│
├── database/                    # 数据库模块
│   ├── __init__.py
│   └── models.py                ⭐ 数据模型（8个表）
│
├── discovery/                   # 智能发现模块 ✨NEW
│   ├── __init__.py
│   ├── search_engine.py         ⭐ 搜索引擎（Serper/Google）
│   └── discoverer.py            ⭐ 竞品发现器
│
├── crawler/                     # 数据采集模块
│   ├── __init__.py
│   └── url_crawler.py           ⭐ URL爬虫（三层策略）
│
├── analysis/                    # AI分析模块
│   ├── __init__.py
│   └── extractor.py             ⭐ 信息提取 + SWOT
│
└── core/                        # 核心编排
    ├── __init__.py
    └── analyzer.py              ⭐ 主分析器
```

### examples/ 示例目录
```
examples/
├── quick_start.py               ⭐ Python API示例
└── config_example.yaml          ⭐ 配置文件示例
```

### 数据目录（自动创建）
```
data/                            # 爬取的原始数据
reports/                         # 生成的分析报告
cache/                           # 搜索缓存
competitive_analysis.db          # SQLite数据库（自动创建）
```

---

## 📊 文件统计

### 代码文件
| 类型 | 数量 | 说明 |
|------|------|------|
| Python 源码 | 13个 | 核心功能实现 |
| 配置文件 | 4个 | 依赖、环境变量等 |
| 示例代码 | 2个 | 使用示例 |
| **总计** | **19个** | **约2000行代码** |

### 文档文件
| 类型 | 数量 | 说明 |
|------|------|------|
| Markdown | 6个 | 文档和说明 |
| 总字数 | ~30000字 | 详细的文档 |

---

## 🔑 核心模块说明

### 1. 配置管理 (`src/config.py`)
- 环境变量加载
- API Key管理
- 路径配置
- 参数配置
- **行数**: ~100行

### 2. 数据库模型 (`src/database/models.py`)
- 8个数据表定义
- ORM关系映射
- 数据库初始化
- **行数**: ~180行

### 3. 搜索引擎 (`src/discovery/search_engine.py`)
- Serper API集成
- Google Search API集成
- 多引擎降级
- 搜索缓存机制
- **行数**: ~180行

### 4. 竞品发现器 (`src/discovery/discoverer.py`)
- 搜索查询构造
- LLM竞品提取
- 模糊匹配去重
- 数据源搜索
- **行数**: ~280行

### 5. URL爬虫 (`src/crawler/url_crawler.py`)
- 平台识别
- Firecrawl集成
- Jina Reader集成
- 图片下载
- 内容保存
- **行数**: ~280行

### 6. 信息提取器 (`src/analysis/extractor.py`)
- 产品信息提取
- 功能特征提取
- 价格策略提取
- 用户评价提取
- SWOT生成
- **行数**: ~250行

### 7. 主分析器 (`src/core/analyzer.py`)
- 工作流编排
- 阶段管理
- 报告生成
- **行数**: ~240行

### 8. 命令行工具 (`main.py`)
- 参数解析
- 命令路由
- 用户交互
- **行数**: ~100行

---

## 🎯 核心功能对应文件

| 功能 | 对应文件 | 状态 |
|------|---------|------|
| **智能发现** | `src/discovery/discoverer.py` | ✅ 完成 |
| **搜索引擎** | `src/discovery/search_engine.py` | ✅ 完成 |
| **URL爬取** | `src/crawler/url_crawler.py` | ✅ 完成 |
| **信息提取** | `src/analysis/extractor.py` | ✅ 完成 |
| **SWOT分析** | `src/analysis/extractor.py` | ✅ 完成 |
| **报告生成** | `src/core/analyzer.py` | ✅ 完成 |
| **数据存储** | `src/database/models.py` | ✅ 完成 |
| **命令行** | `main.py` | ✅ 完成 |
| **配置管理** | `src/config.py` | ✅ 完成 |

---

## 📦 依赖清单

### 核心依赖（必需）
```txt
openai>=1.10.0              # AI分析（必需）
requests>=2.31.0            # HTTP请求
sqlalchemy>=2.0.23          # 数据库ORM
fuzzywuzzy>=0.18.0          # 模糊匹配
python-Levenshtein>=0.23.0  # 加速fuzzywuzzy
python-dotenv>=1.0.0        # 环境变量
```

### 爬虫依赖
```txt
firecrawl-py>=0.0.16        # Firecrawl API（推荐）
beautifulsoup4>=4.12.0      # HTML解析
lxml>=4.9.3                 # XML解析
httpx>=0.25.0               # 异步HTTP（Serper）
```

### AI依赖
```txt
langchain>=0.1.0            # AI工作流
langchain-openai>=0.0.2     # LangChain + OpenAI
anthropic>=0.8.0            # Claude（可选）
```

### 数据处理
```txt
pandas>=2.1.0               # 数据分析
pillow>=10.1.0              # 图片处理
pyyaml>=6.0.1               # YAML解析
```

### 工具库
```txt
tqdm>=4.66.1                # 进度条
jinja2>=3.1.2               # 模板引擎
```

### Web界面（可选）
```txt
streamlit>=1.29.0           # Web UI
fastapi>=0.108.0            # API框架
uvicorn>=0.25.0             # ASGI服务器
```

### 任务调度（可选）
```txt
apscheduler>=3.10.4         # 定时任务
```

**总计**: ~25个依赖包

---

## 🚀 快速导航

### 想要开始使用？
1. 阅读 `README.md` - 项目概述
2. 阅读 `USAGE.md` - 详细使用指南
3. 运行 `python test_setup.py` - 环境检测
4. 运行 `python main.py analyze "主题"` - 开始分析

### 想要了解设计？
1. 阅读 `Design.md` - 完整设计文档
2. 阅读 `PROJECT_SUMMARY.md` - 实现总结
3. 查看 `src/` 目录 - 源代码实现

### 想要二次开发？
1. 查看 `src/` 目录结构
2. 阅读各模块的 docstring
3. 参考 `examples/quick_start.py`
4. 扩展相应的类和方法

---

## 📝 代码质量

### 代码规范
- ✅ 遵循 PEP 8 规范
- ✅ 详细的 docstring
- ✅ 类型提示（部分）
- ✅ 错误处理
- ✅ 日志输出

### 架构设计
- ✅ 模块化设计
- ✅ 松耦合
- ✅ 单一职责
- ✅ 可扩展性
- ✅ 配置外部化

### 测试覆盖
- ⚠️ 单元测试（待补充）
- ✅ 环境检测脚本
- ✅ 示例代码

---

## 📈 版本历史

### v0.1.0 (2026-02-05) - MVP版本
- ✅ 智能数据源发现
- ✅ 三层爬取策略
- ✅ AI信息提取
- ✅ SWOT自动生成
- ✅ Markdown报告
- ✅ 命令行工具
- ✅ 完整文档

---

## 🎉 项目亮点

1. **零配置启动** - 输入主题即可开始
2. **智能发现** - 自动搜索竞品和数据源
3. **三层降级** - 确保爬取成功率
4. **AI赋能** - 深度分析而非简单采集
5. **成本友好** - 优先免费方案
6. **模块化** - 易于扩展和维护
7. **完整文档** - 6个文档文件，3万字

---

**文件清单版本**: v1.0  
**最后更新**: 2026-02-05
