

from __future__ import annotations
from typing import Protocol, Iterator, Tuple, TypeVar, Optional
import collections
import heapq
import geopy.distance as gpd
import numpy as np

global pf_stop1, pf_stop2, pf_obstacle1, pf_obstacle2
pf_stop1 = 0
pf_stop2 = 0
pf_obstacle1 = ("", (0,0), 0)
pf_obstacle2 = ("", (0,0), 0)

T = TypeVar('T')
Location = TypeVar('Location')
class Graph(Protocol):
    def neighbors(self, id: Location) -> list[Location]: pass

class SimpleGraph:
    def __init__(self):
        self.edges: dict[Location, list[Location]] = {}
    
    def neighbors(self, id: Location) -> list[Location]:
        return self.edges[id]

class Queue:
    def __init__(self):
        self.elements = collections.deque()
    
    def empty(self) -> bool:
        return not self.elements
    
    def put(self, x: T):
        self.elements.append(x)
    
    def get(self) -> T:
        return self.elements.popleft()

def from_id_width(id, width):
    return (id % width, id // width)

def draw_tile(graph, id, style):
    r = " . "
    if 'number' in style and id in style['number']: r = " %-2d" % style['number'][id]
    if 'point_to' in style and style['point_to'].get(id, None) is not None:
        (x1, y1) = id
        (x2, y2) = style['point_to'][id]
        if x2 == x1 + 1: r = " > "
        if x2 == x1 - 1: r = " < "
        if y2 == y1 + 1: r = " v "
        if y2 == y1 - 1: r = " ^ "
    if 'path' in style and id in style['path']:   r = " # "
    if 'start' in style and id == style['start']: r = " R "
    if 'goal' in style and id == style['goal']:   r = " G "
    if id in graph.poi0: r = " 0 "
    if id in graph.poi1: r = " 1 "
    if id in graph.poi2: r = " 2 "
    if id in graph.rovers: r = " R "
    if id in graph.walls: r = "ooo"
    if id in graph.survivor: r = " S "
    return r

def draw_grid(graph, **style):
    print("___" * graph.width)
    for y in range(graph.height):
        for x in range(graph.width):
            print("%s" % draw_tile(graph, (x, y), style), end="")
        print()
    print("~~~" * graph.width)

GridLocation = Tuple[int, int]

class SquareGrid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.walls: list[GridLocation] = []
    
    def in_bounds(self, id: GridLocation) -> bool:
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height
    
    def passable(self, id: GridLocation) -> bool:
        return id not in self.walls
    
    def neighbors(self, id: GridLocation, direction = [1,0]) -> Iterator[GridLocation]:
        (x, y) = id
        if direction == [1,0]: #E
            neighbors = [(x+1, y), (x, y-1), (x, y+1), (x-1, y)] # E W N S
        elif direction == [0,-1]: #N
            neighbors = [(x, y-1), (x+1, y), (x-1, y), (x, y+1)] # N E W S
        elif direction == [0,1]: #S
            neighbors = [(x, y+1), (x-1, y), (x, y+1), (x, y-1)] # S W E N
        elif direction == [-1,0]: #W
            neighbors = [(x-1, y), (x, y-1), (x, y+1), (x+1, y)] # W N S E
        if (x + y) % 2 == 0: neighbors.reverse() # S N W E
        results = filter(self.in_bounds, neighbors)
        results = filter(self.passable, results)
        return results

class WeightedGraph(Graph):
    def cost(self, from_id: Location, to_id: Location) -> float: pass

class GridWithWeights(SquareGrid):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.weights: dict[GridLocation, float] = {}
    
    def cost(self, from_node: GridLocation, to_node: GridLocation) -> float:
        return self.weights.get(to_node, 1)

class GridWithAdjustedWeights(GridWithWeights):
    def cost(self, from_node, to_node):
        prev_cost = super().cost(from_node, to_node)
        nudge = 0
        (x1, y1) = from_node
        (x2, y2) = to_node
        if (x1 + y1) % 2 == 1 and x2 != x1: nudge = 1
        if (x1 + y1) % 2 == 0 and y2 != y1: nudge = 1
        return prev_cost + 0.001 * nudge
#diagrams for testing
########
diagram4 = GridWithWeights(20, 10)
diagram4.walls = [(3,2),(3,3),(3,4),(3,1)]
diagram4.weights = {loc: 5 for loc in [(3, 4), (3, 5), (4, 1), (4, 2),
                                       (4, 3), (4, 4), (4, 5), (4, 6),
                                       (4, 7), (4, 8), (5, 1), (5, 2),
                                       (5, 3), (5, 4), (5, 5), (5, 6),
                                       (5, 7), (5, 8), (6, 2), (6, 3),
                                       (6, 4), (6, 5), (6, 6), (6, 7),
                                       (7, 3), (7, 4), (7, 5)]}
diagram5 = GridWithWeights(20, 10)
diagram5.walls = [(3,2),(3,3),(3,4),(3,1),(3,9),(3,8),(4,5)]
diagram5.rovers = []
diagram5.poi0 = []
diagram5.poi1 = []
diagram5.poi2 = []
diagram6= GridWithWeights(20, 10)
diagram6.rovers = []
diagram6.poi0 = []
diagram6.poi1 = []
diagram6.poi2 = []

dimension = (500,500)
diagram= GridWithWeights(dimension[0],dimension[1])
diagram.walls = []
diagram.survivor = []
diagram.rovers = []
########
#internal scale
def scaleGrid(grid_point, dimension = dimension, input = "var", output = "GPS"):
    point1 = (30.6222648,-96.3389598) #change these three to change scale
    point2 = (30.6242960,-96.3370715)
    step = ((point2[0]-point1[0])/(dimension[0] - 1),(point1[1]-point2[1])/(dimension[1] - 1))
    if output == "GPS":
        if input == "list":
            values = []
            for i in range(0,len(grid_point)):
                values.append((point1[0] + grid_point[i][0] * step[0], 
                               point2[1] + grid_point[i][1] * step[1]))
        else:
            values = (point1[0] + grid_point[0] * step[0], ((point2[1] + grid_point[1] * step[1])))
    elif output == "point":
        if input == "list":
            values = []
            for i in range(0,len(grid_point)):
                value = ((grid_point[i][0] - point1[0])/step[0], ((grid_point[i][1] - point2[1])/step[1]))
                value = (round(value[0]),abs(round(value[1])))
                values.append(value)
        else:
            values = ((grid_point[0] - point1[0])/step[0], ((grid_point[1] - point2[1])/step[1]))
            values = (round(values[0]),abs(round(values[1])))
    elif output == "step":
        values = step
    return values

def GPSDistance(point1, point2, input = "point"): #takes as input internal coordinate points. Not GPS points
    if input == "GPS":
        GPS_p1 = point1
        GPS_p2 = point2
    else:
        GPS_p1 = scaleGrid(point1, output = "GPS")
        GPS_p2 = scaleGrid(point2, output = "GPS")
    return gpd.distance(GPS_p1,GPS_p2).meters

class PriorityQueue:
    def __init__(self):
        self.elements: list[tuple[float, T]] = []
    
    def empty(self) -> bool:
        return not self.elements
    
    def put(self, item: T, priority: float):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self) -> T:
        return heapq.heappop(self.elements)[1]

