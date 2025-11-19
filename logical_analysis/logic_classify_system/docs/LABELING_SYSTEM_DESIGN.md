# 문장 단위 발화 의도 분류 시스템 설계

## 📚 문서 역할

**이 문서(LABELING_SYSTEM_DESIGN.md)**는 **라벨링 시스템 설계**를 다루는 문서입니다.
- Label 체계 및 분류 기준
- 분류 로직 및 라우팅
- 평가 프레임워크 설계
- 필터링 시스템 설계

**구현 현황**은 `IMPLEMENTATION_STATUS.md`를 참조하세요.

---

## 1. 시스템 개요

### 1.1 처리 파이프라인

```
[음성 입력] → [STT] → [문장 단위 분할] → [1차: 욕설 필터링] → [2차: 발화 의도 분류] → [Labeling]
                                                                    ↓
                                                          [Normal Label]  [특수 Label]
                                                                    ↓            ↓
                                                          [평가 프레임워크]  [종합 필터링]
                                                                      ↓            ↓
                                                          [매뉴얼 준수 확인]  [이벤트 발생]
                                                                              (통화중단/경고알림)
```

### 1.2 핵심 구성 요소

1. **1차 필터링: 욕설 감지**
   - Tokenization 후 Korcen 라이브러리 기반 욕설 감지
   - 단어 단위 직접적 악성 표현 포착
   - 감지 시 즉시 특수 Label로 분류

2. **2차 분류: 발화 의도 파악**
   - KoSentenceBERT 모델 활용
   - 문장 단위 의미 분석
   - 발화 목적에 따른 Labeling

3. **Label 기반 라우팅**
   - **Normal Label**: 상담사 평가 프레임워크로 이동
   - **특수 Label**: 종합 필터링 단계로 이동

---

## 2. Label 체계 설계

### 2.1 Normal Label (6개)

**목적**: 전화 상담에서 일어날 수 있는 정상적인 발화 상황을 분류하여, 상담사가 시스템 매뉴얼에 따라 적절히 대응했는지 평가하는 프레임워크를 작동시킴.

#### 2.1.1 INQUIRY (문의)
- **정의**: 고객이 정보나 서비스에 대해 질문하는 발화
- **예시**: 
  - "이 상품의 가격이 얼마인가요?"
  - "환불 정책이 어떻게 되나요?"
  - "어떻게 신청하나요?"
- **평가 기준**:
  - 상담사가 정확한 정보를 제공했는가?
  - 매뉴얼에 명시된 절차를 따랐는가?
  - 명확하고 이해하기 쉬운 설명을 했는가?

#### 2.1.2 COMPLAINT (불만/민원)
- **정의**: 고객이 서비스나 제품에 대한 불만을 표현하는 발화
- **예시**:
  - "제품이 고장났어요"
  - "배송이 너무 늦었어요"
  - "서비스가 마음에 들지 않아요"
- **평가 기준**:
  - 상담사가 고객의 불만을 공감하며 받아들였는가?
  - 문제 해결 방안을 제시했는가?
  - 적절한 사과와 보상 절차를 안내했는가?

#### 2.1.3 REQUEST (요청)
- **정의**: 고객이 특정 행동이나 서비스를 요청하는 발화
- **예시**:
  - "환불해주세요"
  - "교환해주세요"
  - "상담원 바꿔주세요"
- **평가 기준**:
  - 상담사가 요청의 적절성을 판단했는가?
  - 매뉴얼에 따른 처리 절차를 안내했는가?
  - 불가능한 요청에 대해 명확히 설명했는가?

#### 2.1.4 CLARIFICATION (명확화 요청)
- **정의**: 고객이 이전 설명에 대해 추가 설명이나 확인을 요청하는 발화
- **예시**:
  - "다시 한번 설명해주세요"
  - "이게 무슨 뜻인가요?"
  - "제가 이해한 게 맞나요?"
- **평가 기준**:
  - 상담사가 고객의 이해도를 확인했는가?
  - 명확하고 다양한 방식으로 재설명했는가?
  - 고객이 이해했는지 확인했는가?

#### 2.1.5 CONFIRMATION (확인)
- **정의**: 고객이 정보나 절차에 대해 확인하는 발화
- **예시**:
  - "그럼 이렇게 하면 되는 거죠?"
  - "확인해주세요"
  - "맞는지 확인하고 싶어요"
