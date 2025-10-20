"""
Authors: Chinwe Ofonagoro, Vincent Jiang
Date: 10/18/2025
Purpose: Socket programming for ICSI416.
This script implements the server side of a TCP-based file transfer application.
It supports file upload and download operations initiated by the client.

Usage:
    python serverTCP.py <port>
        (IE: python serverTCP.py 12345)

Expected client commands:
    put <filename>     # Upload a file to the server
    get <filename>     # Download a file from the server

Files will be stored per client IP under the 'uploads/' directory.

References:
    https://realpython.com/python-sockets/
"""

import socket
import sys
import os

def handle_client(client_socket, client_address):
    """
    Handles a single client connection.
    
    Parameters:
        client_socket (socket): The socket connected to the client.
        client_address (tuple): The client's address (IP, port).
        
    Supports two commands:
        - "put <filename>": receives a file and saves it.
        - "get <filename>": sends a file back to the client.
    """
    print(f"[+] Connection from {client_address}")

    try:
        # Receive the initial command from the client
        command = client_socket.recv(1024).decode().strip()
        print(f"[+] Command received: {command}")

        # Split the command into action and filename
        parts = command.split()
        if len(parts) != 2:
            print("[-] Invalid command format.")
            client_socket.close()
            return

        action, filename = parts[0], parts[1]
        client_ip = client_address[0]

        # Organize files by client IP address
        save_dir = os.path.join("uploads", client_ip.replace('.', '_'))
        os.makedirs(save_dir, exist_ok=True)

        if action == "put":
            # === PUT COMMAND ===
            filepath = os.path.join(save_dir, filename)

            # Acknowledge receipt of command
            client_socket.send("Ack 0".encode())

            # Receive the file content
            with open(filepath, 'wb') as f:
                while True:
                    data = client_socket.recv(1024)
                    if b"<EOF>" in data:
                        f.write(data.replace(b"<EOF>", b""))
                        break
                    f.write(data)

            print(f"[+] File saved to {filepath}")
            client_socket.send("Ack 1".encode())

        elif action == "get":
            # === GET COMMAND ===
            filepath = os.path.join(save_dir, filename)

            # Check if file exists before sending
            if not os.path.exists(filepath):
                client_socket.send("File not found".encode())
                print("[-] Requested file not found.")
                return

            # Acknowledge receipt of command
            client_socket.send("Ack 0".encode())

            # Send the file content
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    client_socket.send(data)

            # Send end-of-file marker
            client_socket.send(b"<EOF>")
            print(f"[+] Sent file {filename} to client.")

        else:
            print("[-] Unknown command.")

    except Exception as e:
        print(f"[-] Error: {e}")

    finally:
        # Close the connection with the client
        client_socket.close()
        print(f"[+] Connection with {client_address} closed.\n")


def main():
    """
    Starts the TCP file server.

    Listens on the port provided via command line argument,
    accepts incoming client connections, and delegates handling
    to the `handle_client` function.
    """
    if len(sys.argv) != 2:
        print("Usage: python serverTCP.py <port>")
        sys.exit(1)

    server_port = int(sys.argv[1])
    server_ip = '0.0.0.0'  # Listen on all available interfaces

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)

    print(f"[+] Server listening on port {server_port}...")

    while True:
        # Accept new client connection
        client_sock, client_addr = server_socket.accept()
        handle_client(client_sock, client_addr)


if __name__ == "__main__":
    main()
