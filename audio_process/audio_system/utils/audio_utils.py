import os
import tempfile
from pydub import AudioSegment
from django.core.files.storage import default_storage
from django.conf import settings

def download_and_convert_to_wav(file_field_or_path) -> str:
    """
    S3(또는 스토리지)에 있는 파일을 로컬 임시 경로로 다운로드하고,
    wav 형식으로 변환하여 로컬 경로를 반환합니다.

    Args:
        file_field_or_path: Django 모델의 FileField 객체 또는 파일 경로 문자열

    Returns:
        local_wav_path: 변환된 로컬 wav 파일의 절대 경로
    """

    file_path = file_field_or_path.name if hasattr(file_field_or_path, 'name') else file_field_or_path
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in [".m4a", ".mp3", ".wav"]:
        raise ValueError(f"지원되지 않는 형식입니다: {ext}")

    temp_source = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    
    try:
        print(f"[S3 Download] 다운로드 시작: {file_path}")
        
        with default_storage.open(file_path, 'rb') as s3_file:
            for chunk in s3_file.chunks():
                temp_source.write(chunk)
        
        temp_source.close()

        if ext == ".wav":
            return temp_source.name

        print(f"[Converting] wav 변환 중...")
        
        wav_temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav_path = wav_temp.name
        wav_temp.close()

        audio = AudioSegment.from_file(temp_source.name, format=ext[1:])
        audio.export(wav_path, format="wav")
        
        print(f"[Complete] 변환 완료: {wav_path}")
        
        os.unlink(temp_source.name)
        
        return wav_path

    except Exception as e:
        if os.path.exists(temp_source.name):
            os.unlink(temp_source.name)
        raise e

def cleanup_temp_file(file_path: str):
    if file_path and os.path.exists(file_path):
        try:
            os.unlink(file_path)
            print(f"🗑️ [Cleanup] 임시 파일 삭제됨: {file_path}")
        except Exception as e:
            print(f"⚠️ 임시 파일 삭제 실패: {e}")