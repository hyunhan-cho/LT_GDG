# core_data/api.py
from typing import List
from ninja import Router, File, UploadedFile, Schema
from django.shortcuts import get_object_or_404
from .models import CallRecording, SpeakerSegment
from ninja_jwt.authentication import JWTAuth
from .audio_system.diarization.speaker_split import diarize_and_transcribe  # AI 분석 함수
from .audio_system.utils.audio_utils import download_and_convert_to_wav, cleanup_temp_file # 유틸 함수
from datetime import date, datetime

router = Router()

class RecordingListSchema(Schema):
    session_id: str
    file_name: str
    created_at: datetime
    duration: float
    processed: bool


@router.post("/upload", auth=JWTAuth())
def upload_and_process(request, file: UploadedFile = File(...)):

    recording = CallRecording.objects.create(
        audio_file=file,
        file_name=file.name,
        uploader=request.user
    )
    
    local_wav_path = None
    try:
        local_wav_path = download_and_convert_to_wav(recording.audio_file)
        
        print(f"분석 시작: {local_wav_path}")
        segments_data = diarize_and_transcribe(local_wav_path)
        
        objs = [
            SpeakerSegment(
                recording=recording,
                speaker_label=item['speaker'],
                start_time=item['start'],
                end_time=item['end'],
                text=item['text']
            ) for item in segments_data
        ]
        SpeakerSegment.objects.bulk_create(objs)
        
        recording.processed = True
        recording.duration = segments_data[-1]['end'] if segments_data else 0.0
        recording.save()
        
        return {
            "status": "success",
            "session_id": recording.session_id,
            "segments_count": len(objs),
            "s3_url": recording.audio_file.url
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        cleanup_temp_file(local_wav_path)

@router.get("/list", response=List[RecordingListSchema], auth=JWTAuth())
def get_recording_list(request, target_date: str = None):
    if target_date:
        try:
            search_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            search_date = date.today()
    else:
        search_date = date.today()


    recordings = CallRecording.objects.filter(
        uploader=request.user,
        created_at__date=search_date
    ).order_by('-created_at')

    return recordings