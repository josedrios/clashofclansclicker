import socket

def click():
    print("Clicked")

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
        print(f"Received data: {data}")
        if data == "click":
            click()
            client_socket.send("Next Base".encode())
        elif data == "base":
            counter += 1
            print(f"{counter}. Found attackable base")
            client_socket.send("Found Base".encode())
        else:
            client_socket.send("Unknown command".encode())  # Fallback response
    except Exception as e:
        print(f"Error: {e}")