- **평가 기준**:
  - 상담사가 정확한 확인을 제공했는가?
  - 고객의 확인 요청에 적절히 응답했는가?
  - 추가 확인이 필요한 사항을 안내했는가?

#### 2.1.6 CLOSING (종료)
- **정의**: 상담 종료와 관련된 발화
- **예시**:
  - "감사합니다"
  - "궁금한 게 더 있으신가요?"
  - "그럼 여기서 마무리하겠습니다"
- **평가 기준**:
  - 상담사가 적절한 종료 절차를 따랐는가?
  - 추가 문의 사항이 있는지 확인했는가?
  - 고객 만족도를 확인했는가?

### 2.2 특수 Label (6개)

**목적**: 문제의 소지가 있는 발화를 감지하여, 종합 필터링 단계로 이동시켜 통화중단/경고알림과 같은 대응 이벤트를 발생시킴.

기존 `classification_criteria.py`의 `ComplaintCategory`를 참고하여 가장 심각하고 즉각 대응이 필요한 6개로 선정.

#### 2.2.1 VIOLENCE_THREAT (폭력_위협)
- **정의**: 폭력, 위협, 범죄 조장 표현
- **기존 카테고리**: `ComplaintCategory.VIOLENCE_THREAT`
- **심각도**: CRITICAL
- **예시**:
  - "죽여버리겠다"
  - "찾아가겠다"
  - "법적 대응하겠다"
  - "끝장내겠다"
- **대응 방안**:
  - 즉시 통화 중단 고려
  - 경고 알림 발송
  - 녹음 보관 및 법적 조치 검토
  - 상담사 보호 조치

#### 2.2.2 SEXUAL_HARASSMENT (성희롱)
- **정의**: 외설, 성적 표현, 성희롱
- **기존 카테고리**: `ComplaintCategory.SEXUAL_HARASSMENT`
- **심각도**: CRITICAL
- **예시**:
  - 성적인 표현
  - 음란한 내용
  - 사적인 만남 제안
- **대응 방안**:
  - 즉시 통화 중단
  - 경고 알림 발송
  - 녹음 보관
  - 법적 조치 검토

#### 2.2.3 PROFANITY (욕설)
- **정의**: 욕설, 저주 표현
- **기존 카테고리**: `ComplaintCategory.PROFANITY`
- **심각도**: HIGH
- **예시**:
  - 직접적 욕설
  - 저주 표현
- **대응 방안**:
  - 경고 알림 발송
  - 통화 중단 경고
  - 반복 시 통화 중단
  - 상담사 지원 제공

#### 2.2.4 HATE_SPEECH (혐오표현)
- **정의**: 성/연령/인종/지역/장애/종교/정치/직업 등에 대한 혐오 표현
- **기존 카테고리**: `ComplaintCategory.HATE_SPEECH`
- **심각도**: HIGH
- **예시**:
  - 성차별 표현
  - 지역 비하
  - 장애인 비하
  - 종교/정치 혐오
- **대응 방안**:
  - 경고 알림 발송
  - 통화 중단 경고
  - 반복 시 통화 중단
  - 상담사 지원 제공

#### 2.2.5 UNREASONABLE_DEMAND (무리한_요구)
- **정의**: 상담원의 매뉴얼이나 권한을 넘는 무리한 요구
- **기존 카테고리**: `ComplaintCategory.UNREASONABLE_DEMAND`
- **심각도**: MEDIUM ~ HIGH
- **예시**:
  - "지금 당장 FBI를 불러주세요"
  - "권한 밖인데 특별히 해주세요"
  - "불가능한데 즉시 처리해주세요"
- **대응 방안**:
  - 상담사에게 권한 밖 요구임을 알림
  - 매뉴얼에 따른 대응 가이드 제공
  - 반복 시 경고
  - 상담사 지원 제공

#### 2.2.6 REPETITION (반복성)
- **정의**: 대화가 진전되지 않고 같은 내용을 반복하는 발화
- **기존 카테고리**: `ComplaintCategory.REPETITION`
- **심각도**: MEDIUM
- **예시**:
  - "앞선 통화에서도 말씀드렸다시피"
  - "또 같은 말씀"
  - "계속 같은 얘기"
