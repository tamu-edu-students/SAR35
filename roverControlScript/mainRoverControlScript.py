# -------------------------------------------------------------
# ECEN 404
# Search and rescue team
#
# This file is used to control the rover subsystem integration
# NOTE: this script needs access to the files directories (RUN IN SUDO)
# NOTE: This file should run on startup
# -------------------------------------------------------------

# Import other python files
import outputControl
import inputControl
import readFromActiveFile
import emgStopHandling
import controlVars
import time
import os

currentWorkingDirectory = os.path.dirname(os.path.realpath(__file__))
# parentDirecotry is up to the ECEN403 folder. so we just need to copy the whole 403 folder to implement
parentDirectory = os.path.dirname(currentWorkingDirectory) #this is the parent directory of all files


# Variables to be updated (settings)
# -------------------------------------------------------------
    # variables:
totalLoopGoalTIme = 1.3   #ajust this so that the loop runs at desired frequency
roverIDNumber = 1 #number of the rover this is running on
cameraConnected = 0 # set to 1 if camera is connected using picamera2 module; set to 0 if camera not in use
# -------------------------------------------------------------

    # output stuff (this is all the paths to create the zip files to send to base station)
gpsOutputFilePath = os.path.join(parentDirectory,"FileSystem","GPSData")
cameraOutputFilePath = os.path.join(parentDirectory,"FileSystem","CameraData")
preZipFolderPath = os.path.join(parentDirectory, "FileSystem", "preZipFolder")
outputZipFolderPath = os.path.join(parentDirectory, "FileSystem","OutputQueue")
fileNamingNumberCSVPath = os.path.join(parentDirectory,"FileSystem","outputFileNameNumber.csv") #include file name
    # input stuff (this is the file paths where data is put into from the base station)
input_folder_queue_path = os.path.join(parentDirectory, "FileSystem","inputFolderQueue")
unzipped_folder_path = os.path.join(parentDirectory,"FileSystem","unzippedFromBase")
movement_data_path = os.path.join(parentDirectory,"FileSystem","MovementData")
emg_stop_path = os.path.join(parentDirectory, "FileSystem","EmgStopData")
ip_address_data_path = os.path.join(parentDirectory, "FileSystem", "ipAddressData")
    # csv path for control vars
controlVarEmgStopPath = os.path.join(parentDirectory, "FileSystem", "controlVarEmgStop.csv")
controlVarTurnBoolPath = os.path.join(parentDirectory,"FileSystem", "controlVarTurnBool.csv")
controlVarNewMovementDataPath = os.path.join(parentDirectory, "FileSystem","controlVarNewMovementData.csv")
controlVarStraightMovementPath = os.path.join(parentDirectory, "FileSystem", "controlVarStraightMovement.csv")
controlVarSendGPSCalibrationPath = os.path.join(parentDirectory, "FileSystem", "controlVarSendGPSCalibration.csv")
controlVarEndOfMovementDataPath = os.path.join(parentDirectory, "FileSystem", "endOfMovementData.csv")
    # internal path for longitude and latitude
longitudeCSVPath = os.path.join(parentDirectory, "FileSystem", "longitude.csv")
latitudeCSVPath = os.path.join(parentDirectory, "FileSystem", "latitude.csv")
longitude_for_calibrationCSVPath = os.path.join(parentDirectory, "FileSystem", "longitude_for_calibration.csv")
latitude_for_calibrationCSVPath = os.path.join(parentDirectory, "FileSystem", "latitude_for_calibration.csv")



# ------Rest of program------

# *******************************FUNCTIONS (start) *******************************
def remove_all_contents_in_directory(directory):
    try:
        # Check if the directory exists
        if not os.path.exists(directory):
            print(f"Directory '{directory}' does not exist.")
            return

        # Iterate over each item in the directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)  # item can be anything i.e. folder or file
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                remove_all_contents_in_directory(item_path)  #recursive call to delete sub directory files
                # After removing files and subdirectories, remove the directory itself
                os.rmdir(item_path)

    except Exception as e:
        print(f"Error occurred while removing contents: {e}")

