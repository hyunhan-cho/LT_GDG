from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
from dotenv import load_dotenv
import json
import os

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Whisper 모델은 미리 초기화해도 괜찮음
whisper_model = WhisperModel("medium", device="cpu", compute_type="float32")

def get_diarization_pipeline():
    """
    화자 분리 파이프라인을 필요할 때만 불러오기
    """
    return Pipeline.from_pretrained(
        "pyannote/speaker-diarization",
        revision="2.1",
        token=HF_TOKEN
    )

def diarize_and_transcribe(audio_path, save_json=False, json_path="segments.json"):
    """
    화자 분리 + 텍스트 추출 + JSON 저장
    """
    # Whisper로 전체 텍스트 추출
    segments, info = whisper_model.transcribe(audio_path, language="ko")

    # 화자 분리 (여기서만 파이프라인 로드)
    diarization_pipeline = get_diarization_pipeline()
    diarization = diarization_pipeline(audio_path)

    results = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        matched_texts = [
            seg.text for seg in segments
            if seg.start >= turn.start and seg.end <= turn.end
        ]
        results.append({
            "speaker": speaker,
            "start": turn.start,
            "end": turn.end,
            "text": " ".join(matched_texts) if matched_texts else ""
        })

    if save_json:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    return results

