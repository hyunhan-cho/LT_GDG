# 파이프라인 구현 파일 구조 설계

## 1. 전체 디렉토리 구조

```
linguaproject/logic_classify_system/
├── __init__.py
├── config/
│   ├── __init__.py
│   ├── labels.py                    # Label 정의 (Normal, Special)
│   ├── model_config.py              # 모델 설정 (KoSentenceBERT, Korcen)
│   └── evaluation_criteria.py       # 평가 기준 설정
├── preprocessing/
│   ├── __init__.py
│   ├── text_splitter.py             # 문장 단위 분할
│   └── tokenizer.py                 # Tokenization
├── profanity_filter/
│   ├── __init__.py
│   ├── korcen_filter.py             # Korcen 기반 욕설 필터
│   ├── baseline_rules.py            # 욕설 감지용 Baseline 규칙 (모듈 내부)
│   └── profanity_detector.py        # 욕설 감지 통합 인터페이스
├── intent_classifier/
│   ├── __init__.py
│   ├── kosentbert_classifier.py     # KoSentenceBERT 기반 분류기
│   ├── baseline_rules.py            # 발화 의도 분류용 Baseline 규칙 (모듈 내부)
│   └── intent_predictor.py          # 발화 의도 예측 통합 인터페이스
├── labeling/
│   ├── __init__.py
│   ├── label_router.py              # Label 기반 라우팅
│   └── label_utils.py               # Label 유틸리티 함수
├── evaluation/
│   ├── __init__.py
│   ├── normal_label_evaluator.py    # Normal Label 평가 프레임워크
│   ├── evaluation_criteria.py      # 평가 기준 정의
│   ├── manual_checker.py            # 매뉴얼 준수 확인
│   └── evaluation_result.py         # 평가 결과 데이터 구조
├── filtering/
│   ├── __init__.py
│   ├── special_label_filter.py      # 특수 Label 종합 필터링
│   ├── baseline_rules.py             # 종합 필터링용 Baseline 규칙 (모듈 내부)
│   ├── event_generator.py            # 이벤트 생성
│   └── alert_system.py               # 알림 시스템
├── pipeline/
│   ├── __init__.py
│   ├── main_pipeline.py             # 메인 파이프라인 오케스트레이터
│   └── pipeline_components.py       # 파이프라인 컴포넌트 인터페이스
├── models/
│   ├── __init__.py
│   └── kosentbert_model.py          # KoSentenceBERT 모델 래퍼
├── data/
│   ├── __init__.py
│   ├── data_structures.py           # 데이터 구조 정의
│   └── session_manager.py           # 세션 관리
├── utils/
│   ├── __init__.py
│   ├── logger.py                    # 로깅 유틸리티
│   └── exceptions.py                 # 커스텀 예외
├── tests/
│   ├── __init__.py
│   ├── test_profanity_filter.py
│   ├── test_intent_classifier.py
│   ├── test_label_router.py
│   ├── test_evaluation.py
│   └── test_filtering.py
└── main.py                           # 실행 진입점
```

---

## 2. 핵심 파일 상세 설계

### 2.1 설정 파일 (config/)

#### 2.1.1 `config/labels.py`

**역할**: Normal Label과 특수 Label 정의 및 관련 상수 관리

**주요 내용**:
```python
from enum import Enum

class NormalLabel(Enum):
    """Normal Label 정의"""
    INQUIRY = "INQUIRY"
    COMPLAINT = "COMPLAINT"
    REQUEST = "REQUEST"
    CLARIFICATION = "CLARIFICATION"
    CONFIRMATION = "CONFIRMATION"
    CLOSING = "CLOSING"

class SpecialLabel(Enum):
    """특수 Label 정의"""
    VIOLENCE_THREAT = "VIOLENCE_THREAT"
    SEXUAL_HARASSMENT = "SEXUAL_HARASSMENT"
    PROFANITY = "PROFANITY"
    HATE_SPEECH = "HATE_SPEECH"
    UNREASONABLE_DEMAND = "UNREASONABLE_DEMAND"
    REPETITION = "REPETITION"

# Label 타입 구분
NORMAL_LABELS = [label.value for label in NormalLabel]
SPECIAL_LABELS = [label.value for label in SpecialLabel]

# Label 설명 및 예시
LABEL_DESCRIPTIONS = {
    # Normal Labels
    "INQUIRY": {
        "description": "고객이 정보나 서비스에 대해 질문하는 발화",
        "examples": ["이 상품의 가격이 얼마인가요?", "환불 정책이 어떻게 되나요?"]
    },
    # ... (나머지 Label들)
}
```

**의존성**: 없음

**사용처**: 모든 모듈에서 Label 참조 시 사용

---

