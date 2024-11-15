import cv2
import numpy as np
import mss

x, y, w, h = 275, 200, 230, 160

# Initialize mss for screen capture
with mss.mss() as sct:
    monitor = sct.monitors[1]  # Adjust for the desired monitor (1 is usually primary)

    while True:
        screen = sct.grab(monitor)
        frame = np.array(screen)
        
        roi = frame[y:y+h, x:x+w]

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)  

        # Display the captured frame
        cv2.imshow("Screen Capture", gray)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
