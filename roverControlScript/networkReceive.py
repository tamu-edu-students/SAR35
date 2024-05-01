# -------------------------------------------------------------
# ECEN 404
# Search and rescue team
#
# This file contains all the networking functions
# NOTE:
# NOTE:
# -------------------------------------------------------------

import socket
import os
import time

def get_ip_address():
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a local address (doesn't really matter which one)
        s.connect(("192.168.0.1", 80))  # Example local IP address
        # Get the local IP address of the Raspberry Pi
        ip_address = s.getsockname()[0]
        # Close the socket
        s.close()
        return ip_address
    except Exception as e:
        print("Error:", e)
        return None

# This program just receives sent files into whatever directory the server is running in for further use
# NOTE: Server runs indefinitely and requires manual shutdown when finished

networkNotSetUp = True
while networkNotSetUp:
    try:
        # change to whatever IP your base station is for wlan hotspot to pi. Find in cmd, then ipconfig on base station
        HOST = get_ip_address()
        print("HOST IP SET TO: ", HOST)
        # otherwise shouldn't need to change anything
        PORT = 5555
        SIZE = 1024
        BYTEORDER_LENGTH = 8
        FORMAT = "utf-8"
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        networkNotSetUp = False
    except Exception as e:
        print("ERROR with receive network setup: ", e)
        time.sleep(2) # wait 2 secs and then try setup again

currentWorkingDirectory = os.path.dirname(os.path.realpath(__file__))
parentDirectory = os.path.dirname(currentWorkingDirectory)

while True:
    try:
        print("Working")
        client = s.accept()
        print(f"\033[33m[*] Listening as {HOST}:{PORT}\033[m")
        print(f"\033[32m[!] Client connected {client[1]}\033[m")

        print(f"Sending 'copy trash' msg")
        client[0].send('copy trash'.encode())

        print(f"[RECV] Receiving the file size")
        file_size_in_bytes = client[0].recv(BYTEORDER_LENGTH)
        file_size = int.from_bytes(file_size_in_bytes, 'big')
        print("File size received:", file_size, " bytes")
        client[0].send("File size received.".encode(FORMAT))

        print(f"[RECV] Receiving the filename.")
        filename = client[0].recv(SIZE).decode(FORMAT)
        print(f"[RECV]Filename received:", filename)
        client[0].send("Filename received.".encode(FORMAT))

        print(f"[RECV] Receiving the file data.")
        # Until we've received the expected amount of data, keep receiving
        packet = b""
        while len(packet) < file_size:
            if (file_size - len(packet)) > SIZE:  # if remaining bytes are more than the defined chunk size
                buffer = client[0].recv(SIZE)  # read SIZE bytes
            else:
                buffer = client[0].recv(file_size - len(packet))  # read remaining number of bytes

            if not buffer:
                raise Exception("Incomplete file received")
            packet += buffer

        filename_list = filename.split("\\")
        filename = filename_list[-1]

        with open(os.path.join(parentDirectory, "FileSystem", "inputFolderQueue",filename), 'wb') as f:
            f.write(packet)

        print(f"[RECV] File data received.")
        client[0].send("File data received".encode(FORMAT))
        client[0].close()
    except Exception as e:
        print("ERROR with network receive side: ",e)
        time.sleep(1)


s.close()