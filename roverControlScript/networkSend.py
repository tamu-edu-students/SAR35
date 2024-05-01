# -------------------------------------------------------------
# ECEN 404
# Search and rescue team
#
# This file is used to send files from the rover to the base station
# NOTE: this script needs access to the files directories (RUN IN SUDO)
# NOTE: This file should run on startup
# NOTE: The delay of this loop should be less than the delay of the main loop. BUT longer than BS processing time
# -------------------------------------------------------------

# Variables to be updated (settings)
# -------------------------------------------------------------
    # variables:
totalLoopGoalTime = 1.1 # a delay of 1.1 is the official run time goal (see image on camera roll on mar 31, 2024)
# -------------------------------------------------------------

import subprocess
import time
import socket
import os
import controlVars
import readFromActiveFile

currentWorkingDirectory = os.path.dirname(os.path.realpath(__file__))
parentDirectory = os.path.dirname(currentWorkingDirectory) #this is the parent directory of all files (403)

# Directories
outputZipFolderPath = os.path.join(parentDirectory, "FileSystem","OutputQueue")
ipAddressFilePath = os.path.join(parentDirectory, "FileSystem", "ipAddressData", "ip_address_of_base.csv")

# ----------- SET UP (start) ------------
def is_connected():
    try:
        output = subprocess.check_output(["iwgetid"])
        return b"ESSID" in output
    except subprocess.CalledProcessError:
        return False

while True:
    if is_connected():
        print("Raspberry Pi is connected to a Wi-Fi network.")
        controlVars.remove_all_contents_in_directory(outputZipFolderPath)
        break
    else:
        print("Raspberry Pi is not connected to a Wi-Fi network.")
        time.sleep(1)

while True:
    if os.path.exists(ipAddressFilePath):
        hostIP = str(readFromActiveFile.read_from_active_file(ipAddressFilePath))
        if hostIP != "":
            controlVars.remove_all_contents_in_directory(outputZipFolderPath)
            break
        else:
            print("ERROR can't read base station IP from csv")
    else:
        print("waiting for ip address csv from base station ...")
        time.sleep(1)

# ------ SET UP (end) --------


# function to send one file
def send_file(fileNameToSend, filePathToSend, hostIp):
    HOST = str(hostIp).strip()  # change to whatever IP your base station is for wlan hotspot to pi. Find in cmd, then ipconfig on base station
    PORT = 5555
    FORMAT = "utf-8"
    SIZE = 1024
    BYTEORDER_LENGTH = 8
    s = socket.socket()
    s.connect((HOST, PORT))
    msg = s.recv(SIZE).decode()
    print('[*] server:', msg)

    file_size = os.path.getsize(filePathToSend)
    print("File Size is :", file_size, "bytes")
    file_size_in_bytes = file_size.to_bytes(BYTEORDER_LENGTH, 'big')

    print("Sending the file size")
    s.send(file_size_in_bytes)
    msg = s.recv(SIZE).decode(FORMAT)
    print(f"[SERVER]: {msg}")

    print("Sending the file name")
    s.send(fileNameToSend.encode(FORMAT))
    msg = s.recv(SIZE).decode(FORMAT)
    print(f"[SERVER]: {msg}")

    print("Sending the file data")
    with open(filePathToSend, 'rb') as f1:
        s.send(f1.read())
    msg = s.recv(SIZE).decode(FORMAT)
    print(f"[SERVER]: {msg}")

    s.close()

def get_queue_number(filename):
    # Extract queue number from the filename
    return int(filename.split('_')[0])

def get_file_with_lowest_queue(directory):
    # Get list of all files in the directory
    files = os.listdir(directory)

    # Filter files that match the naming convention
    datafiles = [filename for filename in files if 'base' in filename]

    if not datafiles:
        return None  # No matching files found

    # Get queue numbers from all datafiles
    queue_numbers = [get_queue_number(filename) for filename in datafiles]

    # Find the file with the lowest queue number
    min_queue_number_index = queue_numbers.index(min(queue_numbers))
    lowest_queue_file = datafiles[min_queue_number_index]

    return lowest_queue_file


resetCounter = 0
while True:
    startLoopTime = time.time()


    fileNameToSend = get_file_with_lowest_queue(outputZipFolderPath)
    if fileNameToSend is None:
        print("No files in output queue with 'base' in the name")
    else:
        filePathToSend = os.path.join(parentDirectory, "FileSystem", "OutputQueue", str(fileNameToSend))
        try:
            send_file(fileNameToSend,filePathToSend,hostIP)
            os.remove(filePathToSend)
            resetCounter = 0
        except Exception as e:
            resetCounter = resetCounter + 1
            if resetCounter > 1:
                os.remove(filePathToSend)
                print(fileNameToSend, ", was removed due to, too many failed sending attempts")
            print(fileNameToSend, ", failed to send")


    #delay logic
    endLoopTime = time.time()
    elapsedTime = endLoopTime - startLoopTime
    if elapsedTime < totalLoopGoalTime:
        time.sleep(totalLoopGoalTime - elapsedTime)