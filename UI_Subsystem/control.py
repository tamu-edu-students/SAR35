import os, csv, socket
from zipfile import ZipFile
from requests import get

'''

***SAR Subsystem: Base Station Control System***

Author: Senran Castro
Section: ECEN 404 - 904
Group Number: 35
Date Created: 01/22/24

Version: 1.1.3
Last Updated: 04/08/24

'''
############# VARIABLES ############
cwd = os.path.dirname(os.path.realpath(__file__))
'''Path for current working directory'''

global que_num1_in, que_num1_out, num_1, server_err, send_emg1, send_emg2
global que_num2_in, que_num2_out, num_2, send_err1, send_err2, send_movement1, send_movement2, setup_val1, setup_val2
que_num1_out = 1
que_num2_out = 1
num_1 = 1
que_num1_in = 1
que_num2_in = 1
num_2 = 1
send_emg1 = 0
send_emg2 = 0
send_err1 = 0
send_err2 = 0
server_err = 0
send_movement1 = 0
send_movement2 = 0
setup_val1 = 1
setup_val2 = 1
####################################

############ FUNCTIONS #############
#Export the Zip File
def output_zip_file(rover_number:int):
    '''
    Outputs a zip file to the output_files folder.

    @param rover_number: Specifies which rover the output file will be made for/sent to.
    '''
    global que_num1_out, que_num2_out, num_1, send_movement1, send_movement2, zip_name1, zip_name2, send_emg1, send_emg2
    if rover_number == 1:
        #check if que_num matches the saved number
        with open(os.path.join(cwd, "que_1_out.csv"), 'r') as file:
            file_read = csv.reader(file)
            for line in file_read:
                for n in line:
                    num_1 = int(n)
            if int(num_1) != que_num1_out:
                que_num1_out = int(num_1)
        #set the name of the zip to the correct name
        zip_name1 = str(que_num1_out)+"_datafile_rover_1.zip"
        #write the zip file
        if (send_movement1 or send_emg1 or (que_num1_in == 1) or (que_num1_in == 2)):
            with ZipFile(os.path.join(cwd,"output_files", zip_name1), "w") as zip:
                #send movement file if updated
                if send_movement1:
                    zip.write(os.path.join(cwd,"path_folder", "movement_data_1.csv"), arcname="movement_data_1.csv")
                    send_movement1 = 0
                #send ip address in first 2 cycles
                if (que_num1_out == 1) or (que_num1_out == 2):
                    zip.write(os.path.join(cwd, "ip_address_of_base.csv"), arcname="ip_address_of_base.csv")
                #send emg stop file
                zip.write(os.path.join(cwd, "emg_stop_1.csv"), arcname="emg_stop_1.csv")
                if (send_emg1):
                    send_emg1 = 0
        #iterate que and save to csv
        que_num1_out += 1
        with open(os.path.join(cwd, "que_1_out.csv"),'w') as file:
            file.write(str(que_num1_out))
    else:
        #check if que_num matches the saved number
        with open(os.path.join(cwd, "que_2_out.csv"), 'r') as file:
            file_read = csv.reader(file)
            for line in file_read:
                for n in line:
                    num = int(n)
            if int(num) != que_num2_out:
                que_num2_out = int(num)
        #set the name of the zip to the correct name
        zip_name2 = str(que_num2_out)+"_datafile_rover_2.zip"
        #write the zip file
        if (send_movement2 or send_emg2 or (que_num2_in == 1) or (que_num2_in == 2)):
            with ZipFile(os.path.join(cwd,"output_files", zip_name2), "w") as zip:
                #send movement file if updated
                if send_movement2:
                    zip.write(os.path.join(cwd,"path_folder", "movement_data_2.csv"), arcname="movement_data_2.csv")
                    send_movement2 = 0
                #send ip address in first 2 cycles
                if (que_num2_out == 1) or (que_num2_out == 2):
                    zip.write(os.path.join(cwd, "ip_address_of_base.csv"), arcname="ip_address_of_base.csv")
                #send emg stop file
                zip.write(os.path.join(cwd, "emg_stop_2.csv"), arcname="emg_stop_2.csv")
                if send_emg2:
                    send_emg2 = 0
        #iterate que and save to csv
        que_num2_out += 1
        with open(os.path.join(cwd, "que_2_out.csv"),'w') as file:
            file.write(str(que_num2_out))
    return

