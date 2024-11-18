import cv2
import numpy as np

def process_image(currency, frame, frame_config):
    x, y, w, h = frame_config
    roi = frame[y:y+h, x:x+w]
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi = cv2.medianBlur(roi, 3)
    _, roi = cv2.threshold(roi, 200, 230, cv2.THRESH_BINARY)
    roi = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    kernel = np.ones((2,2), np.uint8)
    roi = cv2.dilate(roi, kernel, iterations=1)
    roi = cv2.erode(roi, kernel, iterations=1)
    roi = cv2.morphologyEx(roi, cv2.MORPH_OPEN, kernel)
    roi = cv2.medianBlur(roi, 3)
    cv2.imshow(currency, roi)
    return roi