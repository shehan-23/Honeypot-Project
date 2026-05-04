🛡️ Containerized SSH Honeypot (Forensic Logger)
📋 Overview
This project is a high-fidelity SSH Honeypot designed to capture and log unauthorized access attempts. Unlike simple socket listeners, this backend uses the Paramiko library to handle real RSA key exchanges and encrypted handshakes, making it indistinguishable from a real Ubuntu server to automated scripts and scanners.

🛠️ Key Features
Protocol Realism: Implements a full SSH handshake using Paramiko to trick real SSH clients and hacking tools.

Environment Isolation: Built with Docker to ensure the host machine remains secure while interacting with potentially malicious traffic.

Geographic Intelligence: Integrates with the IP-API to identify the country and city of the connection source.

Forensic Logging: Captures credentials (usernames/passwords) and all executed commands, persisting them to a logs.json file on the host machine via Docker Volumes.

🏗️ Technical Stack
Language: Python 3.9

Libraries: Paramiko (SSH), Requests (Geo-IP), JSON, Threading

Infrastructure: Docker

🚀 Getting Started

1. Prerequisites
   Docker installed on your system.

Python 3.x (for local testing).

2. Installation & Deployment
   Clone the repository:

Bash
git clone https://github.com/yourusername/ssh-honeypot.git
cd ssh-honeypot
Build the Docker Image:

Bash
docker build -t ssh-honeypot .
Run the Honeypot:

Bash
docker run -d -p 2222:2222 --name my-honeypot -v ${PWD}/logs.json:/app/logs.json ssh-honeypot 3. Testing the "Trap"
Connect to the honeypot using any standard SSH client:

PowerShell
ssh root@127.0.0.1 -p 2222
Note: Type 'yes' to trust the RSA key and enter any password to access the fake shell.

📊 Log Analysis
Interaction data is stored in logs.json. Example entry:

JSON
{"event": "LOGIN", "ip": "127.0.0.1", "country": "Unknown", "username": "admin", "password": "password123", "timestamp": "2026-05-04 13:05:00"}