#Unpack the zip file
def unpack_zip_file(rover_number:int):
    '''
    Unpacks a zip file from the input_files folder for the specified rover.

    @param rover_number: Specifies which rover number is on the input zip file name.
    '''
    global que_num1_in, que_num2_in, num_1, num_2
    if (rover_number==1):
        #check if que_num matches the saved number
        with open(os.path.join(cwd, "que_1_in.csv"), 'r') as file:
            file_read = csv.reader(file)
            for line in file_read:
                for n in line:
                    num_1 = int(n)
            if int(num_1) != que_num1_in:
                que_num1_in = int(num_1)
        #set the name of the zip to the correct name
        zip_name = str(que_num1_in)+"_datafile_base_1.zip"
        #unpack the zip file (if it exists)
        if (os.path.exists(os.path.join(cwd,"input_files",zip_name))):
            with ZipFile(os.path.join(cwd, "input_files", zip_name),'r') as zip:
                for info in zip.infolist():
                    info.filename = os.path.basename(info.filename)
                    if ((info.filename=="rover_speed_1.csv") or (info.filename=="movement_end_1.csv")):
                        zip.extract(info, os.path.join(cwd,"gps_folder"))
                    if ((info.filename=="gps_coords_1.csv") or (info.filename=="previous_coords_1.csv")):
                        zip.extract(info, os.path.join(cwd,"gps_folder", str(que_num1_in)+"_gps_coords_1"))
                    elif info.filename.endswith(".jpg"):
                        folder_name1 = str(que_num1_in)+"_images_1"
                        zip.extract(info, os.path.join(cwd,"im_rec_folder", folder_name1))
            #iterate que and save to csv
            que_num1_in += 1
            with open(os.path.join(cwd, "que_1_in.csv"),'w') as file:
                file.write(str(que_num1_in))
            #delete unpacked zip files
            os.remove(os.path.join(cwd, "input_files", zip_name))
        else: pass#print("Input zip file '"+zip_name+"' does not exist. Retrying next cycle.")
    else:
        #check if que_num matches the saved number
        with open(os.path.join(cwd, "que_2_in.csv"), 'r') as file:
            file_read = csv.reader(file)
            for line in file_read:
                for n in line:
                    num_2 = int(n)
            if int(num_2) != que_num2_in:
                que_num2_in = int(num_2)
        #set the name of the zip to the correct name
        zip_name = str(que_num2_in)+"_datafile_base_2.zip"
        #unpack the file (if it exists)
        if (os.path.exists(os.path.join(cwd,"input_files",zip_name))):
            with ZipFile(os.path.join(cwd, "input_files", zip_name),'r') as zip:
                for info in zip.infolist():
                    info.filename = os.path.basename(info.filename)
                    if ((info.filename=="rover_speed_2.csv") or (info.filename=="movement_end_2.csv")):
                        zip.extract(info, os.path.join(cwd,"gps_folder"))
                    elif ((info.filename=="gps_coords_2.csv") or (info.filename=="previous_coords_2.csv")):
                        zip.extract(info, os.path.join(cwd,"gps_folder", str(que_num2_in)+"_gps_coords_2"))
                    elif info.filename.endswith(".jpg"):
                        folder_name2 = str(que_num2_in)+"_images_2"
                        zip.extract(info, os.path.join(cwd,"im_rec_folder", folder_name2))
            #iterate que and save to csv
            que_num2_in += 1
            with open(os.path.join(cwd, "que_2_in.csv"),'w') as file:
                file.write(str(que_num2_in))
            #delete unpacked zip files
            os.remove(os.path.join(cwd, "input_files", zip_name))
        else: pass#print("Input zip file '"+zip_name+"' does not exist. Retrying next cycle.")
    return

