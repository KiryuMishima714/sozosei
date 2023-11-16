import julius

def main():
    # Juliusのクライアントを作成
    client = julius.Client(host="localhost", port=10500, timeout=1.0)

    try:
        # Juliusに接続
        client.connect()

        print("Waiting for speech recognition results...")

        # 認識結果が得られるまでループ
        while True:
            result = client.results()
            if result:
                # 認識結果を表示
                print("Recognized:", result["text"])

    except KeyboardInterrupt:
        # プログラムが中断されたらクライアントを切断
        client.disconnect()

if __name__ == "__main__":
    main()
