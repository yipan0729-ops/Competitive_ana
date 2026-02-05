"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """全局配置"""
    
    # 项目路径
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
    REPORTS_DIR = Path(os.getenv("REPORTS_DIR", BASE_DIR / "reports"))
    CACHE_DIR = Path(os.getenv("CACHE_DIR", BASE_DIR / "cache"))
    
    # 确保目录存在
    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
    GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    BING_SEARCH_API_KEY = os.getenv("BING_SEARCH_API_KEY")
    
    # 数据库
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/competitive_analysis.db")
    
    # LLM配置
    DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4-turbo-preview")
    DEFAULT_LLM_TEMPERATURE = float(os.getenv("DEFAULT_LLM_TEMPERATURE", "0.3"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
    
    # 搜索配置
    DEFAULT_SEARCH_ENGINE = os.getenv("DEFAULT_SEARCH_ENGINE", "serper")
    SEARCH_RESULTS_PER_QUERY = int(os.getenv("SEARCH_RESULTS_PER_QUERY", "10"))
    CACHE_EXPIRY_DAYS = int(os.getenv("CACHE_EXPIRY_DAYS", "7"))
    
    # 采集配置
    MAX_CONCURRENT_CRAWLS = int(os.getenv("MAX_CONCURRENT_CRAWLS", "5"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    RETRY_TIMES = int(os.getenv("RETRY_TIMES", "3"))
    
    @classmethod
    def validate(cls) -> bool:
        """验证必要的配置是否存在"""
        required = []
        
        if not cls.OPENAI_API_KEY:
            required.append("OPENAI_API_KEY")
        
        if required:
            print(f"❌ 缺少必要的环境变量: {', '.join(required)}")
            print("请创建 .env 文件并配置相关 API Key")
            return False
        
        return True
    
    @classmethod
    def get_search_api_key(cls, engine: Optional[str] = None) -> Optional[str]:
        """获取搜索引擎API Key"""
        engine = engine or cls.DEFAULT_SEARCH_ENGINE
        
        if engine == "serper":
            return cls.SERPER_API_KEY
        elif engine == "google":
            return cls.GOOGLE_SEARCH_API_KEY
        elif engine == "bing":
            return cls.BING_SEARCH_API_KEY
        
        return None


# 导出配置实例
config = Config()
