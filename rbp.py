import socket

def click():
    print("Clicked")

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 65432

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")
    try:
        data = client_socket.recv(1024).decode()  # Receive data
        print(f"Received data: {data}")

        if data == "click":
            click()
            client_socket.send("Moving to next base".encode())
        elif data == "base":
            print("Found attackable base")
            client_socket.send("Found attackable base".encode())
        else:
            client_socket.send("Unknown command".encode())  # Fallback response
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
