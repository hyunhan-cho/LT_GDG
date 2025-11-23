"""
상담원 발화 Turn 특징점 추출기

해당 Turn 내에서만 추출 가능한 특징점을 추출
"""

from typing import Dict, Any


class AgentFeatureExtractor:
    """상담원 발화 Turn 특징점 추출기"""
    
    def __init__(self):
        """특징점 추출기 초기화"""
        # 향후 매뉴얼 데이터 로드 예정
        pass
    
    def extract_features(
        self,
        text: str,
        customer_label: str
    ) -> tuple[Dict[str, float], Dict[str, Any], Dict[str, Any]]:
        """
        상담원 발화 Turn 특징점 추출
        
        Args:
            text: 해당 Turn의 발화
            customer_label: 해당 손님 발화의 Label
        
        Returns:
            (feature_scores, compliance_details, extracted_features)
            - feature_scores: 특징점 점수 딕셔너리
            - compliance_details: 매뉴얼 준수 상세 정보
            - extracted_features: 추출된 특징점 상세 정보
        """
        feature_scores = {}
        compliance_details = {}
        extracted_features = {}
        
        # 1. 매뉴얼 준수도 평가 (향후 구현)
        compliance_score, compliance_info = self._evaluate_manual_compliance(text, customer_label)
        feature_scores["manual_compliance_score"] = compliance_score
        compliance_details.update(compliance_info)
        
        # 2. 정보 제공 정확성 평가
        info_score = self._evaluate_information_accuracy(text, customer_label)
        feature_scores["information_accuracy_score"] = info_score
        
        # 3. 소통 명확성 평가
        clarity_score = self._evaluate_communication_clarity(text)
        feature_scores["communication_clarity_score"] = clarity_score
        
        # 4. 공감 표현 평가
        empathy_score, empathy_keywords = self._evaluate_empathy(text, customer_label)
        feature_scores["empathy_score"] = empathy_score
        if empathy_keywords:
            extracted_features["empathy_keywords"] = empathy_keywords
        
        # 5. 문제 해결 방안 제시 평가
        problem_solving_score, solution_keywords = self._evaluate_problem_solving(text, customer_label)
        feature_scores["problem_solving_score"] = problem_solving_score
        if solution_keywords:
            extracted_features["solution_keywords"] = solution_keywords
        
        return feature_scores, compliance_details, extracted_features
    
    def _evaluate_manual_compliance(self, text: str, customer_label: str) -> tuple[float, Dict[str, Any]]:
        """매뉴얼 준수도 평가 (향후 구현)"""
        # 임시 구현: 기본 점수 반환
        compliance_details = {
            "phrase_score": 0.7,
            "keyword_score": 0.7,
            "procedure_score": 0.7,
            "complied_items": [],
            "non_complied_items": []
        }
        return 0.7, compliance_details
    
    def _evaluate_information_accuracy(self, text: str, customer_label: str) -> float:
        """정보 제공 정확성 평가"""
        # 임시 구현: 키워드 기반 확인
        accuracy_keywords = ["안내", "확인", "정보", "처리", "절차"]
        text_lower = text.lower()
        found_count = sum(1 for kw in accuracy_keywords if kw in text_lower)
        
        if found_count > 0:
            return min(0.7 + found_count * 0.1, 1.0)
        return 0.5
    
    def _evaluate_communication_clarity(self, text: str) -> float:
        """소통 명확성 평가"""
        # 임시 구현: 문장 길이 및 구조 확인
        if not text:
            return 0.0
        
        words = text.split()
        if len(words) < 3:
            return 0.4  # 너무 짧음
        elif len(words) > 50:
            return 0.6  # 너무 김
        else:
            return 0.8  # 적절함
    
    def _evaluate_empathy(self, text: str, customer_label: str) -> tuple[float, list[str]]:
        """공감 표현 평가"""
        # 임시 구현: 공감 키워드 확인
        empathy_keywords = ["죄송", "불편", "이해", "공감", "안타깝"]
        text_lower = text.lower()
        found_keywords = [kw for kw in empathy_keywords if kw in text_lower]
        
        if not found_keywords:
            return 0.3, []
        elif len(found_keywords) >= 2:
            return 1.0, found_keywords
        else:
            return 0.6, found_keywords
    
    def _evaluate_problem_solving(self, text: str, customer_label: str) -> tuple[float, list[str]]:
        """문제 해결 방안 제시 평가"""
        # 임시 구현: 해결 키워드 확인
        solution_keywords = ["해결", "방안", "제시", "처리", "조치", "대안"]
        text_lower = text.lower()
        found_keywords = [kw for kw in solution_keywords if kw in text_lower]
        
        if not found_keywords:
            return 0.3, []
        elif len(found_keywords) >= 2:
            return 1.0, found_keywords
        else:
            return 0.6, found_keywords

