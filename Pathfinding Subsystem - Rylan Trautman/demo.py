import numpy as py
import BSLoop as bs
import pathfinding as pf
import csv


#initialize values
operation = True

rover1_start = (20,2)
rover2_start = (14,4)
rover_coords = [rover1_start, rover2_start]
points_of_interest = [(1,14),(5,14),(3,2),(6,28),(7,19),
                      (7,27),(16,2),(30,30),(38,12),(35,6),(32,5)]
temp1, temp2 = bs.roverBoundaries(rover1_start,rover2_start,points_of_interest)
rover1_list = [rover1_start]
rover1_list += temp1
rover2_list = [rover2_start]
rover2_list += temp2

rover1_gps = pf.scaleGrid(rover1_start, dimension = (40,35), output = "GPS")
rover2_gps = pf.scaleGrid(rover2_start, dimension = (40,35), output = "GPS")

POI_gps1 = []
POI_gps2 = []
for i in range(0,len(rover1_list)-1):
    POI_gps1.append(pf.scaleGrid(rover1_list[i],dimension = (40,35), output = "GPS"))
for i in range(0,len(rover2_list)-1):
    POI_gps2.append(pf.scaleGrid(rover2_list[i],dimension = (40,35), output = "GPS"))

diagram= pf.GridWithWeights(40, 35)
diagram.walls = []
diagram.rovers = rover_coords
diagram.poi0 = points_of_interest
diagram.poi1 = []
diagram.poi2 = []
pf.draw_grid(diagram)
diagram.poi0 = []
diagram.poi1 = temp1
diagram.poi2 = temp2


total_path1 = []
total_path2 = []

next_orientation1 = [0,1]
next_orientation2 = [0,1]

i = 0 #rover1_list index
j = 0 #rover2_list index
rover1_change = True #decides whether we need to look at next POI
rover2_change = True
pf.draw_grid(diagram)
final_r1 = len(rover1_list) - 1 
final_r2 = len(rover2_list) - 1

#csv function:
def list2csv(list, filename):
    with open(filename+".csv", 'w', newline='') as myfile:
        write = csv.writer(myfile)
        for s in list:
            write.writerow([s])
    return

list2csv(POI_gps1, "rover1poi")
list2csv(POI_gps2, "rover2poi")

