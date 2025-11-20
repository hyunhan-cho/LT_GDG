import sys
from django.conf import settings
from .logic_classify_system.pipeline.main_pipeline import MainPipeline

print("🤖 [AI System] 파이프라인 초기화 중...")
pipeline_instance = MainPipeline()

print("✅ [AI System] 파이프라인 로드 완료!")

def run_pipeline(text: str, session_id: str):
    return pipeline_instance.process(text, session_id)