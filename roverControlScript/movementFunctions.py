# -------------------------------------------------------------
# ECEN 404
# Search and rescue team
#
# This file contains the functions used for movement
# NOTE: movement is contained in the movementControl.py file
# NOTE:
# -------------------------------------------------------------

# Variables to be updated (settings)
# -------------------------------------------------------------
#Calibration data & constants
address = 130
forward_distance = 20 #feet measurement for forward data
forward20ft = [0, 4, [40, 39], 8, 0, 4, [41, 39], 19.9]
turnRight90 = [1, 4, [31, 26], 4]
turnLeft90 = [0, 5, [27, 31], 4]
turn180 = [1, 4, [29, 29], 8]
# -------------------------------------------------------------


#Full motor control python file

#imports
import time
import os
import serial
import controlVars

# File paths
currentWorkingDirectory = os.path.dirname(os.path.realpath(__file__))
parentDirectory = os.path.dirname(currentWorkingDirectory) #this is the parent directory of all files
controlVarSendGPSCalibrationPath = os.path.join(parentDirectory, "FileSystem", "controlVarSendGPSCalibration.csv")

#****ALL CODE FROM SERIAL STUFF****

#set up serial interface
ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0
)


#calculate check sum, input in decimal
def checkSum(address,command,data):
    tempSum = address + command + data
    afterMask = tempSum & 0b01111111 #add mask
    return afterMask #return checksum number

#used for sending simplified serial
def sendSimplifiedSerial(data):
    hex_bytes = bytes([data])
    ser.write(hex_bytes)

#used for sending data pakets of 8N1 0 to 5v TTL levels
def sendData(address,command,data):
    checkSumValue = checkSum(address,command,data)
    checkSumValue_hex_bytes = bytes([checkSumValue])

    address_hex_bytes = bytes([address])
    command_hex_bytes = bytes([command])
    data_hex_bytes = bytes([data])

    ser.write(address_hex_bytes) #send address
    ser.write(command_hex_bytes) #send command
    ser.write(data_hex_bytes) # send data
    ser.write(checkSumValue_hex_bytes) # send check sum

#****ALL CODE FROM SERIAL STUFF****

def readInMove(csvPath):
    import csv

    # Specify the path to your CSV file
    csv_file_path = csvPath
    output_list = []

    # Open the CSV file and read it using the csv.reader
    with open(csv_file_path, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)

        # Iterate over each row in the CSV file
        for row in csv_reader:
            # Access the value in the first (and only) column
            column_value = row[0]

            # Process the column value as needed
            column_value_fixed = column_value.split("$")
            output_list.append(column_value_fixed)
    return output_list

'''
def sendData(address,command,data):
    print("----------------")
    print(address,command,data)
'''

#this will send any thing in the form [X, X, [X, X], X ...]
#input is calibration data and it sends that output. Ex input forward20ft; output moves 20ft
def sendCalibrationData(data):
    for i in range(len(data)):
        if isinstance(data[i],list):
            sendData(address,data[i-2],data[i][0])
            sendData(address,data[i-1],data[i][1])
            time.sleep(data[i+1])
    #stop after done
    sendData(address, 0, 0)
    sendData(address, 4, 0)
    time.sleep(1)

def forwardMovement(meters):
    feetToGo = meters * 3.28084

    for i in range(int(feetToGo/forward_distance)):
        sendCalibrationData(forward20ft)

    ratio = (feetToGo % forward_distance)/forward_distance

    scaledForwardData = [] #scaled data to send to "send calibration data"
    for i in range(len(forward20ft)):
        if isinstance(forward20ft[i], list):
            scaledForwardData.append(forward20ft[i - 2])
            scaledForwardData.append(forward20ft[i - 1])
            scaledForwardData.append(forward20ft[i - 0])
            scaledForwardData.append(forward20ft[i + 1] * ratio)

    sendCalibrationData(scaledForwardData) #send distance less then 20ft

def turnMovement(degrees):
    if degrees == 180:
        sendCalibrationData(turn180)
    if degrees == 90:
        sendCalibrationData(turnLeft90)
    if degrees == -90:
        sendCalibrationData(turnRight90)
    if degrees > 0 and degrees < 90:
        ratio = degrees/90 #ratio to scale time
        scaledTurnData = []  # scaled data to send to "send calibration data"
        for i in range(len(turnLeft90)):
            if isinstance(turnLeft90[i], list):
                scaledTurnData.append(turnLeft90[i - 2])
                scaledTurnData.append(turnLeft90[i - 1])
                scaledTurnData.append(turnLeft90[i - 0])
                scaledTurnData.append(turnLeft90[i + 1] * abs(ratio))
        sendCalibrationData(scaledTurnData) #send out
    if degrees > -90 and degrees < 0:
        ratio = degrees / 90  # ratio to scale time
        scaledTurnData = []  # scaled data to send to "send calibration data"
        for i in range(len(turnRight90)):
            if isinstance(turnRight90[i], list):
                scaledTurnData.append(turnRight90[i - 2])
                scaledTurnData.append(turnRight90[i - 1])
                scaledTurnData.append(turnRight90[i - 0])
                scaledTurnData.append(turnRight90[i + 1] * abs(ratio))
        sendCalibrationData(scaledTurnData) #send otu


# MAIN FUNCTION
def mainMovement(csv_path,straightMovementPath,turnBoolPath):
    for i in readInMove(csv_path):
        if i[0] == 'F':
            if str(i[1]) != "0":
                controlVars.turnOnControlStraight(straightMovementPath)
            else:
                controlVars.turnOffControlStraight(straightMovementPath)
            forwardMovement(float(i[1]))
        elif i[0] == "T":
            controlVars.turnOffControlStraight(straightMovementPath)
            controlVars.turnOnControlTurnBool(turnBoolPath)
            turnMovement(float(i[1]))
        elif i[0] == 'W':
            controlVars.turnOffControlStraight(straightMovementPath)
            time.sleep(int(i[1]))
        elif i[0] == "CalStart":
            controlVars.sendGPSCalibration_Set1(controlVarSendGPSCalibrationPath)

    # ser.close() #cant close serial because it is only set up one time

    # time.sleep(.1) #let serial close

def stopMovement():
    sendData(address, 0, 0)
    sendData(address, 4, 0)