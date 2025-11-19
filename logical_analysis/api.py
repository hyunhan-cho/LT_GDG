# logical_analysis/api.py

from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import datetime

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
                timestamp=res.timestamp or datetime.now()
            ))
        
        ClassificationResult.objects.bulk_create(results_to_create)
        saved_count = len(results_to_create)

    return {
        "status": "success",
        "processed_text_length": len(payload.text),
        "saved_sentences": saved_count
    }