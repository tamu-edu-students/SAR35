import tkinter as tk
import tkintermapview as tkmv
from PIL import Image, ImageTk, ImageFont, ImageDraw
import csv, os, control, glob, shutil
from geopy import distance
import pathfinding.pathfinding as pf
from threading import Thread
from termcolor import colored
import yolov8test as im_rec

'''

***SAR Subsystem: User Interface***

Author: Senran Castro
Section: ECEN 404 - 904
Group Number: 35
Date Created: 09/01/23

Version: 2.6.0
Last Updated: 04/17/2024


'''

############ MAIN WINDOW ############
window = tk.Tk()
w = 1026
h = 610
sw = window.winfo_screenwidth()
sh = window.winfo_screenheight()
x = (sw/3) - (w/3.7)
y = 0
window.geometry('%dx%d+%d+%d' % (w, h, x, y))
window.title("SAR - Base Station")
####################################

global vid_window1, vid_window2

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
        frame1 = tk.Frame(master=window, borderwidth=5, bg="#B4ECFF")
        frame2 = tk.Frame(master=window, relief=tk.SUNKEN, borderwidth=5)
        frame3 = tk.Frame(master=frame2, relief=tk.SUNKEN, borderwidth=5, bg = "#73E992")

        #map
        self.map_widget = tkmv.TkinterMapView(master = map_frame, width = 800, height = 600)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.set_position(30.6134483, -96.3428987) #Simpson Drill Field Coordinates
        self.map_widget.set_zoom(19)
        ####################################

        ############# VARIABLES ############
        #external variables
        self.receive_files = 0
        #rover variables
        self.rover_num = 1
        rover_icon = ImageTk.PhotoImage(Image.open(os.path.join(os.getcwd(),"images","rover_icon.png")).resize((50, 50)))
        self.rover_list = [self.map_widget.set_marker(0,0), self.map_widget.set_marker(0,1, icon=rover_icon, text="Rover 1"), self.map_widget.set_marker(1,0, icon=rover_icon, text="Rover 2")]
        self.surv_pin_list = []
        self.obstacle_list = []
        self.obstacle_icon = ImageTk.PhotoImage(Image.open(os.path.join(os.getcwd(),"images","obstacle_icon.png")).resize((50,50)))
        #waypoint variables
        self.waypoint_list1 = []
        self.position_list1 = []
        self.wayp_pos_list1 = []
        self.wayp_index1 = 0
        self.delete_path1 = 0
        self.waypoint_list2 = []
        self.position_list2 = []
        self.wayp_pos_list2 = []
        self.wayp_index2 = 0
        self.delete_path2 = 0
        self.position_list = []
        self.new_pin = self.map_widget.set_marker(0,0)
        #path variables
        self.new_path1 = self.map_widget.set_path([(0,0), (1,0)])
        self.new_path2 = self.map_widget.set_path([(0,0), (1,0)])
        self.made_path1 = 0
        self.made_file_path1 = 0
        self.mover_index1 = 0
        self.made_path2 = 0
        self.made_file_path2 = 0
        self.mover_index2 = 0
        self.move_control = [0,0]
        self.move_stop1 = 1
        self.move_stop2 = 1
        self.init1 = 0
        self.init2 = 0
        self.check_rover_select = 0
        self.path_list1 = []
        self.path_list2 = []
        self.file_path_change1 = 0
        self.file_path_change2 = 0
        self.final_orient1 = 90
        self.final_orient2 = 90
        #move variables
        self.reset = 0
        self.move_call1 = 0
        self.move_call2 = 0
        self.made_move_path1 = 0
        self.made_move_path2 = 0
        #survivor variables
        self.age_text = ["???"]
        self.gender_text = ["???"]
        self.status_text = ["???"]
        self.survivor_num = 0
        #reload variables
        self.n1 = 0
        self.n2 = 0
        self.written1 = []
        self.path_file_change = 0
        self.setup = 1
        self.rov_speed1 = 0.000138888889 #default speed parameter (miles per sec) 0.5 mi/hr
        self.rov_speed2 = 0.000138888889 #default speed parameter (miles per sec) 0.5 mi/hr
        self.frequency = 1000
        self.load_counter = 0
        self.obst_load_counter1 = 0
        self.obst_timer1 = 0
        self.obst_timer2 = 0
        self.obst_load_counter2 = 0
        #im rec variables
        self.surv_count = 0
        self.im_rec_que_1 = 1
        self.im_rec_que_2 = 1
        self.surv_detect = 0
        self.obst_detect1 = 0
        self.obst_detect2 = 0
        self.image_path_list = []
        self.ml_thread = Thread(target=im_rec.ml_running)
        self.pf_cal_thread1 = Thread(target=self.pf_calibration, args=[1], daemon=True)
        self.pf_cal_thread2 = Thread(target=self.pf_calibration, args=[2], daemon=True)
        ####################################

        ############ FUNCTIONS ############
        #rover selection event
        def select_rover(num):
            self.rover_num = num
            rover_selection.config(text="Current Rover Selected: "+str(self.rover_num))
            if (num == 1):
                rover_1_select_button.config(bg = "grey", fg = "black", text="Rover 1 Selected")
                rover_2_select_button.config(bg="#1A19F3", fg="#D9DDF8", text="Rover 2 Select")
                frame3.config(bg='#73E992')
                #set map at rover 1
                self.map_widget.set_position(self.rover_list[1].position[0], self.rover_list[1].position[1])
            elif (num==2):
                rover_1_select_button.config(bg="#1A19F3", fg="#D9DDF8", text="Rover 1 Select")
                rover_2_select_button.config(bg = "grey", fg = "black", text="Rover 2 Selected")
                frame3.config(bg='#75B7F0')
                #set map at rover 2
                self.map_widget.set_position(self.rover_list[2].position[0], self.rover_list[2].position[1])

        #map right click events
        def add_pin_automatic(coordinates):
            #coordinates = [truncate(x,7) for x in coordinates]
            #print(colored(("Mega list before adding new auto point:"+str(self.position_list)+"\n"), 'light_green'))
            self.new_pin = self.map_widget.set_marker(coordinates[0], coordinates[1])
            if self.new_pin.position not in self.position_list:
                    self.position_list.append(self.new_pin.position)
                    #print("Mega list after adding new auto point:", self.position_list, "\n")
            check_rover_num()

        def check_rover_num():
            #replace wayp_pos_lists
            self.wayp_pos_list1 = []
            for i in self.position_list1:
                if (i != self.rover_list[1].position):
                    self.wayp_pos_list1.append(i)
            self.wayp_pos_list2 = []
            for i in self.position_list2:
                if (i != self.rover_list[2].position):
                    self.wayp_pos_list2.append(i)

            #ADD CALL FOR PATHFINDING
            gps_list = [self.rover_list[1].position, self.rover_list[2].position]
            pos_list_list = [self.position_list.copy(), self.wayp_pos_list1.copy(), self.wayp_pos_list2.copy()]
            self.pos_lists = pf.listCheck(gps_list, pos_list_list) #list of three lists:(overall, rover1, rover2)
            
            '''for i in pos_lists:
                for j in i:
                    j = [truncate(x,7) for x in j]
                    print("j =",j)'''

            #print(colored(("Position lists:"+str(pos_lists[0])+"\n\t"+str(pos_lists[1])+"\n\t"+str(pos_lists[2])+"\n"),'light_cyan'))
            #print(colored(("Mega list:"+str(self.position_list)+"\n"),'light_cyan'))
            #print(colored(("Path Position list 1:"+str(self.wayp_pos_list1)+"\n"),'light_cyan'))
            #print(colored(("Path Position list 2:"+str(self.wayp_pos_list2)+"\n"),'light_cyan'))

            self.wayp_change = 0
            self.check_rover_select = 0
            #check difference between two lists
            #list 1 check
            check_distance(self.pos_lists[1], self.wayp_pos_list1)
            if (self.length_match == 0) or (self.distance_match == 0):
                change_waypoints()
            else:
                self.check_rover_select = 1
            #list 2 check
            check_distance(self.pos_lists[2], self.wayp_pos_list2)
            if (self.length_match == 0) or (self.distance_match == 0):
                change_waypoints()
            else:
                if (self.check_rover_select == 1): 
                    self.check_rover_select = 0
                    print(colored(("Error: both lists match original, point not assigned to a rover."),'light_cyan'))
                else: self.check_rover_select = 2
            
            '''if (pos_lists[1] != self.wayp_pos_list1): #see if list got changed by pathfinding
                if (len(pos_lists[1]) != len(self.wayp_pos_list1)):
                    change_waypoints()
                for i in range(0,len(pos_lists[1])):
                    dist = self.calc_distance(self.wayp_pos_list1[i],pos_lists[1][i])
                    if dist < 0.001:
                        continue
                    else: 
                        change_waypoints()
                        break
                self.check_rover_select = 1
            if (pos_lists[2] != self.wayp_pos_list2):
                if (len(pos_lists[2]) != len(self.wayp_pos_list2)):  
                    change_waypoints()
                if (pos_lists[2] != self.wayp_pos_list2): #see if list got changed by pathfinding
                    for i in range(0,len(pos_lists[2])):
                        dist = self.calc_distance(self.wayp_pos_list2[i],pos_lists[2][i])
                        if dist < 0.1:
                            continue
                        else: 
                            change_waypoints()
                            break
                self.check_rover_select = 2'''
            
            if self.wayp_change == 1:
                self.check_rover_select = 0

            if (self.check_rover_select != 0):
                #check if needs to account for original being dif from calculation
                if ((self.rover_num==2 and self.check_rover_select==1) or (self.rover_num==1 and self.check_rover_select==2)):
                    self.reset = 1
                #set selection based on calculation
                self.rover_num = self.check_rover_select

                #delete old pin and place correct one
                pos = self.new_pin.position
                add_waypoint(pos)
                self.check_rover_select = 0
                self.new_pin.delete()
                
                #reset if original different from calculated
                if (self.reset and self.rover_num==1):
                    self.rover_num = 2
                    self.reset = 0
                elif (self.reset and self.rover_num==2):
                    self.rover_num = 1
                    self.reset = 0

            #replace wayp_pos_lists 
            self.wayp_pos_list1 = []
            for i in self.position_list1:
                if (i != self.rover_list[1].position):
                    self.wayp_pos_list1.append(i)
            self.wayp_pos_list2 = []
            for i in self.position_list2:
                if (i != self.rover_list[2].position):
                    self.wayp_pos_list2.append(i)

            #check if new waypoint lists equal lists from pathfinding
            if (self.wayp_pos_list1 != self.pos_lists[1]):
                check_distance(self.wayp_pos_list1,self.pos_lists[1])
            if (self.wayp_pos_list2 != self.pos_lists[2]):
                check_distance(self.wayp_pos_list2,self.pos_lists[2])

        def check_distance(pos_list_1, pos_list_2):
            '''
            Checks the distance between point x on list 1 and list 2.
            Lengths of two lists should equal, and if not an error message will be sent.
            '''
            print("checking distances...")
            self.length_match = 1
            self.distance_match = 1
            shortest_len = min(len(pos_list_1), len(pos_list_2))
            for i in range(0,shortest_len):
                dist = self.calc_distance(pos_list_1[i], pos_list_2[i])
                if dist < 0.1:
                    continue
                else: 
                    self.distance_match = 0
                    print("uh oh, distance difference too big")
                    print("\tPoint 1:",pos_list_1[i],"\n\tPoint 2:",pos_list_2[i])
            if (len(pos_list_1) != len(pos_list_2)): 
                self.length_match = 0
                print("uh oh length doesn't match")
                print("\tList 1:", pos_list_1, "\n\tList 2:", pos_list_2)

        def change_waypoints():
            print("changing waypoints")
            self.wayp_change = 1
            #clear waypoint and position lists
            clear_wayp(1)
            clear_wayp(2)
            #check if need to reset rover_num after
            reset1 = 0
            reset2 = 0
            if (self.rover_num == 1):
                reset1 = 1
            if (self.rover_num == 2):
                reset2 = 1
            #set rover_num to 1 for first waypoint list
            self.rover_num = 1
            #add on the new points from pathfinding
            for i in self.pos_lists[1]:
                #i = [truncate(x,6) for x in i]
                if (i in self.position_list1):
                    continue
                else:
                    #print("Waypoint to add:",i)
                    add_waypoint(i)
            #print("Position list:",self.position_list)
            #print("Position list 1 after chg_wp:", self.position_list1, "\n")
            #set self.rover_num to 2 for second waypoint list
            self.rover_num = 2
            #add on the new points from pathfinding
            for i in self.pos_lists[2]:
                #i = [truncate(x,7) for x in i]
                if (i in self.position_list2):
                    continue
                else:
                    #print("Waypoint to add:",i)
                    add_waypoint(i)
            #print("Position list:",self.position_list)
            #print("Position list 2 after chg_wp:", self.position_list2, "\n")
            #reset rover num if necessary
            if reset1:
                self.rover_num = 1
            if reset2:
                self.rover_num = 2
            #get rid of original pin
            self.new_pin.delete()

        def add_waypoint(coordinates):
            print("adding waypoint")
            #clip the coordinates so they're easier to manage
            #coordinates = [truncate(i,7) for i in coordinates]
            #check if list 1 initialized yet
            if (self.init1==0):
                self.waypoint_list1.append(self.rover_list[1])
                self.position_list1.append(self.rover_list[1].position)
                self.pos_list_copy1 = self.position_list1.copy()
                self.init1 = 1
            #check if list 2 initialized yet
            if (self.init2==0):
                self.waypoint_list2.append(self.rover_list[2])
                self.position_list2.append(self.rover_list[2].position)
                self.pos_list_copy2 = self.position_list2.copy()
                self.init2 = 1
            #reset the first position
            self.position_list1[0] = self.rover_list[1].position
            self.pos_list_copy1 = self.position_list1.copy()
            self.position_list2[0] = self.rover_list[2].position
            self.pos_list_copy2 = self.position_list2.copy()
            ### Add waypoints ###
            #add new point for list 1
            if (self.rover_num == 1):
                #delete old path
                self.delete_path(1)
                #movement
                if ((self.move_control[0] != 1) and (self.check_rover_select==0)): #set movement to manual
                    self.move_control[0] = 1
                self.mover_index1 = 0
                #increment wayp_index
                self.wayp_index1 += 1
                #add points to lists
                self.waypoint_list1.append(self.rover_list[1]) #add marker for replacing
                self.position_list1.append(coordinates)
                print("position list 1 =", self.position_list1)
                #self.wayp_pos_list1.append(coordinates)
                if coordinates not in self.position_list: #update mega list
                    self.position_list.append(coordinates)
                #set marker
                self.waypoint_list1[self.wayp_index1] = self.map_widget.set_marker(coordinates[0], coordinates[1], marker_color_circle = '#73E992', marker_color_outside = "#26D354")
                #copy list
                #self.pos_list_copy1 = self.position_list1.copy()
                #print("Position list 1 after add_wp:", self.position_list1, "\n")
                self.create_path() #auto update path
                self.calc_time()
            #add new point for list 2
            if (self.rover_num == 2):
                #delete old path
                self.delete_path(2)
                #movement
                if ((self.move_control[1] != 1) and (self.check_rover_select==0)): #set movement to manual
                    self.move_control[1] = 1
                self.mover_index2 = 0
                #increment wayp_index
                self.wayp_index2 += 1
                #add points to lists
                self.waypoint_list2.append(self.rover_list[2]) #add marker for replacing
                self.position_list2.append(coordinates)
                #self.wayp_pos_list2.append(coordinates)
                if coordinates not in self.position_list: #update mega list
                    self.position_list.append(coordinates)
                #set marker
                self.waypoint_list2[self.wayp_index2] = self.map_widget.set_marker(coordinates[0], coordinates[1], marker_color_circle = '#75B7F0', marker_color_outside = "#2683D3")
                #self.pos_list_copy2 = self.position_list2.copy()
                #print("Position list 2 after add_wp:", self.position_list2, "\n")
                self.create_path() #auto update path
                self.calc_time()

        #sidebar events
        def delete_wayp():
            if (self.rover_num==1 and self.wayp_index1):
                print("deleting waypoint")
                #delete path
                self.delete_path(1)
                #delete point self.wayp_index1 from mega list
                if (self.position_list1[self.wayp_index1] in self.position_list):
                    self.position_list.remove(self.position_list1[self.wayp_index1])
                #delete marker from map
                self.waypoint_list1[self.wayp_index1].delete()
                #delete points from lists
                del self.waypoint_list1[self.wayp_index1]
                del self.position_list1[self.wayp_index1]
                #del self.wayp_pos_list1[self.wayp_index1 - 1]
                #copy new list
                self.pos_list_copy1 = self.position_list1.copy()
                #test print statements
                #print("Position list after delete wp 1:", self.position_list, "\n")
                #print("Position list 1 after delete wp 1:", self.position_list1, "\n")
                #print("position list copy 1:", self.pos_list_copy1, "\n")
                #decrement wayp_index
                self.wayp_index1 -= 1
                if (self.wayp_index1 == 0): #stop manual movement
                    self.move_control[0] = 0
                #create new paths and calc time
                self.create_path()
                self.calc_time()
            elif (self.rover_num==2 and self.wayp_index2):
                print("deleting waypoint")
                #delete path
                self.delete_path(2)
                #delete point self.wayp_index2 from mega list
                if (self.position_list2[self.wayp_index2] in self.position_list):
                    self.position_list.remove(self.position_list2[self.wayp_index2])
                #delete marker from map
                self.waypoint_list2[self.wayp_index2].delete()
                #delete points from lists
                del self.waypoint_list2[self.wayp_index2]
                del self.position_list2[self.wayp_index2]
                #del self.wayp_pos_list2[self.wayp_index2 - 1]
                #copy new list
                self.pos_list_copy2 = self.position_list2.copy()
                #test print statements
                #print("Position list after delete wp 2:", self.position_list, "\n")
                #print("Position list 2 after delete wp 2:", self.position_list2, "\n")
                #print("position list copy 2:", self.pos_list_copy2, "\n")
                #decrement wayp_index
                self.wayp_index2 -= 1
                if (self.wayp_index2 == 0): #stop manual movement
                    self.move_control[1] = 0
                #create new paths and calc time
                self.create_path()
                self.calc_time()

        def clear_wayp(num):
            if ((num == 1) and self.wayp_index1):
                print("clearing waypoints")
                self.delete_path(1) #clear the old path
                for i in self.position_list:
                    if i in self.position_list1:
                        del i
                print("\n")
                while (self.wayp_index1 >= 1):
                    if (self.position_list1[self.wayp_index1] in self.position_list):
                        self.position_list.remove(self.position_list1[self.wayp_index1])
                    self.waypoint_list1[self.wayp_index1].delete()
                    del self.waypoint_list1[self.wayp_index1]
                    del self.position_list1[self.wayp_index1]
                    self.wayp_index1 -= 1
                self.move_control[0] = 0
                self.calc_time()
            elif ((num == 2) and self.wayp_index2):
                print("clearing waypoints")
                self.delete_path(2) #clear the old path
                for i in self.position_list:
                    if i in self.position_list2:
                        del i
                while (self.wayp_index2 >= 1):
                    if (self.position_list2[self.wayp_index2] in self.position_list):
                        self.position_list.remove(self.position_list2[self.wayp_index2])
                    self.waypoint_list2[self.wayp_index2].delete()
                    del self.waypoint_list2[self.wayp_index2]
                    del self.position_list2[self.wayp_index2]
                    self.wayp_index2 -= 1
                self.move_control[1] = 0
                self.calc_time()

        def pick_video():
            if (self.rover_num == 1): self.open_vid1()
            else: self.open_vid2()

        #movement for rover
        def send_move():
            if self.rover_num == 1: control.send_movement1 = 1
            else: control.send_movement2 = 1
        
        def call_pf_Cal():
            if self.rover_num == 1: self.pf_cal_thread1.start()
            else: self.pf_cal_thread2.start()
        ####################################

        ############ WIDGETS ############
        #map commands
        new_pin_label = self.map_widget.add_right_click_menu_command(label="Add New Waypoint (Rover Automatically Selected)", command=add_pin_automatic, pass_coords=True)
        waypoint_label = self.map_widget.add_right_click_menu_command(label= "Add New Waypoint Manually (For Currently Selected Rover)", command=add_waypoint, pass_coords=True)

        ### SIDE BAR ###
        self.survivor_count = tk.Label(master=frame1, text="Number of Survivors Found: "+str(self.survivor_num), font = font1, bg="#B4ECFF")
        rover_selection = tk.Label(master=frame2, text="Current Rover Selected: "+str(self.rover_num), font = font1)
        self.time_to_dest1 = tk.Label(master = frame2, text = "Rover 1 Time to destination: \n\tNot calculated",font = font1)
        self.time_to_dest2 = tk.Label(master = frame2, text = "Rover 2 Time to destination: \n\tNot calculated",font = font1)

        #buttons
        calibrate_button = tk.Button(master=frame3, text = "Recalibrate Rover", command = call_pf_Cal)
        start_stop_ml_button = tk.Button(master=frame3, text = "Start/Stop ML", command = self.start_stop_ml)
        send_movement_button = tk.Button(master = frame3, text="Send Move Data", command = send_move)
        rover_1_select_button = tk.Button(master=frame2, font=font2, width=14, height=2, bg = "grey", fg = "black", text="Rover 1 Selected", command=lambda: select_rover(1))
        rover_2_select_button = tk.Button(master=frame2, font=font2, width=14, height=2, bg="#1A19F3", fg="#D9DDF8", text="Rover 2 Select", command=lambda: select_rover(2))
        start_move_button = tk.Button(master=frame3, text = "Start Movement", command = self.start_move)
        stop_move_button = tk.Button(master=frame3, text = "Stop Movement", command = self.stop_move)
        delete_wayp_button = tk.Button(master=frame3, text = "Delete Last \nWaypoint", command = delete_wayp)
        clear_wayp_button = tk.Button(master=frame3, text = "Clear Waypoints", command = lambda : clear_wayp(self.rover_num))
        video_feed_button = tk.Button(master=frame3, text= "Show Camera Feed", command = pick_video)
        ################
        ####################################

        ############# PACKING #############
        self.map_widget.pack()
        self.survivor_count.pack()

        #side bar grid
        rover_selection.grid(row=0,column=0,columnspan=2, sticky="w")
        rover_1_select_button.grid(row=1,column=0)
        rover_2_select_button.grid(row=1,column=1)
        self.time_to_dest1.grid(row=3, column=0, columnspan=2, sticky='w')
        self.time_to_dest2.grid(row=4, column=0, columnspan=2, sticky='w')
        frame2.columnconfigure(0, weight=1)
        frame2.columnconfigure(1, weight=1)
        frame2.rowconfigure(0, weight=0)
        frame2.rowconfigure(1, weight=0)
        frame2.rowconfigure(2, weight=1)
        frame2.rowconfigure(3, weight=0)
        #frame3 grid
        start_move_button.grid(row=0,column=0)
        stop_move_button.grid(row=0,column=1)
        delete_wayp_button.grid(row=1,column=0)
        clear_wayp_button.grid(row=1,column=1)
        video_feed_button.grid(row=2,column=0, columnspan=2)
        send_movement_button.grid(row=3, column=0)
        start_stop_ml_button.grid(row=3, column=1)
        calibrate_button.grid(row=4, column=0, columnspan=2)
        frame3.rowconfigure(0, weight=1)
        frame3.rowconfigure(1, weight=1)
        frame3.rowconfigure(2, weight=1)
        frame3.rowconfigure(3, weight=1)
        frame3.rowconfigure(4, weight=1)
        frame3.columnconfigure(0, weight=1)
        frame3.columnconfigure(1, weight=1)

        #window grid
        map_frame.grid(row=0, column=0, rowspan=2, sticky="w")
        frame1.grid(row=0, column=1, sticky="new")
        frame2.grid(row=1, column=1, sticky="nsew")
        frame3.grid(row=2, column=0, columnspan=2, sticky='nsew')
        ####################################
        
        self.reload()
    pass

    ############## FUNCTIONS ##############
    #map left click events
    def click_pin(self, pin):
        if (pin.image_hidden==False):
            pin.hide_image(True)
        else:
            pin.hide_image(False)

    #survivor pin events
    def place_survivor(self, coordinates):
        self.survivor_num += 1
        self.survivor_count.config(text="Number of Survivors Found: "+str(self.survivor_num))
        survivor_img = self.create_surv_image()
        self.surv_pin_list.append(self.map_widget.set_marker(coordinates[0], coordinates[1], text= "Survivor "+str(self.survivor_num), image=survivor_img, command=self.click_pin))

    def clear_survivors(self):
        for i in self.surv_pin_list:
            i.delete()
            del i
        self.surv_pin_list = []
        self.survivor_num = 0
        self.survivor_count.config(text="Number of Survivors Found: "+str(self.survivor_num))
    
    def create_surv_image(self):
        image_pil = Image.open(os.path.join(os.getcwd(),'images','blank_surv_img.jpg'))
        image_pil = image_pil.resize((290, 170))

        #add survivor picture from image recognition files
        pic_name = 'surv_pic'+str(self.survivor_num)+'.jpg'
        try:
            surv_pic = Image.open(os.path.join(os.getcwd(),'im_rec_folder',pic_name)) #test sample for now
            surv_pic = surv_pic.resize((124, 170))
            offset = (0, 0)
            image_pil.paste(surv_pic, offset)

            im_draw = ImageDraw.Draw(image_pil) #make able to add text
            im_font = ImageFont.truetype("c:\Windows\Fonts\Bahnschrift.ttf", 12)

            #add text (sample for now)
            self.create_image_text()
            try: im_draw.text((148,12), self.age_text[self.survivor_num], font=im_font, fill="#2C2C2C") #age
            except: im_draw.text((148,12), self.age_text[0], font=im_font, fill="#2C2C2C") #age
            try: im_draw.text((162,44), self.gender_text[self.survivor_num], font=im_font, fill="#2C2C2C") #gender
            except: im_draw.text((162,44), self.gender_text[0], font=im_font, fill="#2C2C2C") #gender
            try: im_draw.text((173,75), self.status_text[self.survivor_num], font=im_font, fill="#2C2C2C") #condition
            except: im_draw.text((173,75), self.status_text[0], font=im_font, fill="#2C2C2C") #condition
            surv_img_name = "surv_img"+str(self.survivor_num)+".jpg"
            image_pil.save(os.path.join(os.getcwd(),"images",surv_img_name))
            surv_image = ImageTk.PhotoImage(image_pil)
            return surv_image
        except:
            print("ERROR: Image could not be made for ", self.survivor_num)
            image_pil = ImageTk.PhotoImage(image_pil)
            return image_pil

    def create_image_text(self):
        self.age_text = ["???"]
        self.gender_text = ["???"]
        self.status_text = ["???"]
        with open(os.path.join(os.getcwd(),"im_rec_folder","surv_data.csv"), mode='r') as file:
            surv_data_file = csv.reader(file, delimiter=',')
            for line in surv_data_file:
                j_counter = 0
                for j in line:
                    if (j == []): continue
                    else: j = str(j)
                    if (j_counter == 0):
                        self.gender_text.append(j)
                        j_counter += 1
                    elif (j_counter==1):
                        self.age_text.append(j)
                        j_counter += 1
                    elif (j_counter==2):
                        self.status_text.append(j)
        if len(self.age_text) != (self.survivor_num + 1):
            self.age_text[:self.survivor_num+1] + ["???"] * (self.survivor_num+1 - len(self.age_text))
        if len(self.gender_text) != (self.survivor_num + 1):
            self.gender_text[:self.survivor_num+1] + ["???"] * (self.survivor_num+1 - len(self.gender_text))
        if len(self.status_text) != (self.survivor_num + 1):
            self.status_text[:self.survivor_num+1] + ["???"] * (self.survivor_num+1 - len(self.status_text))
    
    #obstacle pin events
    def place_obstacle(self):
        #clear old list
        for i in self.obstacle_list:
            i.delete()
            del i
        #update new list from file
        with open(os.path.join(os.getcwd(),"gps_folder","obstacle_locations.csv"), mode = "r") as obst_file:
            obstacle_loc_file = csv.reader(obst_file, delimiter=",")
            for i in obstacle_loc_file:
                coordinates = []
                for j in i:
                    if (j == []): continue
                    else: 
                        coordinates.append(float(j))
                if (len(coordinates) == 2):
                    self.obstacle_list.append(self.map_widget.set_marker(coordinates[0], coordinates[1], icon=self.obstacle_icon))
    
    #path events
    def delete_path(self, num):
        if (num == 1):
            self.new_path1.set_position_list([(0,0), (1,0)])
            self.made_path1 = 0
            self.move_path1 = []
            self.made_move_path1 = 0
            if (self.made_file_path1 and self.wayp_index1):
                self.made_file_path1 = 0
                self.mover_index1 = 0
            print("old path 1 deleted")
        if (num == 2):
            self.new_path2.set_position_list([(0,0), (1,0)])
            self.made_path2 = 0
            self.move_path2 = []
            self.made_move_path2 = 0
            if (self.made_file_path2 and self.wayp_index2):
                self.made_file_path2 = 0
                self.mover_index2 = 0
            print("old path 2 deleted")

    def create_path(self): #update to use pathfinding path
        print("creating new paths...")
        #get path from pathfinding function
        self.path_list1 = pf.multiPath(self.position_list1, pf.diagram)
        self.path_list2 = pf.multiPath(self.position_list2, pf.diagram)
        #instruction_set call
        if (((self.move_stop1 == 1) and (self.wayp_index1 >= 1)) or (self.wayp_index1 == 1)) and not (pf.pf_stop1 and (self.wayp_index1 == 0)):
            #try:
                print("rover1 multipath obstacle thing ", (self.position_list1[0], self.position_list1[1]))
                path_inst_list1 = pf.multiPath((self.position_list1[0], self.position_list1[1]), pf.diagram)
                print("path_inst_list1 len =", len(path_inst_list1))
                inst_list1 = pf.instructionset(path_inst_list1, self.final_orient1)
                self.final_orient1 = pf.getFinalOrientation(path_inst_list1[-2], path_inst_list1[-1])
                print("Instruction list 1 = ", inst_list1)
                with open(os.path.join(os.getcwd(), "path_folder", "movement_data_1.csv"), 'w', newline='') as file:
                    write_file = csv.writer(file)
                    for i in inst_list1:
                        write_file.writerow([i])
            #except Exception as e: print("ERROR MAKING PATH:", e)
        if (((self.move_stop2 == 1) and (self.wayp_index2 >= 1)) or (self.wayp_index2 == 1)) and not (pf.pf_stop2 and (self.wayp_index2 == 0)):
            try:
                print("rover2 multipath obstacle thing ", (self.position_list2[0], self.position_list2[1]))
                path_inst_list2 = pf.multiPath((self.position_list2[0], self.position_list2[1]), pf.diagram)
                print("path_inst_list2 len =", len(path_inst_list2))
                inst_list2 = pf.instructionset(path_inst_list2, self.final_orient2)
                self.final_orient2 = pf.getFinalOrientation(path_inst_list2[-2], path_inst_list2[-1])
                print("Instruction list 2 = ", inst_list2)
                with open(os.path.join(os.getcwd(), "path_folder", "movement_data_2.csv"), 'w', newline='') as file:
                    write_file = csv.writer(file)
                    for i in inst_list2:
                        write_file.writerow([i])
            except Exception as e: print("ERROR MAKING PATH:", e)
        #create new paths
        if (self.rover_num == 1 or self.file_path_change1):
            print("rover 1")
            if (len(self.path_list1) < 2):
                print("skipped")
            else:
                print("making path 1...")
                #set new path
                self.new_path1.set_position_list(self.path_list1)
                self.made_path1 = 1
                #set file change variables
                if (self.file_path_change1):
                    self.made_file_path1 = 1
                    self.mover_index1 = 0
                    self.file_path_change1 = 0
                '''#make movement path
                make_move_path(1)
                calc_time()'''
                print("made path 1")
        if (self.rover_num ==2 or self.file_path_change2):
            print("rover 2")
            if (len(self.path_list2) < 2):
                print("skipped")
            else:
                print("making path 2...")
                #set new path
                self.new_path2.set_position_list(self.path_list2)
                self.made_path2 = 1
                #set file change variables
                if (self.file_path_change2):
                    self.made_file_path2 = 1
                    self.mover_index2 = 0
                    self.file_path_change2 = 0
                '''#make movement path
                make_move_path(2)
                calc_time()'''
                print("made path 2")
        #reset the file changed indicator
        if (self.path_file_change): 
            self.path_file_change = 0
    
    def calc_time(self):
        #path 1 calculation
        if (self.made_path1 or self.made_move_path1):
            print("calculating time 1")
            self.make_move_path(1)
            step_num_list = []
            self.time1 = 0
            for i in self.distance_list1:
                step_num_list.append(i/self.step_dist1) #distance i / step distance = number of steps in distance i
            for i in step_num_list:
                self.time1 += ((self.rov_speed1/(self.frequency/1000))/self.step_dist1) * i #time to travel one step X number of steps in dist
            self.time1 += len(self.position_list1) * 30 #add time for stopping at waypoints
            self.time_to_dest1.config(text="Rover 1 Time to destination: \n\t"+str(round(self.time1))+" sec")
        else:
            self.time_to_dest1.config(text="Rover 1 Time to destination: \n\tNot Calculated")
        #path 2 calculation
        if (self.made_path2 or self.made_move_path2):
            print("calculating time 2")
            self.make_move_path(2)
            step_num_list = []
            self.time2 = 0
            for i in self.distance_list2:
                step_num_list.append(i/self.step_dist2) #number of steps to travel distance i
            for i in step_num_list:
                self.time2 += ((self.rov_speed2/(self.frequency/1000))/self.step_dist2) * i #time to travel one step X number of steps in dist
            self.time2 += len(self.position_list2) * 30 #add time for stopping at waypoints
            self.time_to_dest2.config(text="Rover 2 Time to destination: \n\t"+str(round(self.time2))+" sec")
        else:
            self.time_to_dest2.config(text="Rover 2 Time to destination: \n\tNot Calculated")

    def make_move_path(self, num):
        if (num == 1):
            print("making movement path 1...")
            #create movement points
            i = 0
            self.distance_list1 = []
            #make the list of distances between points
            while (i+1 < len(self.new_path1.position_list)):
                self.distance_list1.append(self.calc_distance(self.new_path1.position_list[i], self.new_path1.position_list[i+1])) #distances in miles
                i += 1
            self.made_move_path1 = 1
            print("movement path 1 made")
        else:
            print("making movement path 2...")
            #create movement points
            i = 0
            self.distance_list2 = []
            #make the list of distances between points
            while (i+1 < len(self.new_path2.position_list)):
                self.distance_list2.append(self.calc_distance(self.new_path2.position_list[i], self.new_path2.position_list[i+1]))
                i += 1
            self.made_move_path2 = 1
            print("movement path 2 made")
    
    #distance calculation
    def calc_distance(self, coordinates1, coordinates2):
        dist = distance.distance(coordinates1, coordinates2).miles
        return dist
    
    def start_move(self):
        if (self.rover_num == 1):
            self.move_call1 = 1
        else:
            self.move_call2 = 1
        
    def stop_move(self):
        if (self.rover_num == 1):
            self.move_call1 = 0
            #write to emergency start/stop
            with open(os.path.join(os.getcwd(), "emg_stop_1.csv"), mode='w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerow('0')
        else:
            self.move_call2 = 0
            #write to emergency start/stop
            with open(os.path.join(os.getcwd(), "emg_stop_2.csv"), mode='w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerow('0')

    #image recognition functions
    def image_recognition(self):
        print("start image blurriness loop")
        loop_num = 0
        while loop_num < 9:
            #rover 1 images
            if (os.path.isdir(os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_1)+"_images_1"))):
                #print("image blurriness 1 for que num",self.im_rec_que_1)
                im_rec.least_blurry(os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_1)+"_images_1"))
                #set que num 1 to lowest value
                img_dir_list1 = [os.path.join(os.getcwd(), "im_rec_folder", f) for f in os.listdir(os.path.join(os.getcwd(), "im_rec_folder")) if f.endswith(('_images_1'))]
                num = []
                for i in img_dir_list1:
                    name = os.path.basename(i)
                    num.append(int(name.split("_")[0]))
                if num == []:
                    num = [(self.im_rec_que_1 + 1)]
                self.im_rec_que_1 = min(num)
            else: 
                #set que num 1 to lowest value
                img_dir_list1 = [os.path.join(os.getcwd(), "im_rec_folder", f) for f in os.listdir(os.path.join(os.getcwd(), "im_rec_folder")) if f.endswith(('_images_1'))]
                #print("img_dir_list1 =", img_dir_list1)
                if len(img_dir_list1) > 0:
                    num = []
                    for i in img_dir_list1:
                        name = os.path.basename(i)
                        num.append(int(name.split("_")[0]))
                    self.im_rec_que_1 = min(num)
            #rover 2 images
            if (os.path.isdir(os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_2)+"_images_2"))):
                #print("image blurriness 2 for que num",self.im_rec_que_2)
                im_rec.least_blurry(os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_2)+"_images_2"))
                #set que num 2 to lowest value
                img_dir_list2 = [os.path.join(os.getcwd(), "im_rec_folder", f) for f in os.listdir(os.path.join(os.getcwd(), "im_rec_folder")) if f.endswith(('_images_2'))]
                if len(img_dir_list2) > 0:
                    num = []
                    for i in img_dir_list2:
                        name = os.path.basename(i)
                        num.append(int(name.split("_")[0]))
                    self.im_rec_que_2 = min(num)
            else: 
                #set que num 2 to lowest value
                img_dir_list2 = [os.path.join(os.getcwd(), "im_rec_folder", f) for f in os.listdir(os.path.join(os.getcwd(), "im_rec_folder")) if f.endswith(('_images_2'))]
                #print("img_dir_list2 =", img_dir_list2)
                if len(img_dir_list2) > 0:
                    num = []
                    for i in img_dir_list2:
                        name = os.path.basename(i)
                        num.append(int(name.split("_")[0]))
                    self.im_rec_que_2 = min(num)
            loop_num += 1
    
    def start_stop_ml(self):
        if im_rec.run_ml == 1:
            im_rec.run_ml = 0
        else:
            im_rec.run_ml = 1
            if not self.ml_thread.is_alive():
                self.ml_thread.start()

    #pathfinding functions
    def pf_calibration(self, num):
        if num == 1:
            #reset move stop 1 to zero
            self.move_stop1 = 0
            #send rover calibration movement data with obstacle=True
            instruction_set = pf.calibrationInstructions()
            with open(os.path.join(os.getcwd(), "path_folder", "movement_data_1.csv"), 'w', newline='') as file:
                write_file = csv.writer(file)
                for i in instruction_set:
                    write_file.writerow([i])
            #WAIT UNTIL MOVEMENT STOPPED COMMAND FROM ROVER
            while not (os.path.exists(os.path.join(os.getcwd(), "gps_folder", str(control.que_num1_in - 2)+"_gps_coords_1", "previous_coords_1.csv")) 
                       and os.path.exists(os.path.join(os.getcwd(), "gps_folder", "movement_end_1.csv"))): continue
            print("previous coords found")
            #get the new gps coords
            self.current_gps1 = []
            with open(os.path.join(os.getcwd(), "gps_folder", str(control.que_num1_in - 2)+"_gps_coords_1", "previous_coords_1.csv"), 'r') as file:
                read_file = csv.reader(file, delimiter=",")
                for i in read_file:
                    self.current_gps1.append([float(i[0]), float(i[1])])
            with open(os.path.join(os.getcwd(),"gps_folder", str(control.que_num1_in - 2)+"_gps_coords_1", "gps_coords_1.csv"), mode = "r") as file:
                read_file = csv.reader(file, delimiter=",")
                for i in read_file:
                    self.current_gps1.append([float(i[0]), float(i[1])])
            print("gps coords list =", self.current_gps1)
            #get new calibration instr set
            instruction_set = pf.calibrationAngle(self.current_gps1[0],self.current_gps1[-1])
            with open(os.path.join(os.getcwd(), "path_folder", "movement_data_1.csv"), 'w', newline='') as file:
                write_file = csv.writer(file)
                for i in instruction_set:
                    write_file.writerow([i])
            #create new paths and instruction sets
            if self.rover_num == 2:
                reset = 1
            self.rover_num = 1
            self.create_path()
            if reset:
                self.rover_num = 2
        else:
            #reset move stop 2 to zero
            self.move_stop2 = 0
            #send rover calibration movement data with obstacle=True
            instruction_set = pf.calibrationInstructions()
            with open(os.path.join(os.getcwd(), "path_folder", "movement_data_2.csv"), 'w', newline='') as file:
                write_file = csv.writer(file)
                for i in instruction_set:
                    write_file.writerow([i])
            #send new movement data
            control.send_movement2 = 1
            control.output_zip_file(2)
            try: self.send_thread2.start()
            except: pass
            #WAIT UNTIL MOVEMENT STOPPED COMMAND FROM ROVER
            while not (os.path.exists(os.path.join(os.getcwd(), "gps_folder", str(control.que_num2_in - 2)+"_gps_coords_2", "previous_coords_2.csv")) 
                       and os.path.exists(os.path.join(os.getcwd(), "gps_folder", "movement_end_2.csv"))): continue
            print("previous coords found")
            #get the new gps coords
            self.current_gps2 = []
            with open(os.path.join(os.getcwd(), "gps_folder", str(control.que_num2_in - 2)+"_gps_coords_2", "previous_coords_2.csv"), 'r') as file:
                read_file = csv.reader(file, delimiter=",")
                for i in read_file:
                    self.current_gps2.append([float(i[0]), float(i[1])])
            with open(os.path.join(os.getcwd(),"gps_folder", str(control.que_num2_in - 2)+"_gps_coords_2", "gps_coords_2.csv"), mode = "r") as file:
                read_file = csv.reader(file, delimiter=",")
                for i in read_file:
                    self.current_gps2.append([float(i[0]), float(i[1])])
            #get new calibration instr set
            instruction_set = pf.calibrationAngle(self.current_gps2[0],self.current_gps2[-1])
            with open(os.path.join(os.getcwd(), "path_folder", "movement_data_2.csv"), 'w', newline='') as file:
                write_file = csv.writer(file)
                for i in instruction_set:
                    write_file.writerow([i])
            #send new movement data
            '''control.send_movement2 = 1
            control.output_zip_file(2)
            try: self.send_thread2.start()
            except: pass'''
            #create new paths and instruction sets
            if self.rover_num == 1:
                reset = 1
            self.rover_num = 2
            self.create_path()
            if reset:
                self.rover_num = 1

    def pf_obstacle(self, num):
        print("pf_obstacle start")
        if num == 1:
            #save gps coords for later
            print("saving gps...")
            current_gps1 = []
            path = os.path.join(os.getcwd(), "gps_folder", str(control.que_num1_in - 1)+"_gps_coords_1", "gps_coords_1.csv")
            que = control.que_num1_in - 1
            while not os.path.exists(path):
                que -= 1
                path = os.path.join(os.getcwd(), "gps_folder", str(que)+"_gps_coords_1", "gps_coords_1.csv")
            with open(path, mode = "r") as file:
                read_file = csv.reader(file, delimiter=",")
                for i in read_file:
                    try: a = float(i[0])
                    except: a = ''
                    try: b = float(i[1])
                    except: b = ''
                    if isinstance(a, float) and isinstance(b, float):
                        current_gps1.append((a, b))
                    else: current_gps1 = (0,0)
            print("current gps =", current_gps1)
            #stop the rover
            with open(os.path.join(os.getcwd(), "emg_stop_1.csv"), mode='w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerow('0')
            print("rover stopped")
            #add the obstacle to pathfinding
            if self.wayp_index1 > 0:
                print("adding obstacle to path")
                orientation = pf.findOrientation(current_gps1[0], self.path_list1)
                print("found orientation")
                dest = pf.addObstacle(current_gps1[0], orientation, pf.pf_obstacle1[0], pf.pf_obstacle1[1], pf.pf_obstacle1[2])
                print("got destination:", dest)
                #make instruction set to go around obstacle and continue to waypoint
                path1 = pf.multiPath((self.rover_list[1].position, self.position_list1[1]), pf.diagram)
                print("got multi path")
                instruction_set = pf.avoidCone()
                print("made instruction set =", instruction_set)
                with open(os.path.join(os.getcwd(), "path_folder", "movement_data_1.csv"), 'w', newline='') as file:
                    write_file = csv.writer(file)
                    for i in instruction_set: 
                        write_file.writerow([i])
                '''with open(os.path.join(os.getcwd(), "emg_stop_1.csv"), mode='w', newline='') as file:
                    write_file = csv.writer(file)
                    write_file.writerow('1')'''
            else: 
                print("adding obstacle without path")
                dest = pf.tempAddObstacle(current_gps1[0])
                print("got destination:", dest)
            #add obstacle location to csv
            obst_list = []
            with open(os.path.join(os.getcwd(), "gps_folder", "obstacle_locations.csv"), 'r') as file:
                read_file = csv.reader(file)
                for i in read_file:
                    obst_list.append(i)
            obst_list.append(dest)
            with open(os.path.join(os.getcwd(), "gps_folder", "obstacle_locations.csv"), 'w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerows(obst_list)
            print("obstacle location added to csv")
            #create new paths and instruction sets
            reset = 0
            if self.rover_num == 2:
                reset = 1
            self.rover_num = 1
            self.create_path()
            self.calc_time()
            if reset:
                self.rover_num = 2
        else:
            #save gps coords for later
            current_gps2 = []
            path = os.path.join(os.getcwd(), "gps_folder", str(control.que_num2_in - 1)+"_gps_coords_2", "gps_coords_2.csv")
            que = control.que_num2_in - 1
            while not os.path.exists(path):
                que -= 1
                path = os.path.join(os.getcwd(), "gps_folder", str(que)+"_gps_coords_2", "gps_coords_2.csv")
            with open(path, mode = "r") as file:
                read_file = csv.reader(file, delimiter=",")
                for i in read_file:
                    try: a = float(i[0])
                    except: a = ''
                    try: b = float(i[1])
                    except: b = ''
                    if isinstance(a, float) and isinstance(b, float):
                        current_gps2.append((a, b))
                    else: current_gps2 = (0,0)
            #stop the rover
            with open(os.path.join(os.getcwd(), "emg_stop_2.csv"), mode='w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerow('0')
            #add the obstacle to pathfinding
            if self.wayp_index2 > 0:
                orientation = pf.findOrientation(current_gps2[0], self.path_list2)
                dest = pf.addObstacle(current_gps2[0], orientation, pf.pf_obstacle2[0], pf.pf_obstacle2[1], pf.pf_obstacle2[2])
                #make instruction set to go around obstacle and continue to waypoint
                path2 = pf.multiPath((self.rover_list[2].position, self.position_list2[1]), pf.diagram)
                instruction_set = pf.avoidCone()
                with open(os.path.join(os.getcwd(), "path_folder", "movement_data_2.csv"), 'w', newline='') as file:
                    write_file = csv.writer(file)
                    for i in instruction_set: 
                        write_file.writerow([i])
                '''with open(os.path.join(os.getcwd(), "emg_stop_2.csv"), mode='w', newline='') as file:
                    write_file = csv.writer(file)
                    write_file.writerow('1')'''
                pf.pf_stop2 = 0
            else:
                dest = pf.tempAddObstacle(current_gps2[0])
            #add obstacle location to csv
            obst_list = []
            with open(os.path.join(os.getcwd(), "gps_folder", "obstacle_locations.csv"), 'r') as file:
                read_file = csv.reader(file)
                for i in read_file:
                    if i != '\n': obst_list.append(i)
            obst_list.append(dest)
            with open(os.path.join(os.getcwd(), "gps_folder", "obstacle_locations.csv"), 'w', newline='') as file:
                write_file = csv.writer(file)
                write_file.writerows(obst_list)
            #create new paths and instruction sets
            reset = 0
            if self.rover_num == 1:
                reset = 1
            self.rover_num = 2
            self.create_path()
            self.calc_time()
            if reset:
                self.rover_num = 1
    #######################################
    
    def open_vid1(self):
        global vid_window1
        vid_window1 = VidWindow(self)
        vid_window1.grab_set()
        vid_window1.bind("<Configure>", vid_window1.resize_image)
    pass

    def open_vid2(self):
        global vid_window2
        vid_window2 = VidWindow(self)
        vid_window2.grab_set()
        vid_window2.bind("<Configure>", vid_window2.resize_image)
    pass

    def reload(self):
        ############ VARIABLES ############
        self.step_dist1 = self.rov_speed1 / (self.frequency / 1000) #distance traveled every reload (in miles)
        self.step_dist2 = self.rov_speed2 / (self.frequency / 1000) #distance traveled every reload (in miles)

        self.im_thread = Thread(target = self.image_recognition)
        self.receive_thread = Thread(target=control.receive_files)
        self.send_thread1 = Thread(target=control.send_file, args = [int(control.que_num1_out),1])
        self.send_thread2 = Thread(target=control.send_file, args = [int(control.que_num2_out),2])
        ###################################

        ############ FUNCTIONS ############
        #rover movement functions
        def update_rov_loc():
            if (control.que_num1_in == 1):
                with open(os.path.join(os.getcwd(),"gps_folder","1_gps_coords_1","gps_coords_1.csv"), mode = "r") as rov_file:
                    rover_loc_file = csv.reader(rov_file, delimiter=",")
                    for line in rover_loc_file:
                        self.rover_list[1].set_position(float(line[0]), float(line[1]))
            if (control.que_num2_in == 1):
                with open(os.path.join(os.getcwd(),"gps_folder","1_gps_coords_2","gps_coords_2.csv"), mode = "r") as rov_file:
                    rover_loc_file = csv.reader(rov_file, delimiter=",")
                    for line in rover_loc_file:
                        self.rover_list[2].set_position(float(line[0]), float(line[1]))
            #read location files
            if os.path.exists(os.path.join(os.getcwd(),"gps_folder",str(control.que_num1_in - 1)+"_gps_coords_1","gps_coords_1.csv")):
                with open(os.path.join(os.getcwd(),"gps_folder",str(control.que_num1_in - 1)+"_gps_coords_1","gps_coords_1.csv"), mode = "r") as rov_file:
                    rover_loc_file = csv.reader(rov_file, delimiter=",")
                    for line in rover_loc_file:
                        try: a = float(line[0])
                        except: a = ''
                        try: b = float(line[1])
                        except: b = ''
                        if (isinstance(a, float)) and (isinstance(b, float)):
                            self.rover_list[1].set_position(float(line[0]), float(line[1]))
            if self.made_path1 or self.made_path2:
                self.calc_time()
            if os.path.exists(os.path.join(os.getcwd(),"gps_folder",str(control.que_num2_in - 1)+"_gps_coords_2","gps_coords_2.csv")):
                with open(os.path.join(os.getcwd(),"gps_folder",str(control.que_num2_in - 1)+"_gps_coords_2","gps_coords_2.csv"), mode = "r") as rov_file:
                    rover_loc_file = csv.reader(rov_file, delimiter=",")
                    for line in rover_loc_file:
                        try: a = float(line[0])
                        except: a = ''
                        try: b = float(line[1])
                        except: b = ''
                        if (isinstance(a, float)) and (isinstance(b, float)):
                            self.rover_list[2].set_position(float(line[0]), float(line[1]))

        def update_rov_speed():
            #set the speeds from the files
            with open(os.path.join(os.getcwd(),"gps_folder","rover_speed_1.csv"), mode='r') as file:
                rov_speed_file = csv.reader(file)
                for i in rov_speed_file:
                    self.rov_speed1 = float(i[-1])
            with open(os.path.join(os.getcwd(),"gps_folder","rover_speed_2.csv"), mode='r') as file:
                rov_speed_file = csv.reader(file)
                for i in rov_speed_file:
                    self.rov_speed2 = float(i[-1])

        def move():
            if self.move_call1 and not pf.pf_stop1: #and (self.made_path1 or self.made_file_path1)
                #write to emergency start/stop
                with open(os.path.join(os.getcwd(), "emg_stop_1.csv"), mode='w', newline='') as file:
                    write_file = csv.writer(file)
                    write_file.writerow('1')
                #make the movement path if not done already
                if (self.made_move_path1 != 1):
                    self.make_move_path(1)
                #manual movement
                if (self.move_control[0]):
                    print("moving 1 manually")
                    update_rov_loc()
                    self.calc_time()
                #automatic movement
                elif (self.made_file_path1):
                    print("moving 1 automatically")
                    update_rov_loc()
                    self.calc_time()
            elif not pf.pf_stop1:
                #write to emergency start/stop
                with open(os.path.join(os.getcwd(), "emg_stop_1.csv"), mode='w', newline='') as file:
                    write_file = csv.writer(file)
                    write_file.writerow('0') #0 means stop
            if (self.move_call2) and not pf.pf_stop2:
                #write to emergency start/stop
                with open(os.path.join(os.getcwd(), "emg_stop_2.csv"), mode='w', newline='') as file:
                    write_file = csv.writer(file)
                    write_file.writerow('1')
                #make the movement path if not done already
                if (self.made_move_path2 != 1):
                    self.make_move_path(2)
                #manual movement
                if (self.move_control[1]):
                    print("moving 2 manually")
                    update_rov_loc()
                    self.calc_time()
                #automatic movement
                elif (self.made_file_path2):
                    print("moving 2 automatically")
                    update_rov_loc()
                    self.calc_time()
            elif not pf.pf_stop2:
                #write to emergency start/stop
                with open(os.path.join(os.getcwd(), "emg_stop_2.csv"), mode='w', newline='') as file:
                    write_file = csv.writer(file)
                    write_file.writerow('0') #0 means stop
            return
        
        #read file functions
        def read_rov_loc_file(num):
            file_name = "gps_coords_"+str(num)+".csv"
            if num == 1:
                if os.path.exists(os.path.join(os.getcwd(),"gps_folder", str(control.que_num1_in - 1)+"_gps_coords_"+str(num), file_name)):
                    with open(os.path.join(os.getcwd(),"gps_folder", str(control.que_num1_in - 1)+"_gps_coords_"+str(num), file_name), mode='r') as file:
                        read_file = file.readlines()
                        return read_file
            else:
                if os.path.exists(os.path.join(os.getcwd(),"gps_folder", str(control.que_num2_in - 1)+"_gps_coords_"+str(num), file_name)):
                    with open(os.path.join(os.getcwd(),"gps_folder", str(control.que_num2_in - 1)+"_gps_coords_"+str(num), file_name), mode='r') as file:
                        read_file = file.readlines()
                        return read_file
        
        def read_obst_file():
            with open(os.path.join(os.getcwd(),"gps_folder","obstacle_locations.csv")) as file:
                read_file = file.readlines()
                return read_file
        
        def read_surv_data_file():
            with open(os.path.join(os.getcwd(),"im_rec_folder","surv_data.csv"), mode= 'r') as file:
                read_file = file.readlines()
                return read_file

        def read_surv_loc_file():
            with open(os.path.join(os.getcwd(),"im_rec_folder","survivor_locations.csv")) as file:
                read_file = file.readlines()
                return read_file
        
        def read_rov_move_file(num):
            file_name = "movement_data_"+str(num)+".csv"
            with open(os.path.join(os.getcwd(),"path_folder",file_name), mode='r') as file:
                read_file = file.readlines()
                return read_file

        def read_emg_file(num):
            file_name = "emg_stop_"+str(num)+".csv"
            with open(os.path.join(control.cwd, file_name),'r') as file:
                read_file = file.readlines()
                return read_file
        
        def read_results_folder():
            #get list of previous survivor coords
            surv_coords = []
            with open(os.path.join(os.getcwd(), "im_rec_folder", "survivor_locations.csv"), 'r') as file:
                read_file = csv.reader(file)
                for i in read_file:
                    try: a = float(i[0])
                    except: a = ''
                    try: b = float(i[1])
                    except: b = ''
                    if isinstance(a, float) and isinstance(b, float):
                        surv_coords.append((a, b))
            start_len = len(surv_coords)
            #get list of results files
            file_path_list = [os.path.join(os.getcwd(), "im_rec_folder", "results_folder", i) for i in os.listdir(os.path.join(os.getcwd(), "im_rec_folder", "results_folder"))]
            for i in file_path_list:
                with open(i, 'r') as file:
                    read_file = csv.reader(file)
                    x = list(read_file.__next__())
                    name = os.path.basename(i)
                    que_num = name.split("_")[0]
                    num = name.split("_")[-1]
                    num = num.split(".")[0]
                    #survivors
                    if (int(x[0]) > 0) and (self.surv_detect == 0):
                        print("new survivor detected")
                        try: make_surv_img()
                        except Exception as e: print("Error making survivor images:", e)
                        self.surv_detect = 1
                        for _ in range(int(x[0])):
                            if os.path.isdir(os.path.join(os.getcwd(), "gps_folder", str(que_num)+"_gps_coords_"+str(num))):
                                with open(os.path.join(os.getcwd(), "gps_folder", str(que_num)+"_gps_coords_"+str(num), "gps_coords_"+str(num)+".csv"), 'r') as file1:
                                    reader_file = csv.reader(file1)
                                    for j in reader_file:
                                        try: a = float(j[0])
                                        except: a = ''
                                        try: b = float(j[1])
                                        except: b = ''
                                        if isinstance(a, float) and isinstance(b, float):
                                            surv_coords.append((a, b))
                    elif (int(x[0]) == 0):
                        if self.surv_detect == 1:
                            self.surv_detect = 0
                    #obstacles
                    if (int(x[1]) == 0):
                        print("obstacle left")
                        if (int(num) == 1) and (self.obst_detect1 == 1):
                            self.obst_detect1 = 0
                            pf.pf_stop1 = 0
                        elif (int(num) == 2) and (self.obst_detect2 == 1):
                            self.obst_detect2 = 0
                            pf.pf_stop2 = 0
                        #self.pf_obstacle(int(num))
                if len(surv_coords) > start_len:
                    with open(os.path.join(os.getcwd(), "im_rec_folder", "survivor_locations.csv"), 'w', newline='') as file2:
                        write_file = csv.writer(file2)
                        write_file.writerows(surv_coords)
                #except Exception as e: print("Error making survivor images:", e)
                #get rid of used results file
                try: os.remove(i)
                except: print("couldn't remove results file", i)
        
        def process_surv_loc_file():
            if (self.surv_pin_list != []):
                self.clear_survivors()
            with open(os.path.join(os.getcwd(),"im_rec_folder","survivor_locations.csv"), mode='r') as file:
                file1 = csv.reader(file, delimiter=",")
                for i in file1:
                    coordinates = []
                    for j in i:
                        if (j == []): continue
                        else: coordinates.append(float(j))
                    if (len(coordinates) == 2):
                        self.place_survivor(coordinates)
            for i in self.surv_pin_list:
                self.click_pin(i)
        
        def process_surv_data_file():
            if (self.surv_pin_list != []):
                with open(os.path.join(os.getcwd(),"im_rec_folder","surv_data.csv"), mode='r') as file:
                    file1 = csv.reader(file, delimiter=',')
                    counter = 0
                    temp_survivor_num = self.survivor_num
                    for line in file1:
                        if (counter < len(self.surv_pin_list)):
                            self.survivor_num = counter + 1
                            surv_img = self.create_surv_image()
                            self.surv_pin_list[counter].image = surv_img
                        counter += 1
                    self.survivor_num = temp_survivor_num

        #control script functions
        def make_surv_img():
            '''
            Takes an image and a bounding box for a detection and crops it to make a survivor image.

            @param image: Path to image that will be copyed and cropped to make the survivor image.
            @param tensor: List that includes information about the bounding box of the detected object. format = [x_center, y_center, width, height]
            '''
            if os.path.exists(os.path.join(os.getcwd(), "im_rec_folder", "person")):
                predict_im_list = [x for x in os.listdir(os.path.join(os.getcwd(), "im_rec_folder", "person"))]
                que = ''
                if predict_im_list != []: predict = predict_im_list[0].split("_")[0]
                else: predict = ''
                for x in predict_im_list:
                    if os.path.exists(os.path.join(os.getcwd(), "im_rec_folder", "person", x)):
                        #add image path to list
                        que = x.split("_")[0]
                        if self.surv_detect == 0:
                            predict = que
                        else: predict = ''
                        if (predict == que) and (os.path.join(os.getcwd(), "im_rec_folder", "person", x) not in self.image_path_list):
                            self.image_path_list.append(os.path.join(os.getcwd(), "im_rec_folder", "person", x))
                        #resave the image with new name
                        image = os.path.join(os.getcwd(), "im_rec_folder", "person", x)
                        if image in self.image_path_list:
                            #open image
                            im = Image.open(image)
                            #set new name and save
                            self.surv_count += 1
                            pic_name = 'surv_pic'+str(self.surv_count)+'.jpg'
                            im.save(os.path.join(os.getcwd(),'im_rec_folder',pic_name))
                        #delete used image
                        os.remove(os.path.join(os.getcwd(), "im_rec_folder", "person",x))
            return

        def wayp_achieve(num):
            if num == 1:
                current_coord = []
                with open(os.path.join(os.getcwd(), "gps_folder", str(control.que_num1_in - 1)+"_gps_coords_1", "gps_coords_1.csv"), 'r') as file:
                    read_file = csv.reader(file, delimiter=",")
                    for i in read_file:
                        try: a = float(i[0])
                        except: a = ''
                        try: b = float(i[1])
                        except: b = ''
                        if isinstance(a, float) and isinstance(b, float):
                            current_coord = [float(i[0]), float(i[1])]
                        else: current_coord = self.rover_list[1].position
                dist1 = self.calc_distance(current_coord, self.position_list1[1])
                print("Distance to first waypoint for rover 1", dist1)
                if dist1 <= 1:
                    #delete first waypoint in list
                    self.delete_path(1)
                    #delete point position_list1[1] from mega list
                    if (self.position_list1[1] in self.position_list):
                        self.position_list.remove(self.position_list1[1])
                    #delete marker from map
                    self.waypoint_list1[1].delete()
                    #delete points from lists
                    del self.waypoint_list1[1]
                    del self.position_list1[1]
                    #decrement wayp_index
                    self.wayp_index1 -= 1
                    if (self.wayp_index1 == 0): #stop manual movement
                        self.move_control[0] = 0
                #delete movement_end file
                shutil.move(os.path.join(os.getcwd(), "gps_folder", "movement_end_1.csv"), os.path.join(os.getcwd(), "movement_end_1.csv"))
                #calibrate rover 1
                #self.pf_cal_thread1.start()
                #create new path
                reset = 0
                if self.rover_num != 1: reset = 1
                self.rover_num = 1
                self.create_path()
                self.calc_time()
                if reset: self.rover_num = 2
            else:
                current_coord = []
                with open(os.path.join(os.getcwd(), "gps_folder", str(control.que_num2_in - 1)+"_gps_coords_2", "gps_coords_2.csv"), 'r') as file:
                    read_file = csv.reader(file, delimiter=",")
                    for i in read_file:
                        try: a = float(i[0])
                        except: a = ''
                        try: b = float(i[1])
                        except: b = ''
                        if isinstance(a, float) and isinstance(b, float):
                            current_coord = [float(i[0]), float(i[1])]
                        else: current_coord = self.rover_list[2].position
                dist2 = self.calc_distance(current_coord, self.position_list2[1])
                print("Distance to first waypoint for rover 2 =", dist2)
                if dist2 <= 1:
                    #delete first waypoint in list
                    self.delete_path(2)
                    #delete point position_list2[1] from mega list
                    if (self.position_list2[1] in self.position_list):
                        self.position_list.remove(self.position_list2[1])
                    #delete marker from map
                    self.waypoint_list2[1].delete()
                    #delete points from lists
                    del self.waypoint_list2[1]
                    del self.position_list2[1]
                    #decrement wayp_index
                    self.wayp_index2 -= 1
                    if (self.wayp_index2 == 0): #stop manual movement
                        self.move_control[0] = 0
                #delete movement_end file
                shutil.move(os.path.join(os.getcwd(), "gps_folder", "movement_end_2.csv"), os.path.join(os.getcwd(), "movement_end_2.csv"))
                #calibrate rover 2
                #self.pf_cal_thread2.start()
                #while not os.path.exists(os.path.join(os.getcwd(), "gps_folder", "movement_end_2.csv")): continue
                #create new path
                reset = 0
                if self.rover_num != 2: reset = 1
                self.rover_num = 2
                self.create_path()
                self.calc_time()
                if reset: self.rover_num = 1

        def start_receive_file():
            with open(os.path.join(os.getcwd(), "receive_file.csv"), mode='w') as file:
                write_file = csv.writer(file)
                write_file.writerow('1')
        
        def check_error():
            if (control.server_err == 2):
                control.server_err = 0
            elif (control.server_err == 1):
                with open(os.path.join(os.getcwd(), "receive_file.csv"), 'w') as file:
                    write_file = csv.writer(file)
                    write_file.writerow('0')
                control.server_err = 0
            if (control.send_err1 == -1):
                with open(os.path.join(os.getcwd(), "send_err1.txt"), 'r') as file:
                    read_file = file.readlines()
                    #output error message to terminal
                    for i in read_file:
                        print(i)
                control.send_err1 = 0
                ''' #get que num of the file not sent
                    file_name = os.path.basename(read_file[-1])
                    filename = file_name.split(':')[-1]
                    i = filename.split('_')[0]
                    #attempt to send the file again
                    self.send_thread1 = Thread(target=control.send_file, args=[int(i), 1])
                    self.send_thread1.start()
                    #reset send_thread to follow normal que
                    self.send_thread1 = Thread(target=control.send_file, args=[int(control.que_num1_out), 1])'''
            if (control.send_err2 == -1):
                with open(os.path.join(os.getcwd(), "send_err2.txt"), 'r') as file:
                    read_file = file.readlines()
                    #output error message to terminal
                    for i in read_file:
                        print(i)
                control.send_err2 = 0
                '''#get que num of the file not sent
                    file_name = os.path.basename(read_file[-1])
                    filename = file_name.split(':')[-1]
                    i = filename.split('_')[0]
                    #attempt to send the file again
                    self.send_thread2 = Thread(target=control.send_file, args=[int(i), 2])
                    self.send_thread2.start()
                    #reset send_thread to follow normal que
                    self.send_thread2 = Thread(target=control.send_file, args=[int(control.que_num2_out), 2])'''
        ###################################
                
        #setup for unpacking files
        if (self.setup == 1):
            #start receiving files
            start_receive_file()
            self.receive_thread.start()
            #clear input files
            files = glob.glob(os.path.join(os.getcwd(), "input_files", "*"))
            for file in files:
                os.remove(file)
            #clear output files
            files = glob.glob(os.path.join(os.getcwd(), "output_files", "*"))
            for file in files:
                os.remove(file)
            #setup que number files
            with open(os.path.join(os.getcwd(),"que_1_in.csv"), mode="w") as file:
                test_file = csv.writer(file)
                test_file.writerow([1])
            with open(os.path.join(os.getcwd(),"que_2_in.csv"), mode="w") as file:
                test_file = csv.writer(file)
                test_file.writerow([1])
            with open(os.path.join(os.getcwd(),"que_1_out.csv"), mode="w") as file:
                test_file = csv.writer(file)
                setup_val = [1]
                test_file.writerow(setup_val)
            with open(os.path.join(os.getcwd(),"que_2_out.csv"), mode="w") as file:
                test_file = csv.writer(file)
                setup_val = [1]
                test_file.writerow(setup_val)
            #start image processing
            im_rec.run_ml = 1
            self.ml_thread.start()
        
        #setup que files at lowest que
        if (self.load_counter % 2 == 0):
            file1 = control.get_file_with_lowest_queue(1)
            if file1 != '':
                control.get_queue_number(file1,1)
                with open(os.path.join(os.getcwd(),"que_1_in.csv"), mode="w") as file:
                    test_file = csv.writer(file)
                    test_file.writerow([control.setup_val1])
            file2 = control.get_file_with_lowest_queue(2)
            if file2 != '':
                control.get_queue_number(file2,2)
                with open(os.path.join(os.getcwd(),"que_2_in.csv"), mode="w") as file:
                    test_file = csv.writer(file)
                    test_file.writerow([control.setup_val2])
        
        #unpack the zip file
        control.unpack_zip_file(1)
        control.unpack_zip_file(2)
        
        #initial setup
        if (self.setup == 1):
            #set ip address csv file
            control.get_ip_csv()
            #set rover locations and speeds
            update_rov_loc()
            update_rov_speed()
            #set map at rover 1
            self.map_widget.set_position(self.rover_list[1].position[0], self.rover_list[1].position[1])
            
            #setup im rec que num as lowest file number
            self.im_rec_que_1 = control.setup_val1
            self.im_rec_que_2 = control.setup_val2
            #initialize image recognition
            self.im_thread.start()

            #clear obst/surv location files
            with open(os.path.join(os.getcwd(),"im_rec_folder","survivor_locations.csv"), mode='w', newline='') as file:
                test_file = csv.writer(file)
                setup_list = ''
                test_file.writerow(setup_list)
            with open(os.path.join(os.getcwd(),"gps_folder","obstacle_locations.csv"), mode='w', newline='') as file:
                test_file = csv.writer(file)
                setup_list = ''
                test_file.writerow(setup_list)
            with open(os.path.join(os.getcwd(),"path_folder","movement_data_1.csv"), mode='w', newline='') as file:
                test_file = csv.writer(file)
                setup_list = [['F$0'],['F$3.048'], ['F$0']]
                test_file.writerows(setup_list)
            with open(os.path.join(os.getcwd(),"path_folder","movement_data_2.csv"), mode='w', newline='') as file:
                test_file = csv.writer(file)
                setup_list = [['F$0'],['F$3.048'], ['F$0']]
                test_file.writerows(setup_list)
            
            #remove gps_coords folders
            name_list = [x for x in os.listdir(os.path.join(os.getcwd(), "gps_folder")) if x.__contains__("_gps_coords_")]
            path_list = []
            for i in name_list:
                if ((i != "1_gps_coords_1") and (i != "1_gps_coords_2")):
                    path_list.append(os.path.join(os.getcwd(), "gps_folder", i))
            for i in path_list:
                shutil.rmtree(i)
            #remove results csv files
            name_list = os.listdir(os.path.join(os.getcwd(), "im_rec_folder", "results_folder"))
            path_list = [os.path.join(os.getcwd(), "im_rec_folder", "results_folder", x) for x in name_list]
            for i in path_list: os.remove(i)
            #remove used image files
            name_list = os.listdir(os.path.join(os.getcwd(), "im_rec_folder", "used"))
            path_list = [os.path.join(os.getcwd(), "im_rec_folder", "used", x) for x in name_list]
            for i in path_list: os.remove(i)
            #remove survivor pictures
            name_list = [x for x in os.listdir(os.path.join(os.getcwd(), "im_rec_folder")) if x.__contains__("surv_pic")]
            path_list = [os.path.join(os.getcwd(), "im_rec_folder", x) for x in name_list]
            for i in path_list: os.remove(i)
            #remove survivor data pictures
            name_list = [x for x in os.listdir(os.path.join(os.getcwd(), "images")) if (x.__contains__("surv_img") and x != "blank_surv_img.jpg")]
            path_list = [os.path.join(os.getcwd(), "images", x) for x in name_list]
            for i in path_list: os.remove(i)
            #remove video pictures
            name_list = [x for x in os.listdir(os.path.join(os.getcwd(), "image_recognition")) if x.__contains__("video_pic")]
            path_list = [os.path.join(os.getcwd(), "image_recognition", x) for x in name_list]
            for i in path_list: os.remove(i)
            #remove unnecessary image detections
            name_list = [x for x in os.listdir(os.path.join(os.getcwd(), "im_rec_folder")) if not (x.__contains__("im_process") or 
                                                                                                   x.__contains__("person") or 
                                                                                                   x.__contains__("results_folder") or 
                                                                                                   x.__contains__("used") or 
                                                                                                   x.__contains__("surv_data") or
                                                                                                   x.__contains__("survivor_locations") or
                                                                                                   x.__contains__("video_pic"))]
            path_list = [os.path.join(os.getcwd(), "im_rec_folder", x) for x in name_list]
            for i in path_list: shutil.rmtree(i)

            #TEST SETUP
            '''with open(os.path.join(os.getcwd(),"path_folder","test_path.csv"), mode='w') as file:
                test_file = csv.writer(file)
                setup_list = [[1,30.6136630,-96.3431937],[1,30.6136814,-96.3429041]]
                test_file.writerows(setup_list)
            self.path_file_change = 1
            with open(os.path.join(os.getcwd(),"im_rec_folder","survivor_locations.csv"), mode='w') as file:
                test_file = csv.writer(file)
                setup_list = [[30.6136814,-96.3429041]]
                test_file.writerows(setup_list)
            with open(os.path.join(os.getcwd(),"im_rec_folder","surv_data.csv"), mode='w') as file:
                test_file = csv.writer(file)
                setup_list = [['Female','20-25','Bad']]
                test_file.writerows(setup_list)
            with open(os.path.join(os.getcwd(),"gps_folder","obstacle_locations.csv"), mode='w') as file:
                test_file = csv.writer(file)
                setup_list = [[]]
                test_file.writerows(setup_list)
            self.create_path()
            self.place_obstacle()
            process_surv_loc_file()'''

            #initialize file variables
            self.initial2 = read_obst_file()
            self.initial3 = read_surv_loc_file()
            self.initial4 = read_surv_data_file()
            self.initial5 = read_rov_loc_file(1)
            self.initial6 = read_rov_loc_file(2)
            self.initial7 = read_rov_move_file(1)
            self.initial8 = read_rov_move_file(2)
            self.initial9 = read_emg_file(1)
            self.initial10 = read_emg_file(2)

            #start creating output files and sending them
            control.output_zip_file(1)
            self.send_thread1.start()
            control.output_zip_file(2)
            self.send_thread2.start()

            self.setup = 0
        
        #call move
        if (self.move_call1 or self.move_call2):
            move()

        #check if pathfinding says obstacle found
        if pf.pf_stop1:
            print("Obstacle detected by rover 1")
            if (self.obst_detect1 == 0) and (self.obst_timer1%5 == 0):
                self.pf_obstacle(1)
                self.obst_detect1 = 1
            self.obst_timer1 += 1
        else: self.obst_detect1 = 0
        if pf.pf_stop2:
            print("Obstacle detected by rover 2")
            if (self.obst_detect2 == 0) and (self.obst_timer2%5 == 0):
                self.pf_obstacle(2)
                self.obst_detect2 = 1
            self.obst_timer2 += 1
        else: self.obst_detect2 = 0
        
        #check if movement_end file found
        if os.path.exists(os.path.join(os.getcwd(), "gps_folder", "movement_end_1.csv")):
            print("Found movement_end_1.csv")
            if self.wayp_index1 > 0: wayp_achieve(1)
            else: shutil.move(os.path.join(os.getcwd(), "gps_folder", "movement_end_1.csv"), os.path.join(os.getcwd(), "movement_end_1.csv"))
        if os.path.exists(os.path.join(os.getcwd(), "gps_folder", "movement_end_2.csv")):
            print("Found movement_end_2.csv")
            if self.wayp_index2 > 0: wayp_achieve(2)
            else: shutil.move(os.path.join(os.getcwd(), "gps_folder", "movement_end_2.csv"), os.path.join(os.getcwd(), "movement_end_2.csv"))

        #check if server is running properly
        if ((control.server_err != 0) or (control.send_err1 != 0) or (control.send_err2 != 0)) and (self.load_counter >1):
            if control.server_err == 1:
                global message, message_print
                message = []
                message_print = ''
                with open(os.path.join(os.getcwd(), "server_err.txt"),'r') as file:
                    lines = file.readlines()
                    for i in lines:
                        if i!=[]:
                            message.append(i)
                for i in message:
                    message_print += str(i) + '\n'
                if message_print != '':
                    #tk.messagebox.showerror("Server Error!", message_print)
                    print(message_print)
            check_error()
        
        #start image processing
        if (not self.im_thread.is_alive()) and (self.load_counter>=1):
            self.im_thread.start()

        #update image processing results
        #make_surv_img()
        if self.load_counter == 5: read_results_folder()

        #delete oldest gps_coords folder after 5 exist
        name_list1 = [x for x in os.listdir(os.path.join(os.getcwd(), "gps_folder")) if x.__contains__("_gps_coords_1")]
        path_list1 = []
        path1 = ''
        for i in name_list1:
            if (i != "1_gps_coords_1"):
                path_list1.append(os.path.join(os.getcwd(), "gps_folder", i))
        if len(path_list1) > 5:
            base_list = [os.path.basename(x) for x in path_list1]
            que_list = [int(x.split("_")[0]) for x in base_list]
            que_list.sort()
            for i in base_list:
                que = i.split("_")[0]
                if int(que) == que_list[0]:
                    path1 = os.path.join(os.getcwd(), "gps_folder", i)
                    break
            if path1 != '': shutil.rmtree(path1)
        name_list2 = [x for x in os.listdir(os.path.join(os.getcwd(), "gps_folder")) if x.__contains__("_gps_coords_2")]
        path_list2 = []
        path2 = ''
        for i in name_list2:
            if (i != "1_gps_coords_2"):
                path_list2.append(os.path.join(os.getcwd(), "gps_folder", i))
        if len(path_list2) > 5:
            base_list = [os.path.basename(x) for x in path_list2]
            que_list = [int(x.split("_")[0]) for x in base_list]
            que_list.sort()
            for i in base_list:
                que = i.split("_")[0]
                if int(que) == que_list[0]:
                    path2 = os.path.join(os.getcwd(), "gps_folder", i)
                    break
            if path2 != '': shutil.rmtree(path2)
        
        #update video image 1
        pic_name_list = [x for x in os.listdir(os.path.join(os.getcwd(), "im_rec_folder", "used")) if x.__contains__("video_pic_1")]
        pic_name_list.sort()
        pic_path = ''
        for i in pic_name_list:
            que = i.split("_")[0]
            if int(que) == (control.que_num1_in - 2):
                pic_path = os.path.join(os.getcwd(), "im_rec_folder", "used", i)
            elif int(que) < (control.que_num1_in - 2):
                os.remove(os.path.join(os.getcwd(), "im_rec_folder", "used", i))
        if (pic_path != '') and os.path.exists(pic_path):
            img1 = Image.open(pic_path)
            img1.save(os.path.join(os.getcwd(), "im_rec_folder", "video_pic_1.jpg"))
            os.remove(pic_path)
        #update video image 2
        pic_name_list = [x for x in os.listdir(os.path.join(os.getcwd(), "im_rec_folder", "used")) if x.__contains__("video_pic_2")]
        pic_name_list.sort()
        pic_path = ''
        for i in pic_name_list:
            que = i.split("_")[0]
            if int(que) == (control.que_num2_in - 2):
                pic_path = os.path.join(os.getcwd(), "im_rec_folder", "used", i)
            elif int(que) < (control.que_num2_in - 2):
                os.remove(os.path.join(os.getcwd(), "im_rec_folder", "used", i))
        if (pic_path != '') and os.path.exists(pic_path):
            img1 = Image.open(pic_path)
            img1.save(os.path.join(os.getcwd(), "im_rec_folder", "video_pic_2.jpg"))
            os.remove(pic_path)
        
    
        #check if file changed
        current2 = read_obst_file()
        current3 = read_surv_loc_file()
        current4 = read_surv_data_file()
        current5 = read_rov_loc_file(1)
        current6 = read_rov_loc_file(2)
        current7 = read_rov_move_file(1)
        current8 = read_rov_move_file(2)
        current9 = read_emg_file(1)
        current10 = read_emg_file(2)
        if (self.initial2 != current2): #check obstacle file
            print("obstacles changed")
            self.place_obstacle()
            print("obstacle count =", len(self.obstacle_list))
            self.initial2 = current2
        if (self.initial3 != current3): #check survivor loc file
            print("survivor locations changed")
            process_surv_loc_file()
            self.initial3 = current3
        if (self.initial4 != current4): #check surv data file
            print("survivor data changed")
            process_surv_data_file()
            self.initial4 = current4
        if (self.initial5 != current5): #check rover loc file 1
            print("rover locations changed")
            update_rov_loc()
            self.initial5 = current5
        if (self.initial6 != current6): #check rover loc file 2
            print("rover locations changed")
            update_rov_loc()
            self.initial6 = current6
        if (self.initial7 != current7): #check movement data 1
            print("new movement data 1")
            control.send_movement1 = 1
            self.initial7 = current7
        if (self.initial8 != current8): #check movement data 2
            print("new movement data 2")
            control.send_movement2 = 1
            self.initial8 = current8
        if (self.initial9 != current9): #check emg stop data 1
            print("new emg stop data 1")
            control.send_emg1 = 1
            self.initial9 = current9
        if (self.initial10 != current10): #check emg stop data 2
            print("new emg stop data 2")
            control.send_emg2 = 1
            self.initial10 = current10

        #output and send zip file if something changed
        if ((control.send_movement1 or control.send_emg1) and not self.send_thread1.is_alive()):
            control.output_zip_file(1)
            self.send_thread1.start()
        if ((control.send_movement2 or control.send_emg2) and not self.send_thread2.is_alive()):
            control.output_zip_file(2)
            self.send_thread2.start()

        print("Current que_num1_in =", control.que_num1_in)
        #print("Current que_num2_in =", control.que_num2_in)

        #reset load counter
        if (self.load_counter == 6):
            self.load_counter = 0

        #test printing
        print("loaded")
        #reload the system
        self.load_counter += 1
        self.after(self.frequency, self.reload)
    pass

class VidWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry("310x190")
        self.title("Rover "+str(parent.rover_num)+" Camera Feed")

        ############ VARIABLES ############
        self.setup1 = 0
        self.setup2 = 0
        self.personal_rover_num = parent.rover_num
        self.initial_1 = os.path.getmtime(os.path.join(os.getcwd(),"im_rec_folder","video_pic_1.jpg"))
        self.initial_2 = os.path.getmtime(os.path.join(os.getcwd(),"im_rec_folder","video_pic_2.jpg"))
        self.aspect_ratio = 290 / 170
        ###################################

        ############# WIDGETS #############
        self.feed_canvas1 = tk.Canvas(master=self, width = 300, height = 180, bg = '#B4ECFF')
        self.feed_canvas2 = tk.Canvas(master=self, width = 300, height = 180, bg = '#B4ECFF')
        ###################################

        ############# PACKING #############
        if (parent.rover_num == 1): self.feed_canvas1.pack(anchor=tk.CENTER, fill="both", expand=True)
        else: self.feed_canvas2.pack(anchor=tk.CENTER, fill="both", expand=True)
        ###################################
        
        self.reload2(parent)
    pass

    def reload2(self, parent):
        ############ VARIABLES ############ 
        global vid_image1, vid_image2, feed_image1, feed_image2

        current_1 = os.path.getmtime(os.path.join(os.getcwd(),"im_rec_folder","video_pic_1.jpg"))
        current_2 = os.path.getmtime(os.path.join(os.getcwd(),"im_rec_folder","video_pic_2.jpg"))
        self.personal_rover_num = parent.rover_num
        ###################################

        if (self.personal_rover_num==1):
            #setup initial picture
            if (self.setup1==0):
                img_pil1 = Image.open(os.path.join(os.getcwd(),"im_rec_folder","video_pic_1.jpg"))
                img_pil1 = img_pil1.resize((290,170))
                vid_image1 = ImageTk.PhotoImage(img_pil1)
                feed_image1 = self.feed_canvas1.create_image(7,7,anchor=tk.NW,image=vid_image1)
                self.setup1 = 1
            #check if image changed and reload it
            if (self.initial_1 != current_1):
                self.feed_canvas1.delete(feed_image1)
                img_pil1 = Image.open(os.path.join(os.getcwd(),"im_rec_folder","video_pic_1.jpg"))
                img_pil1 = img_pil1.resize((self.new_width, self.new_height))
                vid_image1 = ImageTk.PhotoImage(img_pil1)
                feed_image1 = self.feed_canvas1.create_image(7,7,anchor=tk.NW,image=vid_image1)
                self.initial_1 = current_1
        else:
            #setup initial picture
            if (self.setup2==0):
                img_pil2 = Image.open(os.path.join(os.getcwd(),"im_rec_folder","video_pic_2.jpg"))
                img_pil2 = img_pil2.resize((290,170))
                vid_image2 = ImageTk.PhotoImage(img_pil2)
                feed_image2 = self.feed_canvas2.create_image(7,7,anchor=tk.NW,image=vid_image2)
                self.setup2 = 1
            #check if image changed and reload it
            if (self.initial_2 != current_2):
                self.feed_canvas2.delete(feed_image2)
                img_pil2 = Image.open(os.path.join(os.getcwd(),"im_rec_folder","video_pic_2.jpg"))
                img_pil2 = img_pil2.resize((self.new_width, self.new_height))
                vid_image2 = ImageTk.PhotoImage(img_pil2)
                feed_image2 = self.feed_canvas2.create_image(7,7,anchor=tk.NW,image=vid_image2)
                self.initial_2 = current_2

        self.after(1000, lambda: self.reload2(parent))
    pass

    def resize_image(self, event):
        global vid_image1, vid_image2, feed_image1, feed_image2
        self.new_width = event.width - 14
        self.new_height = int(self.new_width / self.aspect_ratio)
        if self.new_height > (event.height - 14):
            self.new_height = event.height - 14
            self.new_width = int(self.new_height * self.aspect_ratio)
        if self.personal_rover_num == 1:
            vid_window1.feed_canvas1.delete(feed_image1)
            img_pil1 = Image.open(os.path.join(os.getcwd(),"im_rec_folder","video_pic_1.jpg"))
            img_pil1 = img_pil1.resize((self.new_width, self.new_height))
            vid_image1 = ImageTk.PhotoImage(img_pil1)
            feed_image1 = vid_window1.feed_canvas1.create_image(7,7,anchor=tk.NW,image=vid_image1)
        elif self.personal_rover_num == 2:
            vid_window2.feed_canvas2.delete(feed_image2)
            img_pil2 = Image.open(os.path.join(os.getcwd(),"im_rec_folder","video_pic_2.jpg"))
            img_pil2 = img_pil2.resize((self.new_width, self.new_height))
            vid_image2 = ImageTk.PhotoImage(img_pil2)
            feed_image2 = vid_window2.feed_canvas2.create_image(7,7,anchor=tk.NW,image=vid_image2)

#set the application window object
app = Application(master=window)

############ GRID FOR WINDOW ############
window.rowconfigure(0, weight=0)
window.rowconfigure(1, weight=1)
window.columnconfigure(0, weight=0)
window.columnconfigure(1, weight=1)
##########################################

def on_close():
    '''
    If window closes, run crash protection. Stop the rover, stop network sending.
    '''
    im_rec.run_ml = 0
    app.rover_num = 1
    app.stop_move()
    control.output_zip_file(1)
    app.rover_num = 2
    app.stop_move()
    control.output_zip_file(2)
    #wait for server to stop
    '''while (app.send_thread1.is_alive() or app.send_thread2.is_alive()):
        continue'''
    #close servers
    '''control.send1.close()
    control.send2.close()'''
    with open(os.path.join(os.getcwd(), "receive_file.csv"), 'w') as file:
        writefile = csv.writer(file)
        writefile.writerow('0')
    #print terminal note to save files
    print(colored("\nWindow closure detected. Stopping rovers.", 'red'))
    print("Please save any necessary files in a separate location before running the program again.\n")
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_close)
#window.bind("<Destroy>", lambda event:crash_detection())

'''def image_recognition():
    print("start image rec")
    if (os.path.isdir(os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_1)+"_images_1"))):
        print("starting image recognition 1 for que num",self.im_rec_que_1)
        img = least_blurry([os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_1)+"_images_1", "video_pic_1_1.jpg"), 
                            os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_1)+"_images_1", "video_pic_1_2.jpg"), 
                            os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_1)+"_images_1", "video_pic_1_3.jpg"), 
                            os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_1)+"_images_1", "video_pic_1_4.jpg"), 
                            os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_1)+"_images_1", "video_pic_1_5.jpg")])
        self.im_rec_que_1 += 1
        print("im_rec_que_1 =",self.im_rec_que_1)
        x = ml_running(img)
        with open(os.path.join(os.getcwd(),"im_rec_folder", "detections_1.csv"), 'w') as file:
            write_file = csv.writer(file)
            write_file.writerow(x)
    else: pass

    if (os.path.isdir(os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_2)+"_images_2"))):
        print("starting image recognition 2 for que num",self.im_rec_que_2)
        img = least_blurry([os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_2)+"_images_2", "video_pic_1_1.jpg"), 
                            os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_2)+"_images_2", "video_pic_1_2.jpg"), 
                            os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_2)+"_images_2", "video_pic_1_3.jpg"), 
                            os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_2)+"_images_2", "video_pic_1_4.jpg"), 
                            os.path.join(os.getcwd(), "im_rec_folder", str(self.im_rec_que_2)+"_images_2", "video_pic_1_5.jpg")])
        self.im_rec_que_2 += 1
        print("im_rec_que_2 =",self.im_rec_que_2)
        x = ml_running(img)
        with open(os.path.join(os.getcwd(),"im_rec_folder", "detections_2.csv"), 'w') as file:
            write_file = csv.writer(file)
            write_file.writerow(x)
    else: pass'''

####### MAIN LOOP #######
if __name__ == '__main__':
    app.mainloop()
#########################