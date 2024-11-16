import cv2
import sys
import numpy as np
import mss
import pytesseract

# Global Values
is_empty = 0
new_base_message_shown = False
resources = {"GOLD": "", "ELIXIR": "", "DARK": ""}

def string_extraction_and_cleanup(roi, config, currency):
    global is_empty, resources
    text = pytesseract.image_to_string(roi, config=config)
    text = text.rstrip('\n')
    cleaned_string = ''.join(c for c in text if c.isdigit())
    if(cleaned_string == ""):
        is_empty = is_empty + 1
        resources[currency] = ""
    else:
        resources[currency] = ""
        resources[currency] = cleaned_string
        print(f"GOLD: {resources['GOLD']} | ELIXIR: {resources['ELIXIR']} | DARK: {resources['DARK']}"+" "*10, end='\r')
        is_empty = 0

def image_processing(currency, frame, frame_config, window_coords):
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

# Initialize mss for screen capture
with mss.mss() as sct:
    monitor = sct.monitors[1]  # Adjust for the desired monitor

    while True:
        screen = sct.grab(monitor)
        frame = np.array(screen)
        config = ('--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
        # Base Frame Coordinates/Layout
        
        # GOLD
        frame_config = [275, 200, 170, 40]
        window_coords = [0, 120]
        roi = image_processing("GOLD", frame, frame_config, window_coords)
        string_extraction_and_cleanup(roi, config, "GOLD")

        # ELIXIR
        frame_config = [275, 260, 170, 40]
        window_coords = [200, 120]
        roi = image_processing("ELIXIR", frame, frame_config, window_coords)
        string_extraction_and_cleanup(roi, config, "ELIXIR")

        # DARK
        frame_config = [275, 320, 130, 40]
        window_coords = [400, 120]
        roi = image_processing("DARK", frame, frame_config, window_coords)
        string_extraction_and_cleanup(roi, config, "DARK")

        if is_empty > 4 and not new_base_message_shown:
            print("NEW BASE DETECTED"+" "*40, end='\r')
            new_base_message_shown = True
        elif is_empty == 0:
            new_base_message_shown = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
