from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from emotion_analysis.models import EmotionResult
from .emotion_system.emotion.text_emotion import classify_text_emotion
from .emotion_system.features.extract_features import extract_features
from .emotion_system.emotion.audio_emotion import classify_audio_emotion
import torch

@csrf_exempt
def analyze_emotion_view(request):
    if request.method == "POST":
        source = request.POST.get("source", "text")
        input_data = request.POST.get("input")

        if not input_data:
            return JsonResponse({"error": "No input provided"}, status=400)

        if source == "text":
            label = classify_text_emotion(input_data)
            confidence = None  # KoBERT는 confidence 반환 안 함

        elif source == "audio":
            features = extract_features(input_data)
            features_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
            result = classify_audio_emotion(features_tensor)
            label = result["label"]
            confidence = result["confidence"]

        else:
            return JsonResponse({"error": "Invalid source"}, status=400)

        # DB 저장
        emotion = EmotionResult.objects.create(
            source=source,
            input_text=input_data,
            emotion_label=label,
            confidence=confidence
        )

        return JsonResponse({
            "id": emotion.id,
            "label": label,
            "confidence": confidence
        })
