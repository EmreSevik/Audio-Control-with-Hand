import cv2
import numpy as np
import time
import HandTrackingModule as htm
import math
import subprocess


cap = cv2.VideoCapture(0)
cap.set(3, 660)
cap.set(4, 500)


pTime = 0


detector = htm.HandDetector(detectionCon=0.7)

minVol = 0
maxVol = 100
vol = 50
volPer = 100


def set_volume(volume):
    volume = max(0, min(100, int(volume)))
    mac_volume = np.interp(volume, [0, 100], [0, 100])

    try:
        subprocess.Popen(["osascript", "-e", f"set volume output volume {mac_volume}"])
        print(f"Sound : {mac_volume}% (MacOS Sound Changed)")
    except Exception as e:
        print(f"Error: {e}")


while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame = detector.findHands(frame)
    lmList, _ = detector.findPosition(frame, draw=False)

    if len(lmList) > 8:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2


        cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(frame, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)


        length = math.hypot(x2 - x1, y2 - y1)


        vol = np.interp(length, [50, 600], [minVol, maxVol])
        volPer = np.interp(length, [50, 600], [0, 100])

        set_volume(volPer)
        print(f"Distance: {int(length)}, Volume: {int(volPer)}%")

        if length < 50:
            cv2.circle(frame, (cx, cy), 15, (0, 255, 255), cv2.FILLED)


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime


    bar_x, bar_y = 50, 150
    bar_width, bar_height = 35, 250
    step = bar_height // 10

    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 0, 0), 3)
    filled_height = int(np.interp(volPer, [0, 100], [0, bar_height]))

    for i in range(10):
        bar_segment_y = bar_y + bar_height - (i + 1) * step
        color = (0, 255, 0) if filled_height > (i * step) else (255, 0, 0)
        cv2.rectangle(frame, (bar_x, bar_segment_y), (bar_x + bar_width, bar_segment_y + step), color, cv2.FILLED)


    cv2.putText(frame, f'{int(volPer)}%', (bar_x - 10, bar_y + bar_height + 30), cv2.FONT_HERSHEY_COMPLEX, 1,
                (255, 0, 0), 3)
    cv2.putText(frame, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
