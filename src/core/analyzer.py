"""
竞品分析器（核心编排模块）
"""
import json
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

from src.config import config
from src.discovery.discoverer import CompetitorDiscoverer
from src.crawler.url_crawler import URLCrawler
from src.analysis.extractor import InformationExtractor, ComparisonAnalyzer
from src.database import Competitor, DataSource, RawContent, ParsedData, SessionLocal


class CompetitorAnalyzer:
    """竞品分析器（主入口）"""
    
    def __init__(self):
        self.discoverer = CompetitorDiscoverer()
        self.crawler = URLCrawler()
        self.extractor = InformationExtractor()
        self.comparator = ComparisonAnalyzer()
    
    def analyze_from_topic(
        self,
        topic: str,
        market: str = "中国",
        target_count: int = 3,
        depth: str = "standard",
        auto_crawl: bool = True
    ) -> Dict:
        """
        从主题开始完整分析（智能发现模式）
        
        Args:
            topic: 调研主题
            market: 目标市场
            target_count: 竞品数量
            depth: 搜索深度
            auto_crawl: 是否自动开始爬取
        
        Returns:
            分析结果
        """
        print("\n" + "="*80)
        print(f"🚀 自动化竞品分析: {topic}")
        print("="*80)
        
        # 阶段1: 智能发现
        print("\n📍 阶段 1/4: 智能数据源发现")
        discovery_result = self.discoverer.discover(
            topic=topic,
            market=market,
            target_count=target_count,
            depth=depth
        )
        
        competitors = discovery_result["competitors"]
        
        if not auto_crawl:
            print("\n⏸️  自动爬取已禁用，请手动确认后继续")
            return discovery_result
        
        # 阶段2: 数据采集
        print("\n📍 阶段 2/4: 数据采集")
        crawl_results = self._crawl_competitors(competitors)
        
        # 阶段3: 信息提取
        print("\n📍 阶段 3/4: AI 信息提取")
        extracted_data = self._extract_information(crawl_results)
        
        # 阶段4: 生成报告
        print("\n📍 阶段 4/4: 生成分析报告")
        report_path = self._generate_report(topic, extracted_data)
        
        print("\n" + "="*80)
        print("✅ 分析完成！")
        print(f"📊 报告路径: {report_path}")
        print("="*80 + "\n")
        
        return {
            "topic": topic,
            "competitors": competitors,
            "crawl_results": crawl_results,
            "extracted_data": extracted_data,
            "report_path": report_path
        }
    
    def analyze_from_config(self, config_file: str) -> Dict:
        """从配置文件分析（手动配置模式）"""
        # TODO: 实现配置文件解析
        pass
    
    def _crawl_competitors(self, competitors: List[Dict]) -> List[Dict]:
        """爬取竞品数据"""
        results = []
        
        for i, comp in enumerate(competitors, 1):
            comp_name = comp["name"]
            print(f"\n[{i}/{len(competitors)}] 爬取 {comp_name}")
            
            # 获取数据源
            data_sources = comp.get("data_sources", [])
            if not data_sources:
                print(f"  ⚠️  没有数据源，跳过")
                continue
            
            # 爬取前3个高优先级数据源
            urls_to_crawl = [
                ds["url"] for ds in sorted(
                    data_sources, 
                    key=lambda x: x["priority"]
                )[:3]
            ]
            
            crawl_results = self.crawler.batch_crawl(urls_to_crawl, comp_name)
            
            results.append({
                "competitor": comp_name,
                "confidence": comp.get("confidence", 0.8),
                "crawl_results": crawl_results
            })
        
        return results
    
    def _extract_information(self, crawl_results: List[Dict]) -> List[Dict]:
        """提取信息"""
        extracted = []
        
        for comp_data in crawl_results:
            comp_name = comp_data["competitor"]
            print(f"\n🔍 分析 {comp_name}")
            
            # 合并所有爬取内容
            all_content = ""
            for result in comp_data["crawl_results"]:
                if result.get("success"):
                    all_content += result.get("content", "") + "\n\n"
            
            if not all_content:
                print("  ⚠️  没有有效内容，跳过")
                extracted.append({
                    "competitor": comp_name,
                    "data": {}
                })
                continue
            
            # 提取信息
            data = self.extractor.extract_all(all_content, comp_name)
            
            # 生成 SWOT
            print("  📊 生成 SWOT 分析...")
            swot = self.comparator.generate_swot(data)
            data["swot"] = swot
            
            extracted.append({
                "competitor": comp_name,
                "confidence": comp_data.get("confidence", 0.8),
                "data": data
            })
        
        return extracted
    
    def _generate_report(self, topic: str, extracted_data: List[Dict]) -> str:
        """生成分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = topic.replace(" ", "_")[:30]
        report_name = f"{safe_topic}_{timestamp}"
        report_dir = config.REPORTS_DIR / report_name
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成 Markdown 报告
        report_path = report_dir / "report.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(self._render_markdown_report(topic, extracted_data))
        
        # 保存 JSON 数据
        json_path = report_dir / "data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)
        
        print(f"  📄 Markdown: {report_path}")
        print(f"  📊 JSON: {json_path}")
        
        return str(report_path)
    
    def _render_markdown_report(self, topic: str, extracted_data: List[Dict]) -> str:
        """渲染 Markdown 报告"""
        md = f"""# {topic} - 竞品分析报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**竞品数量**: {len(extracted_data)}  
