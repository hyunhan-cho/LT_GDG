import os
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

def upload_path(instance, filename):
    now = timezone.now()
    ext = filename.split('.')[-1]
    return f"raw_calls/{now.strftime('%Y/%m/%d')}/{instance.session_id}.{ext}"

class CallRecording(models.Model):
    session_id = models.CharField(
        max_length=255, 
        unique=True, 
        default=uuid.uuid4, 
        editable=False,
        db_index=True
    )

    audio_file = models.FileField(
        upload_to=upload_path, 
        verbose_name="녹음 파일"
    )

    file_name = models.CharField(max_length=255, blank=True)
    
    processed = models.BooleanField(default=False)
    duration = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='recordings'
    )

    def __str__(self):
        return f"[{self.created_at.date()}] {self.session_id}"

    class Meta:
        db_table = 'call_recordings'
        ordering = ['-created_at']


class SpeakerSegment(models.Model):
    recording = models.ForeignKey(CallRecording, on_delete=models.CASCADE, related_name='segments')
    speaker_label = models.CharField(max_length=50)
    start_time = models.FloatField()
    end_time = models.FloatField()
    text = models.TextField()
    
    class Meta:
        db_table = 'speaker_segments'
        ordering = ['start_time']