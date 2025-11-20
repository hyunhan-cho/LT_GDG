import sounddevice as sd
import numpy as np
import queue
import soundfile as sf
import uuid
from audio_process.models import AudioFile
from audio_process.audio_system.diarization.speaker_split import diarize_and_transcribe

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

def start_streaming():
    stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=16000)
    stream.start()
    print("🎧 실시간 오디오 입력 시작됨")
    return stream, audio_queue

def process_streaming_to_json(output_path="stream.wav"):
    frames = []
    while not audio_queue.empty():
        frames.append(audio_queue.get())

    if not frames:
        return {"status": "error", "message": "오디오 입력 없음"}

    # Queue → WAV 파일 저장
    data = np.concatenate(frames, axis=0)
    sf.write(output_path, data, 16000)

    # DB 저장
    audio = AudioFile.objects.create(file=output_path)

    # 분석 실행
    results = diarize_and_transcribe(audio.id)
    return {
        "status": "success",
        "audio_id": audio.id,
        "segments": results
    }
