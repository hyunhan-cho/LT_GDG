from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AudioFile, SpeakerSegment
from audio_process.audio_system.diarization.speaker_split import diarize_and_transcribe
from audio_process.audio_system.utils.audio_utils import convert_to_wav

@csrf_exempt
def diarize_and_transcribe_view(request):
    if request.method == "POST":
        audio_file = request.FILES.get("file")
        if not audio_file:
            return JsonResponse({"error": "No audio file provided"}, status=400)

        try:
            # 파일 저장
            audio_instance = AudioFile.objects.create(file=audio_file)
            audio_path = audio_instance.file.path

            # 확장자 확인 후 변환
            if not audio_path.endswith(".wav"):
                audio_path = convert_to_wav(audio_path)

            # diarization + STT 수행
            segments = diarize_and_transcribe(audio_path)

            # DB 저장
            for seg in segments:
                SpeakerSegment.objects.create(
                    audio=audio_instance,
                    speaker=seg.get("speaker", "Unknown"),
                    text=seg.get("text", ""),
                    start_time=seg.get("start", 0.0),
                    end_time=seg.get("end", 0.0)
                )

            return JsonResponse({
                "audio_id": audio_instance.id,
                "segments": segments
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)