import numpy as np
import pathfinding as pf
import Test as ts

start, goal = (1, 4), (6, 2)
came_from, cost_so_far = pf.a_star_search(pf.diagram5, start, goal)

#this function is out of the operation loop since this will only need to be done once
#will take the two rover starting points and a list of points of interest to define boundaries
def roverBoundaries(rover1 = (0,0), rover2 = (10,10), POI = [(5,5)]):
    rover1_points = []
    rover2_points = []
    #first, a line between the rovers will be determined, then a line
    #perpendicular to that will be calculated that will be the decision boundary.
    if rover2[0] - rover1[0] != 0:
        slope = (rover2[1]-rover1[1])/(rover2[0]-rover1[0])
    else:
        slope = float('inf')
    
    if slope !=0 and slope != float('inf'):
        perp_slope = -1/slope
    else:
        perp_slope = 0
    intercept = rover1[1] - perp_slope*rover1[0] #could use rover1 or 2 coords.
    def decisionBoundary(point):
        return perp_slope*point[0] + intercept
    
    #Now to make a linear decision on which points go to which rover.
    for i in range(0,len(POI)):
        POI_determinant = decisionBoundary(POI[i])
        #need to add a float(inf) case here.
        if rover1[1] <= POI_determinant:
            rover1_points.append(POI[i])
        else:
            rover2_points.append(POI[i])
    #before returning the lists, we should check the lists and see if
    #one list has too many points
    while abs(len(rover2_points) - len(rover1_points)) >= 2:
        shortest_dist = 0
        if len(rover2_points) - len(rover1_points) >= 2:
            shortest_dist = ts.getDistance(rover2_points[0],rover1)
            for j in range(0,len(rover2_points)): #iterate through the points
                distance = ts.getDistance(rover2_points[j],rover1)
                if distance <= shortest_dist: #find the shortest distance and compare
                    point_to_pop = j
                    shortest_dist = distance
            rover1_points.append(rover2_points.pop(point_to_pop)) #whichever distance is shortest gets moved to opposite list
        elif len(rover1_points) - len(rover2_points) >= 2:
            shortest_dist = ts.getDistance(rover1_points[0],rover2)
            for j in range(0,len(rover1_points)):
                distance = ts.getDistance(rover1_points[j],rover2)
                if distance <= shortest_dist:
                    point_to_pop = j
                    shortest_dist = distance
            rover2_points.append(rover1_points.pop(point_to_pop))
    
    #reorder the rover1 and 2 points based on distance here
    rover1_points_reordered = []
    num_points = len(rover1_points)
    shortest_dist = 200
    #finding the first point that is closest to the rover.
    for j in range(0,len(rover1_points)):
        distance = ts.getDistance(rover1_points[j],rover1)
        if distance <= shortest_dist:
            point_to_pop = j
            shortest_dist = distance
    rover1_points_reordered.append(rover1_points.pop(point_to_pop))
    #now finding which point is closest to our first POI, then the next after that.
    for i in range(0,num_points-1):
        shortest_dist = 200
        for j in range(0,len(rover1_points)):
            distance = ts.getDistance(rover1_points_reordered[i],rover1_points[j])
            if distance <= shortest_dist:
                point_to_pop = j
                shortest_dist = distance
        rover1_points_reordered.append(rover1_points.pop(point_to_pop))
    #do the same for rover 2
    rover2_points_reordered = []
    num_points = len(rover2_points)
    shortest_dist = 200
    #finding the first point that is closest to the rover.
    for j in range(0,len(rover2_points)):
        distance = ts.getDistance(rover2_points[j],rover2)
        if distance <= shortest_dist:
            point_to_pop = j
            shortest_dist = distance
    rover2_points_reordered.append(rover2_points.pop(point_to_pop))
    #now finding which point is closest to our first POI, then the next after that.
    for i in range(0,num_points-1):
        shortest_dist = 200
        for j in range(0,len(rover2_points)):
            distance = ts.getDistance(rover2_points_reordered[i],rover2_points[j])
            if distance <= shortest_dist:
                point_to_pop = j
                shortest_dist = distance
        rover2_points_reordered.append(rover2_points.pop(point_to_pop))
    return rover1_points_reordered, rover2_points_reordered
    