#### 2.1.2 `config/model_config.py`

**역할**: 모델 설정 및 하이퍼파라미터 관리

**주요 내용**:
```python
# KoSentenceBERT 설정
KOSENTBERT_CONFIG = {
    "model_name": "BM-K/KoSimCSE-roberta-multitask",
    "max_length": 512,
    "batch_size": 32,
    "device": "cuda" if torch.cuda.is_available() else "cpu"
}

# Korcen 설정
KORCEN_CONFIG = {
    "use_korcen": True,
    "fallback_to_baseline": True,
    "baseline_keywords_path": "data/profanity_keywords.txt"
}

# 평가 프레임워크 설정
EVALUATION_CONFIG = {
    "manual_path": "data/manual.json",
    "scoring_weights": {
        "information_accuracy": 0.3,
        "manual_compliance": 0.3,
        "communication_clarity": 0.2,
        "empathy": 0.1,
        "problem_solving": 0.1
    }
}
```

**의존성**: `torch` (PyTorch)

**사용처**: 모델 초기화 시 사용

---

#### 2.1.3 `config/evaluation_criteria.py`

**역할**: Normal Label별 평가 기준 정의

**주요 내용**:
```python
EVALUATION_CRITERIA = {
    "INQUIRY": {
        "criteria": [
            "information_accuracy",  # 정보 제공 정확성
            "manual_compliance",      # 매뉴얼 준수
            "communication_clarity"  # 소통 명확성
        ],
        "required_keywords": ["가격", "정책", "절차"],
        "required_phrases": ["안내드리겠습니다", "확인해보겠습니다"]
    },
    "COMPLAINT": {
        "criteria": [
            "empathy",               # 공감 능력
            "problem_solving",        # 문제 해결 능력
            "manual_compliance"      # 매뉴얼 준수
        ],
        "required_keywords": ["불편", "사과", "해결"],
        "required_phrases": ["불편을 드려 죄송합니다", "해결 방안을 제시하겠습니다"]
    },
    # ... (나머지 Label들)
}
```

**의존성**: 없음

**사용처**: `evaluation/normal_label_evaluator.py`

---

### 2.2 전처리 모듈 (preprocessing/)

#### 2.2.1 `preprocessing/text_splitter.py`

**역할**: STT 결과 텍스트를 문장 단위로 분할

**주요 함수**:
```python
class TextSplitter:
    def split_sentences(self, text: str) -> List[str]:
        """
        텍스트를 문장 단위로 분할
        
        Args:
            text: STT 결과 텍스트
        
        Returns:
            문장 리스트
        """
        pass
    
    def split_by_speaker(self, text: str) -> Tuple[List[str], List[str]]:
        """
        화자별로 문장 분할 (고객/상담사 구분)
        
        Returns:
            (customer_sentences, agent_sentences)
        """
        pass
```

**의존성**: `konlpy`, `spaCy` (한국어 문장 분할)

**사용처**: `pipeline/main_pipeline.py`

---

#### 2.2.2 `preprocessing/tokenizer.py`

**역할**: 텍스트 Tokenization (Korcen 필터용)

**주요 함수**:
```python
class Tokenizer:
    def tokenize(self, text: str) -> List[str]:
        """
        텍스트를 토큰으로 분할
        
        Args:
            text: 입력 텍스트
        
        Returns:
            토큰 리스트
        """
        pass
    
    def normalize(self, text: str) -> str:
        """
        텍스트 정규화 (띄어쓰기, 특수문자 처리)
        """
        pass
```

**의존성**: `konlpy`

**사용처**: `profanity_filter/korcen_filter.py`

---

### 2.3 욕설 필터 모듈 (profanity_filter/)

#### 2.3.1 `profanity_filter/korcen_filter.py`

**역할**: Korcen 라이브러리를 활용한 욕설 감지

**주요 클래스**:
```python
class KorcenFilter:
    def __init__(self, config: dict):
        """
        Korcen 필터 초기화
        
        Args:
            config: model_config.py의 KORCEN_CONFIG
        """
        pass
    
    def check_profanity(self, text: str) -> Tuple[bool, Optional[str], float]:
        """
        욕설 감지
        
        Returns:
            (is_profanity, category, confidence)
        """
        pass
    
    def filter_text(self, text: str) -> str:
        """
        욕설 필터링 (마스킹 또는 제거)
        """
        pass
```

**의존성**: `korcen` (또는 커스텀 `call_center_profanity_filter`)

**사용처**: `profanity_filter/profanity_detector.py`

---

#### 2.3.2 `profanity_filter/baseline_rules.py`

**역할**: 욕설 감지를 위한 Baseline 규칙만 포함 (모듈 내부)