def reconstruct_path(came_from: dict[Location, Location],
                     start: Location, goal: Location) -> list[Location]:

    current: Location = goal
    path: list[Location] = []
    if goal not in came_from:
        return []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    fixed_path = []
    i = len(path)-1
    while i != -1:
        fixed_path.append(path[i])
        i -= 1
    return fixed_path

diagram_nopath = GridWithWeights(10, 10)
diagram_nopath.walls = [(5, row) for row in range(10)]

def heuristic(a: GridLocation, b: GridLocation) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def getOrientation(path, i, curr_orientation = [0,1]):
    next_orientation = curr_orientation
    if len(path) == 0:
        return curr_orientation
    if(path[i][0] - path[i+1][0]) > 0:
        next_orientation = [-1,0] #W
    elif(path[i][0] - path[i+1][0]) < 0:
        next_orientation = [1,0] #E
    elif(path[i][1] - path[i+1][1]) < 0:
        next_orientation = [0,-1] #N
    elif(path[i][1] - path[i+1][1]) > 0:
        next_orientation = [0,1] #S
    return next_orientation

def a_star_search(graph: WeightedGraph, start: Location, goal: Location):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[Location, Optional[Location]] = {}
    cost_so_far: dict[Location, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current: Location = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, goal)
                frontier.put(next, priority)
                came_from[next] = current
    
    return came_from, cost_so_far

