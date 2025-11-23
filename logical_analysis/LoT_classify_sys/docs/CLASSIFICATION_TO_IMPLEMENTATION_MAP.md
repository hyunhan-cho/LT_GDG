# 분류 시스템 → 기능 구현 매핑

## 📚 문서 역할

**이 문서(CLASSIFICATION_TO_IMPLEMENTATION_MAP.md)**는 **분류 결과가 실제로 어떤 기능 구현으로 이어지는지** 명확히 매핑한 문서입니다.

- 분류 결과 → 처리 경로
- 각 경로별 구현 기능
- 현재 구현 상태
- 미구현 기능 및 우선순위

---

## 1. 전체 처리 흐름

```
[STT 결과] 
    ↓
[문장 단위 분할]
    ↓
[1차: 욕설 필터링] → ProfanityDetector
    ↓
[2차: 발화 의도 분류] → IntentPredictor
    ↓
[Label 결정] → Normal Label (6개) 또는 Special Label (6개)
    ↓
[Label 라우팅] → LabelRouter
    ├─ Normal Label → [평가 프레임워크] → NormalLabelEvaluator
    └─ Special Label → [종합 필터링] → SpecialLabelFilter
```

---

## 2. Normal Label (6개) → 평가 프레임워크

### 2.1 목적

**상담사가 시스템 매뉴얼에 따라 적절히 대응했는지 평가**하여, 실시간 피드백 및 개선 제안을 제공합니다.

### 2.2 Normal Label 목록

| Label | 정의 | 평가 기준 |
|-------|------|----------|
| **INQUIRY** | 문의 | 정보 제공 정확성, 매뉴얼 준수, 소통 명확성 |
| **COMPLAINT** | 불만/민원 | 공감 능력, 문제 해결 능력, 매뉴얼 준수 |
| **REQUEST** | 요청 | 매뉴얼 준수, 문제 해결 능력, 소통 명확성 |
| **CLARIFICATION** | 명확화 요청 | 소통 명확성, 공감 능력, 정보 제공 정확성 |
| **CONFIRMATION** | 확인 | 정보 제공 정확성, 소통 명확성 |
| **CLOSING** | 종료 | 매뉴얼 준수, 소통 명확성 |

### 2.3 구현 기능

#### 2.3.1 평가 항목 (5가지)

1. **정보 제공 정확성 (information_accuracy)**
   - **목적**: 상담사가 정확한 정보를 제공했는가?
   - **구현 방법**:
     - ✅ 현재: 키워드 기반 확인 (임시)
     - 🔴 미구현: 매뉴얼 기반 정보 검증
     - 🔴 미구현: 문장 구조 분석 (의존 구문)
   - **가중치**: 0.3

2. **매뉴얼 준수 (manual_compliance)**
   - **목적**: 매뉴얼에 명시된 절차를 따랐는가?
   - **구현 방법**:
     - ✅ 현재: ManualChecker 기본 구조
     - 🔴 미구현: 매뉴얼 JSON 파일 로드
     - 🔴 미구현: 필수 표현/절차 확인
   - **가중치**: 0.3

3. **소통 명확성 (communication_clarity)**
   - **목적**: 명확하고 이해하기 쉬운 설명을 했는가?
   - **구현 방법**:
     - ✅ 현재: 문장 길이 기반 확인 (임시)
     - 🔴 미구현: 문장 구조 분석 (의존 구문)
     - 🔴 미구현: 설명 명확도 측정
   - **가중치**: 0.2

4. **공감 능력 (empathy)**
   - **목적**: 고객의 감정을 인식하고 반영했는가?
   - **구현 방법**:
     - ✅ 현재: 공감 표현 키워드 확인 (임시)
     - 🔴 미구현: 감정 분석 모델 통합
     - 🔴 미구현: 감정 톤 분석
   - **가중치**: 0.1

5. **문제 해결 능력 (problem_solving)**
   - **목적**: 적절한 해결 방안을 제시했는가?
   - **구현 방법**:
     - ✅ 현재: 해결 방안 키워드 확인 (임시)
     - 🔴 미구현: 대화 흐름 분석
     - 🔴 미구현: 해결 방안 적절성 평가
   - **가중치**: 0.1

#### 2.3.2 평가 결과

**데이터 구조**: `EvaluationResult`
```python
@dataclass
class EvaluationResult:
    label: str                    # Normal Label
    score: float                  # 종합 점수 (0-100)
    criteria_scores: Dict[str, float]  # 항목별 점수
    feedback: str                 # 피드백 메시지
    recommendations: List[str]    # 개선 제안
    timestamp: datetime
```

**점수 체계**:
- 90-100점: 우수 (Excellent)
- 80-89점: 양호 (Good)
- 70-79점: 보통 (Average)
- 60-69점: 미흡 (Below Average)
- 0-59점: 불량 (Poor)

