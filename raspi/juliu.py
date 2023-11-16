from pyjulius import Julius

def on_recognition(text):
    print(f"Recognized: {text}")

def main():
    # Juliusクライアントの作成
    julius_client = Julius(host="localhost", port=10500, callback=on_recognition)

    try:
        # Juliusに接続
        julius_client.connect()

        # メインループ
        while True:
            pass

    except KeyboardInterrupt:
        print("KeyboardInterrupt: Disconnecting from Julius.")
        julius_client.disconnect()

if __name__ == "__main__":
    main()

