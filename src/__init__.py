"""
自动化竞品分析工具
"""

__version__ = "0.1.0"
__author__ = "AI"

from .core.analyzer import CompetitorAnalyzer
from .discovery.discoverer import CompetitorDiscoverer
from .crawler.url_crawler import URLCrawler
from .analysis.extractor import InformationExtractor

__all__ = [
    "CompetitorAnalyzer",
    "CompetitorDiscoverer", 
    "URLCrawler",
    "InformationExtractor"
]
