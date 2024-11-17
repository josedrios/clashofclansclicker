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
    print(f"{'Gold':<10}{f'{resources['GOLD']:,}' if resources['GOLD'] != '' else '0':<15}{averages['GOLD']:<20,.2f}{deviations['GOLD']:<20,.2f}")
    print(f"{'Elixir':<10}{f'{resources['ELIXIR']:,}' if resources['ELIXIR'] != '' else '0':<15}{averages['ELIXIR']:<20,.2f}{deviations['ELIXIR']:<20,.2f}")
    print(f"{'Dark':<10}{f'{resources['DARK']:,}' if resources['DARK'] != '' else '0':<15}{averages['DARK']:<20,.2f}{deviations['DARK']:<20,.2f}")

    # Status Section
    print("-" * 65)
    print(f"Time Passed: {elapsed_time:.2f} seconds")
    print(f"Last Client Status: {client_status:<15}")
    print(f"Last Server Response: {server_response:<15}")

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

def sound_alert(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Wait for the music to finish
        pass
with mss.mss() as sct:
    monitor = sct.monitors[1] 

    pygame.mixer.init()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    start_time = time.perf_counter()
    while True:
        screen = sct.grab(monitor)
        frame = np.array(screen)
        config = ('--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
        # Base Frame Coordinates/Layout
        
        # GOLD
        frame_config = [275, 200, 170, 40]
        window_coords = [0, 170]
        roi = process_image("GOLD", frame, frame_config, window_coords)
        string_extraction_and_cleanup(roi, config, "GOLD")

        # ELIXIR
        frame_config = [275, 260, 170, 40]
        window_coords = [400, 170]
        roi = process_image("ELIXIR", frame, frame_config, window_coords)
        string_extraction_and_cleanup(roi, config, "ELIXIR")

        # DARK
        frame_config = [275, 320, 130, 40]
        window_coords = [800, 170]
        roi = process_image("DARK", frame, frame_config, window_coords)
        string_extraction_and_cleanup(roi, config, "DARK")

        current_time = time.perf_counter()
        elapsed_time = current_time - start_time

        if elapsed_time > 5:
            if averages["GOLD"] > 700000 and averages["ELIXIR"] > 700000:
                reset_values()
                sound_alert("alert.mp3")
                client_status = "Stop" + f" ({elapsed_time:.2f}s)"
                send_data_to_server(client_socket, "base")
            elif averages["GOLD"] <= 700000 or averages["ELIXIR"] <= 700000:
                reset_values()
                sound_alert("skip.mp3")
                client_status = "Next" + f" ({elapsed_time:.2f}s)"
                send_data_to_server(client_socket, "click")
            start_time = time.perf_counter()

        for resource, values in resource_values.items():
            if values:
                averages[resource] = sum(values) / len(values)
                deviations[resource] = np.std(values)

        dynamic_printer()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
client_socket.close()
