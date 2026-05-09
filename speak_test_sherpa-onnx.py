import sherpa_onnx
import sounddevice as sd
import numpy as np
import sys
import os
from scipy.signal import resample

def main():
    model_dir = "./model"
    mic_sample_rate = 44100
    model_sample_rate = 16000
    
    encoder = f"{model_dir}/encoder.int8.onnx"
    decoder = f"{model_dir}/decoder.onnx"
    joiner = f"{model_dir}/joiner.int8.onnx"
    tokens = f"{model_dir}/tokens.txt"

    if not all(os.path.exists(f) for f in [encoder, decoder, joiner, tokens]):
        print("❌ 錯誤：找不到模型檔案")
        return

    try:
        recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=tokens,
            encoder=encoder,
            decoder=decoder,
            joiner=joiner,
            num_threads=4,
            sample_rate=model_sample_rate,
            feature_dim=80,
            decoding_method="greedy_search",
            model_type="zipformer2"
        )
        stream = recognizer.create_stream()
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        return

    print("\n🎤 系統啟動 (44100 -> 16000 Resampling)...")
    last_text = ""

    def callback(indata, frames, time, status):
        nonlocal last_text
        if status: pass
        
        # 重採樣
        raw_audio = indata.flatten()
        new_num_samples = int(len(raw_audio) * model_sample_rate / mic_sample_rate)
        resampled_audio = resample(raw_audio, new_num_samples).astype(np.float32)
        
        stream.accept_waveform(model_sample_rate, resampled_audio)
        
        while recognizer.is_ready(stream):
            recognizer.decode_stream(stream)
        
        # --- 修正後的結果讀取 ---
        result = recognizer.get_result(stream)
        text = result.strip() if isinstance(result, str) else result.text.strip()
        
        if text and text != last_text:
            print(f"\r辨識中: {text}\033[K", end="", flush=True)
            last_text = text
            
            if recognizer.is_endpoint(stream):
                print(f"\r[句]: {text}\033[K")
                recognizer.reset(stream)
                last_text = ""

    try:
        with sd.InputStream(channels=1, dtype="float32", samplerate=mic_sample_rate, 
                            callback=callback, blocksize=int(0.1 * mic_sample_rate)):
            while True: sd.sleep(100)
    except KeyboardInterrupt:
        print("\n✅ 已停止")

if __name__ == "__main__":
    main()