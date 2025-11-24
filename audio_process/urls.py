from django.urls import path
from .views import upload_page, detail_page

app_name = 'audio'

urlpatterns = [
    path('upload/', upload_page, name='audio_upload'),
    path('detail/<str:session_id>/', detail_page, name='detail'),
]