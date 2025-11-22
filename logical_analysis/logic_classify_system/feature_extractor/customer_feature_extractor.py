"""
손님 발화 Turn 특징점 추출기

해당 Turn 내에서만 추출 가능한 특징점을 추출
"""

from typing import Dict, Any
from ..data.data_structures import ProfanityResult, ClassificationResult
from ..profanity_filter.baseline_rules import ProfanityBaselineRules
from ..intent_classifier.baseline_rules import IntentBaselineRules


class CustomerFeatureExtractor:
    """손님 발화 Turn 특징점 추출기"""
    
    def __init__(self):
        """특징점 추출기 초기화"""
        self.profanity_rules = ProfanityBaselineRules()
        self.intent_rules = IntentBaselineRules()
    
    def extract_features(
        self,
        text: str,
        profanity_result: ProfanityResult,
        classification_result: ClassificationResult
    ) -> tuple[Dict[str, float], Dict[str, Any]]:
        """
        손님 발화 Turn 특징점 추출
        
        Args:
            text: 해당 Turn의 발화
            profanity_result: 욕설 감지 결과
            classification_result: 분류 결과
        
        Returns:
            (feature_scores, extracted_features)
            - feature_scores: 특징점 점수 딕셔너리
            - extracted_features: 추출된 특징점 상세 정보
        """
        text_lower = text.lower()
        feature_scores = {}
        extracted_features = {}
        
        # 1. 욕설 관련 특징점 추출
        feature_scores["profanity_score"] = profanity_result.confidence if profanity_result.is_profanity else 0.0
        if profanity_result.is_profanity:
            extracted_features["profanity_keywords"] = self._extract_profanity_keywords(text)
            extracted_features["profanity_category"] = profanity_result.category
        
        # 2. 위협 표현 특징점 추출
        threat_score, threat_patterns = self._extract_threat_features(text)
        feature_scores["threat_score"] = threat_score
        if threat_patterns:
            extracted_features["threat_patterns"] = threat_patterns
        
        # 3. 성희롱 표현 특징점 추출
        sexual_score, sexual_keywords = self._extract_sexual_harassment_features(text)
        feature_scores["sexual_harassment_score"] = sexual_score
        if sexual_keywords:
            extracted_features["sexual_keywords"] = sexual_keywords
        
        # 4. 혐오표현 특징점 추출
        hate_score, hate_keywords = self._extract_hate_speech_features(text)
        feature_scores["hate_speech_score"] = hate_score
        if hate_keywords:
            extracted_features["hate_keywords"] = hate_keywords
        
        # 5. 무리한 요구 특징점 추출
        unreasonable_score, unreasonable_keywords = self._extract_unreasonable_demand_features(text)
        feature_scores["unreasonable_demand_score"] = unreasonable_score
        if unreasonable_keywords:
            extracted_features["unreasonable_keywords"] = unreasonable_keywords
        
        # 6. 반복 표현 키워드 특징점 추출 (Turn 단위: 키워드만)
        repetition_keyword_score, repetition_keywords = self._extract_repetition_keyword_features(text)
        feature_scores["repetition_keyword_score"] = repetition_keyword_score
        if repetition_keywords:
            extracted_features["repetition_keywords"] = repetition_keywords
        
        # 7. Normal Label 분류 신뢰도
        if classification_result.label_type == "NORMAL":
            feature_scores["normal_label_confidence"] = classification_result.confidence
        else:
            feature_scores["normal_label_confidence"] = 0.0
        
        return feature_scores, extracted_features
    
    def _extract_profanity_keywords(self, text: str) -> list[str]:
        """욕설 키워드 추출"""
        text_lower = text.lower()
        found_keywords = [
            kw for kw in ProfanityBaselineRules.PROFANITY_KEYWORDS 
            if kw in text_lower
        ]
        return found_keywords
    
    def _extract_threat_features(self, text: str) -> tuple[float, list[str]]:
        """위협 표현 특징점 추출"""
        text_lower = text.lower()
        found_keywords = [
            kw for kw in ProfanityBaselineRules.THREAT_KEYWORDS 
            if kw in text_lower
        ]
        if found_keywords:
            score = min(0.7 + len(found_keywords) * 0.15, 1.0)
            return score, found_keywords
        return 0.0, []
    
    def _extract_sexual_harassment_features(self, text: str) -> tuple[float, list[str]]:
        """성희롱 표현 특징점 추출"""
        text_lower = text.lower()
        found_keywords = [
            kw for kw in ProfanityBaselineRules.SEXUAL_HARASSMENT_KEYWORDS 
            if kw in text_lower
        ]
        if found_keywords:
            score = min(0.6 + len(found_keywords) * 0.2, 1.0)
            return score, found_keywords
        return 0.0, []
    
    def _extract_hate_speech_features(self, text: str) -> tuple[float, list[str]]:
        """혐오표현 특징점 추출"""
        text_lower = text.lower()
        found_keywords = []
        for category, keywords in ProfanityBaselineRules.HATE_SPEECH_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    found_keywords.append(f"{category}:{kw}")
        
        if found_keywords:
            score = min(0.6 + len(found_keywords) * 0.15, 1.0)
            return score, found_keywords
        return 0.0, []
    
    def _extract_unreasonable_demand_features(self, text: str) -> tuple[float, list[str]]:
        """무리한 요구 특징점 추출"""
        text_lower = text.lower()
        found_keywords = []
        
        # 강한 표현
        strong_keywords = [
            kw for kw in IntentBaselineRules.UNREASONABLE_DEMAND_STRONG 
            if kw in text_lower
        ]
        found_keywords.extend(strong_keywords)
        
        # 일반 표현
        normal_keywords = [
            kw for kw in IntentBaselineRules.UNREASONABLE_DEMAND_INDICATORS 
            if kw in text_lower
        ]
        found_keywords.extend(normal_keywords)
        
        if found_keywords:
            if strong_keywords:
                score = min(0.7 + len(strong_keywords) * 0.1, 1.0)
            elif len(normal_keywords) >= 2:
                score = min(0.4 + len(normal_keywords) * 0.2, 1.0)
            else:
                score = 0.3
            return score, found_keywords
        return 0.0, []
    
    def _extract_repetition_keyword_features(self, text: str) -> tuple[float, list[str]]:
        """반복 표현 키워드 특징점 추출 (Turn 단위: 키워드만)"""
        text_lower = text.lower()
        found_keywords = [
            kw for kw in IntentBaselineRules.REPETITION_INDICATORS 
            if kw in text_lower
        ]
        if found_keywords:
            # 키워드만으로 감지 (실제 반복 여부는 후속 모듈에서 판단)
            score = min(0.4 + len(found_keywords) * 0.2, 0.8)
            return score, found_keywords
        return 0.0, []

