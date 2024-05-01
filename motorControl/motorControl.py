#Full motor control python file

#imports
import time


#Calibration data & constants
address = 130
forward_distance = 20 #feet measurement for forward data
forward20ft = [0, 4, [40, 39], 8, 0, 4, [41, 39], 19.9]
turnRight90 = [1, 4, [31, 26], 4]
turnLeft90 = [0, 5, [27, 31], 4]
turn180 = [1, 4, [29, 29], 8]

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

def sendData(address,command,data):
    print("----------------")
    print(address,command,data)

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




#MAIN CODE

#testing stuff
for i in range(0):
    print(readInMove("MovementDataTest.csv"))
    #forwardMovement(3.048)
    turnMovement(45)


for i in readInMove("MovementDataTest.csv"):
    if i[0] == 'F':
        forwardMovement(float(i[1]))
    elif i[0] == "T":
        turnMovement(float(i[1]))