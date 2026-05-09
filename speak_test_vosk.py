import os
import sys
import queue
import json
import pyaudio
import soxr
import numpy as np
from vosk import Model, KaldiRecognizer

# 初始化隊列存放音訊數據
q = queue.Queue()

def callback(indata, frames, time, status):
    """這是一個回調函數，負責將錄製到的音訊放入隊列"""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# 1. 加載模型 (確保 'model' 資料夾與此腳本在同一目錄)
if not os.path.exists("model"):
    print("請先下載並解壓模型至 'model' 資料夾")
    exit(1)

model = Model("model")
# 16000 是大多數模型建議的採樣率
rec = KaldiRecognizer(model, 16000, 
    '["你 好", "你 有 聽 到 嗎", "現 在 幾 點", "沒 有 問 題"]'
)

# 2. 配置音訊輸入 (PyAudio)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=4000)

print("--- 系統已就緒，請開始說話 (Ctrl+C 結束) ---")

# 3. 循環識別
try:
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if len(data) == 0:
            break
        
        data = np.frombuffer(data, dtype=np.int16)
        data = soxr.resample(data, 44100, 16000).astype(np.int16).tobytes()

        # 進行識別
        if rec.AcceptWaveform(data):
            # 這是最終識別結果
            result = json.loads(rec.Result())
            print(f"最終結果: {result['text']}")
        else:
            # 這是過程中的臨時結果 (中間預測)
            partial = json.loads(rec.PartialResult())
            if partial['partial']:
                print(f"正在識別... {partial['partial']}", end='\r')

except KeyboardInterrupt:
    print("\n停止識別")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()