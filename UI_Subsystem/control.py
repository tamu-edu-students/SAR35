import os, csv
from zipfile import ZipFile

'''

***SAR Subsystem: Base Station Control System***

Author: Senran Castro
Section: ECEN 403 - 903
Group Number: 35
Date Created: 01/22/24

Version: 1.0.3
Last Updated: 01/31/24

'''
############# VARIABLES ############
global path_out_file_list, im_file_list, gps_file_list, file_list
####################################

#Pathfinding Folder
def read_path_folder():
    global path_out_file_list
    path_out_file_list = []
    for root, direc, files in os.walk("./path_folder"): 
        for filename in files:
            filepath = os.path.join(root, filename)
            if (filepath not in path_out_file_list) and (filename == "new_path1.csv" or filename == "new_path2.csv"):
                path_out_file_list.append(filepath)
    return

#Image Recognition Folder
def read_im_rec_folder():
    global im_file_list
    im_file_list = []
    for root, direc, files in os.walk("./im_rec_folder"): 
        for filename in files:
            filepath = os.path.join(root, filename)
            if filepath not in im_file_list:
                im_file_list.append(filepath)
    return

#GPS and Movement Folder
def read_gps_folder():
    global gps_file_list
    gps_file_list = []
    for root, direc, files in os.walk("./gps_folder"): 
        for filename in files:
            filepath = os.path.join(root, filename)
            if filepath not in gps_file_list:
                gps_file_list.append(filepath)
    return

#Export the Zip File
def output_zip_file():
    global file_list
    file_list = []
    read_path_folder()
    #read_im_rec_folder()
    #read_gps_folder()
    if path_out_file_list!= []:
        for file1 in path_out_file_list:
            if file1 not in file_list: file_list.append(file1)
    '''if im_file_list!=[]:
        for file2 in im_file_list:
            if file2 not in file_list: file_list.append(file2)
    if gps_file_list!=[]:
        for file3 in gps_file_list:
            if file3 not in file_list: file_list.append(file3)'''
    #print("File list:",file_list)
    with ZipFile("bs_to_rover.zip", "w") as zip:
        for file in file_list:
            zip.write(file)
    return