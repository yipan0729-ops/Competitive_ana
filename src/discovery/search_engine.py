"""
搜索引擎集成模块
"""
import json
import time
from typing import List, Dict, Optional
import requests
from datetime import datetime, timedelta

from src.config import config
from src.database import SearchCache, SessionLocal


class SearchEngine:
    """搜索引擎基类"""
    
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
    
    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """搜索接口"""
        raise NotImplementedError
    
    def _get_cached_results(self, query: str) -> Optional[List[Dict]]:
        """从缓存获取结果"""
        if not self.use_cache:
            return None
        
        db = SessionLocal()
        try:
            cache = db.query(SearchCache).filter(
                SearchCache.query == query,
                SearchCache.expires_at > datetime.utcnow()
            ).first()
            
            if cache:
                cache.hit_count += 1
                db.commit()
                print(f"  📦 使用缓存结果 (命中次数: {cache.hit_count})")
                return cache.results
        finally:
            db.close()
        
        return None
    
    def _save_to_cache(self, query: str, results: List[Dict], engine: str):
        """保存到缓存"""
        if not self.use_cache:
            return
        
        db = SessionLocal()
        try:
            expires_at = datetime.utcnow() + timedelta(days=config.CACHE_EXPIRY_DAYS)
            
            # 检查是否已存在
            cache = db.query(SearchCache).filter(SearchCache.query == query).first()
            if cache:
                cache.results = results
                cache.cached_at = datetime.utcnow()
                cache.expires_at = expires_at
                cache.search_engine = engine
            else:
                cache = SearchCache(
                    query=query,
                    search_engine=engine,
                    results=results,
                    expires_at=expires_at
                )
                db.add(cache)
            
            db.commit()
        finally:
            db.close()


class SerperSearch(SearchEngine):
    """Serper API 搜索"""
    
    def __init__(self, api_key: Optional[str] = None, use_cache: bool = True):
        super().__init__(use_cache)
        self.api_key = api_key or config.SERPER_API_KEY
        self.base_url = "https://google.serper.dev/search"
    
    def search(self, query: str, num_results: int = 10, gl: str = "cn", hl: str = "zh-cn") -> List[Dict]:
        """
        使用 Serper API 搜索
        
        Args:
            query: 搜索查询
            num_results: 返回结果数量
            gl: 地区代码 (cn=中国)
            hl: 语言代码 (zh-cn=简体中文)
        """
        # 检查缓存
        cached = self._get_cached_results(query)
        if cached:
            return cached[:num_results]
        
        if not self.api_key:
            print("  ⚠️  未配置 SERPER_API_KEY，跳过")
            return []
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": num_results,
            "gl": gl,
            "hl": hl
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            # 提取有机搜索结果
            results = []
            for item in data.get("organic", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "serper"
                })
            
            # 保存到缓存
            self._save_to_cache(query, results, "serper")
            
            return results
        
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Serper 搜索失败: {e}")
            return []


class GoogleSearch(SearchEngine):
    """Google Custom Search API"""
    
    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None, use_cache: bool = True):
        super().__init__(use_cache)
        self.api_key = api_key or config.GOOGLE_SEARCH_API_KEY
        self.search_engine_id = search_engine_id or config.GOOGLE_SEARCH_ENGINE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 10, gl: str = "cn", hl: str = "zh-CN") -> List[Dict]:
        """使用 Google Custom Search API"""
        # 检查缓存
        cached = self._get_cached_results(query)
        if cached:
            return cached[:num_results]
        
        if not self.api_key or not self.search_engine_id:
            print("  ⚠️  未配置 Google Search API，跳过")
            return []
        
        try:
            results = []
            # Google API 一次最多返回10条
            for start in range(1, min(num_results + 1, 100), 10):
                params = {
                    "key": self.api_key,
                    "cx": self.search_engine_id,
                    "q": query,
                    "num": min(10, num_results - len(results)),
                    "start": start,
                    "gl": gl,
                    "hl": hl
                }
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                data = response.json()
                
                for item in data.get("items", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "google"
                    })
                
                if len(results) >= num_results:
                    break
                
                time.sleep(0.5)  # 避免频繁请求
            
            # 保存到缓存
            self._save_to_cache(query, results, "google")
            
            return results[:num_results]
        
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Google 搜索失败: {e}")
            return []


class MultiEngineSearch:
    """多引擎搜索（自动降级）"""
    
    def __init__(self, preferred_engine: str = "serper"):
        self.preferred_engine = preferred_engine
        self.engines = {
            "serper": SerperSearch(),
            "google": GoogleSearch()
        }
    
    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        多引擎搜索，自动降级
        优先使用配置的引擎，失败后尝试其他引擎
        """
        # 尝试首选引擎
        if self.preferred_engine in self.engines:
            results = self.engines[self.preferred_engine].search(query, num_results)
            if results:
                return results
        
        # 降级：尝试其他引擎
        for engine_name, engine in self.engines.items():
            if engine_name == self.preferred_engine:
                continue
            
            print(f"  🔄 降级到 {engine_name}")
            results = engine.search(query, num_results)
            if results:
                return results
        
        return []
    
    def batch_search(self, queries: List[str], num_results: int = 10) -> Dict[str, List[Dict]]:
        """批量搜索"""
        results = {}
        for query in queries:
            print(f"🔍 搜索: {query}")
            results[query] = self.search(query, num_results)
            time.sleep(1)  # 避免频繁请求
        return results
