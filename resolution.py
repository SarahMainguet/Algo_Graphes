import numpy as np
from text_to_graph import parse_graph_data, get_correct_index
from rendering_graph import rendering
import sys 

""" Utilities"""


def min(x,y):
    """ Returns a boolean x < y"""
    return x<y

def max(x,y):
    """ Returns a boolean x > y"""
    return x>y

def relacher_init(id,graph, id_List):
    """ Initialize 'd' and 'pere' array for the dijkstra algorithm"""
    d = []
    pere = []
    for j in range(len(graph)):
        d.append(np.inf)
        pere.append(0)
    d[get_correct_index(id_List,id)] = 0
    return (d, pere)

def relacher(i_u, i_v, d, pere, graph, id_List):
    """ Update 'd' and 'pere' values for 'i_v' vertex modified by 'i_u' vertex"""
    if d[i_v] > d[i_u] + graph[i_u][i_v]:
        d[i_v] = d[i_u] + graph[i_u][i_v]
        pere[i_v] = id_List[i_u]

def not_Empty(tab):
    """ Boolean telling if there is a least one non-zero element in 'tab'"""
    for i in tab:
        if i == 1:
            return 1
    return 0

def ind_min(tab, Y):
    """ Returns the index of the minimum of 'tab'"""
    ind=0
    min= np.inf
    for i in range(len(tab)):
        if ((tab[i] < min) and (Y[i] == 1)):
            min = tab[i]
            ind = i
    return ind

def dijkstra(id, graph, id_List):
    """ Returns two arrays: \n 
     - 'd' is the distance to all other vertices starting from 'id' \n
     - 'pere' indicates the previous vertex to visit to reach'id'"""
    (d, pere) = relacher_init(id, graph, id_List)
    Y = [1 for k in range(len(graph))]
    while not_Empty(Y):
        u = ind_min(d, Y)
        Y[u] = 0
        for  v in range(len(graph[u])): 
            if Y[v] == 1 and graph[u][v]!= 0:
                relacher(u, v, d, pere, graph, id_List)
    return (d, pere)


""" Robot functions"""


def robots_all_awake(robot_List):
    """ Checks if it remains at least one robot which is not awake"""
    for robot in robot_List:
        if robot["state"] != "awake":
            return 0
    return 1
    
def awake1(robot_List,id, graph, id_List):
    """ Awaken 'id' robot and finds it a destination far or close depending of 'state'"""
    robot_List[get_correct_index(id_List,id)]["state"] = "awake"
    find_dest1(id, id, robot_List, max, graph, id_List)

def awake_opti(robot_List,id, graph, test, id_List):
    """ Awaken 'id' robot and finds it a destination far or close depending of 'state'"""
    robot_List[get_correct_index(id_List,id)]["state"] = "awake"
    robot_List[get_correct_index(id_List,id)]["range"] = test.__name__
    robot_List[get_correct_index(id_List,id)]["dest"] = []
    robot_List[get_correct_index(id_List,id)]["dist"] = []
    find_dest_opti(id, id, robot_List, test, graph, id_List)

def find_dest1(i, i_position, robot_List, test, graph, id_List):
    """ Update the field "dest" of 'i' with the array of its destination and "dist" with the corresponding distances """
    dist,pere = dijkstra(i_position, graph, id_List) # dist = array of the distance to "id" , "pere" = array of ancestors to join "id"
    if test == min:
        test_dist = np.inf
    else:
        test_dist = 0
    ind = None
    for k in range(len(dist)):
        if test(dist[k], test_dist) and k != i_position and robot_List[k]["state"] == "asleep" :
            test_dist = dist[k]
            ind = k
        
    if ind != None: 
        first_dest = id_List[ind]
        list_dest = [first_dest] # list_dest = road to follow to link "id" and the destination
        list_dist = [dist[get_correct_index(id_List, first_dest)]] # list_dist = list of the distance in relation with list_dest

        while pere[get_correct_index(id_List,first_dest)] != id_List[i_position]:
            first_dest = pere[get_correct_index(id_List,first_dest)]
            list_dest.append(first_dest)
            list_dist.append(dist[get_correct_index(id_List,first_dest)])

        for id in list_dest: # On réserve tout les robots à reveiller en chemin
            if robot_List[get_correct_index(id_List,id)]["state"] == "asleep":
                robot_List[get_correct_index(id_List,id)]["state"] = "reserved"
        list_dest = list_dest[::-1]
        list_dist = list_dist[::-1]

        robot_List[i]["dest"] = list_dest
        robot_List[i]["dist"] = list_dist


