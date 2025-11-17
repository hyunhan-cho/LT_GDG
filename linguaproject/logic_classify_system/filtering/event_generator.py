"""
이벤트 생성

특수 Label에 따른 이벤트 생성
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from .baseline_rules import FilteringBaselineRules


@dataclass
class FilteringEvent:
    """필터링 이벤트"""
    label: str
    severity: str
    action: str
    alert_level: str
    text: str
    session_context: Optional[List[str]]
    timestamp: datetime
    config: Dict[str, Any]  # 추가 설정 정보


class EventGenerator:
    """이벤트 생성기"""
    
    def __init__(self):
        """
        이벤트 생성기 초기화
        """
        # Baseline 규칙은 모듈 내부에 포함
        self.baseline_rules = FilteringBaselineRules()
    
    def generate(self, label: str, severity: str, text: str, 
                 session_context: Optional[List[str]] = None) -> FilteringEvent:
        """
        이벤트 생성
        
        Args:
            label: 특수 Label
            severity: 심각도
            text: 발화 텍스트
            session_context: 세션 맥락
        
        Returns:
            FilteringEvent
        """
        # Label별 이벤트 설정 (모듈 내부 규칙 사용)
        event_config = self.baseline_rules.get_event_config(label)
        
        return FilteringEvent(
            label=label,
            severity=severity,
            action=event_config.get("action", "MONITOR"),
            alert_level=event_config.get("alert_level", "MEDIUM"),
            text=text,
            session_context=session_context,
            timestamp=datetime.now(),
            config=event_config
        )


