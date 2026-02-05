"""
数据库模型定义
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from src.config import config

Base = declarative_base()


class DiscoveryTask(Base):
    """发现任务表"""
    __tablename__ = "discovery_tasks"
    
    id = Column(Integer, primary_key=True)
    topic = Column(String(200), nullable=False)
    market = Column(String(50))
    target_count = Column(Integer)
    search_depth = Column(String(20))  # quick/standard/deep
    status = Column(String(20), default="pending")  # pending/processing/completed/failed
    progress = Column(Integer, default=0)
    competitors_found = Column(Integer, default=0)
    sources_found = Column(Integer, default=0)
    result_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    competitors = relationship("Competitor", back_populates="discovery_task")


class SearchCache(Base):
    """搜索缓存表"""
    __tablename__ = "search_cache"
    
    id = Column(Integer, primary_key=True)
    query = Column(String(500), unique=True, nullable=False, index=True)
    search_engine = Column(String(50))
    results = Column(JSON)
    cached_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, index=True)
    hit_count = Column(Integer, default=0)


class Competitor(Base):
    """竞品表"""
    __tablename__ = "competitors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    company = Column(String(200))
    website = Column(String(500))
    category = Column(String(100))
    discovery_task_id = Column(Integer, ForeignKey("discovery_tasks.id"))
    confidence = Column(Float)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    discovery_task = relationship("DiscoveryTask", back_populates="competitors")
    data_sources = relationship("DataSource", back_populates="competitor")
    change_logs = relationship("ChangeLog", back_populates="competitor")


class DataSource(Base):
    """数据源表"""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=False)
    source_type = Column(String(50))  # 官网/小红书/淘宝等
    url = Column(Text, nullable=False)
    priority = Column(Integer)
    quality_score = Column(Float)
    auto_discovered = Column(Boolean, default=False)
    status = Column(String(20), default="active")
    last_crawl_time = Column(DateTime)
    
    competitor = relationship("Competitor", back_populates="data_sources")
    raw_contents = relationship("RawContent", back_populates="data_source")


class RawContent(Base):
    """原始内容表"""
    __tablename__ = "raw_contents"
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    content_path = Column(Text)  # Markdown文件路径
    content_hash = Column(String(64))  # 内容哈希
    crawl_time = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)
    
    data_source = relationship("DataSource", back_populates="raw_contents")
    parsed_data = relationship("ParsedData", back_populates="raw_content")


class ParsedData(Base):
    """解析结果表"""
    __tablename__ = "parsed_data"
    
    id = Column(Integer, primary_key=True)
    raw_content_id = Column(Integer, ForeignKey("raw_contents.id"), nullable=False)
    data_type = Column(String(50))  # product_info/features/pricing/reviews
    extracted_data = Column(JSON)
    confidence = Column(Float)
    parsed_at = Column(DateTime, default=datetime.utcnow)
    
    raw_content = relationship("RawContent", back_populates="parsed_data")


class AnalysisReport(Base):
    """分析报告表"""
    __tablename__ = "analysis_reports"
    
    id = Column(Integer, primary_key=True)
    report_name = Column(String(200))
    report_type = Column(String(50))  # full/feature_compare/price_compare
    competitors = Column(JSON)  # 包含的竞品列表
    report_path = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChangeLog(Base):
    """变化日志表"""
    __tablename__ = "change_logs"
    
    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=False)
    change_type = Column(String(50))
    field_name = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    impact_level = Column(String(20))  # 高/中/低
    detected_at = Column(DateTime, default=datetime.utcnow)
    notified = Column(Boolean, default=False)
    
    competitor = relationship("Competitor", back_populates="change_logs")


# 数据库引擎和会话
engine = create_engine(config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库初始化完成")


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
