from ninja import Router, File, UploadedFile
from .models import CallRecording
from emotion_analysis.emotion_system.diarization.speaker_split import diarize_and_transcribe
import uuid

router = Router()

@router.post("/upload-call")
def upload_call_recording(request, file: UploadedFile = File(...)):
    """
    통화 녹음 파일 업로드 및 STT 분석 요청
    """
    # 1. 고유 세션 ID 생성
    session_id = str(uuid.uuid4())
    
    # 2. DB에 파일 저장
    recording = CallRecording.objects.create(
        session_id=session_id,
        audio_file=file
    )
    
    # 3. 분석 실행 (동기 실행 - 파일이 크면 오래 걸림)
    try:
        count = diarize_and_transcribe(recording.id)
        return {
            "status": "success",
            "session_id": session_id,
            "message": "분석 완료",
            "segments_count": count
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }