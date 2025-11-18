"""
특수 Label 종합 필터링

특수 Label에 대한 종합 필터링 및 이벤트 생성
"""

from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime

from .baseline_rules import FilteringBaselineRules
from .event_generator import EventGenerator
from .alert_system import AlertSystem


@dataclass
class FilteringResult:
    """필터링 결과"""
    label: str
    severity: str
    action: str
    alert_level: str
    text: str
    session_context: Optional[List[str]]
    timestamp: datetime


class SpecialLabelFilter:
    """특수 Label 필터"""
    
    def __init__(self):
        """
        특수 Label 필터 초기화
        """
        self.baseline_rules = FilteringBaselineRules()
        self.event_generator = EventGenerator()
        self.alert_system = AlertSystem()
    
    def filter(self, label: str, text: str, 
               session_context: Optional[List[str]] = None) -> FilteringResult:
        """
        특수 Label 필터링
        
        Args:
            label: 특수 Label
            text: 발화 텍스트
            session_context: 세션 맥락
        
        Returns:
            FilteringResult (action, alert_level, event)
        """
        # Label별 심각도 확인 (모듈 내부 규칙 사용)
        severity = self.baseline_rules.get_severity(label)
        
        # 이벤트 생성
        event = self.event_generator.generate(label, severity, text, session_context)
        
        # 알림 발송
        self.alert_system.send_alert(event)
        
        return FilteringResult(
            label=label,
            severity=severity,
            action=event.action,
            alert_level=event.alert_level,
            text=text,
            session_context=session_context,
            timestamp=datetime.now()
        )


