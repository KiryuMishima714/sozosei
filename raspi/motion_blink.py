import os,sys
import cv2
import time

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
            print(convert(time_result))

        #画像表示
        cv2.imshow("Frame", frame)

        

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == 27:
        print(f"Stop Time:{convert(time_result)}")
        break  # esc to quit

cap.release()
cv2.destroyAllWindows()