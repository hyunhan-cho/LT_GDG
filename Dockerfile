# ========================================
# Stage 1: 빌드 스테이지 (dependencies 설치)
# ========================================
FROM python:3.12-slim as builder

WORKDIR /app

# 빌드에 필요한 패키지만 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt를 두 개로 분리하여 복사
COPY requirements.txt .

# pip 업그레이드
RUN pip install --no-cache-dir --upgrade pip

# PyTorch CPU 버전 먼저 설치
RUN pip install --no-cache-dir --user \
    torch==2.1.0 \
    torchaudio==2.1.0 \
    --index-url https://download.pytorch.org/whl/cpu

# 나머지 패키지 설치 (PyTorch 제외)
RUN pip install --no-cache-dir --user \
    Django==5.1.2 \
    django-ninja==1.5.0 \
    gunicorn==21.2.0 \
    django-environ==0.11.2 \
    django-storages==1.14.2 \
    boto3==1.34.34 \
    faster-whisper==1.0.0 \
    transformers==4.36.0 \
    librosa==0.10.1 \
    soundfile==0.12.1 \
    pydub==0.25.1 \
    audioread==3.0.1 \
    numpy==1.26.4 \
    requests==2.32.3 \
    PyYAML==6.0.2 \
    python-dateutil==2.9.0

# ========================================
# Stage 2: 런타임 스테이지 (최종 이미지)
# ========================================
FROM python:3.12-slim

WORKDIR /app

# 런타임에 필요한 라이브러리만 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 빌드 스테이지에서 설치한 Python 패키지 복사
COPY --from=builder /root/.local /root/.local

# PATH에 추가
ENV PATH=/root/.local/bin:$PATH

# 애플리케이션 코드 복사
COPY . .

# 정적 파일 수집
RUN python manage.py collectstatic --noinput || true

# Django 마이그레이션
RUN python manage.py migrate --noinput || true

# 포트 노출
EXPOSE 8080

# 애플리케이션 실행
CMD ["gunicorn", "linguaproject.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