#Capture image from camera
def capture_images(picam, num_images, filename_prefix, cameraFolderPath):
    for i in range(1, num_images + 1):
        filename = f"{filename_prefix}_{i}.jpg"
        filepath = os.path.join(cameraFolderPath,filename)
        picam.capture_file(filepath)
# *******************************FUNCTIONS (end) *******************************


#*******************start up operations (start) *********************************
    # Clear all input and output and intermediary directories upon startup

    # Out to base Station
remove_all_contents_in_directory(gpsOutputFilePath)
remove_all_contents_in_directory(cameraOutputFilePath)
remove_all_contents_in_directory(preZipFolderPath)
remove_all_contents_in_directory(outputZipFolderPath)
    # Input:
remove_all_contents_in_directory(input_folder_queue_path)
remove_all_contents_in_directory(unzipped_folder_path)
remove_all_contents_in_directory(movement_data_path)
remove_all_contents_in_directory(emg_stop_path)
remove_all_contents_in_directory(ip_address_data_path)

    # Reset control vars (and make files if they dont exit)
controlVars.turnOffControlTurnBool(controlVarTurnBoolPath)
controlVars.emgStopSet1(controlVarEmgStopPath)
controlVars.newMovementData_Set0(controlVarNewMovementDataPath)
controlVars.turnOffControlStraight(controlVarStraightMovementPath)
controlVars.sendGPSCalibration_Set0(controlVarSendGPSCalibrationPath)
controlVars.endOfMovementData_Set0(controlVarEndOfMovementDataPath)

    # Reset internal vars
controlVars.wipe_and_write_to_csv(longitudeCSVPath,[(0,)]) # set to 0 initially
controlVars.wipe_and_write_to_csv(latitudeCSVPath,[(0,)]) # set to 0 initially
controlVars.wipe_and_write_to_csv(longitude_for_calibrationCSVPath,[()]) # clear
controlVars.wipe_and_write_to_csv(latitude_for_calibrationCSVPath,[()]) # clear

    # remove output queue number file to reset the queue number on startup
try:
    os.remove(fileNamingNumberCSVPath)
except Exception as e:
    print("ERROR: removing csv file for output queue naming: ",e)

    # All the camera startup stuff
try:
    if cameraConnected:
        from picamera2 import Picamera2 #import module
        picam2 = Picamera2()
        video_config = picam2.create_video_configuration(main={"size": (640, 480)})
        picam2.configure(video_config)
        picam2.start() # Start the camera
except ImportError:
    print("ERROR: Camera failed to setup, cameraConnected Var set to 0.")
    cameraConnected = 0
#*******************start up opperations (end) *********************************

