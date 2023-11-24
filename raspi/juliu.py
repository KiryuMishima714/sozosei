import subprocess

# Juliusコマンドの実行
command = ['julius', '-C', 'main.jconf', '-C', 'am-gmm.jconf', '-demo']

# subprocessモジュールを使用してコマンドを実行
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# 出力を表示
stdout, stderr = process.communicate()

print("Standard Output:")
print(stdout)

if stderr:
    print("Error Output:")
    print(stderr)

