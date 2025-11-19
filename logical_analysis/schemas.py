# analysis/schemas.py
from ninja import Schema
from typing import List, Dict, Optional
from datetime import datetime

class ClassificationResultSchema(Schema):
    """개별 문장 분석 결과 스키마"""
    label: str
    label_type: str
    confidence: float
    text: str
    probabilities: Optional[Dict[str, float]] = None
    timestamp: Optional[datetime] = None

class PipelineResultSchema(Schema):
    """전체 파이프라인 결과 스키마 (API 입력용)"""
    session_id: str
    results: List[ClassificationResultSchema]
    timestamp: Optional[datetime] = None

# logical_analysis/schemas.py (기존 코드 아래에 추가)

class ClassificationResultOut(Schema):
    """조회용 개별 결과 스키마"""
    text: str
    label: str
    label_type: str
    confidence: float
    probabilities: Dict[str, float]
    timestamp: Optional[datetime] = None
    action: Optional[str]
    alert_level: Optional[str]
    created_at: datetime

class SessionSummary(Schema):
    """세션 요약 정보"""
    total_sentences: int
    risk_score: int
    highest_alert: str
    primary_intent: str

class AnalysisSessionOut(Schema):
    """조회용 전체 세션 스키마 (업그레이드 버전)"""
    session_id: str
    created_at: datetime
    summary: SessionSummary
    results: List[ClassificationResultOut]
