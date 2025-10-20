"""
Authors: Chinwe Ofonagoro, Vincent Jiang  
Date: 10/20/2025  
Purpose: UDP Socket Programming Project (Client Side)

This script acts as a client for uploading and downloading files
to/from a server using basic file transfer commands (`put`, `get`, and `quit`).

All communication is done over UDP sockets using a stop-and-wait protocol
to ensure reliable transfer of file data.

Usage:
    python clientUDP.py <port> <IP Address>
    Example:
        python clientUDP.py 12345 127.0.0.1

Commands:
    - put <filename> : Uploads a file to the server.
    - get <filename> : Downloads a file from the server.
    - quit           : Exits the client program.

Notes:
    - The server stores uploaded files in directories based on the client's IP address.
    - File transfers are done in chunks (default 1000 bytes).
    - Each chunk requires an ACK for reliable delivery.
    - A final FIN/ACK1 exchange signals end of file transfer.

References:
    https://realpython.com/python-sockets/
"""

import socket
import sys
import os

CHUNK_SIZE = 1000

def run_put(sock, server_addr, filename):
    if not os.path.exists(filename):
        print(f"[-] File '{filename}' does not exist.")
        return

    try:
        # Send the put command
        command = f"put {filename}"
        sock.sendto(command.encode(), server_addr)

        # Wait for Ack 0 from server confirming command
        data, addr = sock.recvfrom(1024)
        if addr != server_addr or data.decode() != "Ack 0":
            print("[-] Server did not acknowledge put command properly.")
            return

        filesize = os.path.getsize(filename)
        # Send LEN:<filesize>
        sock.sendto(f"LEN:{filesize}".encode(), server_addr)

        # Send file in chunks, wait for ACK after each
        with open(filename, 'rb') as f:
            bytes_sent = 0
            while bytes_sent < filesize:
                chunk = f.read(CHUNK_SIZE)
                sock.sendto(chunk, server_addr)

                data, addr = sock.recvfrom(1024)
                if addr != server_addr or data.decode() != "ACK":
                    print("[-] Did not receive ACK for chunk. Aborting.")
                    return
                bytes_sent += len(chunk)

        # Wait for FIN from server
        data, addr = sock.recvfrom(1024)
        if addr == server_addr and data.decode() == "FIN":
            print("[+] File successfully uploaded.")
            # Send final Ack 1 to confirm finish
            sock.sendto(b"Ack 1", server_addr)
        else:
            print("[-] Did not receive FIN from server.")

    except Exception as e:
        print(f"[-] Error in put: {e}")

def run_get(sock, server_addr, filename):
    try:
        # Send get command
        command = f"get {filename}"
        sock.sendto(command.encode(), server_addr)

        # Wait for server response
        data, addr = sock.recvfrom(4096)
        if addr != server_addr:
            print("[-] Received response from unknown sender.")
            return

        response = data.decode()
        if response == "File not found":
            print(f"[-] Server could not find file '{filename}'.")
            return
        elif response != "Ack 0":
            print("[-] Unexpected server response.")
            return

        # Receive LEN:<filesize>
        len_data, addr = sock.recvfrom(1024)
        if addr != server_addr or not len_data.decode().startswith("LEN:"):
            print("[-] Did not receive expected length info.")
            return

        filesize = int(len_data.decode().split(":")[1])
        print(f"[*] Expecting {filesize} bytes.")

        # Send ACK for LEN message
        sock.sendto(b"ACK", server_addr)

        # Receive file chunks, send ACK after each
        bytes_received = 0
        save_name = f"downloaded_{filename}"
        with open(save_name, 'wb') as f:
            while bytes_received < filesize:
                chunk, addr = sock.recvfrom(CHUNK_SIZE + 100)
                if addr != server_addr:
                    print(f"[!] Ignored packet from unknown sender {addr}")
                    continue
                f.write(chunk)
                bytes_received += len(chunk)
                sock.sendto(b"ACK", server_addr)

        # Receive FIN from server
        fin_data, addr = sock.recvfrom(1024)
        if addr == server_addr and fin_data.decode() == "FIN":
            print(f"[+] File downloaded and saved as {save_name}")
            # ✅ Send final acknowledgment
            sock.sendto(b"Ack 1", server_addr)
            print("[+] Final acknowledgment sent to server.")
        else:
            print("[-] Did not receive FIN from server.")

    except Exception as e:
        print(f"[-] Error in get: {e}")

def command_loop(sock, server_addr):
    while True:
        command_line = input("Enter HTTP request (put/get/quit): ").strip()
        if not command_line:
            continue

        parts = command_line.split()
        command = parts[0].lower()

        if command == "quit":
            print("Closing client.")
            break

        if len(parts) != 2:
            print("Usage:\n  put <filename>\n  get <filename>\n  quit")
            continue

        filename = parts[1]

        if command == "put":
            run_put(sock, server_addr, filename)
        elif command == "get":
            run_get(sock, server_addr, filename)
        else:
            print("Unknown command. Use put, get, or quit.")

def main():
    if len(sys.argv) != 3:
        print("Usage: python clientUDP.py <ServerPort> <ServerIP>")
        sys.exit(1)

    server_port = int(sys.argv[1])
    server_ip = sys.argv[2]
    server_addr = (server_ip, server_port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"[+] UDP client started. Sending to {server_ip}:{server_port}")

    try:
        command_loop(sock, server_addr)
    finally:
        sock.close()

if __name__ == "__main__":
    main()