**핵심 원칙**: 
- 모듈 독립성: 외부 파일(`classification_criteria.py`) 의존성 제거
- 필요한 규칙만 포함: 욕설, 모욕, 위협, 성희롱, 혐오 표현 관련 키워드만
- 제외 규칙: 반복성, 무리한 요구, 부당성 등은 다른 모듈에서 처리

**주요 클래스**:
```python
class ProfanityBaselineRules:
    """욕설 감지용 Baseline 규칙"""
    
    PROFANITY_KEYWORDS = [...]  # 욕설 키워드
    INSULT_KEYWORDS = [...]     # 모욕 키워드
    THREAT_KEYWORDS = [...]     # 위협 키워드
    SEXUAL_HARASSMENT_KEYWORDS = [...]  # 성희롱 키워드
    HATE_SPEECH_KEYWORDS = {...}  # 혐오 표현 키워드
    
    @staticmethod
    def detect_profanity(text: str) -> Tuple[bool, Optional[str], float]:
        """Baseline 규칙 기반 욕설 감지"""
        pass
```

**의존성**: 없음 (완전 독립)

**사용처**: `profanity_filter/profanity_detector.py`

---

#### 2.3.3 `profanity_filter/profanity_detector.py`

**역할**: 욕설 감지 통합 인터페이스 (Korcen + Baseline)

**주요 클래스**:
```python
class ProfanityDetector:
    def __init__(self, use_korcen: bool = True):
        """
        욕설 감지기 초기화
        
        Args:
            use_korcen: Korcen 사용 여부
        """
        self.korcen_filter = KorcenFilter(KORCEN_CONFIG) if use_korcen else None
        # Baseline 규칙은 모듈 내부에 포함 (의존성 없음)
        self.baseline_rules = ProfanityBaselineRules()
    
    def detect(self, text: str) -> ProfanityResult:
        """
        욕설 감지 (통합)
        
        Returns:
            ProfanityResult (is_profanity, category, confidence, method)
        """
        # 1. Korcen 시도
        if self.korcen_filter:
            try:
                result = self.korcen_filter.check_profanity(text)
                if result[0]:  # 욕설 감지
                    return ProfanityResult(True, result[1], result[2], "korcen")
            except Exception:
                # Korcen 실패 시 Baseline으로 폴백
                pass
        
        # 2. Baseline 규칙 사용 (모듈 내부 규칙)
        is_prof, category, confidence = self.baseline_rules.detect_profanity(text)
        if is_prof:
            return ProfanityResult(True, category, confidence, "baseline")
        
        return ProfanityResult(False, None, 0.0, None)
```

**의존성**: 
- `profanity_filter/korcen_filter.py`
- `profanity_filter/baseline_rules.py` (모듈 내부)

**사용처**: `pipeline/main_pipeline.py`

---

### 2.4 발화 의도 분류 모듈 (intent_classifier/)

#### 2.4.1 `intent_classifier/kosentbert_classifier.py`

**역할**: KoSentenceBERT 모델을 활용한 발화 의도 분류

**주요 클래스**:
```python
class KoSentenceBERTClassifier:
    def __init__(self, config: dict):
        """
        KoSentenceBERT 분류기 초기화
        
        Args:
            config: model_config.py의 KOSENTBERT_CONFIG
        """
        self.model = load_kosentbert_model(config["model_name"])
        self.tokenizer = load_tokenizer(config["model_name"])
        self.device = config["device"]
    
    def predict(self, text: str, context: Optional[List[str]] = None) -> IntentResult:
        """
        발화 의도 분류
        
        Args:
            text: 분석할 문장
            context: 대화 맥락 (선택)
        
        Returns:
            IntentResult (label, confidence, probabilities)
        """
        # 문장 임베딩 생성
        embedding = self.model.encode(text)
        
        # 분류 (Fine-tuned 모델 또는 유사도 기반)
        label, confidence = self._classify(embedding, context)
        
        return IntentResult(label, confidence, self._get_probabilities(embedding))
    
    def _classify(self, embedding: np.ndarray, context: Optional[List[str]]) -> Tuple[str, float]:
        """
        임베딩 기반 분류
        """
        pass
```

**의존성**: 
- `transformers`
- `sentence_transformers`
- `models/kosentbert_model.py`

**사용처**: `intent_classifier/intent_predictor.py`

---

#### 2.4.2 `intent_classifier/baseline_rules.py`

**역할**: 발화 의도 분류를 위한 Baseline 규칙 (특수 Label 감지용)

**포함 규칙**: 반복성, 무리한 요구, 부당성/무관성 감지 키워드

