# 프로젝트 폴더/urls.py
from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI
from logical_analysis.api import router as analysis_router # 작성한 router import

api = NinjaAPI()
api.add_router("/analysis", analysis_router) # /api/analysis/... 로 연결됨


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),
    path("audio/", include("audio_process.urls")),
    path("emotion/", include("emotion_analysis.urls")),
]