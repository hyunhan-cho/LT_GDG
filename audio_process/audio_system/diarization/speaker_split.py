from faster_whisper import WhisperModel
from pyannote.audio.pipelines.speaker_diarization import SpeakerDiarization
from huggingface_hub import login
from dotenv import load_dotenv
import os
import json
from audio_process.models import AudioFile, SpeakerSegment
from audio_process.audio_system.utils.audio_utils import convert_to_wav

# 환경 변수 로드
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
#login(HF_TOKEN)  # ✅ 토큰을 명시적으로 로그인

# Whisper 모델 초기화
whisper_model = WhisperModel("medium", device="cpu", compute_type="float32")

# 화자 분리 파이프라인은 함수로 감싸서 요청 시점에만 로드
def get_diarization_pipeline():
    pipeline = SpeakerDiarization.from_pretrained(
        "pyannote/speaker-diarization",
        token=HF_TOKEN,
        revision="2.1"  # ✅ 반드시 revision 명시
    )
    pipeline.setup(
        task="speaker_diarization",
        hf_token=HF_TOKEN,
        revision="2.1"  # ✅ 내부 모델에도 revision 명시
    )
    return pipeline

def diarize_and_transcribe(audio_file_id, save_json=False, json_path="segments.json"):
    audio_obj = AudioFile.objects.get(id=audio_file_id)
    original_path = audio_obj.file.path

    # mp3/m4a → wav 변환
    ext = os.path.splitext(original_path)[1].lower()
    if ext in [".mp3", ".m4a"]:
        audio_path = convert_to_wav(original_path)
    else:
        audio_path = original_path

    # Whisper STT
    segments, info = whisper_model.transcribe(audio_path, language="ko")

    # 화자 분리 실행
    diarization_pipeline = get_diarization_pipeline()
    diarization = diarization_pipeline(audio_path)

    results = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        matched_texts = [
            seg.text for seg in segments
            if seg.start >= turn.start and seg.end <= turn.end
        ]
        text = " ".join(matched_texts) if matched_texts else ""

        # DB 저장
        SpeakerSegment.objects.create(
            audio=audio_obj,
            speaker=speaker,
            text=text,
            start_time=turn.start,
            end_time=turn.end
        )

        results.append({
            "speaker": speaker,
            "start": turn.start,
            "end": turn.end,
            "text": text
        })

    if save_json:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    return results