def breadth_first_search(graph: Graph, start: Location, goal: Location):
    frontier = Queue()
    frontier.put(start)
    came_from: dict[Location, Optional[Location]] = {}
    came_from[start] = None
    
    while not frontier.empty():
        current: Location = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current):
            if next not in came_from:
                frontier.put(next)
                came_from[next] = current
    
    return came_from

class SquareGridNeighborOrder(SquareGrid):
    def neighbors(self, id):
        (x, y) = id
        neighbors = [(x + dx, y + dy) for (dx, dy) in self.NEIGHBOR_ORDER]
        results = filter(self.in_bounds, neighbors)
        results = filter(self.passable, results)
        return list(results)

def getTurn(instruction, current_orientation, next_orientation):
    if (current_orientation[1] == -1*next_orientation[1] and current_orientation[1] != 0
            or current_orientation[0] == -1*next_orientation[0] and current_orientation[0] != 0):
            angle = 180
            instruction.append("T$"+str(angle))
    elif current_orientation == [1,0] or current_orientation == [-1,0]:
        angle = -90*current_orientation[0]*next_orientation[1]
        instruction.append("T$"+str(angle))
    elif current_orientation == [0,1] or current_orientation == [0,-1]:
        angle = 90*current_orientation[1]*next_orientation[0]
        instruction.append("T$"+str(angle))
    current_orientation = next_orientation
    return

def instructionset(pathGPS, turn = 90):
    #orientation represented as unit circle. If a rover is to move forward,
    #then it is assumed to be moving at 90 degrees
    instructions = ["F$0"]
    if turn == 90:
        current_orientation = [0,1]
    elif turn == 180:
        current_orientation = [-1,0]
    elif turn == 270:
        current_orientation = [0,-1]
    elif turn == 0:
        current_orientation = [1,0]
    
    #convert path input to point
    if len(pathGPS) == 0:
        instructions.append("F$"+str(0))
        return instructions
    path = scaleGrid(pathGPS, dimension = dimension, input = "list", output = "point")
    
    starting_orientation = getOrientation(path,0, curr_orientation = current_orientation)
    if starting_orientation != current_orientation:
        getTurn(instructions, current_orientation, starting_orientation)
    next_orientation = starting_orientation
    current_orientation = starting_orientation
    i = 0
    distance = 0
    angle = 0
    turn = True
    while i < len(path)-1:
        distance = 0
        current_orientation = next_orientation
        turn = False
        while current_orientation == next_orientation and i != len(path)-1:
            next_orientation = getOrientation(path, i, current_orientation)
            i += 1
            if current_orientation == next_orientation:
                if i != len(path)-1:
                    distance += GPSDistance(path[i],path[i+1])
                else:
                    distance += GPSDistance(path[i-1],path[i])
                #distance += 1
            else:
                turn = True
            if i == len(path)-1 and turn == False:
                instructions.append("F$"+str(round(distance,4)))
                instructions.append("T$"+str(-90))
                instructions.append("T$"+str(-90))
                instructions.append("T$"+str(-90))
                instructions.append("T$"+str(-90))
                instructions.append("F$"+str(0))
                return instructions
        instructions.append("F$"+str(round(distance,4)))
        if turn == True:
            getTurn(instructions, current_orientation, next_orientation)
            if i != len(path)-1:
                i -= 1
            else:
                if current_orientation == [0,1] or current_orientation == [0,-1]:
                    instructions.append("F$"+str(GPSDistance((0,0),(0,1))))
                    #instructions.append("F$"+str(1))
                else:
                    instructions.append("F$"+str(GPSDistance((0,0),(1,0))))
                    #instructions.append("F$"+str(1))
                instructions.append("T$"+str(-90))
                instructions.append("T$"+str(-90))
                instructions.append("T$"+str(-90))
                instructions.append("T$"+str(-90))
                instructions.append("F$"+str(0))
                return instructions
    return instructions

######################################
#Functions for control script
######################################

#This function gets the linear distance between two points
#Replace once integrating with the base station.\
def getDistance(pt1,pt2):
    distance = np.sqrt((pt2[0]-pt1[0])**2+(pt2[1]-pt1[1])**2) #np.sqrt(long_diff**2+lat_diff**2)
    return distance

