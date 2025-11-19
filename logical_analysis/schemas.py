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
    created_at: datetime # DB 저장 시점

class AnalysisSessionOut(Schema):
    """조회용 전체 세션 스키마"""
    session_id: str
    created_at: datetime
    # 1:N 관계에 있는 결과들을 리스트로 포함
    results: List[ClassificationResultOut]