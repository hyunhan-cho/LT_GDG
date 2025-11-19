"""
세션 관리

대화 맥락을 저장하고 관리
"""

from typing import Dict, List, Optional


class SessionManager:
    """세션 매니저"""
    
    def __init__(self):
        """
        세션 매니저 초기화
        """
        self.sessions: Dict[str, List[str]] = {}
    
    def create_session(self, session_id: str):
        """
        세션 생성
        
        Args:
            session_id: 세션 ID
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
    
    def add_sentence(self, session_id: str, sentence: str):
        """
        문장 추가
        
        Args:
            session_id: 세션 ID
            sentence: 추가할 문장
        """
        if session_id not in self.sessions:
            self.create_session(session_id)
        self.sessions[session_id].append(sentence)
    
    def get_context(self, session_id: str, window_size: int = 5) -> List[str]:
        """
        세션 맥락 반환 (최근 N개 문장)
        
        Args:
            session_id: 세션 ID
            window_size: 반환할 최근 문장 수
        
        Returns:
            최근 문장 리스트
        """
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id][-window_size:]
    
    def clear_session(self, session_id: str):
        """
        세션 초기화
        
        Args:
            session_id: 세션 ID
        """
        if session_id in self.sessions:
            del self.sessions[session_id]