**生成工具**: 自动化竞品分析工具 v0.1

---

## 执行摘要

本报告通过智能数据源发现、自动化采集和 AI 分析，对 {len(extracted_data)} 个 {topic} 竞品进行了全面分析。

---

## 竞品概览

"""
        
        # 竞品列表
        for i, comp in enumerate(extracted_data, 1):
            comp_name = comp["competitor"]
            confidence = comp.get("confidence", 0) * 100
            product_info = comp.get("data", {}).get("product_info", {})
            
            md += f"""### {i}. {comp_name}

- **置信度**: {confidence:.0f}%
- **公司**: {product_info.get('company', '未知')}
- **定位**: {product_info.get('tagline', '未知')}
- **简介**: {product_info.get('description', '未知')}

"""
        
        # 详细分析
        md += "\n---\n\n## 详细分析\n\n"
        
        for i, comp in enumerate(extracted_data, 1):
            comp_name = comp["competitor"]
            data = comp.get("data", {})
            
            md += f"### {i}. {comp_name}\n\n"
            
            # 核心功能
            md += "#### 核心功能\n\n"
            features = data.get("features", {}).get("core_features", [])
            if features:
                for feat in features[:5]:
                    unique = "🌟 " if feat.get("unique") else ""
                    md += f"- {unique}**{feat.get('name', '')}**: {feat.get('description', '')}\n"
            else:
                md += "*暂无功能信息*\n"
            md += "\n"
            
            # 价格策略
            md += "#### 价格策略\n\n"
            pricing = data.get("pricing", {})
            if pricing and pricing.get("price_tiers"):
                md += f"**模式**: {pricing.get('pricing_model', '未知')}\n\n"
                for tier in pricing.get("price_tiers", []):
                    price = tier.get("price", 0)
                    currency = tier.get("currency", "CNY")
                    cycle = tier.get("billing_cycle", "")
                    md += f"- **{tier.get('name', '')}**: {currency} {price}/{cycle}\n"
            else:
                md += "*暂无价格信息*\n"
            md += "\n"
            
            # SWOT 分析
            md += "#### SWOT 分析\n\n"
            swot = data.get("swot", {})
            if swot:
                md += "**优势 (Strengths)**:\n"
                for s in swot.get("strengths", [])[:3]:
                    md += f"- {s.get('point', '')} ({s.get('impact', '')}影响)\n"
                md += "\n"
                
                md += "**劣势 (Weaknesses)**:\n"
                for w in swot.get("weaknesses", [])[:3]:
                    md += f"- {w.get('point', '')} ({w.get('impact', '')}影响)\n"
                md += "\n"
                
                md += "**机会 (Opportunities)**:\n"
                for o in swot.get("opportunities", [])[:2]:
                    md += f"- {o.get('point', '')}\n"
                md += "\n"
                
                md += "**威胁 (Threats)**:\n"
                for t in swot.get("threats", [])[:2]:
                    md += f"- {t.get('point', '')}\n"
                md += "\n"
            
            md += "---\n\n"
        
        # 总结
        md += """## 总结与建议

### 市场格局

[基于以上分析，总结市场竞争格局]

### 战略建议

1. **产品策略**: 
2. **定价策略**: 
3. **营销策略**: 

---

*本报告由 AI 自动生成，建议结合人工判断进行决策*
"""
        
        return md
