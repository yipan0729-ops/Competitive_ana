"""
URL 爬虫模块（三层策略：Firecrawl → Jina → Playwright）
"""
import os
import re
import hashlib
from typing import Dict, Optional, List, Tuple
from pathlib import Path
from datetime import datetime
import requests
from urllib.parse import urlparse

from src.config import config


class PlatformIdentifier:
    """平台识别器"""
    
    PLATFORMS = {
        "mp.weixin.qq.com": "微信公众号",
        "xiaohongshu.com": "小红书",
        "xhslink.com": "小红书",
        "zhihu.com": "知乎",
        "douyin.com": "抖音",
        "taobao.com": "淘宝",
        "tmall.com": "天猫",
        "jd.com": "京东",
        "bilibili.com": "B站",
    }
    
    @classmethod
    def identify(cls, url: str) -> Tuple[str, bool]:
        """
        识别平台
        
        Returns:
            (平台名称, 是否需要登录)
        """
        domain = urlparse(url).netloc.lower()
        
        for pattern, platform in cls.PLATFORMS.items():
            if pattern in domain:
                needs_login = platform in ["微信公众号", "小红书", "淘宝", "天猫", "京东"]
                return platform, needs_login
        
        return "官网", False


class URLCrawler:
    """URL 爬虫（三层策略）"""
    
    def __init__(self):
        self.firecrawl_key = config.FIRECRAWL_API_KEY
        self.data_dir = config.DATA_DIR
    
    def crawl(self, url: str, competitor_name: str = "Unknown") -> Dict:
        """
        爬取 URL 内容
        
        Args:
            url: 目标 URL
            competitor_name: 竞品名称
        
        Returns:
            {
                "success": bool,
                "content": str,  # Markdown 内容
                "content_path": str,  # 保存路径
                "images": List[str],  # 图片路径列表
                "metadata": dict
            }
        """
        print(f"🕷️  爬取: {url}")
        
        # 识别平台
        platform, needs_login = PlatformIdentifier.identify(url)
        print(f"   平台: {platform} | 需要登录: {'是' if needs_login else '否'}")
        
        # 策略1: Firecrawl (首选)
        result = self._crawl_with_firecrawl(url)
        if result["success"]:
            print("   ✅ Firecrawl 成功")
            return self._save_content(result, url, competitor_name, platform)
        
        # 策略2: Jina Reader (备选)
        print("   🔄 降级到 Jina Reader")
        result = self._crawl_with_jina(url)
        if result["success"]:
            print("   ✅ Jina Reader 成功")
            return self._save_content(result, url, competitor_name, platform)
        
        # 策略3: Playwright (兜底) - 暂时跳过，需要安装浏览器
        print("   ⚠️  Playwright 暂未实现")
        
        print("   ❌ 所有策略都失败")
        return {
            "success": False,
            "error": "所有爬取策略都失败",
            "url": url
        }
    
    def _crawl_with_firecrawl(self, url: str) -> Dict:
        """使用 Firecrawl API 爬取"""
        if not self.firecrawl_key:
            return {"success": False, "error": "未配置 FIRECRAWL_API_KEY"}
        
        try:
            from firecrawl import FirecrawlApp
            
            app = FirecrawlApp(api_key=self.firecrawl_key)
            result = app.scrape_url(url)
            
            # Firecrawl v2 返回 Document 对象
            markdown = getattr(result, 'markdown', '')
            metadata = getattr(result, 'metadata', {})
            
            # 检查内容是否有效
            if not markdown or len(markdown) < 100:
                return {"success": False, "error": "内容太短或为空"}
            
            # 检查是否是验证页面
            if "验证" in markdown[:200] or "captcha" in markdown.lower()[:200]:
                return {"success": False, "error": "触发验证"}
            
            return {
                "success": True,
                "content": markdown,
                "metadata": metadata if isinstance(metadata, dict) else {}
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _crawl_with_jina(self, url: str) -> Dict:
        """使用 Jina Reader 爬取"""
        try:
            jina_url = f"https://r.jina.ai/{url}"
            headers = {
                "Accept": "text/markdown",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(
                jina_url,
                headers=headers,
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            content = response.text
            
            # 检查内容有效性
            if not content or len(content) < 100:
                return {"success": False, "error": "内容太短或为空"}
            
            return {
                "success": True,
                "content": content,
                "metadata": {}
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _save_content(
        self,
        crawl_result: Dict,
        url: str,
        competitor_name: str,
        platform: str
    ) -> Dict:
        """保存内容到文件"""
        content = crawl_result["content"]
        metadata = crawl_result.get("metadata", {})
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = re.sub(r'[^\w\s-]', '_', competitor_name)[:50]
        folder_name = f"{timestamp}_{safe_name}"
        
        # 创建目录
        save_dir = self.data_dir / folder_name
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存 Markdown
        content_path = save_dir / "content.md"
        
        # 添加元数据头部
        header = f"""---
title: {metadata.get('title', '未知标题')}
url: {url}
platform: {platform}
competitor: {competitor_name}
crawl_time: {datetime.now().isoformat()}
---

"""
        
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(header + content)
        
        # 提取并下载图片
        images = self._extract_and_download_images(content, save_dir, url)
        
        # 替换图片链接为本地路径
        if images:
            content_with_local_images = self._replace_image_urls(content, images)
            with open(content_path, 'w', encoding='utf-8') as f:
                f.write(header + content_with_local_images)
        
        # 计算内容哈希
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        print(f"   💾 保存到: {content_path}")
        print(f"   🖼️  图片: {len(images)} 张")
        
        return {
            "success": True,
            "content": content,
            "content_path": str(content_path),
            "images": [str(img) for img in images],
            "content_hash": content_hash,
            "metadata": {
                "url": url,
                "platform": platform,
                "competitor": competitor_name,
                "crawl_time": datetime.now().isoformat(),
                "content_length": len(content),
                **metadata
            }
        }
    
    def _extract_and_download_images(
        self,
        content: str,
        save_dir: Path,
        base_url: str
    ) -> List[Path]:
        """提取并下载图片"""
        # 提取图片 URL
        image_patterns = [
            r'!\[.*?\]\((https?://[^\)]+)\)',  # Markdown 格式
            r'(https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp))',  # 直接 URL
        ]
        
        image_urls = []
        for pattern in image_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            image_urls.extend(matches)
        
        # 去重
        image_urls = list(set(image_urls))
        
        if not image_urls:
            return []
        
        print(f"   🖼️  发现 {len(image_urls)} 张图片")
        
        # 下载图片
        downloaded = []
        for i, img_url in enumerate(image_urls[:20], 1):  # 最多下载20张
            try:
                img_path = self._download_image(img_url, save_dir, i, base_url)
                if img_path:
                    downloaded.append(img_path)
            except Exception as e:
                print(f"   ⚠️  图片 {i} 下载失败: {e}")
        
        return downloaded
    
    def _download_image(
        self,
        url: str,
        save_dir: Path,
        index: int,
        base_url: str
    ) -> Optional[Path]:
        """下载单张图片"""
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": base_url
        }
        
        # 小红书图片需要特殊 Referer
        if "xiaohongshu.com" in url or "xhscdn.com" in url:
            headers["Referer"] = "https://www.xiaohongshu.com/"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 确定文件扩展名
            content_type = response.headers.get('content-type', '')
            ext = '.jpg'
            if 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'webp' in content_type:
                ext = '.webp'
            
            # 保存
            img_path = save_dir / f"img_{index:02d}{ext}"
            with open(img_path, 'wb') as f:
                f.write(response.content)
            
            return img_path
        
        except Exception as e:
            return None
    
    def _replace_image_urls(self, content: str, local_images: List[Path]) -> str:
        """替换图片 URL 为本地路径"""
        # 简单实现：按顺序替换
        # 实际应该根据 URL 匹配
        for i, img_path in enumerate(local_images, 1):
            content = re.sub(
                r'!\[(.*?)\]\(https?://[^\)]+\)',
                f'![\\1]({img_path.name})',
                content,
                count=1
            )
        return content
    
    def batch_crawl(
        self,
        urls: List[str],
        competitor_name: str = "Unknown"
    ) -> List[Dict]:
        """批量爬取"""
        results = []
        total = len(urls)
        
        print(f"\n📦 批量爬取 {total} 个 URL")
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{total}]")
            result = self.crawl(url, competitor_name)
            results.append(result)
        
        success_count = sum(1 for r in results if r.get("success"))
        print(f"\n✅ 完成: {success_count}/{total} 成功")
        
        return results
