from ninja import Router, File, UploadedFile
from .models import CallRecording
from audio_system.diarization.speaker_split import diarize_and_transcribe
import uuid

router = Router()

@router.post("/upload-call")
def upload_call_recording(request, file: UploadedFile = File(...)):
    session_id = str(uuid.uuid4())
    
    recording = CallRecording.objects.create(
        session_id=session_id,
        audio_file=file
    )
    
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