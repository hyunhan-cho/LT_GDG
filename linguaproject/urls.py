from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI
from accounts.api import router as accounts_router
from logical_analysis.api import router as analysis_router

api = NinjaAPI()
api.add_router("/account", accounts_router)
api.add_router("/analysis", analysis_router)


urlpatterns = [
    path('admin/', admin.site.urls),
    path("audio/", include("audio_process.urls")),
    path("emotion/", include("emotion_analysis.urls")),
]