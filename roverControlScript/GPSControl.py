# -------------------------------------------------------------
# ECEN 404
# Search and rescue team
#
# This file constantly makes the best GPS coordinates and writes to latitude and longitude csvs
# NOTE: this script needs access to the files directories (RUN IN SUDO)
# NOTE: This file should run on startup
# NOTE: its latitude, longitude
# -------------------------------------------------------------

# Variables to be updated (settings)
# -------------------------------------------------------------
samples_to_go_back_for_calibration = 2 #used for GPS algo to determine heading
    # rover needs to collect 2 times this number to get data.
    # it also needs to keep going foward a bit longer so that there is enouph time to write this data to the CSV's
lat_offset = 0
lon_offset = 0
# -------------------------------------------------------------


# imports
from scipy.stats import linregress
import numpy as np
import os
import serial
import controlVars

# File paths
currentWorkingDirectory = os.path.dirname(os.path.realpath(__file__))
parentDirectory = os.path.dirname(currentWorkingDirectory) #this is the parent directory of all files
longitudeCSVPath = os.path.join(parentDirectory, "FileSystem", "longitude.csv")
latitudeCSVPath = os.path.join(parentDirectory, "FileSystem", "latitude.csv")
longitude_for_calibrationCSVPath = os.path.join(parentDirectory, "FileSystem", "longitude_for_calibration.csv")
latitude_for_calibrationCSVPath = os.path.join(parentDirectory, "FileSystem", "latitude_for_calibration.csv")
controlVarTurnBoolPath = os.path.join(parentDirectory,"FileSystem", "controlVarTurnBool.csv")
controlVarStraightMovementPath = os.path.join(parentDirectory, "FileSystem", "controlVarStraightMovement.csv")
controlVarSendGPSCalibrationPath = os.path.join(parentDirectory, "FileSystem", "controlVarSendGPSCalibration.csv")

# --------------------------- START OF FUNCTIONS --------------------------
def linear_regression_point(coordinates,samples_to_go_back_for_calibration):
    '''give this function all the coordinates from a STRAIGHT line and get the output point (most recent and previous)'''
    if coordinates == []:
        return None, None, None, None

    # Convert the list of coordinates to NumPy array
    coordinates_array = np.array(coordinates)

    # Extract latitude and longitude values
    latitudes = coordinates_array[:, 0]
    longitudes = coordinates_array[:, 1]

    # Fit a linear regression line for latitude
    lat_slope, lat_intercept, x, y, z = linregress(range(len(latitudes)), latitudes)

    # Fit a linear regression line for longitude
    lon_slope, lon_intercept, x, y, z = linregress(range(len(longitudes)), longitudes)

    # Calculate the index of the most recent sample (last coordinate)
    most_recent_index = len(latitudes) - 1

    # Calculate the latitude of the point corresponding to the most recent sample on the line
    recent_latitude = lat_slope * most_recent_index + lat_intercept

    # Calculate the longitude of the point corresponding to the most recent sample on the line
    recent_longitude = lon_slope * most_recent_index + lon_intercept

    # Calculate the previous point to determine heading
    back_calibration_latitude = 0
    back_calibration_longitude = 0
    back_index = max(0, most_recent_index - samples_to_go_back_for_calibration)
    try:
        if (most_recent_index > (2 * samples_to_go_back_for_calibration)):
            back_calibration_latitude = lat_slope * back_index + lat_intercept
            back_calibration_longitude = lon_slope * back_index + lon_intercept
    except:
        pass

    return recent_latitude, recent_longitude, back_calibration_latitude, back_calibration_longitude