- **대응 방안**:
  - 상담사에게 반복 상황 알림
  - 대화 전환 전략 제시
  - 상담사 지원 제공
  - 지속 시 상급자 에스컬레이션

---

## 3. 처리 로직

### 3.1 1차 필터링: 욕설 감지

```python
def profanity_filter(text: str) -> Tuple[bool, Optional[str]]:
    """
    Korcen 라이브러리를 활용한 욕설 감지
    
    Returns:
        (is_profanity, category)
    """
    # Tokenization
    tokens = tokenize(text)
    
    # Korcen 기반 욕설 감지
    profanity_result = korcen_filter.check_profanity(text)
    
    if profanity_result.is_profanity:
        # 특수 Label로 분류
        return True, "PROFANITY"
    
    return False, None
```

### 3.2 2차 분류: 발화 의도 분류

```python
def classify_intent(text: str, profanity_detected: bool) -> str:
    """
    KoSentenceBERT 기반 발화 의도 분류
    
    Args:
        text: 분석할 문장
        profanity_detected: 1차 필터링에서 욕설 감지 여부
    
    Returns:
        Label (Normal 또는 특수)
    """
    if profanity_detected:
        # 이미 특수 Label로 분류됨
        return "PROFANITY"
    
    # KoSentenceBERT 모델로 발화 의도 분류
    intent = kosentbert_model.predict(text)
    
    # Normal Label 또는 특수 Label 반환
    return intent
```

### 3.3 Label 기반 라우팅

```python
def route_by_label(label: str, text: str, session_context: List[str]):
    """
    Label에 따라 적절한 처리 경로로 라우팅
    """
    NORMAL_LABELS = [
        "INQUIRY", "COMPLAINT", "REQUEST", 
        "CLARIFICATION", "CONFIRMATION", "CLOSING"
    ]
    
    SPECIAL_LABELS = [
        "VIOLENCE_THREAT", "SEXUAL_HARASSMENT", "PROFANITY",
        "HATE_SPEECH", "UNREASONABLE_DEMAND", "REPETITION"
    ]
    
    if label in NORMAL_LABELS:
        # 평가 프레임워크로 이동
        evaluate_agent_performance(label, text, session_context)
        
    elif label in SPECIAL_LABELS:
        # 종합 필터링 단계로 이동
        trigger_filtering_event(label, text, session_context)
```

---

## 4. 평가 프레임워크 (Normal Label)

### 4.1 평가 항목

각 Normal Label에 대해 상담사가 시스템 매뉴얼에 따라 적절히 대응했는지 평가:

1. **정보 제공 정확성**: 정확한 정보를 제공했는가?
2. **매뉴얼 준수**: 매뉴얼에 명시된 절차를 따랐는가?
3. **소통 능력**: 명확하고 이해하기 쉬운 설명을 했는가?
4. **공감 능력**: 고객의 감정을 인식하고 반영했는가?
5. **문제 해결 능력**: 적절한 해결 방안을 제시했는가?

### 4.2 평가 방법

- **키워드/패턴 매칭**: 매뉴얼에 명시된 필수 표현 사용 여부
- **문장 구조 분석**: 의존 구문 분석을 통한 설명 명확도
- **대화 흐름 분석**: 적절한 순서로 절차를 진행했는지
- **감정 톤 분석**: 적절한 톤과 태도로 대응했는지

---

## 5. 종합 필터링 시스템 (특수 Label)

### 5.1 이벤트 발생 조건

각 특수 Label에 따라 다른 수준의 이벤트 발생:

| Label | 심각도 | 이벤트 유형 |
|-------|--------|------------|
| VIOLENCE_THREAT | CRITICAL | 즉시 통화 중단 + 경고 알림 |
| SEXUAL_HARASSMENT | CRITICAL | 즉시 통화 중단 + 경고 알림 |
| PROFANITY | HIGH | 경고 알림 + 통화 중단 경고 |
| HATE_SPEECH | HIGH | 경고 알림 + 통화 중단 경고 |
| UNREASONABLE_DEMAND | MEDIUM~HIGH | 상담사 지원 알림 |
| REPETITION | MEDIUM | 상담사 지원 알림 |

### 5.2 이벤트 처리

