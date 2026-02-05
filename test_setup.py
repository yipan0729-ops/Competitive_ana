"""
测试脚本 - 验证环境配置
"""
import sys
from pathlib import Path

print("="*60)
print("自动化竞品分析工具 - 环境检测")
print("="*60)

# 1. 检查 Python 版本
print("\n1. Python 版本检测")
print(f"   当前版本: {sys.version}")
if sys.version_info < (3, 10):
    print("   ❌ 需要 Python 3.10 或更高版本")
    sys.exit(1)
else:
    print("   ✅ Python 版本符合要求")

# 2. 检查依赖
print("\n2. 核心依赖检测")

dependencies = {
    "requests": "HTTP 请求",
    "openai": "OpenAI API",
    "sqlalchemy": "数据库",
    "fuzzywuzzy": "模糊匹配",
    "beautifulsoup4": "HTML 解析",
}

missing = []
for package, desc in dependencies.items():
    try:
        __import__(package.replace("-", "_"))
        print(f"   ✅ {package:<20} - {desc}")
    except ImportError:
        print(f"   ❌ {package:<20} - {desc} (缺失)")
        missing.append(package)

if missing:
    print(f"\n   请安装缺失的依赖:")
    print(f"   pip install {' '.join(missing)}")

# 3. 检查配置文件
print("\n3. 配置文件检测")
env_file = Path(".env")
if env_file.exists():
    print("   ✅ .env 文件存在")
    
    # 检查 API Keys
    from src.config import config
    
    print("\n4. API Key 配置检测")
    
    keys = {
        "OPENAI_API_KEY": ("OpenAI API", config.OPENAI_API_KEY, True),
        "SERPER_API_KEY": ("Serper 搜索", config.SERPER_API_KEY, True),
        "FIRECRAWL_API_KEY": ("Firecrawl 爬虫", config.FIRECRAWL_API_KEY, False),
        "GOOGLE_SEARCH_API_KEY": ("Google 搜索", config.GOOGLE_SEARCH_API_KEY, False),
    }
    
    all_required_configured = True
    
    for key_name, (desc, value, required) in keys.items():
        if value and value != f"your_{key_name.lower()}_here":
            status = "✅"
        elif required:
            status = "❌ 必需"
            all_required_configured = False
        else:
            status = "⚠️  可选"
        
        print(f"   {status} {desc:<20} - {key_name}")
    
    if not all_required_configured:
        print("\n   ❌ 缺少必需的 API Key")
        print("   请编辑 .env 文件，填写相关 API Key")
    else:
        print("\n   ✅ 必需的 API Key 已配置")
        
else:
    print("   ❌ .env 文件不存在")
    print("   请复制 .env.example 为 .env 并填写 API Key")

# 5. 检查目录
print("\n5. 目录结构检测")
dirs = ["data", "reports", "cache"]
for dir_name in dirs:
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f"   ✅ {dir_name}/ 目录存在")
    else:
        print(f"   ⚠️  {dir_name}/ 目录不存在（将自动创建）")

# 6. 测试数据库
print("\n6. 数据库检测")
try:
    from src.database import init_db
    init_db()
    print("   ✅ 数据库初始化成功")
except Exception as e:
    print(f"   ❌ 数据库初始化失败: {e}")

# 总结
print("\n" + "="*60)
if missing or not all_required_configured:
    print("❌ 环境配置不完整，请按照提示完成配置")
    print("\n下一步:")
    if missing:
        print("1. 安装缺失的依赖: pip install -r requirements.txt")
    if not all_required_configured:
        print("2. 配置 API Keys: 编辑 .env 文件")
    print("3. 重新运行测试: python test_setup.py")
else:
    print("✅ 环境配置完成！")
    print("\n可以开始使用:")
    print('   python main.py analyze "AI写作助手" --count 2 --depth quick')
print("="*60)
