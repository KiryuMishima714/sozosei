from asyncio.constants import LOG_THRESHOLD_FOR_CONNLOST_WRITES
import smbus
import time
import datetime
import os,sys
import cv2

# LCDの設定
LCD_ADDR = 0x27  # LCDのI2Cアドレス
LCD_WIDTH = 16  # LCDの文字数
LCD_BACKLIGHT = 0x08  # バックライトの設定

# HD44780コマンド
LCD_CLEAR_DISPLAY = 0x01
LCD_RETURN_HOME = 0x02
LCD_ENTRY_MODE = 0x06
LCD_DISPLAY_ON = 0x0C
LCD_DISPLAY_OFF = 0x08
LCD_CURSOR_ON = 0x0E
LCD_BLINK_ON = 0x0F
LCD_SET_DDRAM = 0x80

# PCF8574に接続されたLCDのピン
RS = 0x01
RW = 0x02
EN = 0x04

# LCDの初期化
def lcd_init(bus):
    # 初期化シーケンス
    lcd_send(bus, 0x33, 0)  # 4ビットモードに設定
    time.sleep(0.005)
    lcd_send(bus, 0x32, 0)  # 4ビットモードに設定
    time.sleep(0.005)

    # コマンド設定
    lcd_send(bus, 0x28, 0)  # 2行表示、5x8ドット
    time.sleep(0.00015)
    lcd_send(bus, LCD_DISPLAY_OFF, 0)  # ディスプレイオフ
    time.sleep(0.00015)
    lcd_send(bus, LCD_CLEAR_DISPLAY, 0)  # ディスプレイクリア
    time.sleep(0.002)
    lcd_send(bus, LCD_ENTRY_MODE, 0)  # エントリモード設定
    time.sleep(0.00015)
    lcd_send(bus, LCD_DISPLAY_ON, 0)  # ディスプレイオン
    time.sleep(0.00015)

# データ送信
def lcd_send(bus, data, mode):
    high = mode | (data & 0xF0) | LCD_BACKLIGHT  # 上位4ビット
    low = mode | ((data << 4) & 0xF0) | LCD_BACKLIGHT  # 下位4ビット

    # データを送信
    bus.write_byte(LCD_ADDR, high)
    lcd_toggle_enable(bus, high)
    bus.write_byte(LCD_ADDR, low)
    lcd_toggle_enable(bus, low)

# トグル処理
def lcd_toggle_enable(bus, value):
    bus.write_byte(LCD_ADDR, value | EN)  # Enable ON
    time.sleep(0.0005)
    bus.write_byte(LCD_ADDR, value & ~EN)  # Enable OFF
    time.sleep(0.0005)

# カーソル位置設定
def lcd_set_cursor(bus, col, row):
    addr = LCD_SET_DDRAM | (col + 0x40 * row)
    lcd_send(bus, addr, 0)

# 文字列出力
def lcd_print(bus, text):
    for char in text:
        lcd_send(bus, ord(char), 1)
####################################################################################################

# 秒を時間、分、秒、ミリ秒に変換する関数
def convert(sec):
    # 分に変換
    minutes = sec // 60
    # 秒に変換
    seconds = sec % 60
    # ミリ秒に変換
    milli_sec = (seconds - int(seconds)) * 1000
    # 時間、分、秒、ミリ秒の形式で返す
    hour = minutes // 60
    min = minutes % 60
    return f"{int(hour)}:{int(min)}:{int(seconds)}:{int(milli_sec)}"



# メイン処理
def main():
    bus = smbus.SMBus(1)
    lcd_init(bus)

    #VideoCaptureオブジェクト取得
    cap = cv2.VideoCapture(0)
    # 顔検出用の分類器をロード
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
    # 目検出用の分類器をロード
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml')

    print("start")

    avg = None

    start_time = time.time()
    time_result = 0

    while True:
        #フレームを取得
        ret, frame = cap.read()

        # もしフレームの取得に失敗したら
        if not ret:
            print("not capture")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 顔の検出
        faces = cascade.detectMultiScale(gray, scaleFactor=1.11, minNeighbors=3, minSize=(100, 100))

        #動体検知処理
        #グレースケールに変換
        gray_motion = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 比較用にフレームの切り出し保存
        if avg is None:
            avg = gray_motion.copy().astype("float")
            continue

        #現在のフレームと移動平均との差を計算
        cv2.accumulateWeighted(gray_motion, avg, 0.5)
        frameDelta = cv2.absdiff(gray_motion, cv2.convertScaleAbs(avg))

        #画像を２値化する
        thresh = cv2.threshold(frameDelta, 3, 255, cv2.THRESH_BINARY)[1]

        #輪郭を抽出する
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        # 顔が1つだけ検出された場合
        if len(faces) == 1:
            # 顔の座標とサイズを取得
            x, y, w, h = faces[0, :]
            # 顔の周りに矩形を描画
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # 処理高速化のために顔の上半分を検出対象範囲とする
            eyes_gray = gray[y : y + int(h/2), x : x + w]
            # 目の検出
            eyes = eye_cascade.detectMultiScale(
                eyes_gray, scaleFactor=1.11, minNeighbors=3, minSize=(8, 8))

            for ex, ey, ew, eh in eyes:
                # 目の周りに矩形を描画
                cv2.rectangle(frame, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (255, 255, 0), 1)

            # 差分があった点を画面に描く
            #for target in contours:
            #    x, y, w, h = cv2.boundingRect(target)

                #動体を検出していないand目が開いている(この間時間記録) 
                if w < 300 and len(eyes) != 0:
                    #動体の位置を描画
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 2)
                    cv2.putText(frame,"Sleepy eyes. Wake up!",
                        (10,100), cv2.FONT_HERSHEY_PLAIN, 3, (0,0,255), 2, cv2.LINE_AA)

                #以下、ストップウォッチ停止状態のプログラム
                end_time = time.time()
                time_result += end_time - start_time
                start_time = time.time()

                result_for_disp = convert(time_result)
                
                
                current_time = datetime.datetime.now()
                lcd_set_cursor(bus, 0, 0)
                lcd_print(bus, current_time.strftime("%H:%M"))
                #lcd_print(bus, time.strftime("%Y/%m/%d (%a)", time.gmtime()))
                lcd_set_cursor(bus, 0, 1)
                lcd_print(bus, result_for_disp)
                print(current_time.strftime("%H:%M"), result_for_disp)
                #time.sleep(1)
        
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == 27:
            print(f"Stop Time:{convert(time_result)}")
            break  # esc to quit
    cap.release()
    cv2.destroyAllWindows()


    # 文字列を表示
    # text_line1 = "Hello, world!"
    # text_line2 = "Raspberry Pi"

    # lcd_set_cursor(bus, 0, 0)
    # lcd_print(bus, text_line1)

    # lcd_set_cursor(bus, 0, 1)
    # lcd_print(bus, text_line2)

    # time.sleep(10)  # 10秒間表示を維持
    # lcd_send(bus, LCD_CLEAR_DISPLAY, 1)  # 表示をクリア

if __name__ == "__main__":
    main()