def reservation(robot_List, id_List, first_dest, i, list_dist):
    """ If the robot 'first_dest' is asleep : set the id of the robot that will wake him up (= i)
        If the robot 'first_dest' is reserved : change the reservation and erase it from the previous robot that had reserved him """
    if robot_List[get_correct_index(id_List, first_dest)]["state"] == "reserved":
        old_robot_id = robot_List[get_correct_index(id_List, first_dest)]["dest"][0] # id du précédent robot à l'avoir réservé
        old_robot_res = len(robot_List[get_correct_index(id_List, old_robot_id)]["dest"]) # nombre de réservations de ce robot
        old_robot_obj = robot_List[get_correct_index(id_List, old_robot_id)]["dest"][old_robot_res-1] # objectif final de ce robot

        robot_List[get_correct_index(id_List, first_dest)]["dest"] = [i] # change le robot qui a réservé...
        robot_List[get_correct_index(id_List, first_dest)]["dist"] = [list_dist[-1]] # ... et la distance associée

        # Tant que l'objectif final du précédent robot n'est pas valide, l'enlever jusqu'à ce qu'il soit valide ou qu'il n'en reste qu'un
        while old_robot_res > 1 and (robot_List[get_correct_index(id_List, old_robot_obj)]["state"] == "awake" or robot_List[get_correct_index(id_List, old_robot_obj)]["dest"][0] != old_robot_id):
            robot_List[get_correct_index(id_List, old_robot_id)]["dest"].pop(old_robot_res-1)
            robot_List[get_correct_index(id_List, old_robot_id)]["dist"].pop(old_robot_res-1)
            old_robot_res = old_robot_res - 1
            old_robot_obj = robot_List[get_correct_index(id_List, old_robot_id)]["dest"][old_robot_res-1]

    elif robot_List[get_correct_index(id_List, first_dest)]["state"] == "asleep":
        robot_List[get_correct_index(id_List, first_dest)]["dest"] = [i]
        robot_List[get_correct_index(id_List, first_dest)]["dist"] = [list_dist[-1]]

def find_dest_opti(i, i_position, robot_List, test, graph, id_List):
    """ Update the field "dest" of 'i' with the array of its destination and "dist" with the corresponding distances """
    dist,pere = dijkstra(i_position, graph, id_List) # dist = tableau des distances à id et père = tableau des antécedents pour relier à id
    #print(pere)
    if test == min:
        test_dist = np.inf
    else:
        test_dist = 0
    ind = None
    for k in range(len(dist)):
        if test(dist[k], test_dist) and k != i_position and (robot_List[k]["state"] == "asleep" or (robot_List[k]["state"] == "reserved" and dist[k] < robot_List[k]["dist"][0])):
            test_dist = dist[k]
            ind = k
        
    if ind != None: 
        first_dest = id_List[ind]
        list_dest = [first_dest] # list_dest = chemin à faire pour relier id à sa destination
        list_dist = [dist[get_correct_index(id_List, first_dest)]] # list_dist = liste des distances associées à list_dest
        reservation(robot_List, id_List, first_dest, i, list_dist)

        while pere[get_correct_index(id_List,first_dest)] != id_List[i_position]:
            first_dest = pere[get_correct_index(id_List,first_dest)]
            list_dest.append(first_dest)
            list_dist.append(dist[get_correct_index(id_List,first_dest)])
            reservation(robot_List, id_List, first_dest, i, list_dist)

        for id in list_dest: # On réserve tout les robots à reveiller en chemin
            if robot_List[get_correct_index(id_List,id)]["state"] == "asleep":
                robot_List[get_correct_index(id_List,id)]["state"] = "reserved"
        list_dest = list_dest[::-1]
        list_dist = list_dist[::-1]

        robot_List[i]["dest"] = list_dest
        robot_List[i]["dist"] = list_dist

