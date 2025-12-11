import socket
import time
import random
import sys

SERVICES = ["auth-service", "payment-gateway", "user-db", "analytics-engine", "frontend-api"]
LEVELS = ["INFO", "INFO", "INFO", "WARN", "ERROR", "DEBUG"]
MESSAGES = [
    "User login successful",
    "Processing payment for transaction #{}",
    "Database connection latency high",
    "Failed to authenticate user",
    "Cache miss for key: user_{}",
    "API request received: GET /v1/users/{}",
    "Service starting up...",
    "Health check failed",
    "Transaction {} completed"
]

def generate_log():
    service = random.choice(SERVICES)
    level = random.choice(LEVELS)
    req_id = random.randint(1000, 9999)
    msg_template = random.choice(MESSAGES)
    
    if "{}" in msg_template:
        msg = msg_template.format(req_id)
    else:
        msg = msg_template
        
    return f"{level} [{service}] {msg}"

def send_udp(message, port=9000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), ("127.0.0.1", port))

def send_tcp(message, port=9001):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", port))
        sock.sendall((message + "\n").encode())
        sock.close()
    except Exception as e:
        print(f"TCP Send Error: {e}")

def main():
    print("Starting log generator... Press Ctrl+C to stop.")
    try:
        while True:
            log = generate_log()
            # Randomly choose protocol
            if random.random() > 0.5:
                send_udp(log)
            else:
                send_tcp(log)
            
            print(f"Sent: {log}")
            time.sleep(random.uniform(0.1, 0.5))
    except KeyboardInterrupt:
        print("\nStopping.")

if __name__ == "__main__":
    main()
