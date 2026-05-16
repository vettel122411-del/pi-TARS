import sherpa_onnx
import sounddevice as sd
import numpy as np
import os
import queue
import threading

def main():
    model_dir = "./model"
    mic_rate = 44100
    model_rate = 16000
    TARGETS = ["停下", "向左", "向右", "向前"]
    
    # 建立一個執行緒安全的隊列，用來存放音訊
    audio_queue = queue.Queue()

    # 1. 初始化模型 (強制 4 核心)
    recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=f"{model_dir}/tokens.txt",
        encoder=f"{model_dir}/encoder.int8.onnx",
        decoder=f"{model_dir}/decoder.onnx",
        joiner=f"{model_dir}/joiner.int8.onnx",
        num_threads=4, 
        sample_rate=model_rate,
        feature_dim=80,
        decoding_method="greedy_search",
        model_type="zipformer2"
    )
    
    # 預計算重採樣索引
    duration = 0.3  # 縮短緩衝，降低延遲
    in_samples = int(mic_rate * duration)
    indices = np.round(np.linspace(0, in_samples - 1, int(model_rate * duration))).astype(np.int32)

    def recognition_worker():
        """專門負責 AI 辨識的線程，不會干擾音訊錄製"""
        stream = recognizer.create_stream()
        print("🔥 [AI 線程] 已啟動，四核全速運轉中...")
        
        while True:
            # 從隊列拿取音訊資料
            pcm_data = audio_queue.get()
            if pcm_data is None: break
            
            # 餵入模型
            stream.accept_waveform(model_rate, pcm_data)
            
            # 全速解碼
            while recognizer.is_ready(stream):
                recognizer.decode_stream(stream)
            
            # 取得結果
            res = recognizer.get_result(stream)
            text = (res.text if hasattr(res, 'text') else str(res)).replace(" ", "").strip()
            
            if text:
                print(f"\r👂 聽到了: {text[-20:]}\033[K", end="", flush=True)
                
                # 指令匹配
                for t in TARGETS:
                    if t in text:
                        print(f"\n🎯 命中指令: {t}")
                        recognizer.reset(stream)
                        break
            
            if recognizer.is_endpoint(stream):
                recognizer.reset(stream)
            
            audio_queue.task_done()

    # 啟動辨識線程
    worker_thread = threading.Thread(target=recognition_worker, daemon=True)
    worker_thread.start()

    def audio_callback(indata, frames, time, status):
        """音訊線程：只負責抓資料並丟進隊列，不做任何 AI 運算"""
        if status:
            return
        # 極速抽樣後直接丟進 Queue
        pcm = indata.flatten()[indices].astype(np.float32)
        audio_queue.put(pcm)

    try:
        with sd.InputStream(channels=1, samplerate=mic_rate, 
                            blocksize=in_samples, callback=audio_callback):
            print(f"🎤 錄音中 (指令: {TARGETS})...")
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\n✅ 已停止")
        audio_queue.put(None) # 停止線程

if __name__ == "__main__":
    main()