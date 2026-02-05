"""
命令行入口
"""
import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.database import init_db
from src.core.analyzer import CompetitorAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="自动化竞品分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 智能发现模式
  python main.py analyze "AI写作助手" --market 中国 --count 3
  
  # 手动配置模式
  python main.py analyze-config competitors.yaml
  
  # 初始化数据库
  python main.py init-db
  
  # 启动 Web 界面
  python main.py web
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析竞品（智能发现模式）")
    analyze_parser.add_argument("topic", help="调研主题，如: AI写作助手")
    analyze_parser.add_argument("--market", default="中国", help="目标市场 (默认: 中国)")
    analyze_parser.add_argument("--count", type=int, default=3, help="竞品数量 (默认: 3)")
    analyze_parser.add_argument("--depth", choices=["quick", "standard", "deep"], default="standard", help="搜索深度 (默认: standard)")
    analyze_parser.add_argument("--no-crawl", action="store_true", help="只发现不爬取")
    
    # analyze-config 命令
    config_parser = subparsers.add_parser("analyze-config", help="分析竞品（配置文件模式）")
    config_parser.add_argument("config_file", help="配置文件路径")
    
    # init-db 命令
    subparsers.add_parser("init-db", help="初始化数据库")
    
    # web 命令
    web_parser = subparsers.add_parser("web", help="启动 Web 界面")
    web_parser.add_argument("--port", type=int, default=8501, help="端口号 (默认: 8501)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 验证配置
    if args.command in ["analyze", "analyze-config", "web"]:
        if not config.validate():
            print("\n请先配置必要的 API Key:")
            print("1. 复制 .env.example 为 .env")
            print("2. 填写相关 API Key")
            sys.exit(1)
    
    # 执行命令
    if args.command == "init-db":
        print("🔧 初始化数据库...")
        init_db()
    
    elif args.command == "analyze":
        print(f"🚀 开始分析: {args.topic}")
        
        analyzer = CompetitorAnalyzer()
        result = analyzer.analyze_from_topic(
            topic=args.topic,
            market=args.market,
            target_count=args.count,
            depth=args.depth,
            auto_crawl=not args.no_crawl
        )
        
        print("\n✅ 分析完成!")
        if result.get("report_path"):
            print(f"📊 报告: {result['report_path']}")
    
    elif args.command == "analyze-config":
        print(f"📄 从配置文件分析: {args.config_file}")
        analyzer = CompetitorAnalyzer()
        result = analyzer.analyze_from_config(args.config_file)
    
    elif args.command == "web":
        print(f"🌐 启动 Web 界面... (端口: {args.port})")
        print("⚠️  Web 界面尚未实现，请使用命令行模式")
        # TODO: 启动 Streamlit


if __name__ == "__main__":
    main()
