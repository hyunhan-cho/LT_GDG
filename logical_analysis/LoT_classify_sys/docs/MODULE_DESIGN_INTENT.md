# Logic Classify System 모듈 설계 의도

**작성일**: 2024년  
**모듈명**: `logic_classify_system`  
**목적**: STT화된 텍스트를 기반으로 발화의 논리적 구조를 파악하고 특징점을 추출하는 모듈

---

## 📋 목차

1. [모듈 개요](#모듈-개요)
2. [처리 범위 (Boundary)](#처리-범위-boundary)
3. [책임 (Responsibility)](#책임-responsibility)
4. [입력 데이터 형식](#입력-데이터-형식)
5. [출력 데이터 형식](#출력-데이터-형식)
6. [특징점 추출 전략](#특징점-추출-전략)
7. [사용 지표 (Metrics)](#사용-지표-metrics)
8. [모듈 구조](#모듈-구조)
9. [제한 사항 및 범위 밖 기능](#제한-사항-및-범위-밖-기능)

---

## 모듈 개요

### 핵심 목적

이 모듈은 **STT화된 텍스트를 기반으로 발화에 내재된 논리적 구조를 파악**하는 것을 목적으로 합니다. 

통화 전체에 대한 종합적인 평가는 **이 모듈의 범위 밖**이며, 이후 단계에서 로직화될 예정입니다.

### 설계 철학

- **특징점 추출 중심**: 최대한 많은 특징점을 추출하여 score에 사용할 수 있는 resource를 확보
- **Resource 확보 우선**: 이어받은 모듈에서 심층적인 scoring이 가능하도록 풍부한 특징점 제공
- **명확한 책임 분리**: 손님 발화 분석과 상담원 대응 분석을 명확히 구분

---

## 처리 범위 (Boundary)

### ✅ 포함되는 처리

1. **STT 결과 데이터 처리**
   - JSON 파일 형태의 원본 데이터 처리
   - 화자 분리 및 처리된 형태의 데이터 처리

2. **손님 발화 분석**
   - 특징점 감지 및 labeling/scoring
   - 문제 발생 가능성 추출

3. **상담원 발화 분석**
   - 매뉴얼 준수 여부 판단 근거 추출
   - labeling/scoring

4. **특징점 추출**
   - 다양한 차원에서 특징점 추출
   - Score 계산에 활용 가능한 resource 생성

### ❌ 포함되지 않는 처리

1. **통화 전체 종합 평가**
   - 통화 전체에 대한 종합적인 평가는 이후 단계에서 처리
   - 이 모듈은 개별 발화 단위의 특징점 추출에 집중

2. **실시간 처리**
   - 실시간 스트리밍 데이터 처리
   - 실시간 알림 발송

3. **음성 처리**
   - 음성 파일 직접 처리
   - STT 수행 (STT는 이미 완료된 데이터를 입력으로 받음)

4. **최종 리포트 생성**
   - 리포트 생성 및 시각화
   - 통계 분석 및 트렌드 분석

---

## 책임 (Responsibility)

### 1. 손님 발화 특징점 추출 및 Labeling/Scoring

#### 1.1 목적
손님의 발화에서 **문제 발생 가능성을 추출**하는 것

#### 1.2 처리 내용

**1.2.1 Korcen 기반 욕설 감지**
- **책임**: 단어 단위 직접적 악성 표현 포착
- **입력**: 손님 발화 텍스트
- **출력**: 
  - 욕설 감지 여부 (`is_profanity: bool`)
  - 욕설 카테고리 (`category: str`)
  - 신뢰도 (`confidence: float`)
  - 감지 방법 (`method: str`)

**1.2.2 Normal Label 기반 특징점 감지**
- **책임**: Normal Label에 해당하는 발화 패턴 감지
- **입력**: 손님 발화 텍스트, 세션 맥락
- **출력**:
  - 분류된 Label (`label: str`)
  - Label 타입 (`label_type: str`)
  - 신뢰도 (`confidence: float`)
  - 각 Label별 확률 (`probabilities: Dict[str, float]`)

**1.2.3 특수 Label 감지**
- **책임**: 문제 상황(위협, 성희롱, 혐오표현 등) 감지
- **입력**: 손님 발화 텍스트, 세션 맥락
- **출력**:
  - 특수 Label (`label: str`)
  - 심각도 (`severity: str`)
  - 신뢰도 (`confidence: float`)

#### 1.3 특징점 추출 항목

| 특징점 유형 | 추출 방법 | Score 활용 |
|------------|----------|-----------|
| **욕설 감지** | Korcen + Baseline 규칙 | 문제 발생 가능성 점수 |
| **위협 표현** | 키워드 패턴 + 문맥 분석 | 심각도 점수 |
| **성희롱 표현** | 키워드 패턴 + 문맥 분석 | 심각도 점수 |
| **혐오표현** | 키워드 패턴 + 문맥 분석 | 심각도 점수 |
| **무리한 요구** | 문맥 분석 + 패턴 매칭 | 문제 발생 가능성 점수 |
| **반복성** | 세션 맥락 분석 | 문제 발생 가능성 점수 |
| **Normal Label** | KoSentenceBERT + Baseline 규칙 | 대응 필요성 점수 |

---

### 2. 상담원 대응 매뉴얼 준수 여부 판단 근거 추출 및 Labeling/Scoring

#### 2.1 목적
상담원의 대응에서 **"매뉴얼대로 대응이 이루어졌는가?"**에 대해 판단할 수 있는 근거를 추출

#### 2.2 처리 내용

**2.2.1 매뉴얼 준수 여부 확인**
- **책임**: 상담원 발화가 매뉴얼에 명시된 절차를 따르는지 확인
- **입력**: 
  - 상담원 발화 텍스트
  - 해당하는 Normal Label
  - 매뉴얼 정의
- **출력**:
  - 매뉴얼 준수 점수 (`compliance_score: float`, 0.0-1.0)
  - 준수 항목 리스트 (`complied_items: List[str]`)
  - 미준수 항목 리스트 (`non_complied_items: List[str]`)

**2.2.2 필수 표현 사용 여부 확인**
- **책임**: Label별 필수 표현 사용 여부 확인
- **입력**: 상담원 발화 텍스트, Label별 필수 표현 리스트
- **출력**:
  - 필수 표현 사용 점수 (`phrase_score: float`)
  - 사용된 표현 리스트 (`used_phrases: List[str]`)
  - 미사용 표현 리스트 (`missing_phrases: List[str]`)

**2.2.3 필수 키워드 사용 여부 확인**
- **책임**: Label별 필수 키워드 사용 여부 확인
- **입력**: 상담원 발화 텍스트, Label별 필수 키워드 리스트
- **출력**:
  - 필수 키워드 사용 점수 (`keyword_score: float`)
  - 사용된 키워드 리스트 (`used_keywords: List[str]`)
  - 미사용 키워드 리스트 (`missing_keywords: List[str]`)

**2.2.4 절차 순서 확인**
- **책임**: 매뉴얼에 명시된 절차 순서 준수 여부 확인
- **입력**: 상담원 발화 텍스트, Label별 절차 정의
- **출력**:
  - 절차 준수 점수 (`procedure_score: float`)
  - 수행된 절차 리스트 (`completed_procedures: List[str]`)
  - 미수행 절차 리스트 (`missing_procedures: List[str]`)

#### 2.3 특징점 추출 항목

| 특징점 유형 | 추출 방법 | Score 활용 |
|------------|----------|-----------|
| **매뉴얼 준수도** | 필수 표현/키워드/절차 확인 | 종합 준수 점수 |
| **정보 제공 정확성** | 키워드 매칭 + 문맥 분석 | 정확성 점수 |
| **소통 명확성** | 문장 구조 분석 | 명확성 점수 |
| **공감 표현** | 공감 키워드 감지 | 공감도 점수 |
| **문제 해결 방안 제시** | 해결 키워드 감지 | 해결 능력 점수 |

---

## 입력 데이터 형식

### 1. 원본 STT 결과 (JSON)

```json
{
  "session_id": "session_001",
  "timestamp": "2024-01-01T10:00:00",
  "transcript": "전체 대화 텍스트...",
  "metadata": {
    "duration": 300.5,
    "language": "ko"
  }
}
```

### 2. 화자 분리 처리된 STT 결과 (JSON)

```json
{
  "session_id": "session_001",
  "timestamp": "2024-01-01T10:00:00",
  "turns": [
    {
      "speaker": "customer",
      "text": "안녕하세요",
      "timestamp": 0.0
    },
    {
      "speaker": "agent",
      "text": "네, 안녕하세요. 무엇을 도와드릴까요?",
      "timestamp": 2.5
    },
    {
      "speaker": "customer",
      "text": "환불하고 싶어요",
      "timestamp": 5.0
    }
  ],
  "metadata": {
    "duration": 300.5,
    "language": "ko"
  }
}
```

### 3. 데이터 로드 인터페이스

모듈은 다음 두 가지 형태의 데이터를 모두 처리할 수 있어야 합니다:

- **원본 데이터**: 화자 구분이 없는 전체 텍스트 → 내부에서 화자 분리 수행
- **처리된 데이터**: 이미 화자 구분이 완료된 데이터 → 바로 활용

---

## 출력 데이터 형식

### 1. 손님 발화 분석 결과

```python
@dataclass
class CustomerAnalysisResult:
    """손님 발화 분석 결과"""
    # 기본 정보
    session_id: str
    turn_index: int
    text: str
    timestamp: datetime
    
    # 특징점 추출 결과
    profanity_result: ProfanityResult
    classification_result: ClassificationResult
    
    # Score Resource
    feature_scores: Dict[str, float]  # 각 특징점별 점수
    # 예: {
    #   "profanity_score": 0.8,
    #   "threat_score": 0.3,
    #   "unreasonable_demand_score": 0.6,
    #   ...
    # }
    
    # 추출된 특징점 상세 정보
    extracted_features: Dict[str, Any]
    # 예: {
    #   "profanity_keywords": ["욕설1", "욕설2"],
    #   "threat_patterns": ["위협 패턴1"],
    #   ...
    # }
```

### 2. 상담원 발화 분석 결과

```python
@dataclass
class AgentAnalysisResult:
    """상담원 발화 분석 결과"""
    # 기본 정보
    session_id: str
    turn_index: int
    text: str
    timestamp: datetime
    corresponding_customer_label: str  # 해당하는 손님 발화의 Label
    
    # 매뉴얼 준수 분석 결과
    manual_compliance_score: float  # 0.0-1.0
    compliance_details: Dict[str, Any]
    # 예: {
    #   "phrase_score": 0.8,
    #   "keyword_score": 0.9,
    #   "procedure_score": 0.7,
    #   "complied_items": ["필수 표현 사용", "절차 안내"],
    #   "non_complied_items": ["공감 표현 부족"]
    # }
    
    # Score Resource
    feature_scores: Dict[str, float]
    # 예: {
    #   "manual_compliance_score": 0.8,
    #   "information_accuracy_score": 0.9,
    #   "communication_clarity_score": 0.7,
    #   "empathy_score": 0.6,
    #   "problem_solving_score": 0.8
    # }
    
    # 추출된 특징점 상세 정보
    extracted_features: Dict[str, Any]
    # 예: {
    #   "used_phrases": ["안내드리겠습니다", "확인해보겠습니다"],
    #   "missing_phrases": ["불편을 드려 죄송합니다"],
    #   "used_keywords": ["처리", "절차"],
    #   ...
    # }
```

### 3. 통합 분석 결과

```python
@dataclass
class TurnAnalysisResult:
    """발화 턴별 분석 결과"""
    session_id: str
    turn_index: int
    customer_result: CustomerAnalysisResult
    agent_result: Optional[AgentAnalysisResult]  # 상담원 발화가 있는 경우
    
    # 종합 Score Resource (다음 단계에서 활용)
    turn_scores: Dict[str, float]
    # 예: {
    #   "customer_problem_score": 0.7,
    #   "agent_response_quality_score": 0.8,
    #   "overall_turn_score": 0.75
    # }
```

---

## 특징점 추출 전략

### 목표
**최대한 많은 특징점을 추출하여 score에 사용할 수 있는 resource를 확보**

### 추출 전략

#### 1. 다층적 특징점 추출

**1.1 단어 단위 특징점**
- 욕설 키워드
- 위협 표현 키워드
- 성희롱 표현 키워드
- 혐오표현 키워드
- 매뉴얼 필수 키워드

**1.2 구문 단위 특징점**
- 필수 표현 패턴
- 절차 표현 패턴
- 공감 표현 패턴
- 해결 방안 표현 패턴

**1.3 문장 단위 특징점**
- 문장 구조 복잡도
- 문장 길이
- 톤 및 어조
- 의미적 유사도 (Normal Label 분류)

**1.4 대화 단위 특징점**
- 반복성 패턴
- 대화 흐름
- 맥락 일관성
- 절차 순서 준수

#### 2. 특징점 추출 우선순위

| 우선순위 | 특징점 유형 | 이유 |
|---------|-----------|------|
| **높음** | 욕설/위협/성희롱 감지 | 즉시 대응이 필요한 문제 상황 |
| **높음** | 매뉴얼 준수 여부 | 상담 품질 평가의 핵심 지표 |
| **중간** | Normal Label 분류 | 대응 전략 수립에 필요 |
| **중간** | 공감/해결 방안 표현 | 상담 품질 평가 지표 |
| **낮음** | 문장 구조 분석 | 보조 지표로 활용 |

#### 3. 특징점 확장 전략

- **키워드 기반**: 명시적 표현 감지
- **패턴 기반**: 정규표현식 및 패턴 매칭
- **모델 기반**: KoSentenceBERT 등 의미 분석 모델
- **규칙 기반**: Baseline 규칙으로 폴백

---

## 사용 지표 (Metrics)

### 1. 특징점 추출 지표

#### 1.1 추출 완전도 (Extraction Completeness)
- **정의**: 발화에서 추출 가능한 특징점 중 실제로 추출된 비율
- **계산**: `추출된 특징점 수 / 추출 가능한 특징점 수`
- **목표**: 80% 이상

#### 1.2 특징점 다양성 (Feature Diversity)
- **정의**: 추출된 특징점의 유형 수
- **계산**: 추출된 특징점 유형의 개수
- **목표**: 최소 5개 이상의 유형

#### 1.3 특징점 신뢰도 (Feature Confidence)
- **정의**: 추출된 특징점의 평균 신뢰도
- **계산**: `Σ(각 특징점 신뢰도) / 특징점 수`
- **목표**: 0.7 이상

### 2. 처리 성능 지표

#### 2.1 처리 속도
- **정의**: 발화당 평균 처리 시간
- **목표**: 발화당 1초 이내

#### 2.2 처리 정확도
- **정의**: Label 분류 정확도
- **계산**: `정확히 분류된 발화 수 / 전체 발화 수`
- **목표**: 85% 이상

### 3. Resource 품질 지표

#### 3.1 Score Resource 풍부도
- **정의**: 발화당 평균 특징점 수
- **계산**: `전체 특징점 수 / 전체 발화 수`
- **목표**: 발화당 3개 이상

#### 3.2 Score Resource 활용 가능성
- **정의**: 다음 단계에서 활용 가능한 특징점 비율
- **계산**: `활용 가능한 특징점 수 / 전체 특징점 수`
- **목표**: 90% 이상

---

## 모듈 구조

### 핵심 모듈 구성

```
logic_classify_system/
├── preprocessing/          # 전처리
│   └── text_splitter.py    # 문장 분할, 화자 구분
│
├── profanity_filter/       # 욕설 필터링 (손님 발화)
│   ├── profanity_detector.py
│   └── baseline_rules.py
│
├── intent_classifier/      # 의도 분류 (손님 발화)
│   ├── intent_predictor.py
│   └── baseline_rules.py
│
├── evaluation/             # 매뉴얼 준수 평가 (상담원 발화)
│   ├── normal_label_evaluator.py
│   └── manual_checker.py
│
├── filtering/              # 특수 Label 필터링
│   ├── special_label_filter.py
│   └── baseline_rules.py
│
├── labeling/               # Label 라우팅
│   └── label_router.py
│
├── pipeline/               # 메인 파이프라인
│   └── main_pipeline.py
│
└── data/                   # 데이터 구조
    ├── data_structures.py
    └── session_manager.py
```

### 처리 흐름

```
[STT JSON 입력]
    ↓
[전처리: 화자 구분, 문장 분할]
    ↓
    ├─→ [손님 발화 분석]
    │       ├─→ [욕설 필터링] → 특징점 추출
    │       └─→ [의도 분류] → 특징점 추출
    │
    └─→ [상담원 발화 분석]
            └─→ [매뉴얼 준수 평가] → 특징점 추출
    ↓
[특징점 통합 및 Score Resource 생성]
    ↓
[출력: TurnAnalysisResult]
```

---

## 제한 사항 및 범위 밖 기능

### 제한 사항

1. **통화 전체 종합 평가 불가**
   - 이 모듈은 개별 발화 단위의 특징점 추출에 집중
   - 통화 전체에 대한 종합 평가는 이후 단계에서 처리

2. **실시간 처리 불가**
   - 배치 처리 전용
   - STT 완료된 데이터만 처리

3. **음성 처리 불가**
   - 음성 파일 직접 처리 불가
   - STT는 이미 완료된 것으로 가정

### 범위 밖 기능 (다른 모듈에서 처리)

1. **통화 전체 종합 평가**
   - 여러 발화를 종합하여 통화 전체 품질 평가
   - 상담원 성과 종합 분석

2. **리포트 생성**
   - 분석 결과를 리포트 형태로 생성
   - 시각화 및 통계 분석

3. **트렌드 분석**
   - 기간별/상담원별 트렌드 분석
   - 비교 분석

---

## 다음 단계 활용

이 모듈에서 추출한 특징점과 Score Resource는 다음 단계에서 다음과 같이 활용됩니다:

1. **통화 전체 종합 평가**
   - 발화별 특징점을 종합하여 통화 전체 품질 점수 계산
   - 상담원 성과 종합 평가

2. **심층적인 Scoring**
   - 추출된 특징점을 기반으로 더 정교한 점수 계산
   - 머신러닝 모델 활용 가능

3. **리포트 생성**
   - 특징점 데이터를 기반으로 상세 리포트 생성
   - 개선 제안 생성

---

**참고 문서**:
- `PROJECT_STATUS.md`: 프로젝트 전체 현황
- `LABELING_SYSTEM_DESIGN.md`: 원본 설계 문서
- `BATCH_PROCESSING_MIGRATION.md`: 배치 처리 전환 가이드

