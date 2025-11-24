
'''# core_data/api.py
from ninja import Router, File, UploadedFile
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



'''

# core_data/api.py
from ninja import Router, File, UploadedFile
from django.shortcuts import get_object_or_404
from .models import CallRecording, SpeakerSegment
from .audio_system.diarization.speaker_split import transcribe_with_timestamps  # ✅ STT 전용 함수
from .audio_system.utils.audio_utils import download_and_convert_to_wav, cleanup_temp_file
from ninja_jwt.authentication import JWTAuth
from datetime import date, datetime
from typing import List
from .schemas import *

router = Router()

@router.post("/upload", auth=JWTAuth())
def upload_and_process(request, file: UploadedFile = File(...)):

    print ("요청자: ", request.user)
    recording = CallRecording.objects.create(
        audio_file=file,
        file_name=file.name,
        uploader=request.user
    )
    
    local_wav_path = None
    try:
        # 2. S3에서 다운로드 후 wav 변환
        local_wav_path = download_and_convert_to_wav(recording.audio_file)
        
        print(f"분석 시작: {local_wav_path}")
        
        # 3. Whisper STT 실행
        segments_data = transcribe_with_timestamps(local_wav_path)
        
        # 4. SpeakerSegment DB 저장 (speaker_label은 unknown으로 고정)
        objs = [
            SpeakerSegment(
                recording=recording,
                speaker_label="unknown",
                start_time=item['start'],
                end_time=item['end'],
                text=item['text']
            ) for item in segments_data
        ]
        SpeakerSegment.objects.bulk_create(objs)
        
        # 5. CallRecording 업데이트
        recording.processed = True
        recording.duration = segments_data[-1]['end'] if segments_data else 0.0
        recording.save()
        
        # 6. 응답 반환 (segments_data 포함)
        return {
            "status": "success",
            "session_id": recording.session_id,
            "segments_count": len(objs),
            "s3_url": recording.audio_file.url,
            "segments": segments_data 
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
        # created_at__date=search_date
    ).order_by('-created_at')

    return recordings

@router.get('/{session_id}', response=RecordingDetailSchema, auth=JWTAuth())
def get_recording_detail(request, session_id: str):
    recording = get_object_or_404(CallRecording, session_id=session_id, uploader=request.user)
    segments = recording.segments.all().order_by('start_time')
    
    return {
        "session_id": recording.session_id,
        "file_name": recording.file_name,
        "created_at": recording.created_at,
        "segments": [
            SpeakerSegmentSchema(
                id=seg.id,
                recordid=recording.session_id,
                speaker_label=seg.speaker_label,
                start_time=seg.start_time,
                end_time=seg.end_time,
                text=seg.text
            ) for seg in segments
        ]
    }

@router.post('/{session_id}/confirm', auth=JWTAuth())
def update_speaker_labels(request, session_id: str, payload: SpeakerUpdateSchema):
    recording = get_object_or_404(CallRecording, session_id=session_id, uploader=request.user)
    current_segments ={
        seg.id: seg
        for seg in SpeakerSegment.objects.filter(recording=recording)
    }
    update_list=[]

    for item in payload.segments:
        seg = current_segments.get(item.id)
        if not seg:
            continue
        new_label = 'counselor' if item.is_customer else 'client'

        if seg.text != item.text or seg.speaker_label != new_label:
            seg.text = item.text
            seg.speaker_label = new_label
            update_list.append(seg)

    if update_list:
        SpeakerSegment.objects.bulk_update(update_list, ['speaker_label', 'text'])

    return {"status": "success", "updated_segments": len(update_list)}