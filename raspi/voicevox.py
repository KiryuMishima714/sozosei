import pyopenjtalk
from pydub import AudioSegment
import numpy as np

def text_to_speech(text, pitch=0.0, speed=1.0, out_file="output.wav"):
    # テキストを音声に変換
    wav, sr = pyopenjtalk.tts(text)

    # 速度とピッチを調整
    wav_speed_pitch_adjusted = wav.speedup(playback_speed=speed).set_frame_rate(int(sr * (1 + pitch)))

    # NumPy配列に変換
    audio_array = np.array(wav_speed_pitch_adjusted.get_array_of_samples())

    # WAVファイルとして保存
    pydub.AudioSegment(audio_array.tobytes(), frame_rate=sr, sample_width=audio_array.dtype.itemsize, channels=1).export(out_file, format="wav")

if __name__ == "__main__":
    # テキストを指定して呼び出し
    text_to_speech("こんにちは、Voicevoxを使ってテキストを音声に変換してみました。", pitch=0.5, speed=1.5, out_file="output.wav")
