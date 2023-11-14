import tkinter as tk
from tkinter import ttk
import tkintermapview as tkmv
from PIL import Image, ImageTk, ImageFont, ImageDraw
from functools import partial
import csv
import os
import numpy as np
from geographiclib.geodesic import Geodesic
from geopy import distance

'''

***SAR Subsystem: User Interface***

Author: Senran Castro
Section: ECEN 403 - 903
Group Number: 35
Date Created: 09/01/23

'''

############ MAIN WINDOW ############
window = tk.Tk()
window.geometry('1012x610')
window.title("SAR - Base Station")
####################################

class Application(tk.Frame):
    def __init__(self, master):
        ############ FONTS LIBRARY ############
        font1 = ("Bahnschrift SemiLight Condensed", 12)
        font2 = ("Bahnschrift SemiLight Condensed", 10)
        ####################################

        ############## FRAMES ##############
        tk.Frame.__init__(self, master)
        self.grid(row=0, column=0)

        map_frame = tk.Frame(master = window, bg = '#B4ECFF', borderwidth=5)
        frame1 = tk.Frame(master=window, borderwidth=5, bg="#CFE3CC")
        frame2 = tk.Frame(master=window, relief=tk.SUNKEN, borderwidth=5)
        frame3 = tk.Frame(master = window, relief = tk.RAISED, borderwidth = 5, bg = "#E5E5AA")

        #map
        map_widget = tkmv.TkinterMapView(master = map_frame, width = 800, height = 600)
        map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        map_widget.set_position(30.6134483, -96.3428987) #Simpson Drill Field Coordinates
        map_widget.set_zoom(19)
        ####################################

        ############# VARIABLES ############
        global rover_num, rover_list, rover_icon, obstacle_icon, surv_pin_list, obstacle_list
        rover_num = 1
        rover_list = [map_widget.set_marker(0,0), map_widget.set_marker(0,1), map_widget.set_marker(1,0)]
        rover_icon = ImageTk.PhotoImage(Image.open("./rover_icon.png").resize((50, 50)))
        surv_pin_list = []
        obstacle_list = []
        obstacle_icon = ImageTk.PhotoImage(Image.open("./obstacle_icon.png").resize((50,50)))

        global waypoint_list1, position_list1, pos_list_copy1, wayp_index1, delete_path1
        global waypoint_list2, position_list2, pos_list_copy2, wayp_index2, delete_path2
        waypoint_list1 = []
        position_list1 = []
        pos_list_copy1 = []
        wayp_index1 = 0
        delete_path1 = 0
        waypoint_list2 = []
        position_list2 = []
        pos_list_copy2 = []
        wayp_index2 = 0
        delete_path2 = 0

        global new_path1, made_path1, mover_index1, init1, made_file_path1, send_path_csv1, manual_move1, path_rover_select
        global new_path2, made_path2, mover_index2, init2, made_file_path2, send_path_csv2, manual_move2
        new_path1 = map_widget.set_path([(0,0), (1,0)])
        new_path2 = map_widget.set_path([(0,0), (1,0)])
        made_path1 = 0
        made_file_path1 = 0
        mover_index1 = 0
        made_path2 = 0
        made_file_path2 = 0
        mover_index2 = 0
        manual_move1 = 0
        manual_move2 = 0
        init1 = 0
        init2 = 0
        send_path_csv1 = 0
        send_path_csv2 = 0
        path_rover_select = 0

        global path_list1, path_list2, path_index1, path_index2, file_path_change1, file_path_change2
        global create_path, place_obstacle, place_survivor, clear_survivors, calc_distance,choose_time_text
        path_list1 = []
        path_list2 = []
        path_index1 = 0
        path_index2 = 0
        file_path_change1 = 0
        file_path_change2 = 0

        global i, reset, move_call1, move_call2, time_to_dest1, time_to_dest2
        i=0
        reset = 0
        move_call1 = 0
        move_call2 = 0

        global age_text, gender_text, status_text, survivor_num
        age_text = "???"
        gender_text = "???"
        status_text = "???"
        survivor_num = 0
        ####################################

        ############ FUNCTIONS ############
        #rover selection event
        def select_rover(num):
            global rover_num
            rover_num = num
            rover_selection.config(text="Current Rover Selected: "+str(rover_num))
            if (num == 1):
                rover_1_select_button.config(bg = "grey", fg = "black", text="Rover 1 Selected")
                rover_2_select_button.config(bg="#1A19F3", fg="#D9DDF8", text="Rover 2 Select")
            elif (num==2):
                rover_1_select_button.config(bg="#1A19F3", fg="#D9DDF8", text="Rover 1 Select")
                rover_2_select_button.config(bg = "grey", fg = "black", text="Rover 2 Selected")

        #time to destination text event
        def choose_time_text():
            if rover_num==1:
                text = "Time to destination: "+ str(time1)
            elif rover_num == 2:
                text = "Time to destination: "+str(time2)
            return text

        #survivor pin events
        def place_survivor(coordinates):
            global survivor_num
            survivor_num += 1
            survivor_img = create_surv_image()
            surv_pin_list.append(map_widget.set_marker(coordinates[0], coordinates[1], text= "Survivor "+str(survivor_num), image=survivor_img, command=click_pin))
        
        def clear_survivors():
            global surv_pin_list, survivor_num
            for i in surv_pin_list:
                i.delete()
                del i
            surv_pin_list = []
            survivor_num = 0

        def create_surv_image():
            image_pil = Image.open('./blank_surv_img.jpg')
            image_pil = image_pil.resize((290, 170))

            #add survivor picture from image recognition files
            surv_pic = Image.open('./surv_pic'+str(survivor_num)+'.jpg') #test sample for now
            surv_pic = surv_pic.resize((124, 170))
            offset = (0, 0)
            image_pil.paste(surv_pic, offset)

            im_draw = ImageDraw.Draw(image_pil) #make able to add text
            im_font = ImageFont.truetype("c:\Windows\Fonts\Bahnschrift.ttf", 12)

            #add text (sample for now)
            im_draw.text((148,12), age_text, font=im_font, fill="#2C2C2C") #age
            im_draw.text((162,44), gender_text, font=im_font, fill="#2C2C2C") #gender
            im_draw.text((173,75), status_text, font=im_font, fill="#2C2C2C") #condition
            
            image_pil.save("./surv_img"+str(survivor_num)+".jpg")
            surv_image = ImageTk.PhotoImage(image_pil)
            return surv_image

        #obstacle pin events
        def place_obstacle():
            #clear old list
            for i in obstacle_list:
                i.delete()
                del i
            #update new list from file
            with open("./obstacle_locations.csv", mode = "r") as obst_file:
                obstacle_loc_file = csv.reader(obst_file, delimiter=",")
                for i in obstacle_loc_file:
                    coordinates = []
                    for j in i:
                        if (j == []): continue
                        else: 
                            coordinates.append(float(j))
                    if (len(coordinates) == 2):
                        obstacle_list.append(map_widget.set_marker(coordinates[0], coordinates[1], icon=obstacle_icon))

        #map left click events
        def click_pin(pin):
            if (pin.image_hidden==False):
                pin.hide_image(True)
            else:
                pin.hide_image(False)

        #map right click events
        def add_pin_event(coordinates):
            global new_pin
            new_pin = map_widget.set_marker(coordinates[0], coordinates[1])
            check_rover_num()

        def add_waypoint(coordinates):
            global waypoint_list1, position_list1, pos_list_copy1, wayp_index1, init1, manual_move1, new_path1, rover_list
            global waypoint_list2, position_list2, pos_list_copy2, wayp_index2, init2, manual_move2, new_path2, rover_num
            print("adding waypoint")
            #check if list 1 initialized yet
            if (init1==0):
                waypoint_list1.append(rover_list[1])
                position_list1.append(rover_list[1].position)
                pos_list_copy1 = position_list1.copy()
                init1 = 1
            #check if list 2 initialized yet
            if (init2==0):
                waypoint_list2.append(rover_list[2])
                position_list2.append(rover_list[2].position)
                pos_list_copy2 = position_list2.copy()
                init2 = 1
            #reset the first position if the rover is moving
            if (move_call1 and wayp_index1):
                #waypoint_list1[0].set_position(rover_list[1].position[0], rover_list[1].position[1])
                position_list1[0] = rover_list[1].position
                pos_list_copy1 = position_list1.copy()
            if (move_call2 and wayp_index2):
                #waypoint_list2[0].set_position(rover_list[2].position[0], rover_list[2].position[1])
                position_list2[0] = rover_list[2].position
                pos_list_copy2 = position_list2.copy()
            ### Add waypoints ###
            #add new point for list 1
            if (rover_num == 1):
                delete_path(1)
                if (manual_move1 != 1): #set movement to manual
                    manual_move1 = 1
                wayp_index1 += 1
                waypoint_list1.append(rover_list[1])
                position_list1.append(coordinates)
                waypoint_list1[wayp_index1] = map_widget.set_marker(coordinates[0], coordinates[1], marker_color_circle = '#73E992', marker_color_outside = "#26D354")
                pos_list_copy1 = position_list1.copy()
                create_path() #auto update path
            #add new point for list 2
            if (rover_num == 2):
                delete_path(2)
                if (manual_move2 != 1): #set movement to manual
                    manual_move2 = 1
                wayp_index2 += 1
                waypoint_list2.append(rover_list[2])
                position_list2.append(coordinates)
                waypoint_list2[wayp_index2] = map_widget.set_marker(coordinates[0], coordinates[1], marker_color_circle = '#75B7F0', marker_color_outside = "#2683D3")
                pos_list_copy2 = position_list2.copy()
                create_path() #auto update path

        #sidebar events
        def delete_path(num):
            global new_path1, made_path1, made_file_path1
            global new_path2, made_path2, made_file_path2
            if (num == 1):#(made_path1==1 and rover_num==1 and len(pos_list_copy1)>=2) or (len(pos_list_copy1)>=2 and made_file_path1==1) or delete_path1):
                new_path1.set_position_list([(0,0), (1,0)])
                made_path1 = 0
                if (made_file_path1 and wayp_index1):
                    made_file_path1 = 0
                print("old path 1 deleted")
            if (num == 2):#(made_path2==1 and rover_num==2 and len(pos_list_copy2)>=2) or (made_file_path2==1 and len(pos_list_copy2)>=2) or delete_path2):
                new_path2.set_position_list([(0,0), (1,0)])
                made_path2 = 0
                if (made_file_path2 and wayp_index2):
                    made_file_path2 = 0
                print("old path 2 deleted")

        def create_path():
            global new_path1, made_path1, waypoint_list1, wayp_index1, path_list1, send_path_csv1, made_file_path1, file_path_change1
            global new_path2, made_path2, waypoint_list2, wayp_index2, path_list2, send_path_csv2, made_file_path2, file_path_change2, path_file_change
            print("creating new paths...")
            #check for file change
            if (path_file_change or setup == 1):
                print("file change found")
                call_path_creation() #takes values from pathfinding system for path creation
            else:
                print("no file change found")
                if ((made_file_path1 == 0) or wayp_index1!=0):
                    path_list1 = pos_list_copy1
                if ((made_file_path2 == 0) or wayp_index2!=0):
                    path_list2 = pos_list_copy2
            #create new paths
            if (rover_num == 1 or file_path_change1): # or (path_file_change != 1 and made_file_path1)
                print("rover 1")
                if (len(path_list1) < 2):
                    print("skipped")
                else:
                    #set new path
                    new_path1.set_position_list(path_list1)
                    made_path1 = 1
                    #write the path to the csv
                    with open('new_path1.csv', mode='w')as file:
                        pin_file = csv.writer(file)
                        for i in new_path1.position_list:
                            written = [1, i[0], i[1]]
                            pin_file.writerow(written)
                    send_path_csv1 = 1
                    #set file change variables
                    if (file_path_change1):
                        made_file_path1 = 1
                        file_path_change1 = 0
                    #make movement path
                    make_move_path(1)
                    print("made path 1")
            if (rover_num ==2 or file_path_change2): # or (path_file_change != 1 and made_file_path2)
                print("rover 2")
                if (len(path_list2) < 2):
                    print("skipped")
                else:
                    #set new path
                    new_path2.set_position_list(path_list2)
                    made_path2 = 1
                    #write the path to the csv
                    with open('new_path2.csv', mode='w')as file:
                        pin_file = csv.writer(file)
                        for i in new_path2.position_list:
                            written = [2, i[0], i[1]]
                            pin_file.writerow(written)
                    send_path_csv2 = 1
                    #set file change variables
                    if (file_path_change2):
                        made_file_path2 = 1
                        file_path_change2 = 0
                    #make movement path
                    make_move_path(2)
                    print("made path 2")
            #reset the file changed indicator
            if (path_file_change): 
                path_file_change = 0

        def call_path_creation():
            global path_list1, path_list2, file_path_change1, file_path_change2
            path_temp_list1 = [rover_list[1].position]
            path_temp_list2 = [rover_list[2].position]
            with open('test_path.csv', mode='r') as file: #file name will be from pathfinding system
                pathfinding_path_file = csv.reader(file, delimiter=",")
                for i in pathfinding_path_file:
                    j_counter = 0
                    j_list1 = []
                    j_list2 = []
                    for j in i:
                        if (j != []):
                            j = float(j)
                        else:
                            continue
                        if (j==1 or j==2):
                            rover_num = j
                            j_counter += 1
                        elif (j > 0):
                            if (rover_num == 1):
                                j_list1.append(j)
                            else:
                                j_list2.append(j)
                        else:
                            if (rover_num == 1):
                                j_list1.append(j)
                                if (j_list1[1] != rover_list[1].position[1]):
                                    path_temp_list1.append(j_list1)
                            else:
                                j_list2.append(j)
                                path_temp_list2.append(j_list2)
            if (len(path_temp_list1) > 1):
                file_path_change1 = 1
                clear_wayp(1)
                path_list1 = path_temp_list1.copy()
                #print("Path list 1:", path_list1, "\nPosition list copy 1:", pos_list_copy1)
            if (len(path_temp_list2) > 1):
                file_path_change2 = 1
                clear_wayp(2)
                path_list2 = path_temp_list2.copy()
                #print("Path list 2:", path_list2, "\nPosition list copy 2:", pos_list_copy2)

        def delete_wayp():
            global wayp_index1, waypoint_list1, delete_path1, pos_list_copy1, manual_move1, rover_num
            global wayp_index2, waypoint_list2, delete_path2, pos_list_copy2, manual_move2
            if (rover_num==1 and wayp_index1):
                delete_path(1)
                waypoint_list1[wayp_index1].delete()
                del waypoint_list1[wayp_index1]
                del position_list1[wayp_index1]
                pos_list_copy1 = position_list1.copy()
                wayp_index1 -= 1
                if (wayp_index1 == 0): #stop manual movement
                    manual_move1 = 0
                #delete_path1 = 1
                create_path()
                #delete_path1 = 0
            elif (rover_num==2 and wayp_index2):
                delete_path(2)
                waypoint_list2[wayp_index2].delete()
                del waypoint_list2[wayp_index2]
                del position_list2[wayp_index2]
                pos_list_copy2 = position_list2.copy()
                wayp_index2 -= 1
                if (wayp_index2 == 0): #stop manual movement
                    manual_move2 = 0
                #delete_path2 = 1
                create_path()
                #delete_path2 = 0

        def clear_wayp(num):
            global waypoint_list1, position_list1, pos_list_copy1, init1, wayp_index1, new_path1, manual_move1
            global waypoint_list2, position_list2, pos_list_copy2, init2, wayp_index2, new_path2, manual_move2, rover_num
            if ((num == 1) and wayp_index1):
                print("clearing waypoints")
                delete_path(1) #clear the old path
                while (wayp_index1 >= 1):
                    waypoint_list1[wayp_index1].delete()
                    del waypoint_list1[wayp_index1]
                    del position_list1[wayp_index1]
                    pos_list_copy1 = position_list1.copy()
                    wayp_index1 -= 1
                manual_move1 = 0
            elif ((num == 2) and wayp_index2):
                print("clearing waypoints")
                delete_path(2) #clear the old path
                while (wayp_index2 >= 1):
                    waypoint_list2[wayp_index2].delete()
                    del waypoint_list2[wayp_index2]
                    del position_list2[wayp_index2]
                    pos_list_copy2 = position_list2.copy()
                    wayp_index2 -= 1
                manual_move2 = 0

        def pick_video():
            if (rover_num == 1): self.open_vid1()
            else: self.open_vid2()

        #rover pin events
        ''' #rover pos set
        def rover_pos_set(num, coordinates):
            global rover_list, position_list1, position_list2, wayp_index1, wayp_index2, mover_index1, mover_index2
            rover_list[num].set_position(coordinates[0], coordinates[1])
            if (num == 1):
                position_list1[0] = rover_list[1].position
                if (wayp_index1 != 0):
                    create_path()
            else:
                position_list2[0] = rover_list[2].position
                if (wayp_index2 != 0):
                    create_path()
        '''

        def check_rover_num():
            global new_pin, rover_num, reset, path_rover_select

            #ADD CALL FOR PATHFINDING
            #test selection for now
            path_rover_select = 1

            #check if needs to account for original dif from calculation
            if ((rover_num==2 and path_rover_select==1) or (rover_num==1 and path_rover_select==2)):
                reset = 1
            #set selection based on calculation
            rover_num = path_rover_select

            #delete old pin and place correct one
            pos = new_pin.position
            add_waypoint(pos)
            new_pin.delete()
            
            #reset if original different from calculated
            if (reset and rover_num==1):
                rover_num = 2
                reset = 0
            elif (reset and rover_num==2):
                rover_num = 1
                reset = 0

        #movement for rover
        def start_move():
            global move_call1, move_call2
            if (rover_num == 1):
                move_call1 = 1
            else:
                move_call2 = 1
        
        def stop_move():
            global move_call1, move_call2
            if (rover_num == 1):
                move_call1 = 0
            else:
                move_call2 = 0
        
        def calc_distance(coordinates1, coordinates2):
            dist = distance.distance(coordinates1, coordinates2).miles
            return dist
        ####################################

        ############ WIDGETS ############
        ## Testing ##
        #rover pin
        rover_list[1] = map_widget.set_marker(30.6135706, -96.3435505, icon=rover_icon, text="Rover 1")
        rover_list[2] = map_widget.set_marker(30.6130420, -96.3432125, icon=rover_icon, text="Rover 2")
        #############

        #map commands
        new_pin_label = map_widget.add_right_click_menu_command(label="Add New Waypoint (Rover Automatically Selected)", command=add_pin_event, pass_coords=True)
        waypoint_label = map_widget.add_right_click_menu_command(label= "Add New Waypoint Manually (For Currently Selected Rover)", command=add_waypoint, pass_coords=True)

        ### SIDE BAR ###
        survivor_count = tk.Label(master=frame1, text="Number of Survivors Found: "+str(survivor_num), font = font1, bg="#CFE3CC")
        rover_selection = tk.Label(master=frame2, text="Current Rover Selected: "+str(rover_num), font = font1)
        time_to_dest1 = tk.Label(master = frame2, text = "Rover 1 Time to destination: \n\tNot calculated",font = font1)
        time_to_dest2 = tk.Label(master = frame2, text = "Rover 2 Time to destination: \n\tNot calculated",font = font1)

        #buttons
        rover_1_select_button = tk.Button(master=frame2, font=font2, width=14, height=2, bg = "grey", fg = "black", text="Rover 1 Selected", command=lambda: select_rover(1))
        rover_2_select_button = tk.Button(master=frame2, font=font2, width=14, height=2, bg="#1A19F3", fg="#D9DDF8", text="Rover 2 Select", command=lambda: select_rover(2))
        #make_path_button = tk.Button(master=frame2, text = "Create Path", command = create_path)
        delete_wayp_button = tk.Button(master=frame2, text = "Delete Last \nWaypoint", command = delete_wayp)
        clear_wayp_button = tk.Button(master=frame2, text = "Clear Waypoints", command = lambda : clear_wayp(rover_num))
        start_move_button = tk.Button(master=frame2, text = "Start Movement", command = start_move)
        stop_move_button = tk.Button(master=frame2, text = "Stop Movement", command = stop_move)
        video_feed_button = tk.Button(master = frame2, text= "Show Video Feed", command = pick_video)
        #test_move_button = tk.Button(master=frame2, text = "Test Move", command = test_movement)
        ################
        ####################################

        ############# PACKING #############
        map_widget.pack()
        survivor_count.pack()

        #side bar grid
        rover_selection.grid(row=0,column=0,columnspan=2, sticky="w")
        rover_1_select_button.grid(row=1,column=0)
        rover_2_select_button.grid(row=1,column=1)
        #make_path_button.grid(row=3,column=0)
        delete_wayp_button.grid(row=3,column=0)
        start_move_button.grid(row=2,column=0)
        stop_move_button.grid(row=2,column=1)
        clear_wayp_button.grid(row=3, column=1)
        video_feed_button.grid(row=4, column=0)
        time_to_dest1.grid(row=5, column=0, columnspan=2, sticky='w')
        time_to_dest2.grid(row=6, column=0, columnspan=2, sticky='w')
        frame2.columnconfigure(0, weight=0)
        frame2.columnconfigure(1, weight=0)

        #window grid
        map_frame.grid(row=0, column=0, rowspan=2, sticky="w")
        frame1.grid(row=0,column=1,sticky="new")
        frame2.grid(row=1, column=1, sticky="nsew")
        ####################################
        
        self.reload()
    pass

    def open_vid1(self):
        global vid_window1
        vid_window1 = Window(self)
        vid_window1.grab_set()
    pass

    def open_vid2(self):
            global vid_window2
            vid_window2 = Window(self)
            vid_window2.grab_set()
    pass

    def reload(self):
        # Rover speed = 0.5 mph = 0.22352 meter/s
        ############ VARIABLES ############
        global n1, n2, load_counter, path_file_change, read_path_file, read_obst_file, setup, initial1, initial2, initial3, time1, time2
        global made_move_path1, made_move_path2, move_path1, move_path2, frequency, step_dist1, step_dist2, make_move_path, rov_speed1, rov_speed2
        
        #initialize variables if not already
        if 'n1' not in globals():
            n1 = 0
        if 'n2' not in globals():
            n2 = 0
        if 'load_counter' not in globals():
            load_counter = 0
        if 'path_file_change' not in globals():
            path_file_change = 0
        if 'setup' not in globals():
            setup = 1
        if 'made_move_path1' not in globals():
            made_move_path1 = 0
        if 'made_move_path2' not in globals():
            made_move_path2 = 0
        if 'rov_speed1' not in globals():
            rov_speed1 = 0.00138888889 #default speed parameter (miles per sec)
        if 'rov_speed2' not in globals():
            rov_speed2 = 0.00138888889 #default speed parameter (miles per sec)
        if 'frequency' not in globals():
            frequency = 1000
        
        step_dist1 = rov_speed1 / (frequency / 100) #distance traveled every reload (in miles)
        step_dist2 = rov_speed2 / (frequency / 100) #distance traveled every reload (in miles)
        ###################################

        ############ FUNCTIONS ############
        def split_coordinates(coord1, coord2, dist):
            geod = Geodesic.WGS84
            inv = geod.Inverse(coord1[0], coord1[1], coord2[0], coord2[1])
            azi1 = inv['azi1']
            dist = dist * 1609.344 #convert to meters
            direction = geod.Direct(coord1[0], coord1[1], azi1, dist)
            return (direction['lat2'], direction['lon2'])
        
        def calc_time(): #will be updated once rover moves based on setting position
            global time1, time2
            if 'move_path1' in globals():
                print("calculating time 1")
                path1 = move_path1[mover_index1:-1]
                time1 = (len(path1) * step_dist1 * 10) / (rov_speed1)
                time_to_dest1.config(text="Rover 1 Time to destination: \n\t"+str(round(time1, 5))+" sec")
            if 'move_path2' in globals():
                print("calculating time 2")
                path2 = move_path2[mover_index2:-1]
                time2 = (len(path2) * step_dist2 * 10) / (rov_speed2)
                time_to_dest2.config(text="Rover 2 Time to destination: \n\t"+str(round(time2, 5))+" sec")

        def make_move_path(num):
            global made_move_path1, made_move_path2, move_path1, move_path2
            if (num == 1):
                print("making movement path 1...")
                #create movement points
                i = 0
                distance_list1 = []
                move_path1 = [new_path1.position_list[0]]
                #make the list of distances between points
                while (i+1 < len(new_path1.position_list)):
                    distance_list1.append(calc_distance(new_path1.position_list[i], new_path1.position_list[i+1]))
                    i += 1
                #split path into movement distances and fill movement path
                i = 0
                while (i+1 < len(new_path1.position_list)):
                    for j in distance_list1:
                        step_num = j / step_dist1 #divide the distance into number of steps needed
                        k = 0
                        coord_start = (float(new_path1.position_list[i][0]), float(new_path1.position_list[i][1]))
                        while k <= step_num:
                            if (coord_start != new_path1.position_list[i+1]):
                                move_path1.append(split_coordinates(coord_start, (float(new_path1.position_list[i+1][0]), float(new_path1.position_list[i+1][1])), step_dist1))
                                coord_start = move_path1[-1]
                                k += 1
                        move_path1.append(new_path1.position_list[i+1])
                        i += 1
                made_move_path1 = 1
                print("movement path 1 made")
                calc_time()
            else:
                print("making movement path 2...")
                #create movement points
                i = 0
                distance_list2 = []
                move_path2 = [new_path2.position_list[0]]
                #make the list of distances between points
                while (i+1 < len(new_path2.position_list)):
                    distance_list2.append(calc_distance(new_path2.position_list[i], new_path2.position_list[i+1]))
                    i += 1
                #split path into movement distances and fill movement path
                i = 0
                while (i+1 < len(new_path2.position_list)):
                    for j in distance_list2:
                        step_num = j / step_dist2 #divide the distance into number of steps needed
                        k = 0
                        coord_start = (float(new_path2.position_list[i][0]), float(new_path2.position_list[i][1]))
                        while k <= int(step_num):
                            if (coord_start != new_path2.position_list[i+1]):
                                move_path2.append(split_coordinates(coord_start, (float(new_path2.position_list[i+1][0]), float(new_path2.position_list[i+1][1])), step_dist2))
                                coord_start = move_path2[-1]
                                k += 1
                        move_path2.append(new_path2.position_list[i+1])
                        i += 1
                made_move_path2 = 1
                print("movement path 2 made")
                calc_time()

        def update_rov_loc(num):
            if (num):
                with open("./rover_locations.csv", mode = "w") as rov_file:
                    rov_loc_file = csv.writer(rov_file)
                    if (num==1):
                        for i in rover_list[1].position:
                            written = [1, i[0], i[1]]
                            rov_loc_file.writerow(written)
                    elif (num==2):
                        for i in rover_list[2].position:
                            written = [2, i[0], i[1]]
                            rov_loc_file.writerow(written)
            else:
                #read location file
                with open("./rover_locations.csv", mode = "r") as rov_file:
                    rover_loc_file = csv.reader(rov_file, delimiter=",")
                    for i in rover_loc_file:
                        j_counter = 0
                        j_list1 = []
                        j_list2 = []
                        for j in i:
                            if (j != []):
                                j = float(j)
                            else:
                                continue
                            if (j==1 or j==2):
                                if ((rover_num != j) and (reset != 1)):
                                    reset = 1
                                    temp_rover_num = rover_num
                                rover_num = j
                                j_counter += 1
                            elif (j > 0):
                                if (rover_num == 1):
                                    j_list1.append(j)
                                else:
                                    j_list2.append(j)
                            else:
                                if (rover_num == 1):
                                    j_list1.append(j)
                                    rover_list[1].set_position(j_list1[0][0], j_list1[0][1])
                                else:
                                    j_list2.append(j)
                                    rover_list[2].set_position(j_list2[0][0], j_list2[0][1])
                #reset rover num if necessary
                if reset:
                    if (temp_rover_num == 2):
                        rover_num = 1
                    elif (temp_rover_num == 1):
                        rover_num = 2

        def move(index1, index2):
            global mover_index1, mover_index2, move_path1, move_path2
            if (move_call1):
                #make the movement path if not done already
                if (made_move_path1 != 1 and (made_path1 or made_file_path1)):
                    make_move_path(1)
                if (manual_move1):
                    #start manual movement
                    print("moving 1 manually")
                    # TEST MOVEMENT FROM TEST PATHS
                    # IN REAL INSTANCE MOVEMENT WILL SIMPLY BE SET BY ROVER LOCATION
                    index1 = mover_index1
                    if (mover_index1+1<=len(move_path1) and made_path1):
                        rover_list[1].set_position(move_path1[mover_index1][0], move_path1[mover_index1][1])
                        mover_index1 += 1
                        index1 = mover_index1
                    calc_time()
                elif (made_file_path1):
                    print("moving 1 automatically")
                    #update_rov_loc() <-- real code for future integration
                    #TEST MOVEMENT
                    index1 = mover_index1
                    if (mover_index1+1<=len(move_path1) and made_file_path1):
                        rover_list[1].set_position(move_path1[mover_index1][0], move_path1[mover_index1][1])
                        mover_index1 += 1
                        index1 = mover_index1
                    calc_time()
            if (move_call2):
                #make the movement path if not done already
                if (made_move_path2 != 1 and (made_path2 or made_file_path2)):
                    make_move_path(2)
                if (manual_move2):
                    #start manual movement
                    print("moving 2 manually")
                    # TEST MOVEMENT FROM TEST PATHS
                    # IN REAL INSTANCE MOVEMENT WILL SIMPLY BE SET BY ROVER LOCATION
                    index2 = mover_index2
                    if (mover_index2+1<=len(move_path2) and made_path2):
                        rover_list[2].set_position(move_path2[mover_index2][0], move_path2[mover_index2][1])
                        mover_index2 += 1
                        index2 = mover_index2
                    calc_time()
                elif (made_file_path2):
                    print("moving 2 automatically")
                    #update_rov_loc() <-- real code for future integration
                    #TEST MOVEMENT
                    index2 = mover_index2
                    if (mover_index2+1<=len(move_path2) and made_file_path2):
                        rover_list[2].set_position(move_path2[mover_index2][0], move_path2[mover_index2][1])
                        mover_index2 += 1
                        index2 = mover_index2
                    calc_time()
            return index1, index2
        
        def read_path_file():
            with open("test_path.csv", "r") as file:
                read_file = file.readlines()
                return read_file
        
        def read_obst_file():
            with open("obstacle_locations.csv") as file:
                read_file = file.readlines()
                return read_file
        
        def read_surv_loc_file():
            with open("surv_locations.csv") as file:
                read_file = file.readlines()
                return read_file

        def process_surv_loc_file():
            if (surv_pin_list != []):
                clear_survivors()
            with open("surv_locations.csv") as file:
                file = csv.reader(file, delimiter=",")
                for i in file:
                    coordinates = []
                    for j in i:
                        if (j == []): continue
                        else: coordinates.append(float(j))
                    if (len(coordinates) == 2):
                        place_survivor(coordinates)
        ###################################

        #call move
        if (move_call1 or move_call2):
            n1, n2 = move(n1, n2)

        #initial setup
        if (setup == 1):
            with open("test_path.csv", mode='w') as file:
                test_file = csv.writer(file)
                alternate_list = [[1,30.6135706,-96.3435505],[1,30.6136630,-96.3431937],[1,30.6138546,-96.3430838]]
                test_file.writerows(alternate_list)
            path_file_change = 1
            create_path()
            place_obstacle()
            process_surv_loc_file()
            initial1 = read_path_file()
            initial2 = read_obst_file()
            initial3 = read_surv_loc_file()
            setup = 0
        
        #test change the file
        if (load_counter == 8):
            with open("test_path.csv", mode='w') as file:
                test_file = csv.writer(file)
                row_list = [[2,30.613042,-96.3432125],[2,30.613166678512876,-96.34296307301636],[2,30.613353656804726,-96.34263852572556],[2,30.613559101672045,-96.3424293134224],[2,30.6140162,-96.3427217]]
                test_file.writerows(row_list)  
        if (load_counter == 15):
            with open("test_path.csv", mode='w') as file:
                test_file = csv.writer(file)
                alternate_list = [[1,rover_list[1].position[0],rover_list[1].position[1]],[1,30.6136630,-96.3431937],[1,30.6138546,-96.3430838]]
                test_file.writerows(alternate_list)

        #check if file changed 
        current1 = read_path_file()
        current2 = read_obst_file()
        current3 = read_surv_loc_file()
        if initial1 != current1:
            print("paths changed")
            path_file_change = 1
            initial1 = current1
            create_path()
        if initial2 != current2:
            print("obstacles changed")
            place_obstacle()
            initial2 = current2
        if (initial3 != current3):
            print("survivor locations changed")
            process_surv_loc_file()
            initial3 = current3

        #test printing
        print("loaded")

        #reload the system
        load_counter += 1
        self.after(frequency, self.reload)
    pass

