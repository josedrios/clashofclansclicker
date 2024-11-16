import cv2
import numpy as np
import mss
import pytesseract

# Global Values
is_empty = 0
resources = {"GOLD": "", "ELIXIR": "", "DARK": ""}

def string_extraction_and_cleanup(roi, config, currency):
    global is_empty, resources
    text = pytesseract.image_to_string(roi, config=config)
    text = text.rstrip('\n')
    cleaned_string = ''.join(c for c in text if c.isdigit())
    if(cleaned_string == ""):
        is_empty = is_empty + 1
        resources[currency] = "0"
    else:
        resources[currency] = cleaned_string
        print(f"GOLD: {resources['GOLD']} | ELIXIR: {resources['ELIXIR']} | DARK: {resources['DARK']}", end='\r')
        is_empty = 0

# Initialize mss for screen capture
with mss.mss() as sct:
    monitor = sct.monitors[1]  # Adjust for the desired monitor

    while True:
        screen = sct.grab(monitor)
        frame = np.array(screen)
        config = ('-l eng --oem 1 --psm 6')
        x, y, w, h = 275, 200, 170, 40
        
        # GOLD
        roi = frame[y:y+h, x:x+w] 
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        cv2.imshow("GOLD", roi)
        cv2.moveWindow("GOLD", 0, 120)

        string_extraction_and_cleanup(roi, config, "GOLD")

        # ELIXIR
        y_elixir = y + h + 20
        roi = frame[y_elixir:y_elixir+h, x:x+w]
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        cv2.imshow("ELIXIR", roi)
        cv2.moveWindow("ELIXIR", 200, 120)

        string_extraction_and_cleanup(roi, config, "ELIXIR")

        # DARK
        y_dark = y_elixir + h + 20
        w_dark = w - 40
        roi = frame[y_dark:y_dark+h, x:x+w_dark]
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        cv2.imshow("DARK", roi)
        cv2.moveWindow("DARK", 400, 120)

        string_extraction_and_cleanup(roi, config, "DARK")

        if is_empty > 3:
            sys.stdout.flush()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
