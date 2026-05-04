import socket

HOST = "127.0.0.1"
PORT = 2222

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print(client.recv(1024).decode())  # banner

client.send(b"admin\n")
print(client.recv(1024).decode())

client.send(b"1234\n")

# Receive welcome + prompt
print(client.recv(1024).decode())

# Send commands
client.send(b"ls\n")
print(client.recv(1024).decode())

client.send(b"pwd\n")
print(client.recv(1024).decode())

client.send(b"exit\n")

client.close()
