# logical_analysis/admin.py
from django.contrib import admin
from django.db.models import Count, Q
from .models import AnalysisSession, ClassificationResult

class ClassificationResultInline(admin.TabularInline):
    model = ClassificationResult
    extra = 0
    readonly_fields = ('created_at', 'timestamp')
    can_delete = False
    fields = ('text', 'label', 'label_type', 'confidence', 'action', 'alert_level', 'created_at')
    ordering = ('created_at',)

@admin.register(AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'sentence_count', 'risk_summary', 'created_at')
    search_fields = ('session_id',)
    inlines = [ClassificationResultInline]

    def sentence_count(self, obj):
        """해당 세션의 총 문장 수 계산"""
        return obj.results.count()
    sentence_count.short_description = "문장 수"

    def risk_summary(self, obj):
        """고위험(HIGH/CRITICAL) 알림 개수 표시"""
        high_risks = obj.results.filter(alert_level__in=['HIGH', 'CRITICAL']).count()
        if high_risks > 0:
            return f"위험상황 {high_risks}건"
        return "정상"
    risk_summary.short_description = "위험도 요약"

@admin.register(ClassificationResult)
class ClassificationResultAdmin(admin.ModelAdmin):
    list_display = ('session_id_display', 'label', 'action', 'alert_level', 'short_text', 'created_at')
    list_filter = ('alert_level', 'action', 'label_type')
    search_fields = ('text', 'session__session_id')

    def session_id_display(self, obj):
        return obj.session.session_id
    session_id_display.short_description = "Session ID"

    def short_text(self, obj):
        return obj.text[:40] + "..." if len(obj.text) > 40 else obj.text