from django.db import models

class AnalysisSession(models.Model):
    """한 번의 AI 요청(세션)을 저장하는 테이블"""
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.session_id}"

class ClassificationResult(models.Model):
    """세션에 포함된 개별 문장 분석 결과"""
    session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='results')
    
    text = models.TextField()  # 원본 문장
    label = models.CharField(max_length=50)  # 분류 결과
    label_type = models.CharField(max_length=20) # NORMAL / SPECIAL
    confidence = models.FloatField() # 신뢰도
    
    # 핵심: 확률 정보를 JSON으로 통째로 저장 (PostgreSQL 권장, SQLite/MySQL도 가능)
    probabilities = models.JSONField(default=dict, blank=True) 
    timestamp = models.DateTimeField(null=True, blank=True) # AI 모델이 생성한 시간
    
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
        return f"[{self.label}] {self.text[:20]}..."
    
    class Meta:
        ordering = ['-created_at']