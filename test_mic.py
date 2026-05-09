import pyaudio
p = pyaudio.PyAudio()
info = p.get_default_input_device_info()
print(f"目前預設設備: {info['name']}")
print(f"預設建議採樣率: {info['defaultSampleRate']}")
p.terminate()