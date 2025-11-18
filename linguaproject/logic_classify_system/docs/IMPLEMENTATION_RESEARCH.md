# 전화상담 품질 관리 시스템 구현 연구

## 1. 전반적인 설계 방향 변경

### 1.1 목적 재정의

기존의 단순 악성 민원 분류 시스템에서 **상담원 대상 Training/Assistance 시스템**으로 설계 방향을 전환합니다.

**참고 사례**: [Qualtrics Contact Center Quality Management](https://www.qualtrics.com/marketplace/contact-center-quality-management/)

- **핵심 목표**: 고객과의 대화에서 문제의 소지가 될만한 상황을 실시간으로 포착하고, 상담원에게 즉각적인 피드백 및 가이드를 제공
- **주요 기능**:
  - 문제 신호(Signal) 포착 및 Score화
  - 상담 품질 종합 평가
  - 상담원 코칭 및 개선 제안

### 1.2 시스템 아키텍처

```
[음성 입력] → [STT] → [Signal Detection] → [Quality Scoring] → [Feedback/Coaching]
                                      ↓
                              [Category-based Response]
```

- **Signal Detection**: 단어/문장/대화 단위에서 문제 신호 포착
- **Quality Scoring**: 상담 전반의 품질 평가
- **Category-based Response**: 카테고리별 맞춤형 대응 방안 제시

---

## 2. Signal 포착 방법론 연구

### 2.1 현재 시스템의 한계점

현재 `risk_based_classifier.py`는 두 가지 극단적인 접근 방식을 사용하고 있습니다:

1. **원시적 방법**: 단순 키워드 매칭 및 카운팅 기반 점수 계산
2. **거대 모델 기반**: KoBERT 같은 대규모 언어 모델을 통한 컨텍스트 분석

**문제점**:
- 단어 단위 신호와 문장 단위 신호를 구분하지 못함
- 각 차원에서 최적화된 방법론이 혼재되어 있지 않음
- 불안정한 성능 (과소/과대 감지)

### 2.2 다층 신호 포착 프레임워크

#### 2.2.1 단어 단위(Word-level) 신호 포착

**특징**:
- 직접적이고 명시적인 악성 표현
- 예: 욕설, 위협 표현, 성적 표현

**적용 방법론**:

1. **정규표현식 기반 패턴 매칭**
   - 장점: 빠른 처리 속도, 명확한 규칙
   - 단점: 변형된 표현 감지 어려움
   - 구현: `classification_criteria.py`의 키워드 리스트 확장

2. **Character-level N-gram 모델**
   - 장점: 오타, 변형된 표현 감지 가능
   - 단점: 계산 비용 증가
   - 구현: FastText, Character CNN 활용

3. **전용 욕설 필터 모델**
   - 장점: 도메인 특화, 높은 정밀도
   - 단점: 학습 데이터 필요
   - 구현: `korcen.py` 기반 통화 상담 특화 필터

**권장 조합**:
```
Word-level Detection = 정규표현식 (1차) + Character N-gram (2차) + 전용 필터 (3차)
```

#### 2.2.2 문장 단위(Sentence-level) 신호 포착

**특징**:
- 맥락에 의존하는 간접적 악성 표현
- 예: 반복성, 무리한 요구, 부당성

**적용 방법론**:

1. **의존 구문 분석(Dependency Parsing)**
   - 장점: 문장 구조 이해, 의미 관계 파악
   - 단점: 한국어 파싱 정확도 이슈
   - 구현: KoNLPy, spaCy 한국어 모델

2. **문장 임베딩 기반 유사도**
   - 장점: 의미적 유사도 측정
   - 단점: 계산 비용
   - 구현: Sentence-BERT, KoSentenceBERT

3. **경량 분류 모델**
   - 장점: 빠른 추론, 실시간 처리 가능
   - 단점: 정확도는 거대 모델보다 낮음
   - 구현: DistilBERT, TinyBERT 기반 Fine-tuning

**권장 조합**:
```
Sentence-level Detection = 의존 구문 분석 (구조) + 문장 임베딩 (의미) + 경량 분류 모델 (종합)
```

#### 2.2.3 대화 단위(Dialogue-level) 신호 포착

**특징**:
- 세션 전체 맥락에서 드러나는 패턴
- 예: 반복 민원, 대화 진전 없음, 상담 맥락 이탈

**적용 방법론**:

1. **대화 흐름 분석(Turn-taking Analysis)**
   - 장점: 대화 구조 파악
   - 구현: 대화 턴 수, 길이, 주제 전환 빈도 분석

2. **세션 임베딩**
   - 장점: 전체 대화의 의미 압축
   - 구현: 대화 전체를 하나의 벡터로 표현

3. **시퀀스 모델**
   - 장점: 시간적 패턴 학습
   - 구현: LSTM, GRU, Transformer 기반 대화 모델

### 2.3 통합 프레임워크 설계

```
┌─────────────────────────────────────────┐
│  Word-level Detection                   │
│  (정규표현식 + Character N-gram + 필터) │
└──────────────┬──────────────────────────┘
               │ 신뢰도 높은 직접적 신호
               ↓
┌─────────────────────────────────────────┐
│  Sentence-level Detection               │
│  (의존 구문 + 임베딩 + 경량 분류)        │
└──────────────┬──────────────────────────┘
               │ 맥락 기반 간접적 신호
               ↓
┌─────────────────────────────────────────┐
│  Dialogue-level Detection               │
│  (대화 흐름 + 세션 임베딩 + 시퀀스 모델) │
└──────────────┬──────────────────────────┘
               │
               ↓
        [Ensemble Decision]
        (가중치 기반 통합)
```

**가중치 전략**:
- Word-level: 직접적 악성 표현 → 높은 가중치 (0.5)
- Sentence-level: 맥락 기반 신호 → 중간 가중치 (0.3)
- Dialogue-level: 패턴 기반 신호 → 낮은 가중치 (0.2)

---

## 3. 윤리검증 데이터셋 구조 분석 및 활용 계획

### 3.1 데이터셋 구조 파악

**데이터셋 위치**: `147.텍스트 윤리검증 데이터/01.데이터/1.Training/`

**파일 구조**:
```
라벨링데이터/aihub/TL1_aihub/
  ├── talksets-train-1/talksets-train-1_aihub.json
  ├── talksets-train-2/talksets-train-2.json
  ├── talksets-train-3/talksets-train-3.json
  ├── talksets-train-4/talksets-train-4.json
  └── talksets-train-5/talksets-train-5.json

원천데이터/TS1/
  ├── talksets-train-1/talksets-train-1.txt
  ├── talksets-train-2/talksets-train-2.txt
  ├── talksets-train-3/talksets-train-3.txt
  ├── talksets-train-4/talksets-train-4.txt
  └── talksets-train-5/talksets-train-5.txt
```

**JSON 구조 (talksets)**:
```json
{
  "talksets": [
    {
      "sentences": [
        {
          "text": "문장 내용",
          "is_immoral": true/false,
          "types": ["CENSURE", "HATE", "SEXUAL", ...],
          "intensity": 1-5
        }
      ]
    }
  ]
}
```

**주요 필드**:
- `is_immoral`: 비윤리성 여부 (boolean)
- `types`: 비윤리 유형 리스트 (CENSURE, HATE, SEXUAL 등)
- `intensity`: 비윤리 강도 (1-5 스케일)

### 3.2 데이터셋 분석 계획

#### 3.2.1 구조 분석 스크립트

**파일**: `analyze_ethics_dataset_structure.py`

**기능**:
1. **전체 통계 수집**
   - 총 talksets 수
   - 총 문장 수
   - 비윤리 문장 비율
   - 비윤리 유형 분포
   - 강도(intensity) 분포

2. **샘플 데이터 추출**
   - 각 유형별 대표 샘플
   - 강도별 샘플
   - 정상 문장 샘플

3. **프로젝트 카테고리 매핑**
   - 윤리검증 데이터의 `types` → 프로젝트의 `ComplaintCategory` 매핑
   - 예: `CENSURE` → `PROFANITY`, `INSULT`
   - 예: `HATE` → `HATE_SPEECH`
   - 예: `SEXUAL` → `SEXUAL_HARASSMENT`

#### 3.2.2 데이터 변환 계획

**목표**: 윤리검증 데이터를 프로젝트의 12개 카테고리 체계로 변환

**변환 전략**:
1. **직접 매핑 가능한 카테고리**
   - `PROFANITY`: CENSURE 중 욕설 관련
   - `INSULT`: CENSURE 중 모욕 관련
   - `HATE_SPEECH`: HATE 전체
   - `SEXUAL_HARASSMENT`: SEXUAL 전체

2. **간접 추론 필요한 카테고리**
   - `REPETITION`: 세션 내 문장 반복 패턴 분석
   - `UNREASONABLE_DEMAND`: 문장 구조 분석 (의존 구문 활용)
   - `IRRELEVANCE`: 대화 맥락 분석
   - `VIOLENCE_THREAT`: CENSURE 중 위협 표현

3. **강도(intensity) 활용**
   - `intensity >= 4`: `ComplaintSeverity.HIGH` 이상
   - `intensity == 3`: `ComplaintSeverity.MEDIUM`
   - `intensity <= 2`: `ComplaintSeverity.LOW`

#### 3.2.3 학습 데이터셋 구축

**출력 형식**: CSV 또는 JSON

**필드**:
- `text`: 문장 텍스트
- `category`: ComplaintCategory (멀티 레이블 가능)
- `severity`: ComplaintSeverity
- `intensity`: 원본 강도
- `source`: "ethics_dataset"

**용도**:
- Word-level 필터 Fine-tuning
- Sentence-level 분류 모델 학습
- Baseline 규칙 검증 및 개선

### 3.3 구현 우선순위

1. **1단계**: 데이터셋 구조 분석 스크립트 작성 및 실행
2. **2단계**: 카테고리 매핑 전략 수립 및 변환 스크립트 작성
3. **3단계**: 변환된 데이터셋으로 Baseline 규칙 검증
4. **4단계**: 변환된 데이터셋으로 경량 분류 모델 Fine-tuning

---

## 4. 상담 품질 평가 시스템 설계

### 4.1 평가 목표

**핵심 질문**: "상담이 종합적으로 잘 이루어졌는가?"

**평가 차원**:
1. **고객 측면**: 고객의 문제가 해결되었는가?
2. **상담원 측면**: 상담원의 대응이 적절했는가?
3. **대화 품질**: 대화가 효율적이고 건설적이었는가?

### 4.2 평가 지표 설계

#### 4.2.1 고객 만족도 지표

**신호 포착**:
- 고객의 감정 변화 (초기 vs 종료)
- 해결 여부 표현 ("이제 이해했어요", "감사합니다" vs "여전히 불만이에요")
- 재상담 요청 여부

**측정 방법**:
- 감정 분석 모델 (KoBERT 기반)
- 키워드 기반 만족도 추출
- 대화 종료 시점 감정 점수

#### 4.2.2 상담원 대응 적절성 지표

**평가 항목**:

1. **전문성 (Professionalism)**
   - 정확한 정보 제공
   - 매뉴얼 준수
   - 전문 용어 사용 적절성

2. **공감 능력 (Empathy)**
   - 고객 감정 인식 및 반영
   - 공감 표현 사용
   - 고객 입장 이해도

3. **문제 해결 능력 (Problem-solving)**
   - 문제 파악 정확도
   - 해결 방안 제시
   - 대안 제시 (해결 불가 시)

4. **소통 능력 (Communication)**
   - 명확한 설명
   - 적절한 질문
   - 대화 주도력

**측정 방법**:
- 상담원 발화 분석 (STT 결과)
- 키워드/패턴 매칭
- 문장 구조 분석 (의존 구문)
- 감정 톤 분석

#### 4.2.3 대화 효율성 지표

**평가 항목**:
- 대화 길이 (적절한지)
- 반복 질문 빈도
- 주제 이탈 빈도
- 해결까지 소요 시간

**측정 방법**:
- 대화 턴 수 분석
- 주제 전환 감지
- 시간 기반 메트릭

### 4.3 종합 점수 계산

**점수 체계** (0-100점):

```
종합 점수 = 
  고객 만족도 (30%) +
  상담원 대응 적절성 (50%) +
  대화 효율성 (20%)
```

**등급 체계**:
- 90-100점: 우수 (Excellent)
- 80-89점: 양호 (Good)
- 70-79점: 보통 (Average)
- 60-69점: 미흡 (Below Average)
- 0-59점: 불량 (Poor)

### 4.4 피드백 생성

**카테고리별 대응 방향**:

1. **문제 신호 감지 시**
   - 즉시 알림 (실시간)
   - 권장 대응 방안 제시
   - 예: "고객이 반복 질문을 하고 있습니다. 명확한 해결 방안을 제시해주세요."

2. **상담 종료 후**
   - 종합 평가 리포트
   - 강점 및 개선점 제시
   - 코칭 제안

**구현 방향**:
- Rule-based 템플릿 (초기)
- 템플릿 + LLM 기반 개인화 (향후)

### 4.5 구현 로드맵

**Phase 1: Baseline 구축**
- 키워드/패턴 기반 평가
- 간단한 점수 계산 로직
- 기본 피드백 템플릿

**Phase 2: 모델 통합**
- 감정 분석 모델 통합
- 문장 구조 분석 통합
- 대화 흐름 분석 통합

**Phase 3: 고도화**
- 개인화된 코칭
- 실시간 대시보드
- 트렌드 분석

---

## 5. 통합 구현 계획

### 5.1 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    음성 입력 (STT)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│           다층 신호 포착 시스템                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Word-level   │  │Sentence-level│  │Dialogue-level│  │
│  │  Detection   │  │  Detection   │  │  Detection   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         └─────────────────┴──────────────────┘          │
│                        │                                │
│                        ↓                                │
│              [Ensemble Decision]                        │
│              (카테고리별 분류)                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│            상담 품질 평가 시스템                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │고객 만족도   │  │상담원 대응   │  │대화 효율성   │  │
│  │  평가       │  │  적절성 평가 │  │  평가        │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         └─────────────────┴──────────────────┘          │
│                        │                                │
│                        ↓                                │
│              [종합 점수 계산]                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│            피드백 및 대응 시스템                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │실시간 알림   │  │종합 리포트   │  │코칭 제안     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 5.2 파일 구조

```
linguaproject/logic_classify_system/
├── classification_criteria.py          # 분류 기준 정의 (기존)
├── signal_detection/
│   ├── word_level_detector.py          # 단어 단위 신호 포착
│   ├── sentence_level_detector.py      # 문장 단위 신호 포착
│   ├── dialogue_level_detector.py      # 대화 단위 신호 포착
│   └── ensemble_classifier.py          # 통합 분류기
├── quality_assessment/
│   ├── customer_satisfaction.py         # 고객 만족도 평가
│   ├── agent_performance.py            # 상담원 대응 평가
│   ├── dialogue_efficiency.py           # 대화 효율성 평가
│   └── overall_scorer.py                # 종합 점수 계산
├── feedback_system/
│   ├── realtime_alert.py                # 실시간 알림
│   ├── report_generator.py              # 리포트 생성
│   └── coaching_suggestions.py           # 코칭 제안
├── data_processing/
│   ├── analyze_ethics_dataset.py        # 윤리검증 데이터셋 분석
│   ├── convert_ethics_dataset.py        # 데이터 변환
│   └── dataset_validator.py             # 데이터 검증
└── IMPLEMENTATION_RESEARCH.md           # 본 문서
```

### 5.3 구현 우선순위

**1단계 (즉시)**: 
- 윤리검증 데이터셋 구조 분석
- Word-level + Sentence-level 기본 프레임워크 구축
- Baseline 상담 품질 평가 시스템

**2단계 (단기)**:
- Dialogue-level 신호 포착 추가
- 모델 Fine-tuning (윤리검증 데이터 활용)
- 실시간 피드백 시스템

**3단계 (중기)**:
- 고도화된 상담 품질 평가
- 개인화된 코칭 시스템
- 대시보드 및 시각화

---

## 6. 참고 자료 및 연구 방향

### 6.1 관련 논문 및 연구

- **Contact Center Quality Management**: Qualtrics, Verint 등 상용 솔루션 분석
- **Multi-level Text Classification**: Word/Sentence/Document level 분류 방법론
- **Dialogue Quality Assessment**: 대화 품질 평가 연구
- **Korean NLP**: KoBERT, KoSentenceBERT 등 한국어 특화 모델

### 6.2 기술 스택

- **NLP**: KoBERT, KoSentenceBERT, KoNLPy
- **ML Framework**: PyTorch, Transformers
- **Text Processing**: spaCy (한국어), NLTK
- **Evaluation**: scikit-learn metrics

### 6.3 데이터셋

- **윤리검증 데이터셋**: 147.텍스트 윤리검증 데이터
- **상담 음성 데이터셋**: 022.민원(콜센터)_질의-응답_데이터
- **민간분야 고객 상담 데이터**: 추가 확보 필요

---

## 7. 다음 단계

1. **윤리검증 데이터셋 상세 분석 스크립트 작성**
2. **Word-level + Sentence-level 기본 프레임워크 구현**
3. **Baseline 상담 품질 평가 시스템 설계 및 구현**
4. **카테고리별 대응 방향 정의 및 템플릿 작성**


