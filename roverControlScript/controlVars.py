# -------------------------------------------------------------
# ECEN 404
# Search and rescue team
#
# This file contains variables used to control logic flow across multiple files
# NOTE:
# NOTE: the vars are stored in CSV for persistence
# -------------------------------------------------------------

#imports
import csv
import os


# Function to write to control var csvs
def wipe_and_write_to_csv(file_path, data):

    """
    Wipe the CSV file of all existing data and write new data to it.

    Parameters:
        file_path (str): Path to the CSV file.
        data (list of tuples): Data to be written to the CSV file.
            Each tuple represents a row in the CSV file.
    """
    try:
        # Truncate the existing CSV file to wipe its content
        open(file_path, 'w').close()

        # Write new data to the CSV file
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
    except Exception as e:
        print("Error with control vars csv writing: ",e)

# Example usage of write function##########
# file_path = 'data.csv'
# data = [
#     ('Name', 'Age', 'City'),
#     ('John', 30, 'New York'),
#     ('Alice', 25, 'Los Angeles'),
#     ('Bob', 35, 'Chicago') ]
# #########################################

#Function to read in first entry of CSV
def read_first_entry_from_csv(file_path):
    """
    Read the first data entry from a CSV file.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        str or None: The first data entry from the CSV file, or None if the file is empty.
    """
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            first_row = next(reader, None)  # Get the first row or None if the file is empty

        if first_row:
            return first_row[0]  # Return the first element of the first row
        else:
            return None
    except Exception as e:
        print("Error with control var reading csv: ",e)


# Function to delete a whole directories
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


# *************************CONTROL VAR LOGIC BELOW******************************

# ---TURN BOOL---
def turnOnControlTurnBool(controlVarTurnBoolPath):
    '''Set controlTurnBool = 1'''
    wipe_and_write_to_csv(controlVarTurnBoolPath,[(1,)])

def turnOffControlTurnBool(controlVarTurnBoolPath):
    '''set controlTurnBool = 0'''
    wipe_and_write_to_csv(controlVarTurnBoolPath,[(0,)])

def showControlTurnBool(controlVarTurnBoolPath):
    return read_first_entry_from_csv(controlVarTurnBoolPath)

# ---EMG STOP---
# 0 = stop, 1 = start

def emgStopSet0(emgStopControlBoolPath):
    wipe_and_write_to_csv(emgStopControlBoolPath, [(0,)])

def emgStopSet1(emgStopControlBoolPath):
    wipe_and_write_to_csv(emgStopControlBoolPath, [(1,)])

def showEmgStop(emgStopControlBoolPath):
    return read_first_entry_from_csv(emgStopControlBoolPath)

# ---newMovementData---
# 0 = no new data, 1 = new data

def newMovementData_Set0(filePath):
    wipe_and_write_to_csv(filePath, [(0,)])

def newMovementData_Set1(filePath):
    wipe_and_write_to_csv(filePath, [(1,)])

def showNewMovementDataControlVar(filePath):
    return read_first_entry_from_csv(filePath)


# ---Straight Movement---
# 1 = straight movement, 0 = stationary or turning
# controlled by movement algo
def turnOnControlStraight(filepath):
    '''Set straight movement = 1'''
    wipe_and_write_to_csv(filepath,[(1,)])

def turnOffControlStraight(filepath):
    '''set straight movement = 0'''
    wipe_and_write_to_csv(filepath,[(0,)])

def showControlStraight(filepath):
    return read_first_entry_from_csv(filepath)


# ---send gps calibration ---
# 0 = do not send, 1 = send data (write data to gps calibration coords csv to be sent to base station)

def sendGPSCalibration_Set0(filePath):
    wipe_and_write_to_csv(filePath, [(0,)])

def sendGPSCalibration_Set1(filePath):
    wipe_and_write_to_csv(filePath, [(1,)])

def showSendGPSCalibrationControlVar(filePath):
    return read_first_entry_from_csv(filePath)

# --- end of movement data ---
# 0 = not the end, 1 = end of movement data (meaning a movement instruction set completed all instructions)

def endOfMovementData_Set0(filePath):
    wipe_and_write_to_csv(filePath, [(0,)])

def endOfMovementData_Set1(filePath):
    wipe_and_write_to_csv(filePath, [(1,)])

def showEndOfMovementData(filePath):
    return read_first_entry_from_csv(filePath)