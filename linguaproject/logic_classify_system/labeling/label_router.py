"""
Label 기반 라우팅

Normal Label과 특수 Label에 따라 적절한 처리 경로로 라우팅
"""

from typing import Optional, List
from dataclasses import dataclass

from ..data.data_structures import ClassificationResult
from ..evaluation.normal_label_evaluator import NormalLabelEvaluator
from ..evaluation.evaluation_result import EvaluationResult
from ..filtering.special_label_filter import SpecialLabelFilter, FilteringResult


@dataclass
class RouterResult:
    """라우팅 결과"""
    route_type: str  # "EVALUATION", "FILTERING", "UNKNOWN"
    result: Optional[any]  # EvaluationResult 또는 FilteringResult
    classification_result: ClassificationResult


class LabelRouter:
    """Label 라우터"""
    
    def __init__(self):
        """
        Label 라우터 초기화
        """
        self.evaluator = NormalLabelEvaluator()
        self.filter = SpecialLabelFilter()
    
    def route(self, classification_result: ClassificationResult, 
              session_context: Optional[List[str]] = None,
              agent_text: Optional[str] = None) -> RouterResult:
        """
        Label 기반 라우팅
        
        Args:
            classification_result: 분류 결과
            session_context: 세션 맥락
            agent_text: 상담사 발화 (Normal Label 평가용)
        
        Returns:
            RouterResult (route_type, result)
        """
        if classification_result.label_type == "NORMAL":
            # 평가 프레임워크로 이동
            if agent_text is None:
                agent_text = ""  # 상담사 발화가 없으면 빈 문자열
            
            evaluation_result = self.evaluator.evaluate(
                label=classification_result.label,
                customer_text=classification_result.text,
                agent_text=agent_text,
                session_context=session_context or []
            )
            return RouterResult(
                route_type="EVALUATION",
                result=evaluation_result,
                classification_result=classification_result
            )
        
        elif classification_result.label_type == "SPECIAL":
            # 종합 필터링으로 이동
            filtering_result = self.filter.filter(
                label=classification_result.label,
                text=classification_result.text,
                session_context=session_context
            )
            return RouterResult(
                route_type="FILTERING",
                result=filtering_result,
                classification_result=classification_result
            )
        
        else:
            # 알 수 없는 Label
            return RouterResult(
                route_type="UNKNOWN",
                result=None,
                classification_result=classification_result
            )

