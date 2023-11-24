import subprocess
import numpy as np
import wave
import pyaudio

julius = "/path/to/your/julius"
main = "/path/to/your/main.jconf"
am_dnn = "/path/to/your/am-dnn.jconf"
julius_dnn = "/path/to/your/julius.dnnconf"

# 録音設定
sample_rate = 16000  # サンプリングレート (Hz)
duration = 5  # 録音時間 (秒)

# マイクからの入力を録音
print("録音中...")

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=1024)

frames = []
for i in range(0, int(sample_rate / 1024 * duration)):
    data = stream.read(1024)
    frames.append(data)

print("録音終了")

# 録音データを一時的なWAVファイルに保存
input_audio_file = "input.wav"
with wave.open(input_audio_file, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))

# Juliusを実行
args = [julius, "-C", main, "-C", am_dnn, "-dnnconf", julius_dnn, "-input", "rawfile", "-cutsilence"]
p = subprocess.run(args, stdout=subprocess.PIPE, input=input_audio_file)
print(p.stdout.decode())

# 解析結果から文を抽出
output = p.stdout.decode().split("### read waveform input")[1].split("\n\n")
for i in output:
    if "sentence1:" not in i:
        continue
    sentence = i.split("sentence1:")[1].split("\n")[0].replace(" ", "")
    print(sentence)

# ストリームを閉じる
stream.stop_stream()
stream.close()
p.terminate()

