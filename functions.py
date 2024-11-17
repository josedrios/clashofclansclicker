import cv2
import numpy as np

def process_image(currency, frame, frame_config, window_coords):
    x, y, w, h = frame_config
    roi = frame[y:y+h, x:x+w]
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi = cv2.medianBlur(roi, 3)
    _, roi = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    roi = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    kernel = np.ones((2,2), np.uint8)
    roi = cv2.dilate(roi, kernel, iterations=1)
    roi = cv2.erode(roi, kernel, iterations=1)
    roi = cv2.morphologyEx(roi, cv2.MORPH_OPEN, kernel)
    cv2.imshow(currency, roi)
    cv2.moveWindow(currency, window_coords[0], window_coords[1])
    return roi