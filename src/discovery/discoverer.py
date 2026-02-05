"""
竞品发现和提取模块
"""
import json
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from fuzzywuzzy import fuzz
from openai import OpenAI

from src.config import config
from src.database import DiscoveryTask, Competitor, DataSource, SessionLocal
from src.discovery.search_engine import MultiEngineSearch


class CompetitorDiscoverer:
    """竞品发现器"""
    
    def __init__(self, search_engine: Optional[str] = None):
        self.search_engine = MultiEngineSearch(
            preferred_engine=search_engine or config.DEFAULT_SEARCH_ENGINE
        )
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def discover(
        self,
        topic: str,
        market: str = "中国",
        target_count: int = 5,
        depth: str = "standard"
    ) -> Dict:
        """
        发现竞品
        
        Args:
            topic: 调研主题，如 "AI写作助手"
            market: 目标市场
            target_count: 目标竞品数量
            depth: 搜索深度 quick/standard/deep
        
        Returns:
            {
                "competitors": [竞品列表],
                "task_id": 任务ID
            }
        """
        print(f"\n🚀 开始竞品发现: {topic}")
        print(f"📍 目标市场: {market} | 目标数量: {target_count} | 深度: {depth}")
        
        # 创建发现任务
        task = self._create_task(topic, market, target_count, depth)
        
        try:
            # 阶段1：发现竞品
            print("\n" + "="*60)
            print("阶段1: 竞品发现")
            print("="*60)
            competitors = self._discover_competitors(topic, market, target_count, depth)
            task.competitors_found = len(competitors)
            task.progress = 50
            self._update_task(task)
            
            # 阶段2：搜索数据源
            print("\n" + "="*60)
            print("阶段2: 数据源搜索")
            print("="*60)
            for comp in competitors:
                sources = self._discover_data_sources(comp["name"], topic)
                comp["data_sources"] = sources
            
            total_sources = sum(len(c.get("data_sources", [])) for c in competitors)
            task.sources_found = total_sources
            task.progress = 100
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            task.result_data = {"competitors": competitors}
            self._update_task(task)
            
            # 保存竞品到数据库
            self._save_competitors(task.id, competitors)
            
            print("\n" + "="*60)
            print(f"✅ 发现完成!")
            print(f"📊 找到 {len(competitors)} 个竞品，共 {total_sources} 个数据源")
            print("="*60)
            
            return {
                "task_id": task.id,
                "competitors": competitors,
                "total_sources": total_sources
            }
        
        except Exception as e:
            task.status = "failed"
            task.result_data = {"error": str(e)}
            self._update_task(task)
            raise
    
    def _discover_competitors(
        self,
        topic: str,
        market: str,
        target_count: int,
        depth: str
    ) -> List[Dict]:
        """发现竞品名称"""
        # 构造搜索查询
        queries = self._build_discovery_queries(topic, market, depth)
        
        print(f"📝 生成 {len(queries)} 个搜索查询")
        
        # 批量搜索
        search_results = self.search_engine.batch_search(queries, num_results=10)
        
        # 提取竞品
        all_competitors = []
        
        for query, results in search_results.items():
            if not results:
                continue
            
            print(f"\n  分析查询: {query} ({len(results)} 条结果)")
            
            # 从搜索结果中提取竞品
            competitors = self._extract_competitors_from_results(
                topic, results, max_competitors=10
            )
            
            all_competitors.extend(competitors)
        
        # 去重和合并
        unique_competitors = self._deduplicate_competitors(all_competitors)
        
        # 按置信度排序，取前N个
        unique_competitors.sort(key=lambda x: x["confidence"], reverse=True)
        final_competitors = unique_competitors[:target_count]
        
        print(f"\n📊 去重后得到 {len(unique_competitors)} 个竞品")
        print(f"✅ 选择置信度最高的 {len(final_competitors)} 个")
        
        return final_competitors
    
    def _build_discovery_queries(self, topic: str, market: str, depth: str) -> List[str]:
        """构造搜索查询"""
        queries = []
        
        if depth in ["quick", "standard", "deep"]:
            queries.extend([
                f"{topic} 竞品",
                f"{topic} 对比",
                f"{topic} 有哪些",
            ])
        
        if depth in ["standard", "deep"]:
            queries.extend([
                f"best {topic} alternatives",
                f"{topic} vs",
                f"{topic} 排行榜",
            ])
        
        if depth == "deep":
            queries.extend([
                f"{topic} 推荐",
                f"{topic} 评测",
                f"top {topic} tools",
            ])
        
        return queries
    
    def _extract_competitors_from_results(
        self,
        topic: str,
        search_results: List[Dict],
        max_competitors: int = 10
    ) -> List[Dict]:
        """使用 LLM 从搜索结果中提取竞品"""
        # 合并搜索结果文本
        context = ""
        for i, result in enumerate(search_results[:5], 1):  # 只取前5条
            context += f"{i}. {result['title']}\n{result['snippet']}\n\n"
        
        prompt = f"""你是一位专业的市场研究分析师。请从以下搜索结果中提取所有提到的 "{topic}" 相关产品/工具的名称。

搜索结果：
{context}

要求：
1. 只提取明确提到的产品名称，不要臆测
2. 排除通用名词（如"AI工具"、"软件"等）
3. 每个产品给出置信度评分（0-1），基于它在内容中的提及频率和相关性
4. 按照JSON格式输出，最多返回{max_competitors}个产品

输出格式（纯JSON，不要其他内容）：
{{
    "competitors": [
        {{"name": "产品名", "confidence": 0.95, "reason": "在搜索结果中多次明确提到"}},
        {{"name": "产品名2", "confidence": 0.80, "reason": "在标题中提到"}}
    ]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=config.DEFAULT_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            competitors = data.get("competitors", [])
            print(f"    提取到 {len(competitors)} 个竞品")
            
            return competitors
        
        except Exception as e:
            print(f"    ❌ LLM 提取失败: {e}")
            return []
    
    def _deduplicate_competitors(self, competitors: List[Dict]) -> List[Dict]:
        """去重和合并竞品"""
        unique = []
        
        for comp in competitors:
            is_duplicate = False
            comp_name = comp["name"].lower().strip()
            
            for existing in unique:
                existing_name = existing["name"].lower().strip()
                
                # 使用模糊匹配判断相似度
                similarity = fuzz.ratio(comp_name, existing_name)
                
                if similarity > 85:  # 相似度阈值
                    # 合并置信度（取最高值）
                    existing["confidence"] = max(
                        existing.get("confidence", 0),
                        comp.get("confidence", 0)
                    )
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(comp)
        
        return unique
    
    def _discover_data_sources(self, competitor_name: str, topic: str) -> List[Dict]:
        """为单个竞品发现数据源"""
        print(f"\n  🔍 搜索 {competitor_name} 的数据源...")
        
        # 数据源搜索模板
        source_queries = {
            "官网": [
                f"{competitor_name} 官网",
                f"{competitor_name} official website"
            ],
            "产品功能": [
                f"{competitor_name} features",
                f"{competitor_name} 功能介绍"
            ],
            "定价": [
                f"{competitor_name} pricing",
                f"{competitor_name} 价格"
            ],
            "用户评价": [
                f"{competitor_name} 评价 site:xiaohongshu.com",
                f"{competitor_name} 怎么样 site:zhihu.com"
            ]
        }
        
        all_sources = []
        
        for source_type, queries in source_queries.items():
            # 只搜索第一个查询（节省成本）
            query = queries[0]
            results = self.search_engine.search(query, num_results=3)
            
            if results:
                for result in results[:2]:  # 每种类型取前2个
                    all_sources.append({
                        "type": source_type,
                        "url": result["url"],
                        "title": result["title"],
                        "priority": self._get_priority(source_type),
                        "quality_score": 0.8  # 默认评分
                    })
        
        print(f"    找到 {len(all_sources)} 个数据源")
        return all_sources
    
    def _get_priority(self, source_type: str) -> int:
        """获取数据源优先级"""
        priority_map = {
            "官网": 1,
            "产品功能": 1,
            "定价": 1,
            "用户评价": 2,
            "电商": 2,
            "博客文章": 3,
            "其他": 4
        }
        return priority_map.get(source_type, 4)
    
    def _create_task(self, topic: str, market: str, target_count: int, depth: str) -> DiscoveryTask:
        """创建发现任务"""
        db = SessionLocal()
        try:
            task = DiscoveryTask(
                topic=topic,
                market=market,
                target_count=target_count,
                search_depth=depth,
                status="processing"
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            return task
        finally:
            db.close()
    
    def _update_task(self, task: DiscoveryTask):
        """更新任务"""
        db = SessionLocal()
        try:
            db.merge(task)
            db.commit()
        finally:
            db.close()
    
    def _save_competitors(self, task_id: int, competitors: List[Dict]):
        """保存竞品到数据库"""
        db = SessionLocal()
        try:
            for comp_data in competitors:
                # 创建竞品
                competitor = Competitor(
                    name=comp_data["name"],
                    discovery_task_id=task_id,
                    confidence=comp_data.get("confidence", 0.5),
                    status="active"
                )
                db.add(competitor)
                db.flush()  # 获取 ID
                
                # 创建数据源
                for source_data in comp_data.get("data_sources", []):
                    data_source = DataSource(
                        competitor_id=competitor.id,
                        source_type=source_data["type"],
                        url=source_data["url"],
                        priority=source_data["priority"],
                        quality_score=source_data.get("quality_score", 0.8),
                        auto_discovered=True,
                        status="active"
                    )
                    db.add(data_source)
            
            db.commit()
        finally:
            db.close()
