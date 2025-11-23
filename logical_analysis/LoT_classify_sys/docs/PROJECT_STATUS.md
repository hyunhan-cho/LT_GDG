# 프로젝트 작업 진전 상황 및 주요 기능 문서

**작성일**: 2024년  
**프로젝트**: 전화 상담 품질 관리 시스템 (Logic Classify System)  
**전체 진행률**: 약 **70%** (기본 프레임워크 완료, 모델 통합 대기)

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [주요 기능](#주요-기능)
4. [구현 현황](#구현-현황)
5. [모듈별 상세 기능](#모듈별-상세-기능)
6. [데이터 구조](#데이터-구조)
7. [미구현 사항](#미구현-사항)
8. [향후 계획](#향후-계획)

---

## 프로젝트 개요

### 목적
전화 상담에서 고객 발화를 실시간으로 분석하여:
- **Normal Label**: 상담사가 매뉴얼에 따라 적절히 대응했는지 평가
- **특수 Label**: 문제 상황(욕설, 위협, 성희롱 등)을 감지하여 즉시 대응

### 핵심 가치
- 상담사 교육 및 피드백 제공
- 문제 상황 조기 감지 및 대응
- 상담 품질 향상

---

## 시스템 아키텍처

### 처리 파이프라인

```
[음성 입력] 
    ↓
[STT] 
    ↓
[문장 단위 분할] 
    ↓
[1차: 욕설 필터링] 
    ↓
[2차: 발화 의도 분류] 
    ↓
[Labeling]
    ↓
    ├─→ [Normal Label] → [평가 프레임워크] → [매뉴얼 준수 확인]
    │
    └─→ [특수 Label] → [종합 필터링] → [이벤트 발생] (통화중단/경고알림)
```

### 핵심 구성 요소

1. **전처리 모듈**: 문장 단위 분할, 화자 구분
2. **욕설 필터링**: 1차 필터링으로 악성 표현 감지
3. **의도 분류**: 발화 의도 파악 및 Label 분류
4. **라우팅 시스템**: Label 타입에 따른 처리 경로 분기
5. **평가 프레임워크**: Normal Label에 대한 상담사 평가
6. **종합 필터링**: 특수 Label에 대한 이벤트 생성 및 알림

---

## 주요 기능

### ✅ 완료된 기능

#### 1. 파이프라인 구조 (100%)
- 전체 처리 흐름 구현 완료
- 문장 단위 처리 지원
- 세션 관리 통합

#### 2. Label 체계 (100%)
- **Normal Label 6개**: INQUIRY, COMPLAINT, REQUEST, CLARIFICATION, CONFIRMATION, CLOSING
- **특수 Label 6개**: VIOLENCE_THREAT, SEXUAL_HARASSMENT, PROFANITY, HATE_SPEECH, UNREASONABLE_DEMAND, REPETITION

#### 3. 라우팅 시스템 (100%)
- Normal Label → 평가 프레임워크
- 특수 Label → 종합 필터링
- 자동 분기 처리

#### 4. 평가 프레임워크 (70%)
- 5개 평가 기준: 정보 제공 정확성, 매뉴얼 준수, 소통 능력, 공감 능력, 문제 해결 능력
- 가중치 기반 종합 점수 계산 (0-100점)
- 피드백 및 개선 제안 생성

#### 5. 종합 필터링 (90%)
- Label별 심각도 설정 (CRITICAL, HIGH, MEDIUM, LOW)
- 이벤트 생성 및 알림 발송
- 심각도별 대응 액션 정의

#### 6. 데이터 구조 (100%)
- 모든 데이터 구조 정의 완료
- 타입 안정성 보장

### ⚠️ 부분 완료 기능

#### 1. 욕설 필터링 (50%)
- ✅ Baseline 규칙 기반 감지
- ❌ Korcen 라이브러리 통합 미구현

#### 2. 발화 의도 분류 (30%)
- ✅ Baseline 규칙으로 특수 Label 감지
- ❌ KoSentenceBERT 모델 통합 미구현
- ⚠️ Normal Label은 기본값 반환 (임시 처리)

#### 3. 알림 시스템 (60%)
- ✅ 이벤트 생성 및 콘솔 출력
- ❌ 실시간 알림 시스템 미구현

---

## 구현 현황

### 모듈별 구현 상태

| 모듈 | 파일 경로 | 완성도 | 상태 |
|------|----------|--------|------|
| **파이프라인** | `pipeline/main_pipeline.py` | 100% | ✅ 완료 |
| **전처리** | `preprocessing/text_splitter.py` | 100% | ✅ 완료 |
| **욕설 필터** | `profanity_filter/profanity_detector.py` | 50% | ⚠️ 부분 |
| **의도 분류** | `intent_classifier/intent_predictor.py` | 30% | ⚠️ 부분 |
| **라우팅** | `labeling/label_router.py` | 100% | ✅ 완료 |
| **평가 프레임워크** | `evaluation/normal_label_evaluator.py` | 70% | ⚠️ 기본 |
| **종합 필터링** | `filtering/special_label_filter.py` | 90% | ✅ 완료 |
| **세션 관리** | `data/session_manager.py` | 100% | ✅ 완료 |
| **데이터 구조** | `data/data_structures.py` | 100% | ✅ 완료 |
| **Label 정의** | `config/labels.py` | 100% | ✅ 완료 |

### Phase별 진행 상황

#### Phase 1: 기본 프레임워크 (50%)
- ✅ 파이프라인 구조 구현
- ✅ 라우팅 시스템 구현
- ❌ Korcen 필터 통합
- ❌ KoSentenceBERT 모델 통합

#### Phase 2: 평가 프레임워크 (100%)
- ✅ Normal Label별 평가 기준 정의
- ✅ 매뉴얼 기반 평가 로직 구현
- ✅ 평가 결과 리포트 생성

#### Phase 3: 종합 필터링 (67%)
- ✅ 특수 Label별 이벤트 처리 로직 구현
- ⚠️ 실시간 알림 시스템 기본 구현
- ❌ 통화 중단 연동

#### Phase 4: 고도화 (0%)
- ❌ 모델 Fine-tuning
- ❌ 평가 정확도 향상
- ❌ 개인화된 상담사 지원

---

## 모듈별 상세 기능

### 1. 파이프라인 (`pipeline/main_pipeline.py`)

**역할**: 전체 처리 흐름 조율

**주요 메서드**:
- `process(text, session_id)`: 전체 텍스트 처리
- `process_single_sentence(sentence, session_id)`: 단일 문장 처리

**처리 단계**:
1. 문장 단위 분할
2. 화자별 구분 (고객/상담사)
3. 고객 문장에 대해 욕설 필터링 → 의도 분류
4. 세션 맥락 업데이트

---

### 2. 전처리 (`preprocessing/text_splitter.py`)

**역할**: 텍스트를 문장 단위로 분할하고 화자 구분

**주요 기능**:
- 문장 단위 분할
- 화자별 구분 (고객/상담사)
- 대화 맥락 유지

---

### 3. 욕설 필터링 (`profanity_filter/profanity_detector.py`)

**역할**: 1차 필터링으로 악성 표현 감지

**현재 구현**:
- ✅ Baseline 규칙 기반 감지
- ✅ `ProfanityResult` 반환 (is_profanity, category, confidence, method)

**미구현**:
- ❌ Korcen 라이브러리 통합
- ❌ Tokenization 단계 명시적 구현

**사용 예시**:
```python
detector = ProfanityDetector(use_korcen=False)
result = detector.detect("욕설이 포함된 텍스트")
# ProfanityResult(is_profanity=True, category="PROFANITY", ...)
```

---

### 4. 의도 분류 (`intent_classifier/intent_predictor.py`)

**역할**: 발화 의도 예측 및 Label 분류

**현재 구현**:
- ✅ Baseline 규칙으로 특수 Label 사전 감지
- ✅ Label 타입 결정 (Normal/Special)
- ⚠️ Normal Label은 기본값 반환 (INQUIRY, confidence=0.5)

**미구현**:
- ❌ KoSentenceBERT 모델 통합
- ❌ Normal Label 정확한 분류

**사용 예시**:
```python
predictor = IntentPredictor()
result = predictor.predict(
    text="지금 당장 FBI를 불러주세요",
    profanity_detected=False,
    session_context=None
)
# ClassificationResult(label="UNREASONABLE_DEMAND", ...)
```

---

### 5. 라우팅 (`labeling/label_router.py`)

**역할**: Label 타입에 따른 처리 경로 분기

**기능**:
- Normal Label → 평가 프레임워크
- 특수 Label → 종합 필터링
- `RouterResult` 반환

**사용 예시**:
```python
router = LabelRouter()
router_result = router.route(
    classification_result=classification_result,
    session_context=session_context,
    agent_text=agent_text
)
```

---

### 6. 평가 프레임워크 (`evaluation/normal_label_evaluator.py`)

**역할**: Normal Label에 대한 상담사 평가

**평가 기준 (5개)**:
1. **정보 제공 정확성** (가중치: 0.3)
2. **매뉴얼 준수** (가중치: 0.3)
3. **소통 능력** (가중치: 0.2)
4. **공감 능력** (가중치: 0.1)
5. **문제 해결 능력** (가중치: 0.1)

**기능**:
- Label별 평가 기준 적용
- 가중치 기반 종합 점수 계산 (0-100점)
- 피드백 및 개선 제안 생성

**현재 구현**:
- ✅ 키워드/패턴 매칭
- ✅ 간단한 대화 흐름 분석
- ❌ 문장 구조 분석 (의존 구문 분석)
- ❌ 감정 톤 분석

---

### 7. 종합 필터링 (`filtering/special_label_filter.py`)

**역할**: 특수 Label에 대한 종합 필터링 및 이벤트 생성

**기능**:
- Label별 심각도 확인
- 이벤트 생성
- 알림 발송

**심각도별 대응**:
- **CRITICAL** (VIOLENCE_THREAT, SEXUAL_HARASSMENT): TERMINATE_CALL
- **HIGH** (PROFANITY, HATE_SPEECH): WARN
- **MEDIUM** (UNREASONABLE_DEMAND, REPETITION): SUPPORT_AGENT

---

### 8. 세션 관리 (`data/session_manager.py`)

**역할**: 대화 맥락 저장 및 관리

**기능**:
- 세션 생성/초기화
- 문장 추가
- 세션 맥락 조회 (최근 N개 문장)

---

## 데이터 구조

### 1. ProfanityResult
```python
@dataclass
class ProfanityResult:
    is_profanity: bool
    category: Optional[str]  # PROFANITY, VIOLENCE_THREAT, etc.
    confidence: float  # 0.0-1.0
    method: Optional[str]  # "korcen" or "baseline"
```

### 2. ClassificationResult
```python
@dataclass
class ClassificationResult:
    label: str  # 분류된 Label
    label_type: str  # "NORMAL" or "SPECIAL"
    confidence: float  # 신뢰도 (0.0-1.0)
    text: str  # 원본 문장
    probabilities: Optional[Dict[str, float]] = None
    timestamp: Optional[datetime] = None
```

### 3. PipelineResult
```python
@dataclass
class PipelineResult:
    session_id: str
    results: List[ClassificationResult]
    timestamp: Optional[datetime] = None
```

### 4. EvaluationResult
```python
@dataclass
class EvaluationResult:
    label: str
    score: float  # 0-100
    criteria_scores: Dict[str, float]
    feedback: str
    recommendations: List[str]
    timestamp: datetime
    session_id: str
```

### 5. FilteringResult
```python
@dataclass
class FilteringResult:
    label: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    action: str  # TERMINATE_CALL, WARN, SUPPORT_AGENT
    alert_level: str
    text: str
    session_context: Optional[List[str]]
    timestamp: datetime
```

---

## 미구현 사항

### 🔴 최우선 (모델 통합)

1. **Korcen 필터 통합**
   - `profanity_filter/korcen_filter.py` 구현 필요
   - Tokenization 단계 명시적 구현
   - Baseline 규칙과의 폴백 메커니즘

2. **KoSentenceBERT 모델 통합**
   - `models/kosentbert_model.py` 구현 필요
   - `intent_classifier/kosentbert_classifier.py` 구현 필요
   - 모델 학습 데이터 준비

### 🟡 높은 우선순위 (고도화)

3. **평가 프레임워크 고도화**
   - 문장 구조 분석 (의존 구문 분석)
   - 감정 톤 분석
   - 대화 흐름 분석 개선

4. **실시간 알림 시스템**
   - 메시지 큐 시스템 (Redis 등)
   - 웹소켓 또는 Server-Sent Events
   - 상담사 대시보드 연동

5. **통화 중단 시스템 연동**
   - 통화 중단 API 인터페이스
   - CRITICAL 이벤트 시 자동 중단

### 🟢 중간 우선순위

6. **모델 Fine-tuning**
   - 학습 데이터셋 준비
   - KoSentenceBERT Fine-tuning 스크립트
   - 모델 배포 및 버전 관리

7. **평가 정확도 향상**
   - 평가 기준 정교화
   - 평가 모델 학습 (선택사항)
   - A/B 테스트 및 검증

### 🔵 낮은 우선순위

8. **개인화된 상담사 지원**
   - 상담사 프로필 시스템
   - 맞춤형 피드백 생성
   - 대시보드 구현

9. **Label 유틸리티 함수**
   - `labeling/label_utils.py` 구현
   - Label 설명 및 예시 데이터베이스

10. **통합 테스트 파일**
    - 전체 파이프라인 테스트
    - 성능 테스트

---

## 향후 계획

### 단기 목표 (1-2주)
1. ✅ Korcen 필터 통합
2. ✅ KoSentenceBERT 모델 통합 (기본)
3. ✅ 실시간 알림 시스템 기본 구축

**목표**: 기본 모델 통합 완료, 시스템 동작 가능 상태

### 중기 목표 (1-2개월)
1. ✅ 평가 프레임워크 고도화
2. ✅ 통화 중단 시스템 연동
3. ✅ 모델 Fine-tuning

**목표**: 프로덕션 환경 배포 가능 상태

### 장기 목표 (3개월 이상)
1. ✅ 평가 정확도 향상
2. ✅ 개인화된 상담사 지원
3. ✅ 추가 기능 개발

**목표**: 완전한 상담사 지원 시스템 구축

---

## 파일 구조

```
linguaproject/logic_classify_system/
├── config/
│   └── labels.py                    # Label 정의 (Normal/Special)
├── data/
│   ├── data_structures.py           # 데이터 구조 정의
│   └── session_manager.py           # 세션 관리
├── preprocessing/
│   └── text_splitter.py             # 문장 단위 분할
├── profanity_filter/
│   ├── profanity_detector.py        # 욕설 감지 통합 인터페이스
│   └── baseline_rules.py            # Baseline 규칙
├── intent_classifier/
│   ├── intent_predictor.py          # 의도 분류 통합 인터페이스
│   └── baseline_rules.py            # Baseline 규칙
├── labeling/
│   └── label_router.py              # Label 기반 라우팅
├── evaluation/
│   ├── normal_label_evaluator.py    # 평가 프레임워크
│   ├── manual_checker.py            # 매뉴얼 준수 확인
│   └── evaluation_result.py         # 평가 결과 데이터 구조
├── filtering/
│   ├── special_label_filter.py       # 종합 필터링
│   ├── baseline_rules.py            # Baseline 규칙
│   ├── event_generator.py           # 이벤트 생성
│   └── alert_system.py              # 알림 시스템
├── pipeline/
│   └── main_pipeline.py             # 메인 파이프라인
└── docs/
    ├── PROJECT_STATUS.md            # 이 문서
    ├── IMPLEMENTATION_PROGRESS_ANALYSIS.md
    ├── PRIORITY_TODO_LIST.md
    └── ...
```

---

## 참고 문서

- **설계 문서**: `docs/LABELING_SYSTEM_DESIGN.md`
- **구현 진행 상황**: `personal/IMPLEMENTATION_PROGRESS_ANALYSIS.md`
- **우선순위 TODO**: `personal/PRIORITY_TODO_LIST.md`
- **구현 현황**: `docs/IMPLEMENTATION_STATUS.md`

---

**마지막 업데이트**: 2024년