def shortestDist(location, coords):
    j = 0
    shortest_distance = 1000000
    dist = 0
    for i in range(0,len(coords)):
        dist = gpd.GeodesicDistance(location, coords[i])
        if dist < shortest_distance:
            j = i
    return j

#takes a location and orders the list based on distance to the starting location
#the first two points will always be based on distance to the starting point
#every subsequent point will be ordered based on distance to the last point
def orderDist(location, coords):
    temp_coords = coords
    new_coords = []
    i = 0
    j = 0
    while i < len(coords):
        if i < 2:
            j = shortestDist(location, temp_coords)
        else:
            j = shortestDist(new_coords[len(new_coords)-1], temp_coords)
        new_coords.append(temp_coords.pop(j))
    return new_coords

#takes two lists as an input
#the first list contains correct values to be output
#the second list contains similar but inaccurate values compared to the first, but the desired order
def correctGPS(list_vals, list_order):
    new_vals = []
    no_match = True
    k = 0
    if len(list_vals) != len(list_order):
        no_match = True
        return list_vals
    for i in range(0,len(list_order)):
        k = 0
        no_match = True
        for j in range(0,len(list_vals)):
            if abs(list_order[i][0] - list_vals[j][0]) <= 0.000001 and abs(list_order[i][1] - list_vals[j][1]) <= 0.000001:
                k = j
                no_match = False
        new_vals.append(list_vals[k])
    return new_vals

#This function will take as input two rover starting positions and an overall list of points
#It will then approximate distances from points to rovers and assign points to rovers
#It will return two lists, rover1_list, rover2_list
def roverBoundaries(rover1GPS = (0,0), rover2GPS = (36,-98), POIGPS = [[(5,5)],[],[]]):
    #take GPS as input
    rover1_points = POIGPS[1]
    rover2_points = POIGPS[2]
    
    #first, a line between the rovers will be determined, then a line
    #perpendicular to that will be calculated that will be the decision boundary.
    if rover2GPS[0] - rover1GPS[0] != 0:
        slope = (rover2GPS[1]-rover1GPS[1])/(rover2GPS[0]-rover1GPS[0])
    else:
        slope = float('inf')
    
    if slope !=0 and slope != float('inf'):
        perp_slope = -1/slope
    else:
        perp_slope = 0
    midpoint = ((rover2GPS[0]+rover1GPS[0])/2,(rover2GPS[1]+rover1GPS[1])/2)
    intercept = midpoint[1] - perp_slope*midpoint[0]
    def decisionBoundary(point):
        return perp_slope*point[0] + intercept
    
    #this function will be used when distance determines point assignment
    #returns index of coordinate in list that is shortest dist
    
    #Now to make a linear decision on which points go to which rover.
    for i in range(0,len(POIGPS[0])):
        POI_determinant = decisionBoundary(POIGPS[0][i])
        #need to add a float(inf) case here.
        if POI_determinant > POIGPS[0][i][1] and POIGPS[0][i] not in POIGPS[1] and POIGPS[0][i] not in POIGPS[2]:
            rover1_points.append(POIGPS[0][i])
        elif POIGPS[0][i] not in POIGPS[1] and POIGPS[0][i] not in POIGPS[2]:
            rover2_points.append(POIGPS[0][i])
          
    #check if one list has too many points here:
    #one list shouldn't have more than 3 points
    #but if the point being added has a differential distance between the two rovers greater than
    #X, we simply won't add it to the other list.
    #assumes the point being removed from the list is the last point
    def pointShift(remove_list, add_list, remove_rover, add_rover):
        index = len(remove_list)-1
        distance1 = gpd.GeodesicDistance(remove_rover,remove_list[index])
        distance2 = gpd.GeodesicDistance(add_rover,remove_list[index])
        diff = distance2-distance1
        if diff < 10: #if point is closer to rover1, this always passes. If point is closer to rover2, but only by 10 or less meters, give to rover 1 anyways
            add_list.append(remove_list.pop(index))
        return remove_list, add_list
    
    if len(rover1_points)- len(rover2_points) > 2:
        rover1_points, rover2_points = pointShift(rover1_points,
                                                  rover2_points, rover1GPS, rover2GPS)
    elif len(rover2_points) - len(rover1_points) > 2:
        rover2_points, rover1_points = pointShift(rover2_points,
                                                  rover1_points, rover2GPS, rover1GPS)
    return rover1_points, rover2_points