def serial_get_coordinates(current_coordinates):
    '''reads from serial port and updates coordinate list'''
    # create new coordinate list to return
    new_coordinates = current_coordinates
    new_raw_data = []

    serial_port = "/dev/serial0"  # Change this to your actual port
    baud_rate = 9600  # Change this to match your device's baud rate
    try:
        # Open the serial port
        ser = serial.Serial(serial_port, baud_rate)

        # Read data from the serial port (wait until it gets usable data)
        resetFlag = True
        while resetFlag:
            data = ser.readline().decode().strip()
            print("...waiting for data")
            if "$GPGGA" in data:
                resetFlag = False

        # Write data to new coordinates list to be returned
        new_raw_data.append(data + "\n")

    except serial.SerialException as e:
        print("Error: ", e)
    except KeyboardInterrupt:
        ser.close()
        print("Serial connection closed.")

    for i in new_raw_data:

        # Process each line of the file
        i = i.strip()  # Remove leading and trailing whitespaces

        lineElements = i.split(',')  # split each line into list

        if lineElements[0] == "$GPGGA":  # find essential data line

            # get latitude and longitude data
            latitude = float(lineElements[2][:2]) + float(lineElements[2][2:]) / 60
            if lineElements[3] == 'S':
                latitude = -latitude

            longitude = float(lineElements[4][:3]) + float(lineElements[4][3:]) / 60
            if lineElements[5] == 'W':
                longitude = -longitude

            new_coordinates.append([latitude, longitude])

    return new_coordinates


# --------------------------- END OF FUNCTIONS --------------------------


# --------------------------- MAIN SCRIPT --------------------------

stationaryCoordinates = []
movingCoordinates = []
while True:

    tempSampleControlTurnBool = int(controlVars.showControlTurnBool(controlVarTurnBoolPath).strip())
    tempSampleControlStraight = int(controlVars.showControlStraight(controlVarStraightMovementPath).strip())
    tempSampleControlGPSCalibration = int(controlVars.showSendGPSCalibrationControlVar(controlVarSendGPSCalibrationPath).strip())

    # clear movingCoordinates list
    if (tempSampleControlTurnBool == 1) and (tempSampleControlStraight == 1):
        movingCoordinates = []
        controlVars.turnOffControlTurnBool(controlVarTurnBoolPath)

    # clear stationaryCoordinates list anytime rover is moving along a path (forwards or backwards)
    if tempSampleControlStraight == 1:
        stationaryCoordinates = []

    if tempSampleControlStraight == 1: # use linear regression
        # update coordinate list with new serial data
        try:
            movingCoordinates = serial_get_coordinates(movingCoordinates)
        except Exception as e:
            print("ERROR with serial read for GPS: ", e)

        # get error corrected output point
        recent_latitude, recent_longitude, back_calibration_latitude, back_calibration_longitude = linear_regression_point(movingCoordinates,samples_to_go_back_for_calibration)

        # write output point to csv's
        try:
            controlVars.wipe_and_write_to_csv(latitudeCSVPath,[(recent_latitude + lat_offset,)])
            controlVars.wipe_and_write_to_csv(longitudeCSVPath,[(recent_longitude + lon_offset,)])
        except Exception as e:
            print("ERROR with output lat & lon write to csvs: ", e)

        try:
            if tempSampleControlGPSCalibration == 1:
                controlVars.wipe_and_write_to_csv(latitude_for_calibrationCSVPath,[(back_calibration_latitude + lat_offset,)])
                controlVars.wipe_and_write_to_csv(longitude_for_calibrationCSVPath,[(back_calibration_longitude + lon_offset,)])
        except Exception as e:
            print("ERROR with output lat & lon write to internal csvs ... for calibration data: ", e)

    elif tempSampleControlStraight == 0: #use average
        try:
            stationaryCoordinates = serial_get_coordinates(stationaryCoordinates)
        except Exception as e:
            print("ERROR with serial read for GPS: ", e)

        #extract lon and lat
        localLatitudes = [i[0] for i in stationaryCoordinates]
        localLongitudes = [i[1] for i in stationaryCoordinates]

        #avg lon and lat
        recent_latitude = float(sum(localLatitudes)/len(localLatitudes))
        recent_longitude = float(sum(localLongitudes)/len(localLongitudes))

        # write output point to csv's
        try:
            controlVars.wipe_and_write_to_csv(latitudeCSVPath, [(recent_latitude + lat_offset,)])
            controlVars.wipe_and_write_to_csv(longitudeCSVPath, [(recent_longitude + lon_offset,)])
        except Exception as e:
            print("ERROR with output lat & lon write to csvs: ", e)