**주요 클래스**:
```python
class IntentBaselineRules:
    """발화 의도 분류용 Baseline 규칙"""
    
    REPETITION_INDICATORS = [...]  # 반복성 감지
    UNREASONABLE_DEMAND_STRONG = [...]  # 강한 무리한 요구
    UNREASONABLE_DEMAND_INDICATORS = [...]  # 일반 무리한 요구
    IRRELEVANCE_INDICATORS = [...]  # 부당성/무관성
    
    @staticmethod
    def detect_special_labels(text: str, session_context: Optional[List[str]] = None) -> List[Tuple[str, float]]:
        """특수 Label 감지 (Baseline 규칙 기반)"""
        pass
```

**의존성**: 없음 (완전 독립)

**사용처**: `intent_classifier/intent_predictor.py`

---

#### 2.4.3 `intent_classifier/intent_predictor.py`

**역할**: 발화 의도 예측 통합 인터페이스

**주요 클래스**:
```python
class IntentPredictor:
    def __init__(self):
        """
        발화 의도 예측기 초기화
        """
        self.classifier = KoSentenceBERTClassifier(KOSENTBERT_CONFIG)
        # Baseline 규칙은 모듈 내부에 포함
        self.baseline_rules = IntentBaselineRules()
    
    def predict(self, text: str, profanity_detected: bool, 
                session_context: Optional[List[str]] = None) -> ClassificationResult:
        """
        발화 의도 예측 (통합)
        """
        # 욕설 감지 시 즉시 특수 Label 반환
        if profanity_detected:
            return ClassificationResult(
                label="PROFANITY",
                label_type="SPECIAL",
                confidence=1.0,
                text=text
            )
        
        # Baseline 규칙으로 특수 Label 사전 감지
        baseline_results = self.baseline_rules.detect_special_labels(text, session_context)
        if baseline_results:
            # 가장 높은 신뢰도의 Label 선택
            label, confidence = max(baseline_results, key=lambda x: x[1])
            return ClassificationResult(
                label=label,
                label_type="SPECIAL",
                confidence=confidence,
                text=text
            )
        
        # KoSentenceBERT로 Normal Label 분류
        intent_result = self.classifier.predict(text, session_context)
        
        # Label 타입 결정
        label_type = self._determine_label_type(intent_result.label)
        
        return ClassificationResult(
            label=intent_result.label,
            label_type=label_type,
            confidence=intent_result.confidence,
            text=text
        )
```

**의존성**:
- `intent_classifier/kosentbert_classifier.py`
- `intent_classifier/baseline_rules.py` (모듈 내부)
- `config/labels.py`

**사용처**: `pipeline/main_pipeline.py`

---

### 2.5 Label 라우팅 모듈 (labeling/)

#### 2.5.1 `labeling/label_router.py`

**역할**: Label에 따라 적절한 처리 경로로 라우팅

**주요 클래스**:
```python
class LabelRouter:
    def __init__(self):
        """
        Label 라우터 초기화
        """
        self.evaluator = NormalLabelEvaluator()
        self.filter = SpecialLabelFilter()
    
    def route(self, classification_result: ClassificationResult, 
              session_context: Optional[List[str]] = None) -> RouterResult:
        """
        Label 기반 라우팅
        
        Args:
            classification_result: 분류 결과
            session_context: 세션 맥락
        
        Returns:
            RouterResult (route_type, result)
        """
        if classification_result.label_type == "NORMAL":
            # 평가 프레임워크로 이동
            evaluation_result = self.evaluator.evaluate(
                classification_result.label,
                classification_result.text,
                session_context
            )
            return RouterResult("EVALUATION", evaluation_result)
        
        elif classification_result.label_type == "SPECIAL":
            # 종합 필터링으로 이동
            filtering_result = self.filter.filter(
                classification_result.label,
                classification_result.text,
                session_context
            )
            return RouterResult("FILTERING", filtering_result)
        
        else:
            # 알 수 없는 Label
            return RouterResult("UNKNOWN", None)
```

**의존성**:
- `evaluation/normal_label_evaluator.py`
- `filtering/special_label_filter.py`
- `config/labels.py`

**사용처**: `pipeline/main_pipeline.py`

---

#### 2.5.2 `labeling/label_utils.py`

**역할**: Label 관련 유틸리티 함수

**주요 함수**:
```python
def is_normal_label(label: str) -> bool:
    """Normal Label 여부 확인"""
    pass

def is_special_label(label: str) -> bool:
    """특수 Label 여부 확인"""
    pass

def get_label_description(label: str) -> str:
    """Label 설명 반환"""
    pass

def get_label_examples(label: str) -> List[str]:
    """Label 예시 반환"""
    pass
```

**의존성**: `config/labels.py`

**사용처**: 여러 모듈에서 공통 사용

---

