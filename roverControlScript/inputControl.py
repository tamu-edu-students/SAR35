# -------------------------------------------------------------
# ECEN 404
# Search and rescue team
#
# This file is used to control the rover subsystem integration
# Specifically, handling file input to the rover
# NOTE: nothing
# -------------------------------------------------------------

import os
import zipfile
import shutil

# unzip from input queue
def unzip_and_delete_smallest_number_file(input_folder_queue_path,unzipped_folder_path,roverIDNumber):
    files = os.listdir(input_folder_queue_path)

    target_files = [file for file in files if file.endswith('_rover_'+str(roverIDNumber)+'.zip')]

    if not target_files:
        print("No input files found.")
        return

    file_numbers = [int(file.split('_')[0]) for file in target_files]

    smallest_number_index = file_numbers.index(min(file_numbers))
    smallest_number_file = target_files[smallest_number_index]

    smallest_number_file_path = os.path.join(input_folder_queue_path, smallest_number_file)

    os.makedirs(unzipped_folder_path, exist_ok=True)

    try:
        with zipfile.ZipFile(smallest_number_file_path, 'r') as zip_ref:
            zip_ref.extractall(unzipped_folder_path)

        # will only remove if the try works and there are no exceptions caught
    except Exception as e:
        print(f"Error during extraction: {e}")
        return
        # will end function if there is error
    os.remove(smallest_number_file_path)

# Send out data files to correct directories
def send_out_files_and_cleanup(unzipped_folder_path,movement_data_path,emg_stop_path,ip_address_data_path):

    '''
    Moves files from the unzipped folder to the individual subsystem  (unzippedFromBase)

    This function was modified such that it looks for a folder or just the files (depends on the way the files were unzipped)

    RETURNS 1 IF THERE IS NEW MOVEMENT DATA
    '''

    newMovementDataFlag = 0
    folder_path = unzipped_folder_path
    folderFlag = False # set to True when there is a folder instead of individual files

    # look for folder with "rover" in it
    for folder_name in os.listdir(unzipped_folder_path):
        if "rover" in str(folder_name):
            folder_path = os.path.join(unzipped_folder_path, folder_name)
            folderFlag = True
            break
    else:
        returnFlag = True # set true if you want to return
        for i in os.listdir(folder_path):
            if ("emg" in str(i)) or ("movement" in str(i)) or ("ip" in str(i)):
                returnFlag = False
        if returnFlag:
            return newMovementDataFlag

    # list of all files in the unzipped folder (could be a sub folder or just "unzippedFromBase") -depends on unzip
    filesInUnzippedFolder = os.listdir(folder_path)
    # select the destination folder and copy the file out
    for file_name in filesInUnzippedFolder:
        file_path = os.path.join(folder_path, file_name)
        if "movement" in file_name:
            newMovementDataFlag = 1
            destination_dir = movement_data_path
        elif "emg" in file_name:
            destination_dir = emg_stop_path
        elif "ip" in file_name:
            destination_dir = ip_address_data_path
        else:
            print(f"ERROR: File {file_name} does not match expected naming.")
            continue

        # Copy file out for each file
        try:
            shutil.copy(file_path, destination_dir)
        except:
            os.replace(file_path, destination_dir)

        if folderFlag == False:
            os.remove(file_path)

    # Remove the whole directory containing the original files
    if folderFlag:
        shutil.rmtree(folder_path)
        print(f"Directory {folder_path} deleted.")

    return newMovementDataFlag


