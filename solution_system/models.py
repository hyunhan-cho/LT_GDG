from django.db import models
from audio_process.models import SpeakerSegment

class ResponseManual(models.Model):
    situation_title = models.CharField(max_length=255)
    target_emotion = models.CharField(max_length=100)
    target_logic_flaw = models.CharField(max_length=100)

    script = models.TextField()
    action_guide=models.TextField()

    def __str__(self):
        return f"[{self.situation_title}] {self.target_emotion} / {self.target_logic_flaw}"
    
class SolutionResult(models.Model):
    segment = models.OneToOneField(
        SpeakerSegment, 
        on_delete=models.CASCADE, 
        related_name='solution_result'
    )
    matched_manual = models.ForeignKey(
        ResponseManual,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solution_results'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Solution for Segment ID: {self.segment.id}"