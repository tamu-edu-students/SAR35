# -------------------------------------------------------------
# This file is used to control the rover subsystem integration
# Specifically, the file output function
#
# Course: ECEN 404
# Team: Search and rescue
# -------------------------------------------------------------

import os
import shutil
import csv

# Functions to be used in main control

def copy_and_delete_folder(source, destination):
    """copies all files in source folder to destination folder. Then delete source files.
       Includes data corruption check."""

    # Add pre-zip folder if it does not exist
    if not os.path.exists(destination):
        os.makedirs(destination)

    # go through all the file names in the source folder
    for filename in os.listdir(source):

        # create full file paths
        fullDestination = os.path.join(destination, filename)
        fullSource = os.path.join(source, filename)

        # copy file
        shutil.copy2(fullSource, fullDestination)

        # verification and deleting
        if os.path.exists(fullSource):

            try:
                os.remove(fullSource)
            except:
                 print("File deletion error in output control")
        else:
            print("File Copy error in output control")

def file_naming(file_path):
    # if you want to restart it, change the file path name (or delete the original file_path) instead of editing the actual csv

    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)
            if data:
                last_number = int(data[-1][0])
            else:
                last_number = 0
    except FileNotFoundError:
        last_number = 0
    # uncomment the above to test functionality

    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        new_number = last_number + 1
        writer.writerow([new_number])
    # print(last_number)
    return last_number

def transfer_zipped_files(source_dir, new_dir,csvPathNamingPassthrough,roverIDNumber):
    """
    Args:
      source_dir (str): Directory where the files are initially located.
      new_dir (str): Directory where the zipped files will be moved.
    """

    # does source directory exist
    if not os.path.exists(source_dir) or not os.path.isdir(source_dir):
        print(f"'{source_dir}' does not exist.")
        return

    # is source directory empty
    if not os.listdir(source_dir):
        print(f"'{source_dir}' is empty - no files to transfer.")

    temp_dir = "temp_dir"
    os.makedirs(temp_dir, exist_ok=True) #helpful, removes error

    # Zip the files
    x = str(file_naming(csvPathNamingPassthrough))
    zip_file_name = x+"_datafile_base_"+str(roverIDNumber)+".zip"
    # print(zip_file_name)
    shutil.make_archive(os.path.join(temp_dir, zip_file_name[:-4]), 'zip', source_dir)

    # zipped file to the new directory
    shutil.move(os.path.join(temp_dir, zip_file_name), new_dir)

    # delete the original files from the source directory
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # deletes the temporary directory
    shutil.rmtree(temp_dir)