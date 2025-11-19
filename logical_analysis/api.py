# logical_analysis/api.py

from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import datetime
from django.db.models import Count
from .schemas import AnalysisSessionOut, ClassificationResultOut
from .models import AnalysisSession, ClassificationResult
from .inference import run_pipeline  # 👈 수정된 함수 import

router = Router()

# 1. 요청 스키마 변경 (리스트 -> 통 문자열)
class AnalyzeRequest(Schema):
    session_id: str
    text: str 

@router.post("/run-inference")
def run_inference_and_save(request, payload: AnalyzeRequest):
    """
    MainPipeline을 실행하고 결과를 DB에 저장
    """
    # 1. MainPipeline 실행
    pipeline_result = run_pipeline(payload.text, payload.session_id)
    
    # 2. DB 저장 (dataclass -> ORM 변환)
    saved_count = 0
    with transaction.atomic():
        session, _ = AnalysisSession.objects.get_or_create(
            session_id=payload.session_id
        )
        
        # MainPipeline의 결과(pipeline_result.results)를 반복
        results_to_create = []
        for res in pipeline_result.results:
            results_to_create.append(ClassificationResult(
                session=session,
                text=res.text,
                label=res.label,
                label_type=res.label_type,
                confidence=res.confidence,
                probabilities=res.probabilities or {},
                timestamp=res.timestamp or datetime.now(),
                action='MONITOR',       
                alert_level='LOW',
            ))
        
        ClassificationResult.objects.bulk_create(results_to_create)
        saved_count = len(results_to_create)

    return {
        "status": "success",
        "processed_text_length": len(payload.text),
        "saved_sentences": saved_count
    }

@router.get("/{session_id}", response=AnalysisSessionOut)
def get_analysis_result(request, session_id: str):
    """
    Session ID로 분석 결과 및 요약 통계 조회
    """
    session = get_object_or_404(AnalysisSession, session_id=session_id)
    results = session.results.all().order_by('created_at')

    # --- 요약 통계 계산 로직 ---
    total_count = results.count()
    
    # 1. 위험도 계산 (HIGH, CRITICAL 개수)
    risk_count = results.filter(alert_level__in=['HIGH', 'CRITICAL']).count()
    
    # 2. 최고 위험 레벨 찾기
    levels = [r.alert_level for r in results]
    if 'CRITICAL' in levels:
        highest = 'CRITICAL'
    elif 'HIGH' in levels:
        highest = 'HIGH'
    elif 'MEDIUM' in levels:
        highest = 'MEDIUM'
    else:
        highest = 'LOW'

    # 3. 가장 많이 등장한 라벨(주된 의도) 찾기
    most_common_label = "None"
    if total_count > 0:
        top_label = results.values('label').annotate(count=Count('label')).order_by('-count').first()
        if top_label:
            most_common_label = top_label['label']

    # 요약 객체 생성
    summary_data = {
        "total_sentences": total_count,
        "risk_score": risk_count,
        "highest_alert": highest,
        "primary_intent": most_common_label
    }

    return {
        "session_id": session.session_id,
        "created_at": session.created_at,
        "summary": summary_data,
        "results": list(results)
    }