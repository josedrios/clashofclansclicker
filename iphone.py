import cv2
import numpy as np
import mss
import pytesseract

# Initialize mss for screen capture
with mss.mss() as sct:
    monitor = sct.monitors[1]  # Adjust for the desired monitor (1 is usually primary)

    while True:
        screen = sct.grab(monitor)
        frame = np.array(screen)
        config = ('-l eng --oem 1 --psm 6')
        
        # GOLD
        x, y, w, h = 275, 200, 160, 40
        roi = frame[y:y+h, x:x+w] 
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        cv2.imshow("GOLD", roi)

        text = pytesseract.image_to_string(roi, config=config)
        text = text.rstrip('\n')

        print(F"GOLD: {text}")

        # ELIXIR
        y_elixir = y + h + 15
        roi = frame[y_elixir:y_elixir+h, x:x+w]
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        cv2.imshow("ELIXIR", roi)

        text = pytesseract.image_to_string(roi, config=config)
        text = text.rstrip('\n')

        print(F"ELIXIR: {text}")

        # DARK
        y_dark = y_elixir + h + 20
        w_dark = w - 40
        roi = frame[y_dark:y_dark+h, x:x+w_dark]
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        cv2.imshow("DARK", roi)

        text = pytesseract.image_to_string(roi, config=config)
        text = text.rstrip('\n')

        print(F"DARK: {text}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
