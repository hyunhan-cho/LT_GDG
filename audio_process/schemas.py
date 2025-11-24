from ninja import Router, File, UploadedFile, Schema
from django.shortcuts import get_object_or_404
from .models import CallRecording, SpeakerSegment
from ninja_jwt.authentication import JWTAuth
from datetime import date, datetime

class RecordingListSchema(Schema):
    session_id: str
    file_name: str
    created_at: datetime
    duration: float
    processed: bool

class SpeakerSegmentSchema(Schema):
    id: int
    speaker_label: str
    start_time: float
    end_time: float
    text: str | None = None

    emotion_label: str | None = None
    emotion_confidence: float | None = None

class SegmentUpdateSchema(Schema):
    id: int
    text: str | None = None
    is_counselor: bool

class RecordingDetailSchema(Schema):
    session_id: str
    file_name: str
    created_at: datetime
    segments: list[SpeakerSegmentSchema]

class SpeakerUpdateSchema(Schema):
    segments: list[SegmentUpdateSchema]