def what_to_do1(i,robot_List,graph, id_List):
    """ First implementation of the algorithm for wakening the robot\n
    Strategy: The first robot will wake up the closest sleeping robot, which will wake up the farthest sleeping robot.
    Each time a robot is awakened by another robot, it will go for the farthest sleeping robot whereas the other robot will go for the closest.
    When a robot go for waking up another robot, he will wake up all the sleeping robot on his way. All the robots he plans to wake up are reserved."""
    robot = robot_List[i]
    awake1(robot_List, robot["dest"][0],graph, id_List) # ...on réveille le robot correspondant...
    id_dest = robot["dest"].pop(0)
    robot["dist"].pop(0)
    if len(robot["dest"]) == 0:
        find_dest1(robot["id"], id_dest, robot_List, min, graph,id_List) # ...et on lui assigne sa destination

def what_to_do_opti(i, robot_List, graph, id_List):
    """ Optimization of the previous algorithm\n
    Strategy: Now, the robot has a field (defined when awakened) that define if he looks for the closest or the farthest sleeping robot.
    When a robot that awake close robot wake up a robot, this robot will look for the farthest robot, and The first awake robot will look for the closest.
    Moreover, when a robot is looking for a robot to wake up, he can take a reserved robot if he is closer to this robot
    than the robot that had reserved him."""
    robot = robot_List[i]
    if robot["range"] == "min":
        state = max
        state_i = min
    else:
        state = min
        state_i = max
    awake_opti(robot_List, robot["dest"][0],graph, state, id_List) # ...on réveille le robot correspondant...
    id_dest = robot["dest"].pop(0)
    robot["dist"].pop(0)
    if len(robot["dest"]) == 0:
        find_dest_opti(robot["id"], id_dest, robot_List, state_i, graph, id_List) # ...et on lui assigne sa destination


def move_Robots(robot_List, graph, what_to_do, id_List):
    """ Decrease all distances by 1 and, if necessary, wakes up a robot"""
    for robot in robot_List:
        if robot["state"] != "asleep" and len(robot["dist"]) > 0:
            for k in range(len(robot["dest"])): # On décremente de 1 toutes les distances de "dist"
                robot["dist"][k] -=1
    for robot in robot_List:
        if len(robot["dist"]) >0 and robot["dist"][0] == 0 and robot["state"] == "awake": # Si la plus courte distance tombe à 0... 
            if robot_List[get_correct_index(id_List, robot["dest"][0])]["state"] != "awake": # Si le robot atteint n'est pas encore réveillé
                what_to_do(robot["id"], robot_List, graph, id_List)
            else:
                robot["dist"].pop(0)
                robot["dest"].pop(0)


"""
On suppose que la matrice graph est définie comme suit:
    graph[i] est un tableau contenant l'ensemble des sommets reliés à i et l'élement i,j est le poids associé à l'arrete (i,j)
Nous avons également un tableau robot_List qui contient tous les robots (dictionnaires) ainsi que leurs champs:
    - id 
    - coord (initialisées au coordonées de départs)
    - state: asleep, awake, reserved
    - dest l'array des destination dans l'ordre
    - dist l'array des distances entre le robots et sa/ses destination/s
    - range le paramètre dictant la strat"gie du robot

"""

def main(text_graph): 
    """ The main function, calling all the others, and printing the amount of turns required to wake all robots"""
    id_List,robot_List, graph = parse_graph_data(text_graph)
    rendering(id_List, robot_List, graph, 0)
    tour = 1
    # print("id: ", id_List, "\n")
    # print("\n", tour)
    # for robot in robot_List:
    #     print(robot)
    find_dest_opti(0, 0, robot_List, min, graph, id_List)
    rendering(id_List, robot_List, graph, tour)
    while not robots_all_awake(robot_List):
        tour +=1
        move_Robots(robot_List, graph, what_to_do_opti, id_List)
        rendering(id_List, robot_List, graph, tour)
        # if tour <100:
        #     print("\n",tour)
        #     for robot in robot_List:
        #         print(robot)
        # if tour >2:
        #     return 0
    # print("Pour graphe.txt (aka le graphe du démon) avec méthode: what_to_do1")
    # print("Robot tous réveillé en ",tour,"tours.")
    return tour

if __name__ == "__main__":
    main(sys.argv[1])
