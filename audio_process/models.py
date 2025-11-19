from django.db import models

class AudioFile(models.Model):
    file = models.FileField(upload_to="audio/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AudioFile {self.id} - {self.file.name}"


class SpeakerSegment(models.Model):
    audio = models.ForeignKey(AudioFile, on_delete=models.CASCADE, related_name="segments")
    speaker = models.CharField(max_length=50)
    text = models.TextField()
    start_time = models.FloatField()
    end_time = models.FloatField()

    def __str__(self):
        return f"{self.speaker}: {self.text[:30]}..."