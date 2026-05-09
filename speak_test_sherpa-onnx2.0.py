import sherpa_onnx
import sounddevice as sd
import numpy as np
import os

def main():
    # --- 配置區 ---
    model_dir = "./model"
    mic_sample_rate = 44100   
    model_sample_rate = 16000 
    TARGET_SENTENCES = '["向前", "向後", "跑步", "慢走"]'

    config_files = {
        "encoder": f"{model_dir}/encoder.int8.onnx",
        "decoder": f"{model_dir}/decoder.onnx",
        "joiner": f"{model_dir}/joiner.int8.onnx",
        "tokens": f"{model_dir}/tokens.txt"
    }

    # 1. 初始化模型 (四核全開)
    recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=config_files["tokens"],
        encoder=config_files["encoder"],
        decoder=config_files["decoder"],
        joiner=config_files["joiner"],
        num_threads=4,
        sample_rate=model_sample_rate,
        feature_dim=80,
        decoding_method="greedy_search",
        model_type="zipformer2"
    )
    
    # 預計算抽樣索引
    block_duration = 0.4 
    input_samples = int(mic_sample_rate * block_duration)
    target_samples = int(model_sample_rate * block_duration)
    keep_indices = np.linspace(0, input_samples - 1, target_samples).astype(np.int32)

    stream = recognizer.create_stream()

    print(f"✅ 系統啟動成功！")
    print(f"📢 監聽指令: {TARGET_SENTENCES}")
    print("-" * 30)

    def callback(indata, frames, time, status):
        if status:
            return

        # 2. 極速抽樣 (Slicing)
        raw_audio = indata.flatten()[keep_indices].astype(np.float32)
        
        # 3. 餵入並解碼
        stream.accept_waveform(model_sample_rate, raw_audio)
        while recognizer.is_ready(stream):
            recognizer.decode_stream(stream)
        
        # 4. 取得結果 (相容性修正)
        result = recognizer.get_result(stream)
        
        # --- 核心修正處：判斷 result 類型 ---
        if isinstance(result, str):
            text = result.strip()
        elif hasattr(result, 'text'):
            text = result.text.strip()
        else:
            text = str(result).strip()
        # --------------------------------

        if text:
            print(f"\r👂 聽到了: {text}\033[K", end="", flush=True)
            
            # 5. 檢查是否命中指令
            matched = False
            for target in TARGET_SENTENCES:
                if target in text:
                    print(f"\n🎯 【觸發動作】: {target}")
                    matched = True
                    break
            
            if matched:
                # 命中後立即徹底重置，準備迎接下一句
                recognizer.reset(stream)
                print("(系統已重置，等待新指令...)")

        # 6. 端點偵測重置
        if recognizer.is_endpoint(stream):
            recognizer.reset(stream)

    try:
        # blocksize 設長一點 (0.4秒)，給予樹莓派足夠時間處理
        with sd.InputStream(channels=1, 
                            dtype="float32", 
                            samplerate=mic_sample_rate, 
                            callback=callback, 
                            blocksize=input_samples):
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\n✅ 已停止")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main()