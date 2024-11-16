import cv2
import numpy as np
import mss
import pytesseract
import socket
import os 
import time

# Global Values
SERVER_HOST = "10.0.0.24"
SERVER_PORT = 65432
empty_tracker = 0
base_searching = False

# Currency Values for Terminal Printing
resources = {"GOLD": "", "ELIXIR": "", "DARK": ""}
# Currency Values for Averaging
resource_values = {
    "GOLD": [],
    "ELIXIR": [],
    "DARK": []
}
# Averaged Currency Values
averages = {
    "GOLD": 0.0,
    "ELIXIR": 0.0,
    "DARK": 0.0,
}
deviations = {
    "GOLD": 0.0,
    "ELIXIR": 0.0,
    "DARK": 0.0
}
searching_state = "SEARCHING..."

def dynamic_printer():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Gold: {resources['GOLD']}")
    print(f"Elixir: {resources['ELIXIR']}")
    print(f"Dark: {resources['DARK']}")
    print(f"Average Gold: {averages['GOLD']:.2f}")
    print(f"Gold Average Deviation: {deviations['GOLD']:.2f}")
    print(f"Average Elixir: {averages['ELIXIR']:.2f}")
    print(f"Elixir Average Deviation: {deviations['ELIXIR']:.2f}")
    print(f"Average Dark: {averages['DARK']:.2f}")
    print(f"Dark Average Deviation: {deviations['DARK']:.2f}")
    print(f"STATUS: {"Searching..." if base_searching else "Idle"}")

def reset_values():
    global resources, resource_values, averages, deviations
    resources = {"GOLD": "", "ELIXIR": "", "DARK": ""}
    resource_values = {
        "GOLD": [],
        "ELIXIR": [],
        "DARK": []
    }
    averages = {
        "GOLD": 0.0,
        "ELIXIR": 0.0,
        "DARK": 0.0,
    }
    deviations = {
        "GOLD": 0.0,
        "ELIXIR": 0.0,
        "DARK": 0.0
    }

def string_extraction_and_cleanup(roi, config, currency):
    global empty_tracker, resources, resource_values
    text = pytesseract.image_to_string(roi, config=config)
    text = text.rstrip('\n')
    cleaned_string = ''.join(c for c in text if c.isdigit())

    if(cleaned_string == ""):
        empty_tracker = empty_tracker + 1
        resources[currency] = 0
    else:
        currency_integer = int(cleaned_string)
        resources[currency] = currency_integer
        resource_values[currency].append(currency_integer)
        empty_tracker = 0

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

with mss.mss() as sct:
    monitor = sct.monitors[1] 

    # Socket stuff
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client_socket.connect((SERVER_HOST, SERVER_PORT))
    # client_socket.send("sop".encode())
    # response = client_socket.recv(1024).decode()
    # print(f"Response from server: {response}")
    # client_socket.close()

    while True:
        screen = sct.grab(monitor)
        frame = np.array(screen)
        config = ('--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
        # Base Frame Coordinates/Layout
        
        # GOLD
        frame_config = [275, 200, 170, 40]
        window_coords = [0, 170]
        roi = image_processing("GOLD", frame, frame_config, window_coords)
        string_extraction_and_cleanup(roi, config, "GOLD")

        # ELIXIR
        frame_config = [275, 260, 170, 40]
        window_coords = [400, 170]
        roi = image_processing("ELIXIR", frame, frame_config, window_coords)
        string_extraction_and_cleanup(roi, config, "ELIXIR")

        # DARK
        frame_config = [275, 320, 130, 40]
        window_coords = [800, 170]
        roi = image_processing("DARK", frame, frame_config, window_coords)
        string_extraction_and_cleanup(roi, config, "DARK")

        if empty_tracker > 4 and not base_searching:
            reset_values()
            base_searching = True
            for currency in resource_values:
                resource_values[currency].clear()
        elif empty_tracker == 0:
            base_searching = False

        dynamic_printer()

        for resource, values in resource_values.items():
            if values:
                averages[resource] = sum(values) / len(values)
                deviations[resource] = np.std(values)
            else:
                averages[resource] = 0.0
                deviations[resource] = 0.0

        dynamic_printer()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()