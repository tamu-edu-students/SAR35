from __future__ import annotations
from typing import Protocol, Iterator, Tuple, TypeVar, Optional
import collections
import heapq
import geopy.distance as gpd

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
########
#internal scale
def scaleGrid(grid_point, dimension = (40,35), output = "GPS"):
    point1 = (30.613067, -96.343093) #change these three to change scale
    point2 = (30.613752, -96.341826)
    step = ((point2[0]-point1[0])/(dimension[0] - 1),(point2[1]-point1[1])/(dimension[1] - 1))
    if output == "GPS":
        value = (point1[0] + grid_point[0] * step[0], point1[1] - grid_point[1] * step[1])
    elif output == "point":
        value = ((grid_point[0] - point1[0])/step[0], -1*(grid_point[1] - point1[1])/step[1])
        value = (round(value[0]),round(value[1]))
    elif output == "step":
        value = step
    return value

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
        angle = 90*current_orientation[0]*next_orientation[1]
        instruction.append("T$"+str(angle))
    elif current_orientation == [0,1] or current_orientation == [0,-1]:
        angle = -90*current_orientation[1]*next_orientation[0]
        instruction.append("T$"+str(angle))
    current_orientation = next_orientation
    return

def instructionset(path, current_orientation = [0,1]):
    #orientation represented as unit circle. If a rover is to move forward,
    #then it is assumed to be moving at 90 degrees
    instructions = []
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
                    #instructions.append("F$"+str(GPSDistance((0,0),(0,1))))
                    instructions.append("F$"+str(1))
                else:
                    #instructions.append("F$"+str(GPSDistance((0,0),(1,0))))
                    instructions.append("F$"+str(1))
                instructions.append("T$"+str(-90))
                instructions.append("T$"+str(-90))
                instructions.append("T$"+str(-90))
                instructions.append("T$"+str(-90))
                instructions.append("F$"+str(0))
                return instructions
    return instructions