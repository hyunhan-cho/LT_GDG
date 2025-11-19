from django.db import models
from django.conf import settings

class CallRecording(models.Model):
    counselor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calls',
        verbose_name="담당 상담원"
    )

    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    audio_file = models.FileField(upload_to='call_records/%Y/%m/%d/')
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_name = self.counselor.korean_name if self.counselor else "Unknown"
        return f"Call {self.session_id} ({user_name})"

class CallSegment(models.Model):
    recording = models.ForeignKey(CallRecording, on_delete=models.CASCADE, related_name='segments')
    speaker = models.CharField(max_length=50)
    start_time = models.FloatField()
    end_time = models.FloatField()
    text = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.speaker}] {self.text[:20]}..."
    
    class Meta:
        ordering = ['start_time']