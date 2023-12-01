#master control file to run on raspberry pi

import time
import gpsMain
import csv

#Functions for main Control

def write_list_to_csv(data_list,file_path):
    with open(file_path,'w',newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(data_list)

#End of functions for main Contorl

turnBool = False

gps_output_csv_path = 'gps_algorithm_output.csv'

while True:
    time.sleep(1) # cycle time

    gpsOutputList = gpsMain.mainGPS() #sample GPS
    print(gpsOutputList) #dispay GPS output
    write_list_to_csv(gpsOutputList,gps_output_csv_path) #gps data to CSV

    #if turn is TRUE **pause gps collection** and delete file data
    if turnBool == True:
        with open('straightWalkEdit.txt', 'w') as file:
            pass  # The 'with' block will truncate the file, so no specific action is needed here