#### 2.3.3 구현 상태

| 기능 | 상태 | 파일 | 비고 |
|------|------|------|------|
| 기본 평가 프레임워크 | ✅ 완료 | `evaluation/normal_label_evaluator.py` | 기본 구조 완성 |
| 키워드 기반 평가 | ✅ 완료 | `evaluation/normal_label_evaluator.py` | 임시 구현 |
| 매뉴얼 준수 확인 | 🔴 미구현 | `evaluation/manual_checker.py` | 기본 구조만 있음 |
| 문장 구조 분석 | 🔴 미구현 | - | 의존 구문 분석 필요 |
| 감정 분석 모델 | 🔴 미구현 | - | KoBERT 기반 모델 통합 필요 |
| 대화 흐름 분석 | 🔴 미구현 | - | 세션 맥락 분석 필요 |

---

## 3. Special Label (6개) → 종합 필터링

### 3.1 목적

**문제의 소지가 있는 발화를 감지**하여, 심각도에 따라 **통화 중단/경고 알림/상담사 지원**과 같은 대응 이벤트를 발생시킵니다.

### 3.2 Special Label 목록

| Label | 심각도 | 이벤트 유형 | 대응 방안 |
|-------|--------|------------|----------|
| **VIOLENCE_THREAT** | CRITICAL | 즉시 통화 중단 + 경고 알림 | 통화 중단, 녹음 보관, 법적 조치 검토 |
| **SEXUAL_HARASSMENT** | CRITICAL | 즉시 통화 중단 + 경고 알림 | 통화 중단, 녹음 보관, 법적 조치 검토 |
| **PROFANITY** | HIGH | 경고 알림 + 통화 중단 경고 | 경고 알림, 반복 시 통화 중단 |
| **HATE_SPEECH** | HIGH | 경고 알림 + 통화 중단 경고 | 경고 알림, 반복 시 통화 중단 |
| **UNREASONABLE_DEMAND** | MEDIUM~HIGH | 상담사 지원 알림 | 권한 밖 요구 알림, 매뉴얼 가이드 제공 |
| **REPETITION** | MEDIUM | 상담사 지원 알림 | 반복 상황 알림, 대화 전환 전략 제시 |

### 3.3 구현 기능

#### 3.3.1 이벤트 생성

**데이터 구조**: `FilteringEvent`
```python
@dataclass
class FilteringEvent:
    label: str                    # Special Label
    severity: str                 # CRITICAL, HIGH, MEDIUM
    action: str                   # TERMINATE_CALL, WARN, SUPPORT_AGENT
    alert_level: str              # CRITICAL, HIGH, MEDIUM
    timestamp: datetime
    session_id: str
    context: List[str]            # 대화 맥락
```

**이벤트 유형**:
1. **TERMINATE_CALL**: 즉시 통화 중단
   - VIOLENCE_THREAT, SEXUAL_HARASSMENT
   - 녹음 보관, 법적 조치 검토

2. **WARN**: 경고 알림 + 통화 중단 경고
   - PROFANITY, HATE_SPEECH
   - 반복 시 통화 중단

3. **SUPPORT_AGENT**: 상담사 지원 알림
   - UNREASONABLE_DEMAND, REPETITION
   - 매뉴얼 가이드 제공, 대화 전환 전략 제시

#### 3.3.2 알림 시스템

**구현 기능**:
- ✅ 현재: AlertSystem 기본 구조
- 🔴 미구현: 실시간 알림 발송 (웹소켓, API 등)
- 🔴 미구현: 알림 레벨별 우선순위 처리
- 🔴 미구현: 알림 히스토리 관리

#### 3.3.3 통화 중단 연동

**구현 기능**:
- 🔴 미구현: 통화 중단 API 연동
- 🔴 미구현: 중단 사유 기록
- 🔴 미구현: 중단 후 조치 프로세스

#### 3.3.4 구현 상태

| 기능 | 상태 | 파일 | 비고 |
|------|------|------|------|
| 기본 필터링 구조 | ✅ 완료 | `filtering/special_label_filter.py` | 기본 구조 완성 |
| 이벤트 생성 | ✅ 완료 | `filtering/event_generator.py` | 기본 구조 완성 |
| 알림 시스템 | 🔴 미구현 | `filtering/alert_system.py` | 기본 구조만 있음 |
| 통화 중단 연동 | 🔴 미구현 | - | API 연동 필요 |
| 반복 감지 로직 | 🔴 미구현 | - | 세션 맥락 기반 반복 감지 필요 |

---

## 4. Label 라우팅

### 4.1 목적

**Label 타입에 따라 적절한 처리 경로로 라우팅**합니다.

### 4.2 라우팅 로직

