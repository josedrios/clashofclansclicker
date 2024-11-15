# Libraries
import cv2
import pytesseract
# import easyocr

# Start Stream from webcam
stream = cv2.VideoCapture(0)

# Check if stream is opened
if not stream.isOpened():
    print("NO STREAM")
    exit()

# Main loop
while True:
    # Ret is a flag (success or failure) and frame is the image
    ret, frame = stream.read()
    # If Ret is false, break
    if not ret:
        print("NO MORE STREAM")
        break

    # cv2.imshow("Webcam", frame)

    # Conver our frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
    # Display the grayscaled image
    cv2.imshow("Grayerson", gray)

    # Extract text from image with Tesseract
    text_tesseract = pytesseract.image_to_string(gray)
    # Extract text from image with EasyOCR
    # reader = easyocr.Reader(['en'])
    # text_easyocr, _ = reader.readtext(gray)

    # print(f"EASYOCR: {text_easyocr if text_easyocr.strip() else 'N/A'}")
    print(f"TESSERACT: {text_tesseract if text_tesseract.strip() else 'N/A'}")


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stream.release()
cv2.destroyAllWindows()