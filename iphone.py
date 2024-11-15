import cv2
import pytesseract

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("STREAM STARTUP FAILED")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame.")
        break

    cv2.imshow("CLASH OF CLANS LOOT DETECTOR (iPhone)", frame)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
    cv2.imshow("CLASH OF CLANS LOOT DETECTOR (iPhone/GRAY)", gray)

    # text_normal = pytesseract.image_to_string(gray)
    # print(f"NORMAL: {text_normal if text_normal.strip() else 'N/A'}")

    text_gray = pytesseract.image_to_string(gray)
    print(f"GRAY: {text_gray if text_gray.strip() else 'N/A'}")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()