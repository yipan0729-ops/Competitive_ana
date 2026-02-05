"""
快速使用示例
"""
from src.core.analyzer import CompetitorAnalyzer
from src.database import init_db

# 初始化数据库
init_db()

# 创建分析器
analyzer = CompetitorAnalyzer()

# 方式1：智能发现模式（推荐）
print("="*60)
print("示例1: 智能发现模式")
print("="*60)

result = analyzer.analyze_from_topic(
    topic="AI写作助手",
    market="中国",
    target_count=3,
    depth="quick",  # 快速模式，节省时间
    auto_crawl=True
)

print(f"\n✅ 分析完成!")
print(f"📊 报告: {result.get('report_path')}")
print(f"📈 竞品数: {len(result.get('competitors', []))}")

# 查看发现的竞品
print("\n发现的竞品:")
for i, comp in enumerate(result.get('competitors', []), 1):
    print(f"{i}. {comp['name']} (置信度: {comp['confidence']*100:.0f}%)")
    print(f"   数据源: {len(comp.get('data_sources', []))} 个")