#this function will take an overall list and two smaller lists.
#compare the overall lists to the two smaller lists. It will also need the rover coordinates
#This function will manually change the lists and return the overall
def listCheck(rover=[[]],list=[[],[],[]]):
    new_list = [[],[],[]]
    new_list[0] = list[0]
    new_list[1] = list[1]
    new_list[2] = list[2]
    element = [] #element used to check overall
    for k in range(0,len(list[0])):
        element = list[0][k]
        if element not in list[1] and element not in list[2]:
            new_list[1], new_list[2] = roverBoundaries(rover[0],rover[1],list)
    return new_list

#this function will be used for recalibration
#it will take two GPS points as an input and use those points to calculate the
#amount of turning the rover needs to do to realign with the cardinal directions.
#VALIDATE THIS LATER
def calibrationAngle(point1GPS, point2GPS):
    instruction = []
    instruction.append("F$0")
    a = point1GPS
    b = point2GPS
    geod = gpd.Geodesic.WGS84
    inv = geod.Inverse(a[0],a[1],b[0],b[1])
    azi1 = inv['azi1']
    print('Initial Azimuth from A to B = ' + str(azi1))
    #if azi1 >= 90: need to break the angle up into multiple turns. Rover can't turn more than 90
    if azi1 >= 0 and azi1 < 90:
        instruction.append("T$"+str(90-azi1))
    elif azi1 > 90 and azi1 <=180:
        instruction.append("T$"+str((90-azi1)))
    elif azi1 < 0 and azi1 > -90:
        instruction.append("T$"+str(90))
        instruction.append("T$"+str(-1*azi1))
    elif azi1 <= -90 and azi1 >= -180:
        instruction.append("T$"+str(-90))
        instruction.append("T$"+str(-1*(90+azi1)))
    instruction.append("F$0")
    return instruction

#IMPORTANT ADDITIONS TO CALIBRATION FUNCTION
#DO THIS IMMEDAITELY
#If the angle is greater than 90 degrees, do a 180 degree turn first, then
#turn the rest of the way to get the proper calibration
#Example: 125 turn right would yield 180 turn right, then a 55 degree turn left

#use this to tell Sam to calibrate and collect points
def calibrationInstructions(obstacle = False):
    instruction = []
    instruction.append("F$0")
    instruction.append("W$1")
    if obstacle == True:
        instruction.append("T$-90")
    instruction.append("CalStart$0")
    #other instructions go here
    instruction.append("F$1.34")
    instruction.append("F$0")
    instruction.append("CalStop$0")
    return instruction

def multiPath(rover_gps, diagram):
    rover_list = scaleGrid(rover_gps, dimension = dimension, input = "list", output = "point")
    total_path = []
    for i in range (0,len(rover_list)-1):
        path = []
        came_from, cost_so_far = a_star_search(diagram, rover_list[i], rover_list[i+1])
        path=reconstruct_path(came_from, start=rover_list[i], goal=rover_list[i+1])
        #next_orientation = getOrientation([diagram.rovers[0],path[i]], 0)
        for j in range(0,len(path)-1):
            total_path.append(scaleGrid(path[j], dimension = dimension, input = "var", output = "GPS"))
    return total_path

######Obstacle detection functionality######
#these functions will take the bounding box area as input to estimate distance from the rover
def calcDistance(obstacle_type, center_point, area):
    dist = 0
    angle = 0
    if obstacle_type == "Cone":
        if center_point[0] > 270 and center_point[0] < 340: #cone is in front of us
            dist = -2.51256281407*np.log(area/41718)
            angle = 0
        elif center_point[0] < 270: #cone is angled to the left
            dist = (40/23)*np.log(81813/area)
            angle = 20 #degrees
        elif center_point[0] > 340: #cone angled to right
            dist = (40/23)*np.log(81813/area)
            angle = -20 #degrees
    elif obstacle_type == "Box":
        if center_point[0] > 270 and center_point[0] < 340:
            dist = (5/2)*np.log(64061/area)
            angle = 0
        elif center_point[0] < 270:
            dist = -(250/119)*np.log(area/77053)
            angle = 20
        elif center_point[0] > 340:
            dist = -(250/119)*np.log(area/77053)
            angle = -20
    elif obstacle_type == "human":
        if center_point[0] > 270 and center_point[0] < 340:
            dist = 6
            angle = 0
        elif center_point[0] < 280:
            dist = 6
            angle = 20
        elif center_point[0] > 340:
            dist = 6
            angle = -20
    return dist, angle

