from django.db import models
from audio_process.models import SpeakerSegment

class ClassificationResult(models.Model):
    segment = models.OneToOneField(
        SpeakerSegment, 
        on_delete=models.CASCADE, 
        related_name='logical_analysis',
        verbose_name="분석 대상 구간"
    )
    
    label = models.CharField(max_length=50)
    label_type = models.CharField(max_length=20)
    confidence = models.FloatField()
    probabilities = models.JSONField(default=dict, blank=True) 
    
    action = models.CharField(
        max_length=50, 
        default='MONITOR', 
        verbose_name='필터링 조치'
    )
    alert_level = models.CharField(
        max_length=50, 
        default='LOW', 
        verbose_name='경고 레벨'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.label}] {self.segment.text[:20]}..."

    class Meta:
        ordering = ['-created_at']
        verbose_name = "AI 논리 분석 결과"