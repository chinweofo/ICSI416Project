"""
Authors: Chinwe Ofonagoro, Vincent Jiang  
Date: 10/20/2025  
Purpose: UDP Socket Programming Project (Server Side)

This script implements a UDP server capable of receiving and sending files
to/from clients using simple commands (`put`, `get`). The server uses a
stop-and-wait protocol to ensure reliable data transfer over UDP.

Usage:
    python serverUDP.py <Port>
    Example:
        python serverUDP.py 12345

Commands:
    - put <filename> : Client uploads a file to the server.
    - get <filename> : Client requests a file download from the server.

Behavior:
    - Files uploaded by clients are saved in directories named after
      their IP addresses (e.g., uploads_127_0_0_1).
    - File transfers are chunked (1000 bytes) and require ACKs.
    - The server responds with FIN to signal successful upload/download completion.

References:
    https://realpython.com/python-sockets/
"""

import socket
import sys
import os

CHUNK_SIZE = 1000

def save_file_directory(client_ip):
    dir_name = f"uploads_{client_ip.replace(':', '_')}"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name

def receive_file(sock, expected_size, addr, save_path):
    try:
        bytes_received = 0
        with open(save_path, 'wb') as f:
            while bytes_received < expected_size:
                data, sender = sock.recvfrom(CHUNK_SIZE + 100)
                if sender != addr:
                    print(f"[!] Ignored packet from unknown sender {sender}")
                    continue
                f.write(data)
                bytes_received += len(data)
                sock.sendto(b"ACK", addr)  # ACK for chunk

        # Send FIN after all bytes received
        sock.sendto(b"FIN", addr)
        print(f"[+] File received and saved as {save_path}")

    except Exception as e:
        print(f"[-] Error receiving file: {e}")

def handle_get(sock, filename, client_addr):
    if not os.path.exists(filename):
        sock.sendto(b"File not found", client_addr)
        print(f"[-] File {filename} not found.")
        return

    # Step 1: Acknowledge command
    sock.sendto(b"Ack 0", client_addr)

    # Step 2: Send LEN:<filesize>
    filesize = os.path.getsize(filename)
    sock.sendto(f"LEN:{filesize}".encode(), client_addr)

    # Step 3: Wait for client ACK on length
    data, addr = sock.recvfrom(1024)
    if addr != client_addr or data.decode() != "ACK":
        print("[-] Client did not ACK file length.")
        return

    # Step 4: Send chunks with stop-and-wait
    with open(filename, 'rb') as f:
        bytes_sent = 0
        while bytes_sent < filesize:
            chunk = f.read(CHUNK_SIZE)
            sock.sendto(chunk, client_addr)

            # Wait for ACK
            data, addr = sock.recvfrom(1024)
            if addr != client_addr or data.decode() != "ACK":
                print("[-] Client did not ACK chunk. Aborting.")
                return

            bytes_sent += len(chunk)

    # Step 5: Send FIN to signal completion
    sock.sendto(b"FIN", client_addr)

    # Step 6: Wait for Ack 1
    data, addr = sock.recvfrom(1024)
    if addr == client_addr and data.decode() == "Ack 1":
        print(f"[+] File {filename} delivered successfully.")
    else:
        print("[-] Did not receive final Ack 1 from client.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python serverUDP.py <Port>")
        sys.exit(1)

    server_port = int(sys.argv[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', server_port))
    print(f"[+] UDP Server listening on port {server_port}")

    while True:
        print("[*] Waiting for client command...")
        data, client_addr = sock.recvfrom(4096)
        message = data.decode().strip()
        print(f"[+] Received from {client_addr}: {message}")

        # Filter out non-command messages like "Ack 1"
        parts = message.split()
        if len(parts) < 2 or parts[0].lower() not in ["put", "get"]:
            print("[-] Invalid or unrecognized command. Ignored.")
            continue

        command = parts[0].lower()
        filename = parts[1]

        if command == "put":
            # Step 1: Acknowledge the put command
            sock.sendto(b"Ack 0", client_addr)

            # Step 2: Receive LEN:<filesize>
            len_data, addr = sock.recvfrom(1024)
            if addr != client_addr or not len_data.decode().startswith("LEN:"):
                print("[-] Invalid LEN from client.")
                continue

            filesize = int(len_data.decode().split(":")[1])
            print(f"[*] Expecting {filesize} bytes from client.")

            # Step 3: Prepare file path and receive file
            save_dir = save_file_directory(client_addr[0])
            save_path = os.path.join(save_dir, filename)
            receive_file(sock, filesize, client_addr, save_path)

            # Step 4: Wait for Ack 1 from client
            data, addr = sock.recvfrom(1024)
            if addr == client_addr and data.decode() == "Ack 1":
                print(f"[+] Upload of {filename} complete.")
            else:
                print("[-] Upload did not complete cleanly.")

        elif command == "get":
            handle_get(sock, filename, client_addr)

if __name__ == "__main__":
    main()

