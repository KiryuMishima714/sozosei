import subprocess
import sys
import os
import pyaudio
import wave

# Juliusの実行ファイルへのパスを指定してください
JULIUS_PATH = "/path/to/julius"

# サンプリングレートやサンプルサイズ、Juliusの設定ファイルのパスなどを設定します
RATE = 16000
CHUNK = 1024
FORMAT = pyaudio.paInt16

# 録音した音声を一時的に保存するファイル名
AUDIO_FILENAME = "recorded_audio.wav"

def record_audio(filename, duration=5):
    """
    マイクから音声を録音し、指定したファイルに保存する関数。

    :param filename: 保存する音声ファイルの名前
    :param duration: 録音する時間（秒）
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    print("Recording...")

    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # 録音した音声をWAVファイルとして保存
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def run_julius(audio_filename):
    """
    Juliusを起動し、録音した音声ファイルを認識して結果を表示する関数。

    :param audio_filename: 録音した音声ファイルの名前
    """
    # Juliusのコマンドライン引数を設定
    command = [JULIUS_PATH, '-C', '/path/to/julius-kit/dictation-kit-v4.4/main.jconf', '-module']

    # Juliusプロセスを起動し、標準入力から音声データを渡す
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 録音した音声ファイルを読み込む
    with open(audio_filename, 'rb') as audio_file:
        audio_data = audio_file.read()

    # Juliusに音声データを渡して認識結果を取得
    stdout, stderr = process.communicate(input=audio_data)

    # 認識結果を表示
    print("Recognition result:")
    print(stdout)

    # エラーメッセージがあれば表示
    if stderr:
        print("Error:", stderr)

if __name__ == "__main__":
    # 録音した音声を保存するファイル
    audio_filename = AUDIO_FILENAME

    # 音声の録音とJuliusの実行
    record_audio(audio_filename)
    run_julius(audio_filename)

    # Clean up: 一時的に作成した音声ファイルを削除
    os.remove(audio_filename)