#Send rover file over network, MUST START AFTER RECEIVER
def send_file(i, num):
    global send_err1, send_err2, send1, send2
    #setup the server
    try:
        if num == 1:
            HOST = "192.168.137.115" #Rover 1 IP
            PORT = 5555
            FORMAT = "utf-8"
            SIZE = 1024
            BYTEORDER_LENGTH = 8
            send1 = socket.socket()
            send1.connect((HOST, PORT))
            msg = send1.recv(SIZE).decode()
            print('[*] sending server:', msg)
            send_err1 = send1.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        else:
            HOST = "192.168.137.244" #Rover 2 IP
            PORT = 5555
            FORMAT = "utf-8"
            SIZE = 1024
            BYTEORDER_LENGTH = 8
            send2 = socket.socket()
            send2.connect((HOST, PORT))
            msg = send2.recv(SIZE).decode()
            print('[*] sending server:', msg)
            send_err2 = send2.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
    except Exception as e:
        message = "ERROR SENDING FILE TO ROVER "+str(num)+": %s. \nFiles will not be sent. Please fix the error before starting movement." %e
        print(message)
        if num == 1:
            with open(os.path.join(cwd, "send_err1.txt"),'w') as file:
                file.writelines(message)
            send_err1 = 1
        else:
            with open(os.path.join(cwd, "send_err2.txt"),'w') as file:
                file.writelines(message)
            send_err2 = 1

    #start sending the files
    if ((num == 1) and (send_err1 != 1)): # and (send_emg1 or send_emg2 or send_movement1 or send_movement2)
        try:
            file_name = os.path.join(cwd, "output_files", str(i)+"_datafile_rover_1.zip")
            file_size = os.path.getsize(file_name)
            print("File Size is :", file_size, "bytes")
            file_size_in_bytes = file_size.to_bytes(BYTEORDER_LENGTH, 'big')
            
            print("Sending the file size")
            send1.send(file_size_in_bytes)
            msg = send1.recv(SIZE).decode(FORMAT)
            print(f"[SERVER]: {msg}")
                
            print("Sending the file name")
            send1.send(file_name.encode(FORMAT))
            msg = send1.recv(SIZE).decode(FORMAT)
            print(f"[SERVER]: {msg}")

            print("Sending the file data")
            with open (file_name,'rb') as f1:
                send1.send(f1.read())
            msg = send1.recv(SIZE).decode(FORMAT)
            print(f"[SERVER]: {msg}")

            os.remove(file_name)
        except Exception as e:
            file_name = os.path.join(os.getcwd(), "output_files", str(i)+"_datafile_rover_"+str(num)+".zip")
            message = ("SENDING ERROR: %s"%e, "File could not be sent. File name:"+ str(file_name))
            with open(os.path.join(cwd, "send_err1.txt"),'w') as file:
                file.writelines(message)
            send_err1 = -1
    if ((num == 2) and (send_err2 != 1)): # and (send_emg1 or send_emg2 or send_movement1 or send_movement2)
        try:
            file_name = os.path.join(cwd, "output_files", str(i)+"_datafile_rover_2.zip")
            file_size = os.path.getsize(file_name)
            print("File Size is :", file_size, "bytes")
            file_size_in_bytes = file_size.to_bytes(BYTEORDER_LENGTH, 'big')
            
            print("Sending the file size")
            send2.send(file_size_in_bytes)
            msg = send2.recv(SIZE).decode(FORMAT)
            print(f"[SERVER]: {msg}")
                
            print("Sending the file name")
            send2.send(file_name.encode(FORMAT))
            msg = send2.recv(SIZE).decode(FORMAT)
            print(f"[SERVER]: {msg}")

            print("Sending the file data")
            with open (file_name,'rb') as f1:
                send2.send(f1.read())
            msg = send2.recv(SIZE).decode(FORMAT)
            print(f"[SERVER]: {msg}")

            os.remove(file_name)
        except Exception as e:
            file_name = os.path.join(os.getcwd(), "output_files", str(i)+"_datafile_rover_"+str(num)+".zip")
            message = ("SENDING ERROR: %s"%e, "File could not be sent. File name:"+ str(file_name))
            with open(os.path.join(cwd, "send_err2.txt"),'w') as file:
                file.writelines(message)
            send_err2 = -1
    
    if num == 1: send1.close()
    else: send2.close()