class Window(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry("310x190")
        self.title("Rover "+str(rover_num)+" Video Feed")

        ############ VARIABLES ############
        global feed_canvas1, feed_canvas2, vid_window1, vid_window2
        ###################################

        ############# WIDGETS #############
        feed_canvas1 = tk.Canvas(master=self, width = 300, height = 180, bg = '#B4ECFF')
        feed_canvas2 = tk.Canvas(master=self, width = 300, height = 180, bg = '#B4ECFF')
        ###################################

        ############# PACKING #############
        if (rover_num == 1): feed_canvas1.pack(anchor=tk.CENTER, expand=True)
        else: feed_canvas2.pack(anchor=tk.CENTER, expand=True)
        ###################################
        
        self.reload2()
    pass

    def reload2(self):
        ############ VARIABLES ############ 
        global feed_canvas1, feed_canvas2, vid_image1, vid_image2, feed_image1, feed_image2
        global initial_1, initial_2, reload_counter, setup1, setup2

        if 'reload_counter' not in globals():
            reload_counter = 0
        if 'setup1' not in globals():
            setup1 = 0
        if 'setup2' not in globals():
            setup2 = 0
        if 'initial_1' not in globals():
            initial_1 = os.path.getmtime("./video_pic1.jpg")
        if 'initial_2' not in globals():
            initial_2 = os.path.getmtime("./video_pic2.jpg")
        ###################################

        current_1 = os.path.getmtime("./video_pic1.jpg")
        current_2 = os.path.getmtime("./video_pic2.jpg")

        if (rover_num==1):
            #setup initial picture
            if (setup1==0):
                img_pil1 = Image.open("video_pic1.jpg")
                img_pil1 = img_pil1.resize((290,170))
                vid_image1 = ImageTk.PhotoImage(img_pil1)
                feed_image1 = feed_canvas1.create_image(7,7,anchor=tk.NW,image=vid_image1)
                setup1 = 1
            #check if image changed and reload it
            if (initial_1 != current_1):
                feed_canvas1.delete(feed_image1)
                img_pil1 = Image.open("video_pic1.jpg")
                img_pil1 = img_pil1.resize((290,170))
                vid_image1 = ImageTk.PhotoImage(img_pil1)
                feed_image1 = feed_canvas1.create_image(7,7,anchor=tk.NW,image=vid_image1)
                initial_1 = current_1
        else:
            #setup initial picture
            if (setup2==0):
                img_pil2 = Image.open("video_pic2.jpg")
                img_pil2 = img_pil2.resize((290,170))
                vid_image2 = ImageTk.PhotoImage(img_pil2)
                feed_image2 = feed_canvas2.create_image(7,7,anchor=tk.NW,image=vid_image2)
                setup2 = 1
            #check if image changed and reload it
            if (initial_2 != current_2):
                feed_canvas2.delete(feed_image2)
                img_pil2 = Image.open("video_pic2.jpg")
                img_pil2 = img_pil2.resize((290,170))
                vid_image2 = ImageTk.PhotoImage(img_pil2)
                feed_image2 = feed_canvas2.create_image(7,7,anchor=tk.NW,image=vid_image2)
                initial_2 = current_2

        #test change the image
        os.rename("./video_pic1.jpg", "./video_pic1_.jpg")
        os.rename("./video_pic1_alternate.jpg", "./video_pic1.jpg")
        os.rename("./video_pic1_.jpg", "./video_pic1_alternate.jpg")
        
        '''img1 = Image.open("./video_pic1.jpg")
        img1_alt = Image.open("./video_pic1_alternate.jpg")
        img1_alt.save("./video_pic1.jpg")
        img1.save("./video_pic1_alternate.jpg")'''

        os.rename("./video_pic2.jpg", "./video_pic2_.jpg")
        os.rename("./video_pic2_alternate.jpg", "./video_pic2.jpg")
        os.rename("./video_pic2_.jpg", "./video_pic2_alternate.jpg")
        '''
        img2 = Image.open("./video_pic2.jpg")
        img2_alt = Image.open("./video_pic2_alternate.jpg")
        img2_alt.save("./video_pic2.jpg")
        img2.save("./video_pic2_alternate.jpg")'''

        reload_counter += 1
        self.after(1000, self.reload2)
    pass
        

############ GRID FOR WINDOW ############
window.rowconfigure(0, weight=0)
window.rowconfigure(1, weight=1)
window.columnconfigure(0, weight=0)
window.columnconfigure(1, weight=1)
##########################################

app = Application(master=window)

####### MAIN LOOP #######
window.mainloop()
#########################