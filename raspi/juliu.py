import subprocess

def run_julius(julius_path, jconf_path):
    julius_command = f"{julius_path} -C {jconf_path}"
    julius_process = subprocess.Popen(julius_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        while True:
            output = julius_process.stdout.readline().strip()

            # 認識結果が出力されたら表示
            if "sentence1:" in output:
                recognized_words = output.split("sentence1:")[1].strip()
                print("Recognized words:", recognized_words)

    except KeyboardInterrupt:
        # プログラムが中断されたらプロセスを終了
        julius_process.terminate()

if __name__ == "__main__":
    # Juliusの実行ファイルと設定ファイルのパスを指定
    julius_path = "/path/to/julius"
    jconf_path = "/path/to/your/julius.jconf"

    # Juliusの実行
    run_julius(julius_path, jconf_path)
