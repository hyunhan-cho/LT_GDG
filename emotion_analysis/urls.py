from django.urls import path
from .views import analyze_emotion_view

urlpatterns = [
    path("analyze/", analyze_emotion_view, name="analyze_emotion"),
]
