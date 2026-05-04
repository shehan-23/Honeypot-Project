FROM python:3.9-slim

WORKDIR /app

# Install paramiko and requests inside the image
RUN pip install --no-cache-dir paramiko requests

COPY . .

CMD ["python", "honeypot.py"]