def receive_files():
    global server_err, receive
    try:
        HOST = "192.168.137.1" #Base station IP
        PORT = 5555
        SIZE = 1024
        BYTEORDER_LENGTH = 8
        FORMAT = "utf-8"
        receive = socket.socket()
        receive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        receive.bind((HOST, PORT))
        receive.listen(1)
    except Exception as e:
        message = "ERROR STARTING SERVER: %s. \nFiles will not be received. Please fix the error and restart the application." %e
        print(message)
        with open(os.path.join(cwd, "server_err.txt"),'w') as file:
            file.writelines(message)
        server_err = 1
    
    while server_err == 0:
        global receive_file
        receive_file = 0
        with open(os.path.join(cwd, "receive_file.csv"), 'r') as file:
            file_read = csv.reader(file)
            for i in file_read:
                print(i)
                if i != []:
                    receive_file = int(i[0])
        if receive_file!=0:
            print("Starting server...")
            try:
                print("loop start")
                client = receive.accept()
                print(f"\033[33m[*] Listening as {HOST}:{PORT}\033[m")
                print(f"\033[32m[!] Client connected {client[1]}\033[m")

                print(f"Sending 'copy trash' msg")
                client[0].send('copy trash'.encode())

                print(f"[RECV] Receiving the file size")
                file_size_in_bytes = client[0].recv(BYTEORDER_LENGTH)
                file_size= int.from_bytes(file_size_in_bytes, 'big')
                print("File size received:", file_size, " bytes")
                client[0].send("File size received.".encode(FORMAT))

                print(f"[RECV] Receiving the filename.")
                filename = client[0].recv(SIZE).decode(FORMAT)
                print(f"[RECV] Filename received:", filename)
                client[0].send("Filename received.".encode(FORMAT))

                print(f"[RECV] Receiving the file data.")
                # Until we've received the expected amount of data, keep receiving
                packet = b""
                while len(packet) < file_size:
                    if(file_size - len(packet)) > SIZE:  # if remaining bytes are more than the defined chunk size
                        buffer = client[0].recv(SIZE)  # read SIZE bytes
                    else:
                        buffer = client[0].recv(file_size - len(packet))  # read remaining number of bytes

                    if not buffer:
                        raise Exception("Incomplete file received")
                    packet += buffer
                    
                filename_list = filename.split("/")
                filename = filename_list[-1]

                with open(os.path.join(os.getcwd(), "input_files",filename), 'wb') as f:
                    f.write(packet)
                    
                print(f"[RECV] File data received.")
                client[0].send("File data received".encode(FORMAT))
                client[0].close()
                print("loop end")
            except Exception as e:
                message = "ERROR RECEIVING FILES: %s. \nFile was not received. Restarting server." %e
                print(message)
                with open(os.path.join(cwd, "server_err.txt"),'w') as file:
                    file.writelines(message)
        else: break

    print("Ending server...")
    receive.close()

def get_ip_csv():
    local_ip = socket.gethostbyname_ex(socket.getfqdn()) #get('https://api.ipify.org').content.decode('utf8')
    with open(os.path.join(cwd, "ip_address_of_base.csv"), 'w', newline='') as file:
        write_file = csv.writer(file)
        write_file.writerow([local_ip[2][0]])

def get_queue_number(filename, num):
    global setup_val1, setup_val2
    # Extract queue number from the filename
    que = int(filename.split('_')[0])
    if num == 1:
        setup_val1 = que
    elif num == 2:
        setup_val2 = que
    return que

def get_queue(filename):
    return int(filename.split('_')[0])

def get_file_with_lowest_queue(num):
    # Get list of all files in the directory
    files = os.listdir(os.path.join(cwd, "input_files"))

    # Filter files that match the naming convention
    if num == 1:
        file_search = 'base_1'
    else:
        file_search = 'base_2'
    datafiles = [filename for filename in files if file_search in filename]

    if not datafiles:
        return ''  # No matching files found

    # Get queue numbers from all datafiles
    queue_numbers = [get_queue(filename) for filename in datafiles]

    # Find the file with the lowest queue number
    min_queue_number_index = queue_numbers.index(min(queue_numbers))
    lowest_queue_file = datafiles[min_queue_number_index]

    return lowest_queue_file
####################################