```python
def trigger_filtering_event(label: str, text: str, session_context: List[str]):
    """
    특수 Label에 따른 이벤트 발생
    """
    event_config = {
        "VIOLENCE_THREAT": {
            "action": "TERMINATE_CALL",
            "alert": "CRITICAL",
            "recording": True,
            "legal_review": True
        },
        "SEXUAL_HARASSMENT": {
            "action": "TERMINATE_CALL",
            "alert": "CRITICAL",
            "recording": True,
            "legal_review": True
        },
        "PROFANITY": {
            "action": "WARN",
            "alert": "HIGH",
            "terminate_on_repeat": True
        },
        "HATE_SPEECH": {
            "action": "WARN",
            "alert": "HIGH",
            "terminate_on_repeat": True
        },
        "UNREASONABLE_DEMAND": {
            "action": "SUPPORT_AGENT",
            "alert": "MEDIUM",
            "provide_guidance": True
        },
        "REPETITION": {
            "action": "SUPPORT_AGENT",
            "alert": "MEDIUM",
            "provide_strategy": True
        }
    }
    
    config = event_config[label]
    
    # 이벤트 발생
    emit_event(label, config, text, session_context)
```

---

## 6. 구현 우선순위

### 6.1 Phase 1: 기본 프레임워크
1. Korcen 기반 욕설 필터 구현
2. KoSentenceBERT 모델 통합
3. 기본 Label 분류 로직 구현
4. 라우팅 시스템 구현

### 6.2 Phase 2: 평가 프레임워크
1. Normal Label별 평가 기준 정의
2. 매뉴얼 기반 평가 로직 구현
3. 평가 결과 리포트 생성

### 6.3 Phase 3: 종합 필터링
1. 특수 Label별 이벤트 처리 로직 구현
2. 실시간 알림 시스템 구축
3. 통화 중단 연동

### 6.4 Phase 4: 고도화
1. 모델 Fine-tuning (윤리검증 데이터 활용)
2. 평가 정확도 향상
3. 개인화된 상담사 지원

---

## 7. 데이터 구조

### 7.1 분류 결과 데이터 구조

```python
@dataclass
class ClassificationResult:
    """분류 결과"""
    text: str                          # 원본 문장
    label: str                         # 분류된 Label
    label_type: str                    # "NORMAL" or "SPECIAL"
    confidence: float                  # 신뢰도 (0.0-1.0)
    profanity_detected: bool          # 욕설 감지 여부
    profanity_category: Optional[str] # 욕설 카테고리
    timestamp: datetime               # 처리 시간
    session_id: str                   # 세션 ID
```

### 7.2 평가 결과 데이터 구조

```python
@dataclass
class EvaluationResult:
    """평가 결과 (Normal Label용)"""
    label: str                         # Normal Label
    score: float                       # 평가 점수 (0-100)
    criteria_scores: Dict[str, float]  # 항목별 점수
    feedback: str                      # 피드백 메시지
    recommendations: List[str]         # 개선 제안
```

### 7.3 이벤트 데이터 구조

```python
@dataclass
class FilteringEvent:
    """필터링 이벤트 (특수 Label용)"""
    label: str                         # 특수 Label
    severity: str                      # 심각도
    action: str                        # 조치 유형
    alert_level: str                   # 알림 레벨
    timestamp: datetime                # 발생 시간
    session_id: str                    # 세션 ID
    context: List[str]                 # 대화 맥락
```

---

## 8. 참고 사항

### 8.1 기존 시스템과의 연계

- `classification_criteria.py`의 키워드 리스트는 Korcen 필터의 보조 수단으로 활용
- `risk_based_classifier.py`의 메타데이터 분석은 평가 프레임워크에서 활용 가능
- 기존 12개 카테고리 중 사용하지 않는 카테고리는 평가 프레임워크의 세부 항목으로 활용 가능

### 8.2 모델 학습 데이터

- **Normal Label**: 상담 음성 데이터셋, 민간분야 고객 상담 데이터 활용
- **특수 Label**: 윤리검증 데이터셋 활용 (기존 카테고리 매핑)

### 8.3 확장성

- Normal Label은 상담 유형에 따라 추가 가능
- 특수 Label은 새로운 위험 유형 발견 시 추가 가능
- 각 Label별 세부 카테고리 추가 가능

