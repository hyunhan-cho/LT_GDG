from django.db import models

class EmotionResult(models.Model):
    source = models.CharField(max_length=20, choices=[("text", "Text"), ("audio", "Audio")])
    input_text = models.TextField()
    emotion_label = models.CharField(max_length=50)
    confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.source}] {self.emotion_label} - {self.input_text[:30]}..."