```python
if label_type == "NORMAL":
    # 평가 프레임워크로 이동
    evaluation_result = evaluator.evaluate(
        label, customer_text, agent_text, session_context
    )
    return RouterResult("EVALUATION", evaluation_result)

elif label_type == "SPECIAL":
    # 종합 필터링으로 이동
    filtering_result = filter.filter(
        label, text, session_context
    )
    return RouterResult("FILTERING", filtering_result)
```

### 4.3 구현 상태

| 기능 | 상태 | 파일 | 비고 |
|------|------|------|------|
| 기본 라우팅 | ✅ 완료 | `labeling/label_router.py` | 기본 구조 완성 |
| 평가 프레임워크 연동 | ✅ 완료 | `labeling/label_router.py` | 연동 완료 |
| 필터링 시스템 연동 | ✅ 완료 | `labeling/label_router.py` | 연동 완료 |

---

## 5. 파이프라인 통합

### 5.1 현재 구현 상태

**파일**: `pipeline/main_pipeline.py`

**구현된 기능**:
- ✅ 문장 단위 분할
- ✅ 욕설 필터링 (1차)
- ✅ 발화 의도 분류 (2차)
- ✅ 세션 관리

**미구현 기능**:
- 🔴 Label 라우팅 통합
- 🔴 평가 프레임워크 통합
- 🔴 필터링 시스템 통합

### 5.2 필요한 통합 작업

1. **Label 라우팅 통합**
   ```python
   # main_pipeline.py에 추가 필요
   from ..labeling.label_router import LabelRouter
   
   router = LabelRouter()
   router_result = router.route(classification_result, session_context, agent_text)
   ```

2. **평가 결과 처리**
   ```python
   if router_result.route_type == "EVALUATION":
       evaluation_result = router_result.result
       # 평가 결과 저장/전송
   ```

3. **필터링 결과 처리**
   ```python
   if router_result.route_type == "FILTERING":
       filtering_result = router_result.result
       # 이벤트 처리 (통화 중단, 알림 등)
   ```

---

## 6. 우선순위별 구현 계획

### 6.1 🔴 최우선 (즉시 구현 필요)

1. **파이프라인 통합**
   - Label 라우팅 통합
   - 평가 프레임워크 통합
   - 필터링 시스템 통합
   - **예상 소요**: 1-2일

2. **KoSentenceBERT 모델 통합**
   - Normal Label 분류 기능
   - 모델 로더 구현
   - 추론 인터페이스 구현
   - **예상 소요**: 5-7일

### 6.2 🟡 높은 우선순위 (단기)

1. **평가 프레임워크 고도화**
   - 매뉴얼 JSON 파일 로드
   - 문장 구조 분석 (의존 구문)
   - 감정 분석 모델 통합
   - 대화 흐름 분석
   - **예상 소요**: 4-5일

2. **필터링 시스템 고도화**
   - 실시간 알림 시스템 구축
   - 통화 중단 API 연동
   - 반복 감지 로직 구현
   - **예상 소요**: 3-4일

### 6.3 🟢 중간 우선순위 (중기)

1. **모델 Fine-tuning**
   - 윤리검증 데이터셋 활용
   - Normal Label 학습 데이터 준비
   - **예상 소요**: 7-10일

2. **평가 정확도 향상**
   - 평가 기준 정교화
   - A/B 테스트 및 검증
   - **예상 소요**: 5-7일

---

## 7. 구현 체크리스트

### 7.1 Normal Label 평가 프레임워크

- [x] 기본 평가 프레임워크 구조
- [x] 키워드 기반 평가 (임시)
- [ ] 매뉴얼 JSON 파일 로드
- [ ] 문장 구조 분석 (의존 구문)
- [ ] 감정 분석 모델 통합
- [ ] 대화 흐름 분석
- [ ] 평가 결과 리포트 생성

### 7.2 Special Label 필터링 시스템

- [x] 기본 필터링 구조
- [x] 이벤트 생성 구조
- [ ] 실시간 알림 시스템
- [ ] 통화 중단 API 연동
- [ ] 반복 감지 로직
- [ ] 이벤트 히스토리 관리

### 7.3 파이프라인 통합

- [x] 기본 파이프라인 구조
- [x] 욕설 필터링 통합
- [x] 발화 의도 분류 통합
- [ ] Label 라우팅 통합
- [ ] 평가 프레임워크 통합
- [ ] 필터링 시스템 통합

---

## 8. 참고 문서

- **라벨링 시스템 설계**: `LABELING_SYSTEM_DESIGN.md`
- **파일 구조 설계**: `IMPLEMENTATION_FILE_STRUCTURE.md`
- **구현 현황**: `IMPLEMENTATION_STATUS.md`
- **연구 및 설계 방향**: `IMPLEMENTATION_RESEARCH.md`

---

**최종 업데이트**: 2024년 (현재 시점)

