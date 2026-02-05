"""
信息提取模块（使用 LLM 从原始内容中提取结构化信息）
"""
import json
from typing import Dict, Optional, List
from openai import OpenAI

from src.config import config


class InformationExtractor:
    """信息提取器"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def extract_product_info(self, content: str, competitor_name: str) -> Dict:
        """提取产品基础信息"""
        prompt = f"""你是一位专业的产品分析师。请从以下内容中提取 {competitor_name} 的产品信息。

内容：
{content[:3000]}

请按照以下JSON格式输出：
{{
    "product_name": "产品名称",
    "company": "公司名称",
    "tagline": "产品定位/slogan",
    "target_users": ["目标用户群1", "目标用户群2"],
    "founding_year": "成立年份（如果提到）",
    "description": "产品简介（100字内）"
}}

注意：
1. 如果信息缺失，字段值设为null
2. 保持客观，避免主观评价
"""
        
        return self._call_llm(prompt, "product_info")
    
    def extract_features(self, content: str, competitor_name: str) -> Dict:
        """提取功能特征"""
        prompt = f"""你是一位专业的产品分析师。请从以下内容中提取 {competitor_name} 的核心功能。

内容：
{content[:4000]}

请按照以下JSON格式输出：
{{
    "core_features": [
        {{
            "name": "功能名称",
            "description": "功能描述（简短）",
            "category": "基础功能/核心功能/高级功能",
            "unique": true/false
        }}
    ]
}}

注意：
1. 提取实际提到的功能，不要臆造
2. unique字段表示是否是差异化功能
3. 至少提取5个核心功能
"""
        
        return self._call_llm(prompt, "features")
    
    def extract_pricing(self, content: str, competitor_name: str) -> Dict:
        """提取价格策略"""
        prompt = f"""你是一位专业的产品分析师。请从以下内容中提取 {competitor_name} 的价格信息。

内容：
{content[:4000]}

请按照以下JSON格式输出：
{{
    "pricing_model": "订阅制/买断制/免费+增值/其他",
    "price_tiers": [
        {{
            "name": "套餐名称",
            "price": 价格数字,
            "currency": "CNY/USD",
            "billing_cycle": "月付/年付/一次性",
            "features": ["包含功能1", "包含功能2"]
        }}
    ],
    "trial": {{
        "available": true/false,
        "duration": "试用时长"
    }}
}}

注意：
1. 如果没有明确价格信息，返回空对象
2. 价格用数字表示，不要包含货币符号
"""
        
        return self._call_llm(prompt, "pricing")
    
    def extract_reviews_summary(self, content: str, competitor_name: str) -> Dict:
        """提取用户评价摘要"""
        prompt = f"""你是一位专业的产品分析师。请从以下用户评价内容中总结 {competitor_name} 的用户反馈。

内容：
{content[:4000]}

请按照以下JSON格式输出：
{{
    "sentiment": {{
        "positive": 0.0-1.0,
        "neutral": 0.0-1.0,
        "negative": 0.0-1.0
    }},
    "key_praise": ["优点1", "优点2", "优点3"],
    "key_complaints": ["缺点1", "缺点2", "缺点3"],
    "common_keywords": ["高频词1", "高频词2"],
    "summary": "整体评价摘要（100字内）"
}}