### 2.6 평가 프레임워크 모듈 (evaluation/)

#### 2.6.1 `evaluation/normal_label_evaluator.py`

**역할**: Normal Label에 대한 상담사 평가

**주요 클래스**:
```python
class NormalLabelEvaluator:
    def __init__(self):
        """
        평가 프레임워크 초기화
        """
        self.manual_checker = ManualChecker()
        self.criteria = EvaluationCriteria()
    
    def evaluate(self, label: str, customer_text: str, 
                  agent_text: str, session_context: List[str]) -> EvaluationResult:
        """
        Normal Label 평가
        
        Args:
            label: Normal Label
            customer_text: 고객 발화
            agent_text: 상담사 발화
            session_context: 세션 맥락
        
        Returns:
            EvaluationResult (score, criteria_scores, feedback, recommendations)
        """
        # 평가 기준 가져오기
        criteria = self.criteria.get_criteria(label)
        
        # 각 기준별 점수 계산
        criteria_scores = {}
        for criterion in criteria:
            score = self._evaluate_criterion(criterion, label, customer_text, agent_text, session_context)
            criteria_scores[criterion] = score
        
        # 종합 점수 계산
        total_score = self._calculate_total_score(criteria_scores, criteria)
        
        # 피드백 생성
        feedback = self._generate_feedback(label, criteria_scores, total_score)
        
        # 개선 제안 생성
        recommendations = self._generate_recommendations(label, criteria_scores)
        
        return EvaluationResult(
            label=label,
            score=total_score,
            criteria_scores=criteria_scores,
            feedback=feedback,
            recommendations=recommendations
        )
    
    def _evaluate_criterion(self, criterion: str, label: str, 
                           customer_text: str, agent_text: str, 
                           session_context: List[str]) -> float:
        """
        개별 기준 평가
        """
        if criterion == "manual_compliance":
            return self.manual_checker.check_compliance(label, agent_text)
        elif criterion == "information_accuracy":
            return self._check_information_accuracy(label, agent_text)
        # ... (나머지 기준들)
    
    def _calculate_total_score(self, criteria_scores: Dict[str, float], 
                              criteria: List[str]) -> float:
        """
        종합 점수 계산 (가중치 적용)
        """
        weights = EVALUATION_CONFIG["scoring_weights"]
        total = 0.0
        for criterion in criteria:
            total += criteria_scores[criterion] * weights.get(criterion, 0.0)
        return total
```

**의존성**:
- `evaluation/manual_checker.py`
- `evaluation/evaluation_criteria.py`
- `config/evaluation_criteria.py`
- `config/model_config.py`

**사용처**: `labeling/label_router.py`

---

#### 2.6.2 `evaluation/manual_checker.py`

**역할**: 매뉴얼 준수 여부 확인

**주요 클래스**:
```python
class ManualChecker:
    def __init__(self, manual_path: str):
        """
        매뉴얼 체커 초기화
        
        Args:
            manual_path: 매뉴얼 JSON 파일 경로
        """
        self.manual = self._load_manual(manual_path)
    
    def check_compliance(self, label: str, agent_text: str) -> float:
        """
        매뉴얼 준수 여부 확인
        
        Returns:
            점수 (0.0-1.0)
        """
        # Label별 필수 표현 확인
        required_phrases = self.manual[label]["required_phrases"]
        required_keywords = self.manual[label]["required_keywords"]
        
        # 필수 표현 사용 여부 확인
        phrase_score = self._check_phrases(agent_text, required_phrases)
        keyword_score = self._check_keywords(agent_text, required_keywords)
        
        # 절차 순서 확인
        procedure_score = self._check_procedure(label, agent_text)
        
        # 종합 점수
        return (phrase_score * 0.4 + keyword_score * 0.3 + procedure_score * 0.3)
```

**의존성**: `config/evaluation_criteria.py`

**사용처**: `evaluation/normal_label_evaluator.py`

---

#### 2.6.3 `evaluation/evaluation_result.py`

**역할**: 평가 결과 데이터 구조 정의

**주요 내용**:
```python
@dataclass
class EvaluationResult:
    """평가 결과"""
    label: str                         # Normal Label
    score: float                       # 종합 점수 (0-100)
    criteria_scores: Dict[str, float]  # 항목별 점수
    feedback: str                     # 피드백 메시지
    recommendations: List[str]         # 개선 제안
    timestamp: datetime               # 평가 시간
    session_id: str                   # 세션 ID
```

**의존성**: 없음

**사용처**: 모든 평가 관련 모듈

---

### 2.7 종합 필터링 모듈 (filtering/)

#### 2.7.1 `filtering/baseline_rules.py`

**역할**: 종합 필터링을 위한 Baseline 규칙 (이벤트 생성 시 참고용)

