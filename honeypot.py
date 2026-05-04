import socket
import paramiko
import threading
import json
import requests
import datetime

# --- CONFIGURATION ---
HOST = "0.0.0.0"
PORT = 2222
LOGS_FILE = "logs.json"

# This is the "brain" of your fake terminal
FAKE_RESPONSES = {
    "ls": "bin  boot  dev  etc  home  lib  opt  root  sys  tmp  usr  var",
    "pwd": "/root",
    "uname -a": "Linux ubuntu 5.4.0-42-generic #46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020 x86_64",
    "cat /etc/passwd": "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin",
    "ls -la": "total 20\ndrwxr-xr-x 2 root root 4096 May  2 10:00 .\n-rw------- 1 root root  512 May  2 10:05 .bash_history",
    "whoami": "root"
}


def save_log(data):
    data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOGS_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")


def get_geo_info(ip_address):
    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip_address}", timeout=5)
        data = response.json()
        return {"country": data.get("country", "Unknown"), "city": data.get("city", "Unknown")}
    except:
        return {"country": "Unknown", "city": "Unknown"}

# --- SSH SERVER INTERFACE ---


class HoneypotInterface(paramiko.ServerInterface):
    def __init__(self, client_ip, geo):
        self.client_ip = client_ip
        self.geo = geo
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        # Capture Login
        print(f"[+] Capture: {username}:{password} from {self.client_ip}")
        save_log({
            "event": "LOGIN",
            "ip": self.client_ip,
            "country": self.geo['country'],
            "city": self.geo['city'],
            "username": username,
            "password": password
        })
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return "password"

# --- CLIENT HANDLING ---


def handle_client(client_socket, addr):
    ip = addr[0]
    geo = get_geo_info(ip)

    try:
        transport = paramiko.Transport(client_socket)
        # Add a generated RSA key for the handshake
        host_key = paramiko.RSAKey.generate(2048)
        transport.add_server_key(host_key)

        server = HoneypotInterface(ip, geo)
        transport.start_server(server=server)

        channel = transport.accept(20)  # Wait for session
        if channel is None:
            return

        channel.send("\r\nWelcome to Ubuntu 20.04 LTS\r\n\r\n")

        while True:
            channel.send("root@server:~# ")
            # Receive command
            buf = b""
            while not buf.endswith(b"\r"):
                char = channel.recv(1)
                if not char:
                    break
                channel.send(char)  # Echo back characters to user
                buf += char

            command = buf.decode().strip()
            if not command:
                channel.send("\r\n")
                continue

            if command == "exit":
                channel.send("\r\nlogout\r\n")
                break

            # Handle the response
            response = FAKE_RESPONSES.get(
                command, f"bash: {command}: command not found")
            channel.send(f"\r\n{response}\r\n")

            # Log command
            save_log({
                "event": "COMMAND",
                "ip": ip,
                "command": command
            })

    except Exception as e:
        print(f"Error with {ip}: {e}")
    finally:
        client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(100)
    print(f"[*] Advanced SSH Honeypot active on {HOST}:{PORT}")

    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(
            client, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
