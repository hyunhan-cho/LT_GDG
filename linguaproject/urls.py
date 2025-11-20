from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI

from accounts.api import router as accounts_router
from logical_analysis.api import router as analysis_router
from audio_process.api import router as audio_router

api = NinjaAPI()
api.add_router("/account", accounts_router)
api.add_router("/analysis", analysis_router)
api.add_router("/audio", audio_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("emotion/", include("emotion_analysis.urls")),
    path("api/", api.urls),
]