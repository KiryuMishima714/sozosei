import os,sys
import cv2
import time
import numpy as np

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
    return f"{int(hour)}:{int(min)}:{int(seconds)}"

def preprocess_for_allmotion(gray, avg, move_total):
    #現在のフレームと移動平均との差を計算、、avgの更新
    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    #画像を２値化する
    thresh = cv2.threshold(frameDelta, 3, 255, cv2.THRESH_BINARY)[1]
    #輪郭を抽出する(写っているすべてのもの)
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    #移動の程度を計算
    move_total = np.sum(frameDelta)
    delta_avg = move_total//(frameDelta.shape[0] + frameDelta.shape[1])
    print(delta_avg)
    return contours, delta_avg

def update_time(start_time, time_result):
    #
    end_time = time.time()
    time_result += end_time - start_time
    start_time = time.time()
    return time_result

if __name__ == '__main__':
    #VideoCaptureオブジェクト取得
    cap = cv2.VideoCapture(0)
    # 顔検出用の分類器をロード
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
    # 目検出用の分類器をロード
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml')

    print("start")

    avg = None
    start_time = None
    time_result = 0
    delta_threshold = 50 #移動度合いがこれより大きいものを検知する
    w_threshold = 30 #これよりframeが大きいものを検知する
    move_total = 0
    concentrate_flag = True

    while True:
        #フレームを取得
        ret, frame = cap.read()
        # もしフレームの取得に失敗したら
        if not ret:
            print("not capture")
            break
        
        #グレースケールに変換
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 顔の検出
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.11, minNeighbors=3, minSize=(100, 100))

        # 比較用にフレームの切り出し保存
        if avg is None:
            avg = gray.copy().astype("float")
            continue
        
        #動体の程度などを取得
        contours, delta = preprocess_for_allmotion(gray, avg, move_total)

        # 顔が1つだけ検出された場合
        if len(faces) == 1:
            # 顔の座標とサイズを取得
            x, y, w, h = faces[0, :]

            # 処理高速化のために顔の上半分を検出対象範囲とする
            eyes_gray = gray[y : y + int(h/2), x : x + w]
            # 目の検出
            eyes = eye_cascade.detectMultiScale(
                eyes_gray, scaleFactor=1.11, minNeighbors=3, minSize=(8, 8))

            # 顔の周りに矩形を描画
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            for ex, ey, ew, eh in eyes:
                # 目の周りに矩形を描画
                cv2.rectangle(frame, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (255, 255, 0), 1)

            # 差分があった点を画面に描く（すべての動体 not only face）
            for target in contours:
                x, y, w, h = cv2.boundingRect(target)

                #if 輪郭がある値より大きく、移動度がある値より大きい（not 集中）
                if w > w_threshold and delta > delta_threshold:
                    concentrate_flag = False
                    #動体の位置を描画
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 2)
                    break #集中していないことが判定できたのでfor文終了

                #if目が認識できていない（not 集中）
                if len(eyes) == 0:
                    concentrate_flag = False
                    break #集中していないことが判定できたのでfor文終了
            
            if concentrate_flag == True:
                #以下、集中できているときの処理を記述
                cv2.putText(frame,"good concentration!!", (10,100),
                                cv2.FONT_HERSHEY_PLAIN, 3, (0,0,255), 2, cv2.LINE_AA)
            
            else:
                concentrate_flag = True #初期化
            

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == 27:
            print(f"Stop Time:{convert(time_result)}")
            break  # esc to quit

    cap.release()
    cv2.destroyAllWindows()