注意：
1. sentiment三个值加起来应该等于1.0
2. 基于实际内容提取，避免臆造
"""
        
        return self._call_llm(prompt, "reviews")
    
    def extract_all(self, content: str, competitor_name: str) -> Dict:
        """提取所有信息（一次性）"""
        print(f"🔍 提取 {competitor_name} 的信息...")
        
        results = {
            "product_info": {},
            "features": {},
            "pricing": {},
            "reviews": {}
        }
        
        # 根据内容长度判断是否包含有价值信息
        if len(content) < 200:
            print("  ⚠️  内容太短，跳过提取")
            return results
        
        # 提取产品信息
        print("  📝 提取产品信息...")
        results["product_info"] = self.extract_product_info(content, competitor_name)
        
        # 提取功能
        print("  🔧 提取功能特征...")
        results["features"] = self.extract_features(content, competitor_name)
        
        # 提取价格（如果内容中包含价格相关词）
        if any(word in content.lower() for word in ['price', 'pricing', '价格', '定价', '¥', '$']):
            print("  💰 提取价格信息...")
            results["pricing"] = self.extract_pricing(content, competitor_name)
        
        # 提取评价（如果内容中包含评价相关词）
        if any(word in content.lower() for word in ['评价', '体验', '使用', 'review', '推荐', '好用']):
            print("  ⭐ 提取用户评价...")
            results["reviews"] = self.extract_reviews_summary(content, competitor_name)
        
        print("  ✅ 提取完成")
        return results
    
    def _call_llm(self, prompt: str, extraction_type: str) -> Dict:
        """调用 LLM"""
        try:
            response = self.client.chat.completions.create(
                model=config.DEFAULT_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.DEFAULT_LLM_TEMPERATURE,
                max_tokens=config.MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            return data
        
        except Exception as e:
            print(f"  ❌ LLM 调用失败 ({extraction_type}): {e}")
            return {}


class ComparisonAnalyzer:
    """对比分析器"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    def generate_feature_matrix(self, competitors_data: List[Dict]) -> Dict:
        """生成功能对比矩阵"""
        # 收集所有功能
        all_features = set()
        for comp in competitors_data:
            features = comp.get("features", {}).get("core_features", [])
            for feature in features:
                all_features.add(feature.get("name", ""))
        
        # 构建矩阵
        matrix = {
            "features": list(all_features),
            "competitors": {}
        }
        
        for comp in competitors_data:
            comp_name = comp.get("product_info", {}).get("product_name", "Unknown")
            comp_features = {f.get("name"): f for f in comp.get("features", {}).get("core_features", [])}
            
            matrix["competitors"][comp_name] = {
                feature: "✅" if feature in comp_features else "❌"
                for feature in all_features
            }
        
        return matrix
    
    def generate_swot(self, competitor_data: Dict, market_context: str = "") -> Dict:
        """生成 SWOT 分析"""
        competitor_name = competitor_data.get("product_info", {}).get("product_name", "Unknown")
        
        # 准备上下文
        context = f"""
产品名称: {competitor_name}
产品信息: {json.dumps(competitor_data.get('product_info', {}), ensure_ascii=False)}
功能特征: {json.dumps(competitor_data.get('features', {}), ensure_ascii=False)}
价格策略: {json.dumps(competitor_data.get('pricing', {}), ensure_ascii=False)}
用户评价: {json.dumps(competitor_data.get('reviews', {}), ensure_ascii=False)}
"""
        
        prompt = f"""你是一位专业的战略分析师。请基于以下信息，为 {competitor_name} 生成 SWOT 分析。

{context}

请按照以下JSON格式输出：
{{
    "strengths": [
        {{
            "point": "优势点",
            "evidence": "支持证据",
            "impact": "高/中/低"
        }}
    ],
    "weaknesses": [
        {{
            "point": "劣势点",
            "evidence": "支持证据",
            "impact": "高/中/低"
        }}
    ],
    "opportunities": [
        {{
            "point": "机会点",
            "context": "市场背景",
            "action": "建议行动"
        }}
    ],
    "threats": [
        {{
            "point": "威胁点",
            "context": "威胁背景",
            "action": "应对建议"
        }}
    ],
    "overall_assessment": "整体评估（100字内）"
}}

要求：
1. 每个维度至少3个要点
2. 基于数据分析，避免空洞描述
3. impact/action要具体可执行
"""
        
        try:
            response = self.client.chat.completions.create(
                model=config.DEFAULT_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            print(f"❌ SWOT 生成失败: {e}")
            return {}
