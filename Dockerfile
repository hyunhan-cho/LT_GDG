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

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt && \
    pip install --no-cache-dir --user gunicorn

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
