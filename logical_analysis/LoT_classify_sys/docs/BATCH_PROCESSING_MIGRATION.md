# 실시간 처리 → 배치 처리 전환 가이드

**작성일**: 2024년  
**목적**: STT된 데이터를 기반으로 상담원의 통화 품질을 분석하는 배치 처리 형태로 프레임워크 전환 시 필요한 모듈별 변동사항 정리

---

## 📋 목차

1. [전환 개요](#전환-개요)
2. [아키텍처 변경](#아키텍처-변경)
3. [모듈별 변동사항](#모듈별-변동사항)
4. [데이터 구조 변경](#데이터-구조-변경)
5. [새로운 모듈 필요성](#새로운-모듈-필요성)
6. [마이그레이션 체크리스트](#마이그레이션-체크리스트)

---

## 전환 개요

### 현재 구조 (실시간 처리)
- **입력**: 실시간 음성 스트림 → STT → 문장 단위 실시간 처리
- **처리**: 문장이 들어올 때마다 즉시 분석 및 알림
- **출력**: 실시간 알림, 통화 중단 명령

### 변경 후 구조 (배치 처리)
- **입력**: 완료된 통화의 STT 결과 (전체 대화 텍스트)
- **처리**: 전체 대화를 한 번에 분석하여 종합 평가
- **출력**: 통화 품질 리포트, 개선 제안, 통계 분석

### 주요 차이점

| 항목 | 실시간 처리 | 배치 처리 |
|------|------------|----------|
| **처리 시점** | 통화 중 실시간 | 통화 종료 후 |
| **입력 데이터** | 스트리밍 문장 | 전체 대화 텍스트 |
| **세션 관리** | 실시간 업데이트 | 전체 맥락 한 번에 로드 |
| **알림** | 즉시 알림 발송 | 리포트에 포함 |
| **평가** | 문장별 평가 | 통화 전체 종합 평가 |
| **목적** | 실시간 개입/지원 | 사후 분석/교육 |

---

## 아키텍처 변경

### 기존 파이프라인 (실시간)
```
[음성 스트림] → [STT] → [문장 단위 분할] → [즉시 처리] → [실시간 알림]
                                                          ↓
                                                    [통화 중단]
```

### 변경 후 파이프라인 (배치)
```
[STT 완료 데이터] → [전체 대화 로드] → [전체 분석] → [종합 평가] → [리포트 생성]
                                                                    ↓
                                                          [통계/트렌드 분석]
```

---

## 모듈별 변동사항

### 1. 파이프라인 모듈 (`pipeline/main_pipeline.py`)

#### 🔴 주요 변경사항

**현재 구조**:
```python
def process(self, text: str, session_id: str) -> PipelineResult:
    # 문장 단위로 순차 처리
    for sentence in customer_sentences:
        # 즉시 처리 및 세션 업데이트
        result = self.intent_predictor.predict(...)
        self.session_manager.add_sentence(session_id, sentence)
```

**변경 후 구조**:
```python
def process_batch(self, full_transcript: str, session_id: str) -> BatchAnalysisResult:
    """
    전체 통화를 한 번에 분석
    
    Args:
        full_transcript: 전체 STT 결과 (고객/상담사 구분 포함)
        session_id: 세션 ID
    
    Returns:
        BatchAnalysisResult (전체 통화 분석 결과)
    """
    # 1. 전체 대화 구조 분석
    conversation_structure = self._analyze_conversation_structure(full_transcript)
    
    # 2. 전체 문장을 한 번에 분할
    all_sentences = self.text_splitter.split_all_sentences(full_transcript)
    customer_sentences, agent_sentences = self.text_splitter.split_by_speaker(full_transcript)
    
    # 3. 전체 맥락을 한 번에 로드 (세션 관리자 변경 필요)
    full_context = self.session_manager.load_full_context(session_id, all_sentences)
    
    # 4. 배치 처리 (병렬 처리 가능)
    classification_results = []
    for customer_sentence, agent_sentence in zip(customer_sentences, agent_sentences):
        # 고객 발화 분석
        profanity_result = self.profanity_detector.detect(customer_sentence)
        classification_result = self.intent_predictor.predict(
            customer_sentence,
            profanity_result.is_profanity,
            full_context  # 전체 맥락 사용
        )
        
        # 상담사 발화 평가 (Normal Label인 경우)
        if classification_result.label_type == "NORMAL":
            evaluation_result = self.label_router.route(
                classification_result,
                full_context,
                agent_sentence
            )
            classification_results.append((classification_result, evaluation_result))
        else:
            filtering_result = self.label_router.route(
                classification_result,
                full_context
            )
            classification_results.append((classification_result, filtering_result))
    
    # 5. 종합 분석
    summary = self._generate_summary(classification_results, conversation_structure)
    
    return BatchAnalysisResult(
        session_id=session_id,
        results=classification_results,
        summary=summary,
        timestamp=datetime.now()
    )
```

#### 변경 포인트
- ✅ `process()` → `process_batch()` 메서드로 변경
- ✅ 전체 대화를 한 번에 처리
- ✅ 세션 관리자에서 전체 맥락을 한 번에 로드
- ✅ 종합 분석 및 리포트 생성 기능 추가
- ❌ `process_single_sentence()` 메서드 제거 또는 deprecated 처리

---

### 2. 세션 관리 모듈 (`data/session_manager.py`)

#### 🔴 주요 변경사항

**현재 구조**:
```python
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, List[str]] = {}  # 실시간 업데이트
    
    def add_sentence(self, session_id: str, sentence: str):
        # 실시간으로 문장 추가
        self.sessions[session_id].append(sentence)
    
    def get_context(self, session_id: str, window_size: int = 5):
        # 최근 N개 문장만 반환
        return self.sessions[session_id][-window_size:]
```

**변경 후 구조**:
```python
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, ConversationContext] = {}
    
    def load_full_context(self, session_id: str, all_sentences: List[str]) -> ConversationContext:
        """
        전체 대화 맥락을 한 번에 로드
        
        Args:
            session_id: 세션 ID
            all_sentences: 전체 문장 리스트
        
        Returns:
            ConversationContext (전체 대화 맥락)
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationContext()
        
        context = ConversationContext()
        context.all_sentences = all_sentences
        context.conversation_structure = self._analyze_structure(all_sentences)
        context.turn_count = len(all_sentences)
        context.duration = self._calculate_duration(all_sentences)  # 타임스탬프 기반
        
        self.sessions[session_id] = context
        return context
    
    def get_full_context(self, session_id: str) -> ConversationContext:
        """전체 맥락 반환"""
        return self.sessions.get(session_id)
    
    def get_context_window(self, session_id: str, start_idx: int, end_idx: int) -> List[str]:
        """
        특정 구간의 맥락 반환 (대화 흐름 분석용)
        
        Args:
            session_id: 세션 ID
            start_idx: 시작 인덱스
            end_idx: 종료 인덱스
        """
        context = self.sessions.get(session_id)
        if not context:
            return []
        return context.all_sentences[start_idx:end_idx]
    
    # 실시간 메서드는 deprecated 처리
    def add_sentence(self, session_id: str, sentence: str):
        """Deprecated: 배치 처리에서는 사용하지 않음"""
        warnings.warn("add_sentence is deprecated for batch processing", DeprecationWarning)
        # ... 기존 로직 유지 (하위 호환성)
```

#### 새로운 데이터 구조
```python
@dataclass
class ConversationContext:
    """전체 대화 맥락"""
    all_sentences: List[str]
    conversation_structure: Dict[str, Any]  # 대화 구조 분석 결과
    turn_count: int  # 발화 횟수
    duration: float  # 통화 시간 (초)
    customer_sentences: List[str]
    agent_sentences: List[str]
    timestamps: Optional[List[datetime]] = None  # 각 발화의 타임스탬프
```

#### 변경 포인트
- ✅ 실시간 업데이트 방식 → 전체 로드 방식
- ✅ `ConversationContext` 데이터 구조 추가
- ✅ 대화 구조 분석 기능 추가
- ✅ 타임스탬프 기반 분석 지원
- ⚠️ 기존 `add_sentence()` 메서드는 deprecated 처리 (하위 호환성)

---

### 3. 알림 시스템 모듈 (`filtering/alert_system.py`)

#### 🔴 주요 변경사항

**현재 구조**:
```python
class AlertSystem:
    def send_alert(self, event: FilteringEvent):
        # 즉시 알림 발송
        if event.alert_level == "CRITICAL":
            self._send_critical_alert(event)  # 즉시 통화 중단
```

**변경 후 구조**:
```python
class AlertSystem:
    def __init__(self):
        self.alert_history: List[FilteringEvent] = []
        self.report_generator = ReportGenerator()  # 리포트 생성기 추가
    
    def collect_alert(self, event: FilteringEvent):
        """
        알림 수집 (즉시 발송하지 않음)
        
        Args:
            event: 필터링 이벤트
        """
        self.alert_history.append(event)
    
    def generate_alert_report(self, session_id: str) -> AlertReport:
        """
        세션별 알림 리포트 생성
        
        Args:
            session_id: 세션 ID
        
        Returns:
            AlertReport (알림 리포트)
        """
        session_alerts = [e for e in self.alert_history if e.session_id == session_id]
        
        # 심각도별 통계
        severity_stats = self._calculate_severity_stats(session_alerts)
        
        # 알림 타임라인
        alert_timeline = self._generate_timeline(session_alerts)
        
        # 권장 사항
        recommendations = self._generate_recommendations(session_alerts)
        
        return AlertReport(
            session_id=session_id,
            alerts=session_alerts,
            severity_stats=severity_stats,
            timeline=alert_timeline,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    # 기존 실시간 메서드는 deprecated 처리
    def send_alert(self, event: FilteringEvent):
        """Deprecated: 배치 처리에서는 collect_alert 사용"""
        warnings.warn("send_alert is deprecated for batch processing", DeprecationWarning)
        self.collect_alert(event)
```

#### 변경 포인트
- ✅ 즉시 알림 발송 → 알림 수집 및 리포트 생성
- ✅ `AlertReport` 데이터 구조 추가
- ✅ 심각도별 통계 및 타임라인 생성
- ✅ 권장 사항 자동 생성
- ❌ 실시간 통화 중단 기능 제거 (배치 처리에서는 불필요)

---

### 4. 평가 프레임워크 모듈 (`evaluation/normal_label_evaluator.py`)

#### 🟡 주요 변경사항

**현재 구조**:
```python
def evaluate(self, label: str, customer_text: str, agent_text: str, 
             session_context: List[str]) -> EvaluationResult:
    # 단일 발화에 대한 평가
    criteria_scores = {}
    for criterion in criteria:
        score = self._evaluate_criterion(...)
    return EvaluationResult(...)
```

**변경 후 구조**:
```python
def evaluate(self, label: str, customer_text: str, agent_text: str, 
             session_context: ConversationContext) -> EvaluationResult:
    """
    단일 발화 평가 (기존 유지, 하지만 전체 맥락 활용)
    """
    # 전체 대화 맥락 활용 가능
    conversation_flow = session_context.conversation_structure
    # ... 기존 로직
    
def evaluate_conversation(self, session_id: str, 
                        all_evaluations: List[EvaluationResult]) -> ConversationEvaluation:
    """
    전체 통화 종합 평가 (새로운 메서드)
    
    Args:
        session_id: 세션 ID
        all_evaluations: 모든 발화별 평가 결과
    
    Returns:
        ConversationEvaluation (전체 통화 평가)
    """
    # 1. Label별 평가 통계
    label_stats = self._calculate_label_stats(all_evaluations)
    
    # 2. 평가 기준별 평균 점수
    criteria_averages = self._calculate_criteria_averages(all_evaluations)
    
    # 3. 통화 전체 종합 점수
    overall_score = self._calculate_overall_score(all_evaluations)
    
    # 4. 개선 영역 식별
    improvement_areas = self._identify_improvement_areas(criteria_averages)
    
    # 5. 강점 식별
    strengths = self._identify_strengths(criteria_averages)
    
    # 6. 통화 품질 등급
    quality_grade = self._calculate_quality_grade(overall_score)
    
    return ConversationEvaluation(
        session_id=session_id,
        overall_score=overall_score,
        quality_grade=quality_grade,
        label_stats=label_stats,
        criteria_averages=criteria_averages,
        improvement_areas=improvement_areas,
        strengths=strengths,
        individual_evaluations=all_evaluations,
        timestamp=datetime.now()
    )
```

#### 새로운 데이터 구조
```python
@dataclass
class ConversationEvaluation:
    """전체 통화 평가"""
    session_id: str
    overall_score: float  # 0-100
    quality_grade: str  # "EXCELLENT", "GOOD", "FAIR", "POOR"
    label_stats: Dict[str, int]  # Label별 발생 횟수
    criteria_averages: Dict[str, float]  # 평가 기준별 평균 점수
    improvement_areas: List[str]  # 개선이 필요한 영역
    strengths: List[str]  # 강점
    individual_evaluations: List[EvaluationResult]  # 개별 평가 결과
    timestamp: datetime
```

#### 변경 포인트
- ✅ 단일 발화 평가 유지 (하지만 전체 맥락 활용)
- ✅ 전체 통화 종합 평가 메서드 추가
- ✅ 통계 및 트렌드 분석 기능 추가
- ✅ 개선 영역 및 강점 자동 식별

---

### 5. 라우팅 모듈 (`labeling/label_router.py`)

#### 🟡 변경사항 (미미함)

**현재 구조**: 이미 배치 처리에 적합한 구조

**변경 사항**:
- `session_context` 파라미터 타입 변경: `List[str]` → `ConversationContext`
- 전체 맥락 활용 가능

```python
def route(self, classification_result: ClassificationResult, 
          session_context: ConversationContext,  # 타입 변경
          agent_text: Optional[str] = None) -> RouterResult:
    # 기존 로직 유지, 하지만 전체 맥락 활용 가능
```

---

### 6. 전처리 모듈 (`preprocessing/text_splitter.py`)

#### 🟡 변경사항 (보완 필요)

**추가 기능**:
```python
def split_all_sentences(self, text: str) -> List[str]:
    """
    전체 텍스트를 문장 단위로 분할 (타임스탬프 포함 가능)
    
    Args:
        text: 전체 STT 결과
    
    Returns:
        문장 리스트
    """
    # 기존 로직 + 타임스탬프 파싱 (STT 결과에 포함된 경우)
    pass

def analyze_conversation_structure(self, text: str) -> Dict[str, Any]:
    """
    대화 구조 분석
    
    Returns:
        {
            "turn_count": int,  # 발화 횟수
            "customer_turns": int,
            "agent_turns": int,
            "avg_turn_length": float,
            "conversation_phases": List[str]  # 인사, 본문, 마무리 등
        }
    """
    pass
```

---

### 7. 종합 필터링 모듈 (`filtering/special_label_filter.py`)

#### 🟡 변경사항

**현재 구조**:
```python
def filter(self, label: str, text: str, 
           session_context: Optional[List[str]] = None) -> FilteringResult:
    # 즉시 이벤트 생성 및 알림 발송
    event = self.event_generator.generate(...)
    self.alert_system.send_alert(event)
```

**변경 후 구조**:
```python
def filter(self, label: str, text: str, 
           session_context: Optional[ConversationContext] = None) -> FilteringResult:
    """
    필터링 (이벤트는 수집만, 발송하지 않음)
    """
    event = self.event_generator.generate(...)
    self.alert_system.collect_alert(event)  # send_alert → collect_alert
    
    return FilteringResult(...)
```

---

## 데이터 구조 변경

### 새로운 데이터 구조

#### 1. BatchAnalysisResult
```python
@dataclass
class BatchAnalysisResult:
    """배치 분석 결과"""
    session_id: str
    results: List[Tuple[ClassificationResult, Union[EvaluationResult, FilteringResult]]]
    summary: ConversationSummary
    timestamp: datetime
```

#### 2. ConversationSummary
```python
@dataclass
class ConversationSummary:
    """통화 요약"""
    total_turns: int
    customer_turns: int
    agent_turns: int
    duration: float  # 초
    normal_labels: Dict[str, int]  # Normal Label별 발생 횟수
    special_labels: Dict[str, int]  # 특수 Label별 발생 횟수
    overall_quality_score: float
    quality_grade: str
```

#### 3. AlertReport
```python
@dataclass
class AlertReport:
    """알림 리포트"""
    session_id: str
    alerts: List[FilteringEvent]
    severity_stats: Dict[str, int]  # 심각도별 통계
    timeline: List[Dict[str, Any]]  # 알림 타임라인
    recommendations: List[str]
    timestamp: datetime
```

#### 4. ConversationEvaluation
```python
@dataclass
class ConversationEvaluation:
    """전체 통화 평가"""
    session_id: str
    overall_score: float
    quality_grade: str
    label_stats: Dict[str, int]
    criteria_averages: Dict[str, float]
    improvement_areas: List[str]
    strengths: List[str]
    individual_evaluations: List[EvaluationResult]
    timestamp: datetime
```

---

## 새로운 모듈 필요성

### 1. 리포트 생성 모듈 (`reporting/report_generator.py`)

**역할**: 분석 결과를 리포트 형태로 생성

**기능**:
- 통화 품질 리포트 생성 (PDF, HTML, JSON)
- 통계 및 차트 생성
- 개선 제안 리포트
- 비교 분석 (다른 통화와 비교)

```python
class ReportGenerator:
    def generate_quality_report(self, evaluation: ConversationEvaluation) -> QualityReport:
        """통화 품질 리포트 생성"""
        pass
    
    def generate_alert_report(self, alert_report: AlertReport) -> AlertReportDocument:
        """알림 리포트 생성"""
        pass
    
    def generate_comparison_report(self, evaluations: List[ConversationEvaluation]) -> ComparisonReport:
        """비교 분석 리포트 생성"""
        pass
```

### 2. 통계 분석 모듈 (`analysis/statistics_analyzer.py`)

**역할**: 여러 통화에 대한 통계 분석

**기능**:
- 상담사별 통계
- 기간별 트렌드 분석
- Label별 발생 빈도 분석
- 품질 점수 분포 분석

```python
class StatisticsAnalyzer:
    def analyze_agent_performance(self, agent_id: str, 
                                 evaluations: List[ConversationEvaluation]) -> AgentStatistics:
        """상담사별 성과 분석"""
        pass
    
    def analyze_trends(self, evaluations: List[ConversationEvaluation], 
                      period: str) -> TrendAnalysis:
        """트렌드 분석"""
        pass
```

### 3. 데이터 로더 모듈 (`data/data_loader.py`)

**역할**: STT 결과 데이터 로드 및 전처리

**기능**:
- STT 결과 파일/DB에서 로드
- 데이터 형식 변환
- 타임스탬프 파싱
- 화자 구분 정보 파싱

```python
class DataLoader:
    def load_stt_result(self, session_id: str) -> STTResult:
        """STT 결과 로드"""
        pass
    
    def load_batch(self, session_ids: List[str]) -> List[STTResult]:
        """여러 세션 일괄 로드"""
        pass
```

---

## 마이그레이션 체크리스트

### Phase 1: 데이터 구조 변경
- [ ] `ConversationContext` 데이터 구조 추가
- [ ] `BatchAnalysisResult` 데이터 구조 추가
- [ ] `ConversationSummary` 데이터 구조 추가
- [ ] `AlertReport` 데이터 구조 추가
- [ ] `ConversationEvaluation` 데이터 구조 추가

### Phase 2: 세션 관리 모듈 변경
- [ ] `SessionManager.load_full_context()` 메서드 구현
- [ ] `SessionManager.get_context_window()` 메서드 구현
- [ ] 기존 `add_sentence()` 메서드 deprecated 처리
- [ ] 대화 구조 분석 기능 추가

### Phase 3: 파이프라인 모듈 변경
- [ ] `MainPipeline.process_batch()` 메서드 구현
- [ ] 종합 분석 기능 추가
- [ ] 기존 `process()` 메서드 유지 또는 deprecated 처리

### Phase 4: 알림 시스템 변경
- [ ] `AlertSystem.collect_alert()` 메서드 구현
- [ ] `AlertSystem.generate_alert_report()` 메서드 구현
- [ ] 기존 `send_alert()` 메서드 deprecated 처리
- [ ] 리포트 생성 기능 추가

### Phase 5: 평가 프레임워크 확장
- [ ] `NormalLabelEvaluator.evaluate_conversation()` 메서드 구현
- [ ] 통계 분석 기능 추가
- [ ] 개선 영역 식별 기능 추가

### Phase 6: 새로운 모듈 추가
- [ ] `reporting/report_generator.py` 구현
- [ ] `analysis/statistics_analyzer.py` 구현
- [ ] `data/data_loader.py` 구현

### Phase 7: 테스트 및 검증
- [ ] 배치 처리 단위 테스트 작성
- [ ] 통합 테스트 작성
- [ ] 성능 테스트 (대용량 데이터 처리)
- [ ] 리포트 생성 검증

---

## 주요 고려사항

### 1. 성능 최적화
- **병렬 처리**: 여러 발화를 병렬로 처리 가능
- **메모리 관리**: 전체 대화를 메모리에 로드하므로 대용량 처리 시 주의
- **캐싱**: 동일 세션 재분석 시 캐싱 활용

### 2. 데이터 저장
- **분석 결과 저장**: DB 또는 파일 시스템에 저장
- **리포트 저장**: 생성된 리포트 영구 보관
- **통계 데이터**: 집계 데이터 별도 저장

### 3. 하위 호환성
- 기존 실시간 처리 기능은 deprecated 처리하되 유지
- 점진적 마이그레이션 지원

### 4. 확장성
- 여러 통화 일괄 처리 지원
- 상담사별/기간별 분석 지원
- 대시보드 연동 준비

---

## 결론

실시간 처리에서 배치 처리로 전환 시:

1. **파이프라인**: 전체 대화를 한 번에 처리하는 방식으로 변경
2. **세션 관리**: 실시간 업데이트 → 전체 맥락 로드
3. **알림 시스템**: 즉시 발송 → 수집 및 리포트 생성
4. **평가 프레임워크**: 단일 발화 평가 → 전체 통화 종합 평가
5. **새로운 모듈**: 리포트 생성, 통계 분석, 데이터 로더 추가

이러한 변경을 통해 통화 품질을 더 깊이 있게 분석하고, 상담사 교육에 활용할 수 있는 종합적인 리포트를 생성할 수 있습니다.

---

**참고 문서**:
- `PROJECT_STATUS.md`: 현재 프로젝트 상태
- `LABELING_SYSTEM_DESIGN.md`: 원본 설계 문서

