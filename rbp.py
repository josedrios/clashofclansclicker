import socket
import RPi.GPIO as GPIO
import time

TOUCH_PIN = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN, GPIO.OUT)

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 65432

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
counter = 0

print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")
client_socket, client_address = server_socket.accept()
print(f"Connection from {client_address}")

while True:
    try:
        data = client_socket.recv(1024).decode()  # Receive data
        if data == "click":
            counter = counter + 1
            GPIO.output(TOUCH_PIN, GPIO.HIGH)
            time.sleep(0.35)
            GPIO.output(TOUCH_PIN, GPIO.LOW)
            print(f"Base No.{counter} \033[1;31mskipped\033[0m")
            client_socket.send(f"Base No.{counter} Skipped".encode())
        elif data == "base":
            counter = counter + 1
            print(f"Base No.{counter} \033[1;32mmarked\033[0m")
            print("Waiting for user approval...")
            while True:
                user_input = input("Press 'R' to continue: ").strip().lower()
                if user_input == 'r':
                    break
            client_socket.send(f"Base No.{counter} Was Reviewed/Attacked".encode())
        else:
            client_socket.send("Unknown command".encode())  # Fallback response
    except Exception as e:
        print(f"Error: {e}")