userinput = input("Press enter to begin operation.")
while operation == True:
    if i < len(rover1_list)-1 and rover1_change == True: #iterate through the first list to create a path and instructions
        path1_gps = []
        came_from1, cost_so_far1 = pf.a_star_search(diagram, rover1_list[i], rover1_list[i+1])
        path1=pf.reconstruct_path(came_from1, start=rover1_list[i], goal=rover1_list[i+1])
        instructions1 = pf.instructionset(path1, current_orientation = next_orientation1)
        i += 1
        rover1_change = False
        next_orientation1 = pf.getOrientation([diagram.rovers[0],path1[1]], 0)
        for p in path1:
            path1_gps.append(pf.scaleGrid(p, dimension = (40,35), output = "GPS"))
        list2csv(instructions1, "instructions1")
        list2csv(path1_gps, "path1")
        print("Rover 1 instructions1.csv and path1.csv updated")
    if j < len(rover2_list)-1 and rover2_change == True:
        path2_gps = []
        came_from2, cost_so_far2 = pf.a_star_search(diagram, rover2_list[j], rover2_list[j+1])
        path2=pf.reconstruct_path(came_from2, start=rover2_list[j], goal=rover2_list[j+1])        
        j += 1
        rover2_change = False
        instructions2 = pf.instructionset(path2, current_orientation = next_orientation2)
        next_orientation2 = pf.getOrientation([diagram.rovers[1],path2[1]], 0)
        list2csv(instructions2, "instructions2")
        for p in path2:
            path2_gps.append(pf.scaleGrid(p, dimension = (40,35), output = "GPS"))
        list2csv(instructions2, "instructions2")
        list2csv(path2_gps, "path2")
        print("Rover 2 instructions2.csv and path2.csv updated")
    total_path = path1 + path2
    pf.draw_grid(diagram, path=total_path)
    print("Rover 1 is currently located at " + str(pf.scaleGrid(diagram.rovers[0], dimension = (40,35), output = "GPS")))
    if diagram.rovers[0] != rover1_list[-1]:
        print("Rover 1 is heading towards"+str(pf.scaleGrid(rover1_list[i], dimension = (40,35), output = "GPS")))
        print("Rover 1 has "+str(len(rover1_list) - i)+" points left to check")
    else:
        print("Rover 1 has completed its operation")
    print("Rover 2 is currently located at " + str(pf.scaleGrid(diagram.rovers[1], dimension = (40,35), output = "GPS")))
    if diagram.rovers[1] != rover2_list[-1]:    
        print("Rover 2 is heading towards"+str(pf.scaleGrid(rover2_list[j], dimension = (40,35), output = "GPS")))
        print("Rover 2 has "+str(len(rover2_list) - j)+" points left to check")
    else:
        print("Rover 2 has complete its operation")
    userinput = input("Press enter to continue operation.")
    #area for obstacle detection
    if userinput == "c": #rover 1 detection
        print("Rover 1 has detected an obstacle. Rover 1 will reroute.")
        if len(path1) != 2:
            obs_center = path1[2]
        else:
            obs_center = path1[1]
        diagram.walls.append(obs_center)
        diagram.walls.append((obs_center[0],obs_center[1]+1))
        diagram.walls.append((obs_center[0]+1,obs_center[1]+1))
        diagram.walls.append((obs_center[0]-1,obs_center[1]+1))
        diagram.walls.append((obs_center[0],obs_center[1]-1))
        diagram.walls.append((obs_center[0]+1,obs_center[1]-1))
        diagram.walls.append((obs_center[0]-1,obs_center[1]-1))
        diagram.walls.append((obs_center[0]+1,obs_center[1]))
        diagram.walls.append((obs_center[0]-1,obs_center[1]))
        if rover1_list[i] in diagram.walls:
            i += 1
        came_from1, cost_so_far1 = pf.a_star_search(diagram, diagram.rovers[0], rover1_list[i])
        path1=pf.reconstruct_path(came_from1, start=diagram.rovers[0], goal=rover1_list[i])
        instructions1 = pf.instructionset(path1, current_orientation = next_orientation1)
        next_orientation1 = pf.getOrientation(path1, 0)
        total_path = path1 + path2
        pf.draw_grid(diagram, path=total_path)
    elif userinput == "v": #rover 2 detection
        print("Rover 2 has detected an obstacle. Rover 2 will reroute.")
        if len(path2) != 2:
            obs_center = path2[2]
        else:
            obs_center = path2[1]
        diagram.walls.append(obs_center)
        diagram.walls.append((obs_center[0],obs_center[1]+1))
        diagram.walls.append((obs_center[0]+1,obs_center[1]+1))
        diagram.walls.append((obs_center[0]-1,obs_center[1]+1))
        diagram.walls.append((obs_center[0],obs_center[1]-1))
        diagram.walls.append((obs_center[0]+1,obs_center[1]-1))
        diagram.walls.append((obs_center[0]-1,obs_center[1]-1))
        diagram.walls.append((obs_center[0]+1,obs_center[1]))
        diagram.walls.append((obs_center[0]-1,obs_center[1]))
        if rover2_list[j] in diagram.walls:
            j += 1
        came_from2, cost_so_far2 = pf.a_star_search(diagram, diagram.rovers[1], rover2_list[j])
        path2=pf.reconstruct_path(came_from2, start=diagram.rovers[1], goal=rover2_list[j])
        instructions2 = pf.instructionset(path2, current_orientation = next_orientation1)
        next_orientation2 = pf.getOrientation(path2, 0)
        total_path = path1 + path2
        pf.draw_grid(diagram, path=total_path)
        #
    elif userinput == "b": #edge case; paths cross
        for x in range(0,40):
            if x != 20:
                diagram.walls.append((x,25))
        came_from1, cost_so_far1 = pf.a_star_search(diagram, diagram.rovers[0], rover1_list[i])
        path1=pf.reconstruct_path(came_from1, start=diagram.rovers[0], goal=rover1_list[i])
        instructions1 = pf.instructionset(path1, current_orientation = next_orientation1)
        next_orientation1 = pf.getOrientation(path1, 0)
        came_from2, cost_so_far2 = pf.a_star_search(diagram, diagram.rovers[1], rover2_list[j])
        path2=pf.reconstruct_path(came_from2, start=diagram.rovers[1], goal=rover2_list[j])
        instructions2 = pf.instructionset(path2, current_orientation = next_orientation1)
        next_orientation2 = pf.getOrientation(path2, 0)
        total_path = path1 + path2
        pf.draw_grid(diagram, path=total_path)
    if any(check in path1 for check in path2) == True:
        diagram.rovers = [path1.pop(0),diagram.rovers[1]]
    else:
        diagram.rovers = [path1.pop(0),path2.pop(0)]
    if path1 == []:
        rover1_change = True
        if i == len(rover1_list) - 1:
            path1 = [diagram.rovers[0]]
    if path2 == []:
        rover2_change = True
        if j == len(rover2_list) - 1:
            path2 = [diagram.rovers[1]]
    if rover1_change == False and len(path1) != 1:
        next_orientation1 = pf.getOrientation(path1, 0)
    elif rover2_change == False and len(path2) != 1:
        next_orientation2 = pf.getOrientation(path2, 0) 
    if diagram.rovers == [rover1_list[final_r1],rover2_list[final_r2]]:
        diagram.rovers = [path1.pop(0),path2.pop(0)]
        pf.draw_grid(diagram, path=total_path)
        print("Both rovers have completed their operations.")
        operation = False
    