#This function will take ML data from Hafsa: The object type, center point, and bounding box area
#The function will use this to determine if an obstacle is close and if we need to send a stop signal
def obstacleDetection(obstacle_type, center_point, area, num):
    global pf_stop1, pf_stop2, pf_obstacle1, pf_obstacle2
    dist, angle = calcDistance(obstacle_type, center_point, area)
    if dist <= 6: #feet
        if num == 1:
            pf_stop1 = 1
            pf_obstacle1 = (obstacle_type, center_point, area)
        else:
            pf_stop2 = 1
            pf_obstacle2 = (obstacle_type, center_point, area)

#this function will take as input a rover location, a distance and an angle
#the fuction will add the corresponding obstacle to the diagram and return the GPS coordinate to UI
def addObstacle(rover_coordinate, orientation, obstacle_type, center_point, area):
    dist, angle = calcDistance(obstacle_type, center_point, area)
    orientation += angle
    dest_calc = gpd.distance(feet=dist).destination(rover_coordinate, bearing=orientation)
    destination = (dest_calc[0],dest_calc[1])
    
    #add obsatacle to diagram below
    rover_node = scaleGrid(rover_coordinate, input = "var", output = "point")
    obstacle_node = scaleGrid(destination, input = "var", output = "point")
    
    #we want to add walls around the obstacle to account for inaccuracies
    #we want the obstacle to have a boundary of two feet, so calculate how many node coordinates that is
    i = 8 #INCREASE IF IT DOESN'T AVOID ENOUGH
    for j in range(i,-i-1,-1):
        if (rover_node[0] < obstacle_node[0] - j or rover_node[0] > obstacle_node[0]) - j and (rover_node[1] < obstacle_node[1] - j or rover_node[1] > obstacle_node[1] - j):
            for k in range(i,-i-1,-1):
                #check if rover is going to be covered by obstacle or not
                if (rover_node[0] < obstacle_node[0] - k or rover_node[0] > obstacle_node[0] - k) and (rover_node[1] < obstacle_node[1] - k or rover_node[1] > obstacle_node[1] - k):
                    diagram.walls.append((obstacle_node[0]+k,obstacle_node[1]+j))
    return destination

def tempAddObstacle(current_point):
    gps_point = (current_point[0],current_point[1]+0.001)
    gps_node = scaleGrid(gps_point, input = "var", output = "point")
    i = 8
    for j in range(i,-i-1,-1):
        for k in range(i,-i-1,-1):
        #check if rover is going to be covered by obstacle or not
            diagram.walls.append((gps_node[0]+k,gps_node[1]+j+1))
    return

#this function will take the current rover point, the current path, and find it's approximate orientaiton.
def findOrientation(gps_point, path):
    node_point = scaleGrid(gps_point, input = "var", output = "point")
    node_list = scaleGrid(path, input = "list", output = "point")
    current_node = (0,0)
    next_node = (0,0)
    tol = 1
    while node_point not in node_list:
        if (node_point[0+tol],node_point[1]) in node_list:
            node_point = (node_point[0+tol],node_point[1])
        elif (node_point[0-tol],node_point[1]) in node_list:
            node_point = (node_point[0-tol],node_point[1])
        elif (node_point[0],node_point[1+tol]) in node_list:
            node_point = (node_point[0],node_point[1+tol])
        elif (node_point[0],node_point[1-tol]) in node_list:
            node_point = (node_point[0],node_point[1-tol])
    
    for i in range(0,len(node_list)):
        if node_point[0] == node_list[i][0] and node_point[1] == node_list[i][1]:
            current_node = node_list[i]
            next_node = node_list[i+1]
          
    #for this case, 0 degrees is east, 90 north, 180 west, 270 south
    orientation = [next_node[0]-current_node[0],next_node[1]-current_node[1]]
    if orientation[0] == 1:
        angle = 0
    elif orientation[0] == -1:
        angle = 180
    elif orientation[1] == -1:
        angle = 90
    elif orientation [1] == 1:
        angle = 270
    return angle
