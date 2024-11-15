# Importing necessary libraries
import cv2 # For image processing
from time import time # For timing
import socket # For networking
from goprocam import GoProCamera, constants # For GoPro camera control
import pytesseract # For OCR

# WRITE is false so that the images are not saved
WRITE = False
# Initializing the GoPro camera
gpCam = GoProCamera.GoPro()
# Creating a UDP socket to send commands to the GoPro
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Tracking the time
t=time()

# Starting the GoPro livestream
gpCam.livestream("start")
# Configuring the GoPro camera video settings
gpCam.video_settings(res='1440p', fps='30')
# Setting window size
gpCam.gpControlSet(constants.Stream.WINDOW_SIZE, constants.Stream.WindowSize.R720)
# Opening the GoPro livestream through OpenCV with UDP
cap = cv2.VideoCapture("udp://10.5.5.9:8554", cv2.CAP_FFMPEG)

counter = 0

while True:
    # Captures a frame from the GoPro
        # nmat is a flag (success or failure)
        # frame is the image
    nmat, frame = cap.read()
    # cv2 is used to display the image
    #cv2.imshow("GoPro OpenCV", frame)

    # Conver our frame to grayscale (Better for OCR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    cv2.imshow("Grayscale Frame", gray)
    # Extract text from image with OCR
    text = pytesseract.image_to_string(gray)
    # Print read text to terminal
    print(f"Detected Text: {text if text.strip() else 'N/A'}")
    if WRITE == True:
        # Saving the image
        cv2.imwrite(str(counter)+".jpg", frame)
        # for testing purposes (mental representation)
        print(f"Image {counter} saved")
        counter += 1

        if counter >= 10:
            break
    # When 'q' is pressed, exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # Sending commands to the GoPro to keep it streaming
    if time() - t >= 2.5:
        sock.sendto("_GPHD_:0:0:2:0.000000\n".encode(), ("10.5.5.9", 8554))
        # reset timer
        t=time()
# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()