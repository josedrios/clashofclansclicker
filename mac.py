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
is_empty = 0
new_base_message_shown = False
resources = {"GOLD": "", "ELIXIR": "", "DARK": ""}
resource_values = {
    "GOLD": [],
    "ELIXIR": [],
    "DARK": []
}
averages = {}

print_state = {
    "GOLD": 0,
    "ELIXIR": 0,
    "DARK": 0,
    "avg_GOLD": 0.0,
    "avg_ELIXIR": 0.0,
    "avg_DARK": 0.0,
    "searching_indicator": "Idle"
}

def dynamic_printer():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"GOLD: {print_state['GOLD']}")
    print(f"ELIXIR: {print_state['ELIXIR']}")
    print(f"DARK: {print_state['DARK']}")
    print(f"AVG GOLD: {print_state['avg_GOLD']:.2f}")
    print(f"AVG ELIXIR: {print_state['avg_ELIXIR']:.2f}")
    print(f"AVG DARK: {print_state['avg_DARK']:.2f}")
    print(f"STATUS: {print_state['searching_indicator']}")

def string_extraction_and_cleanup(roi, config, currency):
    global is_empty, resources, resource_values
    text = pytesseract.image_to_string(roi, config=config)
    text = text.rstrip('\n')
    cleaned_string = ''.join(c for c in text if c.isdigit())
    if(cleaned_string == ""):
        is_empty = is_empty + 1
        resources[currency] = ""
    else:
        resources[currency] = ""
        resources[currency] = cleaned_string
        print_state[currency] = cleaned_string
        if resources[currency] != "":
            currency_integer = int(resources[currency])
            resource_values[currency].append(currency_integer)
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
        window_coords = [0, 120]
        roi = image_processing("GOLD", frame, frame_config, window_coords)
        string_extraction_and_cleanup(roi, config, "GOLD")

        # ELIXIR
        frame_config = [275, 260, 170, 40]
        window_coords = [400, 120]
        roi = image_processing("ELIXIR", frame, frame_config, window_coords)
        string_extraction_and_cleanup(roi, config, "ELIXIR")

        # DARK
        frame_config = [275, 320, 130, 40]
        window_coords = [800, 120]
        roi = image_processing("DARK", frame, frame_config, window_coords)
        string_extraction_and_cleanup(roi, config, "DARK")

        if is_empty > 4 and not new_base_message_shown:
            averages.clear()
            value_resets = list(print_state.keys())[:6]  # Get the first 6 keys
            for key in value_resets:
                print_state[key] = 0
            print_state["searching_indicator"] = "Searching"
            dynamic_printer()
            new_base_message_shown = True
            for currency in resource_values:
                resource_values[currency].clear()
        elif is_empty == 0:
            print_state["searching_indicator"] = "Idle"
            dynamic_printer()
            new_base_message_shown = False

        for resource, values in resource_values.items():
            if values:
                averages[resource] = sum(values) / len(values)
                print_state[f"avg_{resource}"] = averages[resource]
                dynamic_printer()
            else:
                averages[resource] = 0
                print_state[f"avg_{resource}"] = 0
                dynamic_printer()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()