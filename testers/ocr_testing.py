import mss
import cv2
import numpy as np

def tester(currency, frame, frame_config):
    x, y, w, h = frame_config
    roi = frame[y:y+h, x:x+w]
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi = cv2.medianBlur(roi, 3)
    _, roi = cv2.threshold(roi, 200, 300, cv2.THRESH_BINARY)
    roi = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    kernel = np.ones((1,1), np.uint8)
    roi = cv2.dilate(roi, kernel, iterations=1)
    roi = cv2.erode(roi, kernel, iterations=1)
    roi = cv2.morphologyEx(roi, cv2.MORPH_CLOSE, kernel)
    roi = cv2.medianBlur(roi, 3)
    cv2.imshow(currency, roi)
    return roi

config = ('--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
moved = False

with mss.mss() as sct:
    monitor = sct.monitors[1] 
    frame_config = [275, 207, 170, 40]
    window_coords = [0, 170]
    
    while True:
        screen = sct.grab(monitor)
        frame = np.array(screen)
        roi = tester("GOLD", frame, frame_config, window_coords)
        if moved == False:
            cv2.moveWindow("GOLD", window_coords[0], window_coords[1])
            moved = True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break