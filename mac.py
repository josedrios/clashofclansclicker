import cv2
import numpy as np
import mss
import pytesseract
import socket
import os 
import time
import pygame

from constants import *
from functions import process_image

def dynamic_printer():
    os.system('cls' if os.name == 'nt' else 'clear')

    # Print Column Headers
    print(f"{'Resource':<10}{'Amount':<15}{'Average':<20}{'Standard Dev.':<20}")
    print("-" * 65)

    # Print Rows
    print(f"\033[1;33m{'Gold':<10}\033[0m{f'{resources['GOLD']:,}' if resources['GOLD'] != '' else '0':<15}{averages['GOLD']:<20}{deviations['GOLD']:<20}")
    print(f"\033[1;35m{'Elixir':<10}\033[0m{f'{resources['ELIXIR']:,}' if resources['ELIXIR'] != '' else '0':<15}{averages['ELIXIR']:<20}{deviations['ELIXIR']:<20}")
    # print(f"\033[1m{'Dark':<10}\033[0m{f'{resources['DARK']:,}' if resources['DARK'] != '' else '0':<15}{averages['DARK']:<20}{deviations['DARK']:<20}")

    # Status Section
    print("-" * 65)
    print(f"Raw Value: {raw_string:<15}")
    print(f"Final Value: {corrected_string:<15}")
    print(f"Last Client Status: {client_status:<15}")
    print(f"Last Server Response: {server_response:<15}")

def reset_values():
    global resources, resource_values, averages, deviations
    resources = {
        "GOLD": "", 
        "ELIXIR": "", 
        "DARK": ""
    }
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
    global raw_string, resources, resource_values, translation_table, corrected_string
    text = pytesseract.image_to_string(roi, config=config)
    text = text.rstrip('\n')
    raw_string = text
    text = text.translate(translation_table)
    corrected_string = text
    cleaned_string = ''.join(c for c in text if c.isdigit())

    if(cleaned_string == ""):
        resources[currency] = 0
    else:
        currency_integer = int(cleaned_string)
        resources[currency] = currency_integer
        resource_values[currency].append(currency_integer)

def send_data_to_server(client_socket, message):
    global server_response
    try:
        client_socket.send(message.encode())
        server_response = client_socket.recv(1024).decode()
    except:
        server_response = "ERROR"

def sound_alert(filename, volume):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Wait for the music to finish
        pass
with mss.mss() as sct:
    monitor = sct.monitors[1] 

    pygame.mixer.init()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    start_time = time.perf_counter()
    moved_windows = False
    # config = ('--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
    config = ('--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789OoBLlSs$()')
    while True:
        screen = sct.grab(monitor)
        frame = np.array(screen)
        # Base Frame Coordinates/Layout
        
        # GOLD
        frame_config = [275, 209, 170, 40]
        roi = process_image("GOLD", frame, frame_config)
        string_extraction_and_cleanup(roi, config, "GOLD")

        # ELIXIR
        frame_config = [275, 267, 170, 40]
        roi = process_image("ELIXIR", frame, frame_config)
        string_extraction_and_cleanup(roi, config, "ELIXIR")

        if moved_windows == False:
            cv2.moveWindow("GOLD", 0, 160)
            cv2.moveWindow("ELIXIR", 400, 160)
            moved_windows = True

        # DARK
        # frame_config = [275, 325, 130, 40]
        # window_coords = [800, 160]
        # roi = process_image("DARK", frame, frame_config, window_coords)
        # string_extraction_and_cleanup(roi, config, "DARK")

        current_time = time.perf_counter()
        elapsed_time = current_time - start_time

        if elapsed_time > 5:
            #ADD A TOP CAP
            if 1200000 < averages["GOLD"] < 5000000 and 1200000 < averages["ELIXIR"] < 5000000:
                sound_alert("alert.mp3", 0.4)
                client_status = "Stop" + f" ({elapsed_time:.2f}s)"
                send_data_to_server(client_socket, "base")
            else:
                # sound_alert("skip.mp3", 0.2)
                client_status = "Next" + f" ({elapsed_time:.2f}s)"
                send_data_to_server(client_socket, "click")
                time.sleep(2)
            start_time = time.perf_counter()
            reset_values()

        for resource, values in resource_values.items():
            if values:
                averages[resource] = sum(values) / len(values)
                deviations[resource] = np.std(values)

        dynamic_printer()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
client_socket.close()