# Main control loop to be continuously run on the rover
while True:

    startLoopTime = time.time() #get time starting loop so we know how long to delay the loop

    # STEP 1: pull together data from sensors to one folder
    try:
        #x = int("skip")
        outputControl.copy_and_delete_folder(gpsOutputFilePath, preZipFolderPath)
        outputControl.copy_and_delete_folder(cameraOutputFilePath, preZipFolderPath)
    except:
        print("MAIN ROVER CONTROL: ERROR with file pull from Sensors - step 1")

    # this creates a new csv file in the preZip folder that has "1" for data
    # the CSV file is only added to preZip folder when the end of movement control var is 1
    try:
        if int(controlVars.showEndOfMovementData(controlVarEndOfMovementDataPath).strip()) == 1:
            controlVars.wipe_and_write_to_csv(os.path.join(parentDirectory, "FileSystem", "preZipFolder","movement_end_"+str(roverIDNumber)+".csv"), [(1,)])
            controlVars.endOfMovementData_Set0(controlVarEndOfMovementDataPath)
    except Exception as e:
        print("MAIN ROVER CONTROL: ERROR with end of movement flag - step 1: ",e)



    # STEP 2: Create output zip file
    try:
        #x = int("skip")
        outputControl.transfer_zipped_files(preZipFolderPath,outputZipFolderPath,fileNamingNumberCSVPath,roverIDNumber)
    except Exception as e2:
        print("MAIN ROVER CONTROL: ERROR with output zip - step 2: ", e)


    # STEP 3: Call sensors to make more data
    try:
        # x = int("skip")
        #NEED TO ADD ...more

        #GPS Coords
        longitudeSample = readFromActiveFile.read_from_active_file(longitudeCSVPath).strip("\n")
        latitudeSample = readFromActiveFile.read_from_active_file(latitudeCSVPath).strip("\n")
        if not(("nan" in str(longitudeSample)) or ("nan" in str(latitudeSample))):
            controlVars.wipe_and_write_to_csv(gpsOutputFilePath + "/gps_coords_" + str(roverIDNumber) + ".csv",[(latitudeSample, longitudeSample,)])

        # creates the calibration output file, only when rover is moving and send calibration is high
        if (int(controlVars.showSendGPSCalibrationControlVar(controlVarSendGPSCalibrationPath).strip()) == 1) and (int(controlVars.showControlStraight(controlVarStraightMovementPath).strip()) == 1):
            longitude_for_calibration_Sample = readFromActiveFile.read_from_active_file(longitude_for_calibrationCSVPath).strip("\n")
            latitude_for_calibration_Sample = readFromActiveFile.read_from_active_file(latitude_for_calibrationCSVPath).strip("\n")
            controlVars.wipe_and_write_to_csv(gpsOutputFilePath + "/previous_coords_" + str(roverIDNumber) + ".csv",[(latitude_for_calibration_Sample, longitude_for_calibration_Sample,)])

        #TAKE 5 IMAGES
        imageFileNamePrefix = "video_pic_"+str(roverIDNumber)
        if cameraConnected:
            capture_images(picam2,5,imageFileNamePrefix,cameraOutputFilePath)
    except Exception as e:
        print("MAIN ROVER CONTROL: ERROR sensor calls - step 3: ",e)

    # STEP 4: Call file input handling - unzip and send out
    try:
        #x = int("skip")
        inputControl.unzip_and_delete_smallest_number_file(input_folder_queue_path, unzipped_folder_path,roverIDNumber)
        # temp = 1 if there is new movement data. 0 otherwise
        temp_newData = inputControl.send_out_files_and_cleanup(unzipped_folder_path, movement_data_path, emg_stop_path,ip_address_data_path)
        if int(temp_newData) == 1:
            controlVars.newMovementData_Set1(controlVarNewMovementDataPath)
    except Exception as e:
        print("MAIN ROVER CONTROL: ERROR file input handling - step 4: ", e)

    # STEP 5: emg stop handling
    try:
        csvFileName = str("/emg_stop_" + str(roverIDNumber) + ".csv")
        tempEmgStop = emgStopHandling.read_first_entry_of_emg_stop_csv(str(emg_stop_path) + csvFileName)
        if tempEmgStop == 1:
            controlVars.emgStopSet1(controlVarEmgStopPath)
        elif tempEmgStop == 0:
            controlVars.emgStopSet0(controlVarEmgStopPath)
        else:
            print("Error with emg stop var, data is not = 0 or 1. It is: ",tempEmgStop)

    except Exception as e:
        print("MAIN ROVER CONTROL: ERROR with emergency stop write - step 5: ",e)

    # STEP 6: refresh rate
    print("END OF MAIN ROVER CONTROL LOOP...")


    # **--**
    # test stuff after cycle
        #print("nothing to test")
    # **--**

    endLoopTime = time.time()
    elapsedTime = endLoopTime - startLoopTime

    if elapsedTime < totalLoopGoalTIme:
        time.sleep(totalLoopGoalTIme - elapsedTime)

    print("LOOP TIME: ", time.time() - startLoopTime)
    print()

print("Program Done")