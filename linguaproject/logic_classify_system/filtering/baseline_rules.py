"""
종합 필터링용 Baseline 규칙

특수 Label의 심각도 판단 및 이벤트 생성에 사용
"""

from typing import Dict


class FilteringBaselineRules:
    """종합 필터링용 Baseline 규칙"""
    
    # 심각도별 Label 매핑
    SEVERITY_MAP: Dict[str, list] = {
        "CRITICAL": ["VIOLENCE_THREAT", "SEXUAL_HARASSMENT"],
        "HIGH": ["PROFANITY", "HATE_SPEECH"],
        "MEDIUM": ["UNREASONABLE_DEMAND", "REPETITION"]
    }
    
    # Label별 이벤트 설정
    EVENT_CONFIG: Dict[str, Dict[str, any]] = {
        "VIOLENCE_THREAT": {
            "action": "TERMINATE_CALL",
            "alert_level": "CRITICAL",
            "recording": True,
            "legal_review": True
        },
        "SEXUAL_HARASSMENT": {
            "action": "TERMINATE_CALL",
            "alert_level": "CRITICAL",
            "recording": True,
            "legal_review": True
        },
        "PROFANITY": {
            "action": "WARN",
            "alert_level": "HIGH",
            "terminate_on_repeat": True
        },
        "HATE_SPEECH": {
            "action": "WARN",
            "alert_level": "HIGH",
            "terminate_on_repeat": True
        },
        "UNREASONABLE_DEMAND": {
            "action": "SUPPORT_AGENT",
            "alert_level": "MEDIUM",
            "provide_guidance": True
        },
        "REPETITION": {
            "action": "SUPPORT_AGENT",
            "alert_level": "MEDIUM",
            "provide_strategy": True
        }
    }
    
    @staticmethod
    def get_severity(label: str) -> str:
        """
        Label별 심각도 반환
        
        Args:
            label: 특수 Label
        
        Returns:
            심각도 (CRITICAL, HIGH, MEDIUM)
        """
        for severity, labels in FilteringBaselineRules.SEVERITY_MAP.items():
            if label in labels:
                return severity
        return "MEDIUM"
    
    @staticmethod
    def get_event_config(label: str) -> Dict[str, any]:
        """
        Label별 이벤트 설정 반환
        
        Args:
            label: 특수 Label
        
        Returns:
            이벤트 설정 딕셔너리
        """
        return FilteringBaselineRules.EVENT_CONFIG.get(label, {
            "action": "MONITOR",
            "alert_level": "MEDIUM"
        })