**포함 규칙**: 모든 특수 Label 관련 심각도 판단 및 이벤트 설정

**주요 클래스**:
```python
class FilteringBaselineRules:
    """종합 필터링용 Baseline 규칙"""
    
    SEVERITY_MAP = {...}  # 심각도별 Label 매핑
    EVENT_CONFIG = {...}  # Label별 이벤트 설정
    
    @staticmethod
    def get_severity(label: str) -> str:
        """Label별 심각도 반환"""
        pass
    
    @staticmethod
    def get_event_config(label: str) -> dict:
        """Label별 이벤트 설정 반환"""
        pass
```

**의존성**: 없음 (완전 독립)

**사용처**: `filtering/special_label_filter.py`, `filtering/event_generator.py`

---

#### 2.7.2 `filtering/special_label_filter.py`

**역할**: 특수 Label에 대한 종합 필터링 및 이벤트 생성

**주요 클래스**:
```python
class SpecialLabelFilter:
    def __init__(self):
        """
        특수 Label 필터 초기화
        """
        self.event_generator = EventGenerator()
        self.alert_system = AlertSystem()
        # Baseline 규칙은 모듈 내부에 포함
        self.baseline_rules = FilteringBaselineRules()
    
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
            action=event.action,
            alert_level=event.alert_level,
            event=event
        )
```

**의존성**:
- `filtering/event_generator.py`
- `filtering/alert_system.py`
- `filtering/baseline_rules.py` (모듈 내부)

**사용처**: `labeling/label_router.py`

---

#### 2.7.3 `filtering/event_generator.py`

**역할**: 특수 Label에 따른 이벤트 생성

**주요 클래스**:
```python
class EventGenerator:
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
        
        Returns:
            FilteringEvent
        """
        # Label별 이벤트 설정 (모듈 내부 규칙 사용)
        event_config = self.baseline_rules.get_event_config(label)
        
        return FilteringEvent(
            label=label,
            severity=severity,
            action=event_config["action"],
            alert_level=event_config["alert_level"],
            text=text,
            session_context=session_context,
            timestamp=datetime.now()
        )
```

**의존성**: 
- `filtering/baseline_rules.py` (모듈 내부)
- `data/data_structures.py`

**사용처**: `filtering/special_label_filter.py`

---

#### 2.7.4 `filtering/alert_system.py`

**역할**: 알림 시스템 (경고, 통화 중단 등)

**주요 클래스**:
```python
class AlertSystem:
    def send_alert(self, event: FilteringEvent):
        """
        알림 발송
        
        Args:
            event: 필터링 이벤트
        """
        if event.alert_level == "CRITICAL":
            self._send_critical_alert(event)
        elif event.alert_level == "HIGH":
            self._send_high_alert(event)
        elif event.alert_level == "MEDIUM":
            self._send_medium_alert(event)
    
    def _send_critical_alert(self, event: FilteringEvent):
        """
        CRITICAL 알림 발송 (즉시 통화 중단)
        """
        # 상담사에게 알림
        # 관리자에게 알림
        # 통화 중단 명령
        pass
    
    def _send_high_alert(self, event: FilteringEvent):
        """
        HIGH 알림 발송 (경고)
        """
        # 상담사에게 경고 알림
        # 반복 시 통화 중단 경고
        pass
    
    def _send_medium_alert(self, event: FilteringEvent):
        """
        MEDIUM 알림 발송 (상담사 지원)
        """
        # 상담사에게 지원 가이드 제공
        pass
```

**의존성**: `filtering/event_generator.py`

**사용처**: `filtering/special_label_filter.py`

---

### 2.8 파이프라인 오케스트레이터 (pipeline/)

#### 2.8.1 `pipeline/main_pipeline.py`

**역할**: 전체 파이프라인 오케스트레이션

**주요 클래스**:
```python
class MainPipeline:
    def __init__(self):
        """
        메인 파이프라인 초기화
        """
        self.text_splitter = TextSplitter()
        self.profanity_detector = ProfanityDetector()
        self.intent_predictor = IntentPredictor()
        self.label_router = LabelRouter()
        self.session_manager = SessionManager()
    
    def process(self, audio_path: str, session_id: str) -> PipelineResult:
        """
        전체 파이프라인 실행
        
        Args:
            audio_path: 음성 파일 경로
            session_id: 세션 ID
        
        Returns:
            PipelineResult (전체 처리 결과)
        """
        # 1. STT (외부 모듈)
        text = self._stt(audio_path)
        
        # 2. 문장 단위 분할
        sentences = self.text_splitter.split_sentences(text)
        customer_sentences, agent_sentences = self.text_splitter.split_by_speaker(text)
        
        # 3. 각 문장 처리
        results = []
        for sentence in customer_sentences:
            # 1차: 욕설 필터링
            profanity_result = self.profanity_detector.detect(sentence)
            
            # 2차: 발화 의도 분류
            classification_result = self.intent_predictor.predict(
                sentence, 
                profanity_result.is_profanity,
                self.session_manager.get_context(session_id)
            )
            
            # Label 기반 라우팅
            router_result = self.label_router.route(
                classification_result,
                self.session_manager.get_context(session_id)
            )
            
            results.append(router_result)
            
            # 세션 맥락 업데이트
            self.session_manager.add_sentence(session_id, sentence)
        
        return PipelineResult(session_id, results)
```

