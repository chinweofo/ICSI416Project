"""
Authors: Chinwe Ofonagoro, Vincent Jiang  
Date: 10/18/2025  
Course: ICSI416  
Purpose: TCP Socket Programming Project (Client Side)

This script acts as a client for uploading and downloading files
to/from a server using basic file transfer commands (`put`, `get`, and `quit`).

All communication is done over TCP sockets.

Commands:
    - put <filename> : Uploads a file to the server.
    - get <filename> : Downloads a file from the server.
    - quit           : Exits the client program.

The server stores uploaded files in directories based on the client's IP address.

References:
    https://realpython.com/python-sockets/
"""

import socket
import sys

# ========================== Helper Functions ==========================

def commandLoop():
    """
    Loop to continually prompt the user for commands until 'quit' is entered.
    Handles 'put', 'get', and 'quit' commands.
    """
    while True:
        commandLine = input("Enter command (put <file>, get <file>, quit): ").strip()

        if not commandLine:
            continue

        parts = commandLine.split()

        if len(parts) == 0:
            print("Empty input. Try again.")
            continue

        command = parts[0].upper()

        if command == "QUIT":
            runQuit()
            break  # Exit the loop after quitting

        if len(parts) != 2:
            print("Incorrect input. Usage:\nput <filename>\nget <filename>\nquit")
            continue

        fileName = parts[1]

        if command == "PUT":
            runPut(fileName)

        elif command == "GET":
            runGet(fileName)

        else:
            print("Unknown command. Try again.")


def fileToBytes(fileName, sock):
    """
    Reads a file in binary mode and sends it over the socket in chunks.

    Args:
        fileName (str): The name of the file to send.
        sock (socket): The socket to send the file through.
    """
    try:
        with open(fileName, 'rb') as f:
            fileBytes = f.read(1024)
            while fileBytes:
                sock.send(fileBytes)
                fileBytes = f.read(1024)
        sock.send(b"<EOF>")  # Mark end of file for the server

    except FileNotFoundError:
        print(f"[-] Error: The file '{fileName}' was not found.")
    except IOError as ioe:
        print(f"[-] Error reading file '{fileName}': {ioe}")


def runPut(fileName):
    """
    Handles the file upload ("put") command.
    Sends the file to the server and waits for acknowledgment.

    Args:
        fileName (str): The file to upload.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ipAddress, int(serverPort)))
        print("[+] Connected to Server")

        command = f"put {fileName}"
        sock.send(command.encode())

        acknowledgment = sock.recv(1024).decode()
        if acknowledgment != "Ack 0":
            print("[-] Server error or unexpected acknowledgment.")
            sock.close()
            return
        else:
            print("[+] Server ready. Sending file...")

        fileToBytes(fileName, sock)

        acknowledgment = sock.recv(1024).decode()
        if acknowledgment != "Ack 1":
            print("[-] Server failed to confirm upload.")
        else:
            print("[+] File successfully uploaded.")

    except Exception as e:
        print(f"[-] Error in runPut: {e}")

    finally:
        sock.close()


def runGet(fileName):
    """
    Handles the file download ("get") command.
    Receives the file from the server and saves it locally.

    Args:
        fileName (str): The file to download.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ipAddress, int(serverPort)))
        print("[+] Connected to Server")

        command = f"get {fileName}"
        sock.send(command.encode())

        acknowledgment = sock.recv(1024).decode()
        if acknowledgment == "File not found":
            print("[-] Server could not find the requested file.")
            return
        elif acknowledgment != "Ack 0":
            print("[-] Unexpected server response.")
            return

        print("[+] Server acknowledged. Receiving file...")

        with open(f"downloaded_{fileName}", 'wb') as f:
            while True:
                data = sock.recv(1024)
                if b"<EOF>" in data:
                    f.write(data.replace(b"<EOF>", b""))
                    break
                f.write(data)

        print("[+] File delivered from server.")

    except Exception as e:
        print(f"[-] Error in runGet: {e}")

    finally:
        sock.close()


def runQuit():
    """
    Handles the quit command. Simply notifies the user and exits.
    """
    print("Closing client connection to server...")


# ========================== Main Function ==========================

def main():
    """
    Parses command line arguments and starts the client command loop.
    Expected usage:
        python clientTCP.py <ServerPort> <ServerIP>
    """
    global serverPort, ipAddress

    if len(sys.argv) != 3:
        print("Incorrect input. Usage: python clientTCP.py <ServerPort> <ServerIP>")
        sys.exit(1)

    serverPort = sys.argv[1]
    ipAddress = sys.argv[2]

    commandLoop()


if __name__ == "__main__":
    main()
