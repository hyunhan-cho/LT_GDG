from django.db import models

class CallRecording(models.Model):
    """
    통화 녹음 파일 원본 및 메타데이터
    """
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    audio_file = models.FileField(upload_to='call_records/%Y/%m/%d/') # 파일 저장 경로
    processed = models.BooleanField(default=False) # 분석 완료 여부
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Call {self.session_id}"

class CallSegment(models.Model):
    recording = models.ForeignKey(CallRecording, on_delete=models.CASCADE, related_name='segments')
    speaker = models.CharField(max_length=50) # 예: SPEAKER_00, SPEAKER_01
    start_time = models.FloatField() # 시작 시간 (초)
    end_time = models.FloatField()   # 종료 시간 (초)
    text = models.TextField()        # 변환된 텍스트
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.speaker}] {self.text[:20]}..."
    
    class Meta:
        ordering = ['-start_time'] # 시간순 정렬