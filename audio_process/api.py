# core_data/api.py
from ninja import Router, File, UploadedFile
from django.shortcuts import get_object_or_404
from .models import CallRecording, SpeakerSegment
from .audio_system.diarization.speaker_split import diarize_and_transcribe  # AI 분석 함수
from .audio_system.utils.audio_utils import download_and_convert_to_wav, cleanup_temp_file # 유틸 함수

router = Router()

@router.post("/upload")
def upload_and_process(request, file: UploadedFile = File(...)):
    """
    [Standard S3 Workflow]
    1. 파일 업로드 (S3 자동 저장)
    2. S3에서 다운로드 및 변환
    3. AI 분석
    4. 결과 저장
    """

    recording = CallRecording.objects.create(
        audio_file=file,
        file_name=file.name
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