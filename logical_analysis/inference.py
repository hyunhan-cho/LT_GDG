# logical_analysis/inference.py

import sys
from django.conf import settings
from .logic_classify_system.pipeline.main_pipeline import MainPipeline

print("🤖 [AI System] 파이프라인 초기화 중...")

# 2. 전역 인스턴스 생성 (Singleton)
# 서버 실행 시 모델(BERT 등)이 메모리에 로드됩니다.
pipeline_instance = MainPipeline()

print("✅ [AI System] 파이프라인 로드 완료!")

def run_pipeline(text: str, session_id: str):
    """
    api.py에서 호출할 래퍼 함수
    """
    return pipeline_instance.process(text, session_id)