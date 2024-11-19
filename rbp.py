from gpiozero import AngularServo
import socket
from time import sleep

servo = AngularServo(4, min_pulse_width=0.0006, max_pulse_width=0.0023)
servo.angle = -60

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
            servo.angle = -90
            sleep(0.18)
            servo.angle = -60
            sleep(0.2)
            print(f"Base No.{counter} \033[1;31mskipped\033[0m")
            # If having issue here, remove last sleep and add it here for 0.35
            client_socket.send(f"Base No.{counter} Skipped".encode())
        elif data == "base":
            counter = counter + 1
            print(f"Base No.{counter} \033[1;32mmarked\033[0m")
            print("Waiting for user approval...")
            while True:
                user_input = input("Enter Good (g) or Bad (b): ").strip().lower()
                if user_input == 'g':
                    break
                if user_input == 'b':
                    servo.angle = -90
                    sleep(0.18)
                    servo.angle = -60
                    sleep(0.2)
                    break
            client_socket.send(f"Base No.{counter} Was Reviewed/Attacked".encode())
        else:
            client_socket.send("Unknown command".encode())  # Fallback response
    except Exception as e:
        print(f"Error: {e}")
        servo.angle = 0
        exit()
