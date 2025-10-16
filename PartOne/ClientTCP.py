"""
Author: Chinwe Ofonagoro, Vincent Jiang
Date: 
Purpose: Socket programming for ICSI416.
Allows the user to upload, download and quit the program.
Need to create two files to bounce back and forth: clientTCP.py, serverTCP.py
All exchanges (upload or download) will be initiated by the client.
"""
#pip install requests # type: ignore

import socket
import socketserver
import sys
import requests 

fileName = ""
serverPort = ""
ipAddress = ""

#Implement the following: 

"""Upload: Copy a file from the client to the server using the put command, which
takes as an input argument the full path to a file <file> on the client. Files uploaded to the server
should be stored in separate directories based on the client IP Address. Upon a successful receipt
of a file, the origin server would send back “File successfully uploaded.” message and close the
connection.

Example execution with prompts on the client:
put <file>
File successfully uploaded.
"""

def runPut(fileName):
    #upload_url = 'http://127.0.0.1:5000/upload/my_document.pdf'
    upload = (f"http://{serverPort}:{ipAddress}/upload/{fileName}")

    with open(fileName, 'rb') as f:
        file_content = f.read()

    r = requests.put(upload, data=file_content)

    if requests.status_code == 200:
        print("File successfully uploaded")
    



"""Download: Copy a file from the server to the client using the get command, which
also takes as an argument the full path to a file <file> on the server.
A control message sent from the server to the client stating “File delivered from server.” should
be displayed to the user.

Example execution with prompts on the client:
get <file>
File delivered from server.


def Download(command):
    
    print("File successfully uploaded")
"""



"""Quit: Close the program per user request."""
#def Quit():



"""Command Line Arguments. When starting your client and server, you will need to
specify several command line arguments, as detailed below:
• server - the server will take as command line inputs
(1) a port on which to run
• client - the client will take as command line inputs
(1) the server IP, (2) the server port
"""




def main():
    print("Input the Server port and ip address: ")
    print(sys.argv)
    serverPort = sys.argv[0]
    ipAddress = sys.argv[1] 


    print("Input HTTP command and file: ")
    print(sys.argv)
    currentCommand = sys.argv[0]
    fileName = sys.argv[1]
    #need the parameters into variables then use those variables as parameters in runPut()
    if sys.argv[0] == "put" or sys.argv[0] == "PUT":
        runPut(fileName)

    

if __name__ == "__main__":
    main()