**의존성**: 모든 핵심 모듈

**사용처**: `main.py`

---

#### 2.8.2 `pipeline/pipeline_components.py`

**역할**: 파이프라인 컴포넌트 인터페이스 정의

**주요 내용**:
```python
from abc import ABC, abstractmethod

class PipelineComponent(ABC):
    """파이프라인 컴포넌트 인터페이스"""
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """처리 메서드"""
        pass

class TextProcessor(PipelineComponent):
    """텍스트 처리 컴포넌트"""
    pass

class Classifier(PipelineComponent):
    """분류 컴포넌트"""
    pass
```

**의존성**: 없음

**사용처**: 파이프라인 확장 시 사용

---

### 2.9 모델 래퍼 (models/)

#### 2.9.1 `models/kosentbert_model.py`

**역할**: KoSentenceBERT 모델 로드 및 관리

**주요 함수**:
```python
def load_kosentbert_model(model_name: str) -> Any:
    """
    KoSentenceBERT 모델 로드
    
    Args:
        model_name: 모델 이름 (예: "BM-K/KoSimCSE-roberta-multitask")
    
    Returns:
        로드된 모델
    """
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name)

def load_tokenizer(model_name: str) -> Any:
    """
    토크나이저 로드
    """
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(model_name)
```

**의존성**: `sentence_transformers`, `transformers`

**사용처**: `intent_classifier/kosentbert_classifier.py`

---

### 2.10 데이터 구조 (data/)

#### 2.10.1 `data/data_structures.py`

**역할**: 모든 데이터 구조 정의

**주요 내용**:
```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class ClassificationResult:
    """분류 결과"""
    label: str
    label_type: str  # "NORMAL" or "SPECIAL"
    confidence: float
    text: str
    probabilities: Optional[Dict[str, float]] = None
    timestamp: datetime = None

@dataclass
class ProfanityResult:
    """욕설 감지 결과"""
    is_profanity: bool
    category: Optional[str]
    confidence: float
    method: Optional[str]  # "korcen" or "baseline"

@dataclass
class EvaluationResult:
    """평가 결과"""
    label: str
    score: float
    criteria_scores: Dict[str, float]
    feedback: str
    recommendations: List[str]
    timestamp: datetime = None

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

@dataclass
class PipelineResult:
    """파이프라인 결과"""
    session_id: str
    results: List[Any]
    timestamp: datetime = None
```

**의존성**: 없음

**사용처**: 모든 모듈

---

#### 2.10.2 `data/session_manager.py`

**역할**: 세션 관리 (대화 맥락 저장)

**주요 클래스**:
```python
class SessionManager:
    def __init__(self):
        """
        세션 매니저 초기화
        """
        self.sessions: Dict[str, List[str]] = {}
    
    def create_session(self, session_id: str):
        """세션 생성"""
        self.sessions[session_id] = []
    
    def add_sentence(self, session_id: str, sentence: str):
        """문장 추가"""
        if session_id not in self.sessions:
            self.create_session(session_id)
        self.sessions[session_id].append(sentence)
    
    def get_context(self, session_id: str, window_size: int = 5) -> List[str]:
        """
        세션 맥락 반환 (최근 N개 문장)
        """
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id][-window_size:]
```

**의존성**: 없음

**사용처**: `pipeline/main_pipeline.py`

---

### 2.11 유틸리티 (utils/)

#### 2.11.1 `utils/logger.py`

**역할**: 로깅 유틸리티

**주요 내용**:
```python
import logging

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    로거 설정
    
    Args:
        name: 로거 이름
        log_file: 로그 파일 경로 (선택)
    
    Returns:
        설정된 로거
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 파일 핸들러 (선택)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    
    logger.addHandler(console_handler)
    return logger
```

**의존성**: `logging`

**사용처**: 모든 모듈

---

#### 2.11.2 `utils/exceptions.py`

**역할**: 커스텀 예외 정의

