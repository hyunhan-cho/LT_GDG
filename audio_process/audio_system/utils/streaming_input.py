import sounddevice as sd
import numpy as np
import queue

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

def start_streaming():
    stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=16000)
    stream.start()
    print("🎧 실시간 오디오 입력 시작됨")
    return stream, audio_queue
