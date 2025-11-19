from django.contrib import admin
from .models import AnalysisSession, ClassificationResult

@admin.register(AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    """
    분석 세션 정보 관리
    """
    list_display = ('session_id', 'created_at')
    search_fields = ('session_id',)

@admin.register(ClassificationResult)
class ClassificationResultAdmin(admin.ModelAdmin):
    """
    문장별 분석 결과 관리
    """
    # Admin 목록에 표시될 필드
    list_display = (
        'session_link', 
        'label', 
        'label_type', 
        'confidence', 
        'short_text', 
        'created_at'
    )
    # 필터링 옵션
    list_filter = ('label_type', 'label')
    # 검색 가능 필드 (text 내용, 연결된 session_id)
    search_fields = ('text', 'session__session_id') 
    
    # 긴 텍스트 내용을 잘라서 미리 보여주는 헬퍼 함수
    def short_text(self, obj):
        return obj.text[:40] + "..." if len(obj.text) > 40 else obj.text
    short_text.short_description = 'Text Preview'
    
    # 세션 ID를 클릭 가능한 링크로 표시 (Inlines 설정이 없어서 이렇게 단순 링크 처리)
    def session_link(self, obj):
        from django.utils.html import format_html
        return format_html('<a href="/admin/logical_analysis/analysissession/{}/change/">{}</a>',
                           obj.session.pk,
                           obj.session.session_id)
    session_link.short_description = 'Session ID'