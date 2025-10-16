"""
Authors: Chinwe Ofonagoro, Vincent Jiang
Date: 
Purpose: Socket programming for ICSI416.
Allows the user to upload, download and quit the program.
Need to create two files to bounce back and forth: clientTCP.py, serverTCP.py
All exchanges (upload or download) will be initiated by the client.

Utilized this website for explanations: https://realpython.com/python-sockets/
"""


import socket
import socketserver
import sys


#Helper methods

def commandLoop():
    while True:
        commandLine = input("Enter HTTP request (put/get/quit): ").strip()
        #if not commandLine:
            #continue  

        parts = commandLine.split() #this will take the command line argument and split it into the command and the file name and put it into a list
        command = parts[0].upper()
        fileName = parts[1]

        #Handles the PUT command
        if command == "PUT":
            if len(parts) != 2:
                print("Incorrect input. Should be: put <filename>") #will restart the command line question
                continue
            fileName = parts[1]
            runPut(fileName)

        #Handles the GET command
        if command == "GET":
            if len(parts) != 2:
                print("Incorrect input. Should be: get <filename>") #will restart the command line question
                continue
            fileName = parts[1]
            runGet(fileName)

        #Handles the QUIT command
        elif command == "QUIT":
            runQuit()

        else:
            print("Unknown command. Try again.")


"""
Converts a file's content into a bytes object
"""
def fileToBytes(fileName, sock):
    try:
        with open(fileName, 'rb') as f:
            fileBytes = f.read(1024)
            while fileBytes:
                socket.send(fileBytes)
                fileBytes = f.read(1024)
        sock.send(b"<EOF>") #marks the end of the file for the server
        
    except FileNotFoundError:
        print(f"[-] Error: The file '{fileName}' was not found.")
        return None
    except IOError as ioe:
        print(f"[-] Error reading file '{fileName}': {ioe}")
        return None



#Implement the following: 

"""Upload: Copy a file from the client to the server using the put command, which
takes as an input argument the full path to a file <file> on the client. Files uploaded to the server
should be stored in separate directories based on the client IP Address. Upon a successful receipt
of a file, the origin server would send back “File successfully uploaded.” message and close the
connection.

Example execution with prompts on the client:
put <file>
File successfully uploaded.

def runPut(fileName):
    #upload_url = 'http://127.0.0.1:5000/upload/my_document.pdf'
    upload = (f"http://{serverPort}:{ipAddress}/upload/{fileName}")

    with open(fileName, 'rb') as f:
        file_content = f.read()

    r = requests.put(upload, data=file_content)

    if .status_code == 200:
        print("File successfully uploaded")
"""
def runPut(fileName):
    #create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SOCK_STREAM for TCP

    if(sock < 0): #checkpoint
        print("[-] Socket Error\n")
        exit(1)
    print("[+] TCP Server Socket Created.\n")

    #connect to the server
    sock.connect((ipAddress, int(serverPort)))
    print("[+] Connected to Server")

    #upload to the server
    #convert the file to bytes first to send through the socket
    #Tells the server what the client wants to upload instead of just uploading it
    command = f"put {fileName}"
    sock.send(command, fileName.encode())

    #wait for an acknowledgement from the server and convert that from bytes
    acknowledgment = sock.recv(1024).decode() 

    if acknowledgment != "Ack 0": #checkpoint test
            print("[-] Server Error")
            exit(1)
    else:
        print("[+] Acknowledgment received")

    #once given confirmation that the server is ready to receive, send the file (in bytes)
    fileToBytes(fileName, sock)

    acknowledgment = sock.recv(1024).decode()

    if acknowledgment != "Ack 1": #checkpoint test
            print("[-] Server Error")
            exit(1)
    else:
        print("[+] File successfully uploaded ")
    


    

"""Download: Copy a file from the server to the client using the get command, which
also takes as an argument the full path to a file <file> on the server.
A control message sent from the server to the client stating “File delivered from server.” should
be displayed to the user.

Example execution with prompts on the client:
get <file>
File delivered from server.


def Download(command):
    
    print("File successfully downloaded")
"""
def runGet():
    pass


"""Quit: Close the program per user request."""
def runQuit():
    print("Closing client connection to server...")
    #then close the client connection to server
    



"""Command Line Arguments. When starting your client and server, you will need to
specify several command line arguments, as detailed below:
• server - the server will take as command line inputs
(1) a port on which to run
• client - the client will take as command line inputs
(1) the server IP, (2) the server port
"""




def main():
    global serverPort, ipAddress, fileName
    
    print("Input the Server port and ip address: ")
    #print(sys.argv)

    if len(sys.argv) != 3:
        print("Incorrect input. Should be: python ClientTCP.py <ServerPort> <ServerIP>")
        sys.exit(1)

    serverPort = sys.argv[1]
    ipAddress = sys.argv[2] 

    commandLoop()

    

if __name__ == "__main__":
    main()

