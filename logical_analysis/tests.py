from django.test import TestCase

# Create your tests here.
import requests
import json

# 로컬 서버 주소 (스크린샷에 나온 경로와 일치해야 함)
url = "http://127.0.0.1:8000/api/analysis/save-results"

# 테스트용 더미 데이터
data = {
    "session_id": "TEST_SESSION_001",
    "results": [
        {
            "label": "ADVERTISEMENT",
            "label_type": "SPECIAL",
            "confidence": 0.99,
            "text": "테스트 데이터입니다.",
            "probabilities": {"ADVERTISEMENT": 0.99, "NORMAL": 0.01}
        }
    ]
}

try:
    res = requests.post(url, json=data)
    print(f"상태 코드: {res.status_code}")
    print(f"응답 본문: {res.json()}")
except Exception as e:
    print("에러 발생:", e)