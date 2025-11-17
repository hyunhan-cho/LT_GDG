"""
알림 시스템

경고, 통화 중단 등의 알림 발송
"""

from typing import List
from .event_generator import FilteringEvent


class AlertSystem:
    """알림 시스템"""
    
    def __init__(self):
        """
        알림 시스템 초기화
        """
        self.alert_history: List[FilteringEvent] = []
    
    def send_alert(self, event: FilteringEvent):
        """
        알림 발송
        
        Args:
            event: 필터링 이벤트
        """
        # 알림 이력 저장
        self.alert_history.append(event)
        
        if event.alert_level == "CRITICAL":
            self._send_critical_alert(event)
        elif event.alert_level == "HIGH":
            self._send_high_alert(event)
        elif event.alert_level == "MEDIUM":
            self._send_medium_alert(event)
        else:
            self._send_low_alert(event)
    
    def _send_critical_alert(self, event: FilteringEvent):
        """
        CRITICAL 알림 발송 (즉시 통화 중단)
        
        Args:
            event: 필터링 이벤트
        """
        print(f"[CRITICAL ALERT] {event.label} 감지")
        print(f"  텍스트: {event.text}")
        print(f"  조치: {event.action}")
        print(f"  심각도: {event.severity}")
        
        if event.config.get("recording", False):
            print("  → 녹음 보관 필요")
        
        if event.config.get("legal_review", False):
            print("  → 법적 검토 필요")
        
        # 실제 구현 시:
        # - 상담사에게 즉시 알림
        # - 관리자에게 알림
        # - 통화 중단 명령 전송
        # - 로그 기록
    
    def _send_high_alert(self, event: FilteringEvent):
        """
        HIGH 알림 발송 (경고)
        
        Args:
            event: 필터링 이벤트
        """
        print(f"[HIGH ALERT] {event.label} 감지")
        print(f"  텍스트: {event.text}")
        print(f"  조치: {event.action}")
        
        if event.config.get("terminate_on_repeat", False):
            print("  → 반복 시 통화 중단 경고")
        
        # 실제 구현 시:
        # - 상담사에게 경고 알림
        # - 반복 시 통화 중단 경고
        # - 로그 기록
    
    def _send_medium_alert(self, event: FilteringEvent):
        """
        MEDIUM 알림 발송 (상담사 지원)
        
        Args:
            event: 필터링 이벤트
        """
        print(f"[MEDIUM ALERT] {event.label} 감지")
        print(f"  텍스트: {event.text}")
        print(f"  조치: {event.action}")
        
        if event.config.get("provide_guidance", False):
            print("  → 상담사 지원 가이드 제공")
        
        if event.config.get("provide_strategy", False):
            print("  → 대화 전환 전략 제시")
        
        # 실제 구현 시:
        # - 상담사에게 지원 가이드 제공
        # - 로그 기록
    
    def _send_low_alert(self, event: FilteringEvent):
        """
        LOW 알림 발송 (모니터링)
        
        Args:
            event: 필터링 이벤트
        """
        print(f"[LOW ALERT] {event.label} 감지")
        print(f"  텍스트: {event.text}")
        print(f"  조치: 모니터링")
        
        # 실제 구현 시:
        # - 로그 기록만