**주요 내용**:
```python
class PipelineError(Exception):
    """파이프라인 오류"""
    pass

class ModelLoadError(PipelineError):
    """모델 로드 오류"""
    pass

class ClassificationError(PipelineError):
    """분류 오류"""
    pass

class EvaluationError(PipelineError):
    """평가 오류"""
    pass
```

**의존성**: 없음

**사용처**: 모든 모듈

---

### 2.12 실행 진입점 (main.py)

#### 2.12.1 `main.py`

**역할**: 프로그램 실행 진입점

**주요 내용**:
```python
from pipeline.main_pipeline import MainPipeline
from utils.logger import setup_logger

def main():
    """
    메인 함수
    """
    logger = setup_logger("main")
    
    # 파이프라인 초기화
    pipeline = MainPipeline()
    
    # 예제 실행
    audio_path = "sample_audio.wav"
    session_id = "session_001"
    
    try:
        result = pipeline.process(audio_path, session_id)
        logger.info(f"처리 완료: {result}")
    except Exception as e:
        logger.error(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
```

**의존성**: `pipeline/main_pipeline.py`

---

## 3. 파일 간 의존성 관계

```
main.py
  └── pipeline/main_pipeline.py
        ├── preprocessing/text_splitter.py
        ├── profanity_filter/profanity_detector.py
        │     ├── profanity_filter/korcen_filter.py
        │     └── classification_criteria.py (Baseline)
        ├── intent_classifier/intent_predictor.py
        │     └── intent_classifier/kosentbert_classifier.py
        │           └── models/kosentbert_model.py
        ├── labeling/label_router.py
        │     ├── evaluation/normal_label_evaluator.py
        │     │     ├── evaluation/manual_checker.py
        │     │     └── config/evaluation_criteria.py
        │     └── filtering/special_label_filter.py
        │           ├── filtering/event_generator.py
        │           └── filtering/alert_system.py
        └── data/session_manager.py
```

---

## 4. 구현 우선순위

### Phase 1: 핵심 파이프라인
1. `config/labels.py` - Label 정의
2. `data/data_structures.py` - 데이터 구조
3. `preprocessing/text_splitter.py` - 문장 분할
4. `profanity_filter/profanity_detector.py` - 욕설 필터 (Baseline 우선)
5. `intent_classifier/intent_predictor.py` - 발화 의도 분류 (기본 로직)
6. `labeling/label_router.py` - 라우팅
7. `pipeline/main_pipeline.py` - 메인 파이프라인
8. `main.py` - 실행 진입점

### Phase 2: 평가 및 필터링
1. `evaluation/normal_label_evaluator.py` - 평가 프레임워크
2. `evaluation/manual_checker.py` - 매뉴얼 체커
3. `filtering/special_label_filter.py` - 종합 필터링
4. `filtering/event_generator.py` - 이벤트 생성
5. `filtering/alert_system.py` - 알림 시스템

### Phase 3: 모델 통합
1. `profanity_filter/korcen_filter.py` - Korcen 통합
2. `intent_classifier/kosentbert_classifier.py` - KoSentenceBERT 통합
3. `models/kosentbert_model.py` - 모델 래퍼

### Phase 4: 고도화
1. `utils/logger.py` - 로깅
2. `utils/exceptions.py` - 예외 처리
3. `data/session_manager.py` - 세션 관리
4. 테스트 파일들

---

## 5. 설정 파일 예시

### 5.1 `data/manual.json`

```json
{
  "INQUIRY": {
    "required_phrases": [
      "안내드리겠습니다",
      "확인해보겠습니다"
    ],
    "required_keywords": ["가격", "정책", "절차"],
    "procedure": [
      "고객 질문 확인",
      "정보 제공",
      "추가 문의 확인"
    ]
  },
  "COMPLAINT": {
    "required_phrases": [
      "불편을 드려 죄송합니다",
      "해결 방안을 제시하겠습니다"
    ],
    "required_keywords": ["불편", "사과", "해결"],
    "procedure": [
      "불만 내용 확인",
      "공감 표현",
      "해결 방안 제시",
      "사과"
    ]
  }
}
```

---

## 6. 요약

이 파일 구조는 다음과 같은 원칙을 따릅니다:

1. **모듈화**: 각 기능을 독립적인 모듈로 분리
2. **단일 책임**: 각 파일은 하나의 명확한 역할만 담당
3. **의존성 최소화**: 순환 의존성 방지, 명확한 의존성 관계
4. **확장성**: 새로운 Label이나 기능 추가 시 쉽게 확장 가능
5. **테스트 용이성**: 각 모듈을 독립적으로 테스트 가능

각 파일은 명확한 인터페이스를 가지고 있으며, 다른 모듈과의 결합도를 최소화하여 유지보수와 확장이 용이하도록 설계되었습니다.

