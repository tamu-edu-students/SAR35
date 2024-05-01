# -------------------------------------------------------------
# ECEN 404
# Search and rescue team
#
# This file contains variables used to control logic flow across multiple files
# NOTE: This file should run on startup
# NOTE: threading was used before multiprocessing, therefore the word thread is used incorrectly, and it's really
#       a background process
# NOTE: Movement is restart if a new path is received ... so it should be receiving new paths constantly
# -------------------------------------------------------------

# imports
import time
import readFromActiveFile
import controlVars
import multiprocessing
import os
import movementFunctions

currentWorkingDirectory = os.path.dirname(os.path.realpath(__file__))
parentDirectory = os.path.dirname(currentWorkingDirectory) #this is the parent directory of all files
# Variables to be updated (settings)
# -------------------------------------------------------------
controlVarEmgStopPath = os.path.join(parentDirectory, "FileSystem","controlVarEmgStop.csv")
controlVarTurnBoolPath = os.path.join(parentDirectory,"FileSystem", "controlVarTurnBool.csv")
controlVarNewMovementDataPath = os.path.join(parentDirectory, "FileSystem", "controlVarNewMovementData.csv")
controlVarStraightMovementPath = os.path.join(parentDirectory, "FileSystem", "controlVarStraightMovement.csv")
movement_data_path = os.path.join(parentDirectory,"FileSystem","MovementData")
controlVarSendGPSCalibrationPath = os.path.join(parentDirectory, "FileSystem", "controlVarSendGPSCalibration.csv")
longitude_for_calibrationCSVPath = os.path.join(parentDirectory, "FileSystem", "longitude_for_calibration.csv")
latitude_for_calibrationCSVPath = os.path.join(parentDirectory, "FileSystem", "latitude_for_calibration.csv")
controlVarEndOfMovementDataPath = os.path.join(parentDirectory, "FileSystem", "endOfMovementData.csv")
# -------------------------------------------------------------

# Start the movement script on a thread (process)
# Define a function that represents the background task (process)
def background_task():
    # EDIT HERE:
    # call to movement algo
    # this should do one instruction for csv. check to make sure the csv has not changed. then do the next instruction. and so on
    # there should be a try block incase the csv changes while its trying to read a instruction.
    # it also needs to catch errors when there is no data.
    # IF ROVER IS TURNING, TURN ON TURN CONTROL VAR FOR GPS. Also, set turn bool =1 when starting straight movement
    listOfFiles = os.listdir(movement_data_path)
    movement_csv_path = ""
    if len(listOfFiles) == 1:
        movement_csv_path = os.path.join(movement_data_path, listOfFiles[0])

    try:
        if os.path.exists(movement_csv_path):
            movementFunctions.mainMovement(movement_csv_path,controlVarStraightMovementPath,controlVarTurnBoolPath)
    except Exception as e:
        print("ERROR with physical movement:",e)

    print("MOVEMENT TASK FINISHED")

    #Added end of movement data flag
    controlVars.endOfMovementData_Set1(controlVarEndOfMovementDataPath)

# Function to create and start the background thread
def start_background_thread():
    global movement_process
    movement_process = multiprocessing.Process(target=background_task)
    movement_process.start()


# Function to stop the background thread
def stop_background_thread():
    global movement_process
    if movement_process.is_alive():
        movement_process.terminate()
        movement_process.join()


# Start the background thread initially

start_background_thread()
alreadyRunningFlag = True

# *********LOOP TO STOP MOVE THREAD***********
while True:
    try:
        if int(readFromActiveFile.read_from_active_file(controlVarEmgStopPath)) == 0 and (alreadyRunningFlag == True):
            # stop
            stop_background_thread()
            movementFunctions.stopMovement()
            alreadyRunningFlag = False
            controlVars.turnOffControlStraight(controlVarStraightMovementPath)

        elif (int(readFromActiveFile.read_from_active_file(controlVarEmgStopPath)) == 1) and (alreadyRunningFlag == False):
            # start
            start_background_thread()
            alreadyRunningFlag = True

        if int(readFromActiveFile.read_from_active_file(controlVarNewMovementDataPath)) == 1:
            print("GOT IT, NEW MOVEMENT")
            #   set the send calibration control var back to zero && reset internal vars so that next recalibration they are blank
            controlVars.sendGPSCalibration_Set0(controlVarSendGPSCalibrationPath)
            controlVars.wipe_and_write_to_csv(longitude_for_calibrationCSVPath, [()])  # clear
            controlVars.wipe_and_write_to_csv(latitude_for_calibrationCSVPath, [()])  # clear

            # Stop the background thread
            stop_background_thread()
            movementFunctions.stopMovement()
            alreadyRunningFlag = False
            time.sleep(.1) # wait for signal propagation
            # reset new movement data
            controlVars.newMovementData_Set0(controlVarNewMovementDataPath)
            # restart the movement thread
            if int(readFromActiveFile.read_from_active_file(controlVarEmgStopPath)) == 1:
                start_background_thread()
                alreadyRunningFlag = True

        time.sleep(.05)  # delay loop
    except Exception as e:
        print("ERROR with movement control checking for emg stop or new movement data: ", e)
