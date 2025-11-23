"""
Turn 단위 분석 데이터 구조 정의

기존 구조를 확장하여 Turn 단위 특징점 추출 결과를 포함
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class ProfanityResult:
    """욕설 감지 결과"""
    is_profanity: bool
    category: Optional[str]  # PROFANITY, VIOLENCE_THREAT, SEXUAL_HARASSMENT, HATE_SPEECH, INSULT
    confidence: float  # 0.0-1.0
    method: Optional[str]  # "korcen" or "baseline"


@dataclass
class ClassificationResult:
    """분류 결과"""
    label: str  # 분류된 Label
    label_type: str  # "NORMAL" or "SPECIAL"
    confidence: float  # 신뢰도 (0.0-1.0)
    text: str  # 원본 문장
    probabilities: Optional[Dict[str, float]] = None  # 각 Label별 확률
    timestamp: Optional[datetime] = None


@dataclass
class CustomerAnalysisResult:
    """손님 발화 Turn 분석 결과"""
    # 기본 정보
    session_id: str
    turn_index: int
    text: str  # 해당 Turn의 발화만
    timestamp: datetime
    
    # 특징점 추출 결과
    profanity_result: ProfanityResult
    classification_result: ClassificationResult
    
    # Turn 단위 특징점 점수 (해당 Turn만으로 추출)
    feature_scores: Dict[str, float]
    # 예: {
    #   # Special Label 특징점 (korcen + baseline 규칙 기반)
    #   "profanity_score": 0.8,           # 해당 Turn 내 욕설 감지 신뢰도
    #   "threat_score": 0.3,              # 해당 Turn 내 위협 표현 감지
    #   "sexual_harassment_score": 0.0,   # 해당 Turn 내 성희롱 표현 감지
    #   "hate_speech_score": 0.0,         # 해당 Turn 내 혐오표현 감지
    #   "unreasonable_demand_score": 0.6, # 해당 Turn 내 무리한 요구 감지
    #   "repetition_keyword_score": 0.4,  # 해당 Turn 내 반복 표현 키워드 존재 여부
    #   # Special Label 신뢰도 (요인들 합산)
    #   "special_label_confidence": 0.85, # Special Label을 붙이게 된 계기(요인들)의 합산 신뢰도
    #   # Special Label 요인별 점수 (probabilities 기반)
    #   "profanity_factor_score": 0.5,    # PROFANITY 요인 기여도
    #   "unreasonable_demand_factor_score": 0.3, # UNREASONABLE_DEMAND 요인 기여도
    #   # 주의: Normal Label confidence는 제거됨 (정량화하기 어려움)
    #   # Normal Label은 Special Label이 아닐 뿐, 정상 발화의 근거를 확신할 수 없음
    # }
    
    # 추출된 특징점 상세 정보 (해당 Turn 내에서 발견된 것만)
    extracted_features: Dict[str, Any]
    # 예: {
    #   # Special Label 특징점
    #   "profanity_keywords": ["욕설1"],           # 해당 Turn에서 발견
    #   "threat_patterns": ["위협 패턴1"],         # 해당 Turn에서 발견
    #   "unreasonable_keywords": ["공짜로", "배상"], # 해당 Turn에서 발견
    #   "repetition_keywords": ["또 같은 말씀"],   # 해당 Turn에서 발견 (실제 반복 여부는 후속 모듈)
    #   # 주의: Normal Label 키워드는 추출하지 않음 (Normal Label은 Special Label이 아닐 뿐)
    # }


@dataclass
class AgentAnalysisResult:
    """상담원 발화 Turn 분석 결과"""
    # 기본 정보
    session_id: str
    turn_index: int
    text: str  # 해당 Turn의 발화만
    timestamp: datetime
    corresponding_customer_label: str  # 해당 손님 발화의 Label
    
    # 매뉴얼 준수 분석 결과 (해당 Turn + 해당 Label 매뉴얼 기준)
    manual_compliance_score: float  # 0.0-1.0
    compliance_details: Dict[str, Any]
    # 예: {
    #   "phrase_score": 0.8,      # 해당 Turn 내 필수 표현 사용 여부
    #   "keyword_score": 0.9,     # 해당 Turn 내 필수 키워드 사용 여부
    #   "procedure_score": 0.7,   # 해당 Turn 내 절차 순서 (Turn 내에서 판단 가능한 부분만)
    #   "complied_items": ["필수 표현 사용", "절차 안내"],
    #   "non_complied_items": ["공감 표현 부족"]
    # }
    
    # Turn 단위 특징점 점수 (해당 Turn만으로 추출)
    feature_scores: Dict[str, float]
    # 예: {
    #   "manual_compliance_score": 0.8,         # 해당 Turn의 매뉴얼 준수도
    #   "information_accuracy_score": 0.9,      # 해당 Turn의 정보 제공 정확성
    #   "communication_clarity_score": 0.7,     # 해당 Turn의 소통 명확성
    #   "empathy_score": 0.6,                   # 해당 Turn의 공감 표현
    #   "problem_solving_score": 0.8            # 해당 Turn의 해결 방안 제시
    # }
    
    # 추출된 특징점 상세 정보 (해당 Turn 내에서 발견된 것만)
    extracted_features: Dict[str, Any]
    # 예: {
    #   "used_phrases": ["안내드리겠습니다"],     # 해당 Turn에서 사용된 표현
    #   "missing_phrases": ["불편을 드려 죄송합니다"],  # 해당 Turn에서 미사용 표현
    #   "used_keywords": ["처리", "절차"],        # 해당 Turn에서 사용된 키워드
    #   ...
    # }


@dataclass
class TurnAnalysisResult:
    """발화 턴별 분석 결과 (Turn 단위)"""
    session_id: str
    turn_index: int
    customer_result: CustomerAnalysisResult
    agent_result: Optional[AgentAnalysisResult]  # 상담원 발화가 있는 경우
    
    # Turn 단위 종합 Score Resource (다음 단계에서 활용)
    # 주의: 이 점수들은 "해당 Turn"에 대한 평가만 포함
    turn_scores: Dict[str, float]
    # 예: {
    #   "customer_problem_score": 0.7,           # 해당 Turn의 손님 문제 발생 가능성
    #   "agent_response_quality_score": 0.8,     # 해당 Turn의 상담원 대응 품질
    #   "turn_risk_score": 0.65,                 # 해당 Turn의 리스크 점수
    #   # 주의: "overall_turn_score"는 Turn 단위 평가지만,
    #   #       세션 전체 평가는 후속 모듈에서 수행
    # }


@dataclass
class PipelineResult:
    """파이프라인 결과 (Turn 기반)"""
    session_id: str
    turn_results: List[TurnAnalysisResult]  # Turn 단위 분석 결과 리스트
    timestamp: Optional[datetime] = None


