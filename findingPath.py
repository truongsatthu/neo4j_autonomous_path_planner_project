#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys,os,time,yaml,argparse,itertools
from numpy.lib.arraysetops import isin
from queue import PriorityQueue
from mpl_toolkits.mplot3d import Axes3D
from neo4j import GraphDatabase
from scipy import spatial
import copy
from bresenham import bresenham
sys.setrecursionlimit(5000) 

_image_root_dir = os.getcwd()+"/map/"
_neo4j_root_dir = os.getcwd()+"/Neo4j_setting/"

def plotVoronoiPath(path):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    map1 = mpimg.imread(_image_root_dir+'chinokyoten1f.png')
    map2 = mpimg.imread(_image_root_dir+'chinokyoten2f.png')
    map3 = mpimg.imread(_image_root_dir+'chinokyoten3f.png')
    y, x = np.ogrid[0:map1.shape[0], 0:map1.shape[1]]
    ax.plot_surface(x, y, np.atleast_2d(100),rstride=15,cstride=15,facecolors=map1,shade=False)
    ax.plot_surface(x, y, np.atleast_2d(200),rstride=15,cstride=15,facecolors=map2,shade=False)
    ax.plot_surface(x, y, np.atleast_2d(300),rstride=15,cstride=15,facecolors=map3,shade=False)

    #setting view
    ax.view_init(30, 30)
    # make the panes transparent
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    # make the grid lines transparent
    ax.xaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.yaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.zaxis._axinfo["grid"]['color'] =  (1,1,1,0)

    for i in range(len(path)-1):
        p1 = path[i]
        p2 = path[i+1]
        plt.plot([p1[2], p2[2]], [p1[1], p2[1]], [p1[0], p2[0]], 'r-')
    for i in (range(len(number_list))):
        ax.plot([float(number_list[i][2])], [float(number_list[i][1])], [float(number_list[i][0])], 'ko', markersize=3)
    for i in (range(len(elevs))):
        ax.plot([float(elevs[i][2])], [float(elevs[i][1])], [float(elevs[i][0])], 'yo', markersize=3) 
    plt.show()

class DBnode():
    def __init__(self,*args):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--id_map', help='map ID', nargs='+', required=True)
        parser.add_argument('-n', '--neo4j_file', help='neo4j setting file', nargs='+', required=True)
        parser.add_argument('-s', '--start_pos', help='start position', nargs='+', required=True)
        parser.add_argument('-g', '--goal_pos', help='goal position', nargs='+', required=True)
        parser.add_argument('-w', '--waypoints', help='waypoints position', nargs='+', required=False)
        parser.add_argument('-alg', '--algorithm', help='planning algorithm', nargs='+', required=False)
        args = parser.parse_args()

        self._id_map = args.id_map
        _neo4j_path = args.neo4j_file[0]
        self._start_pos = list((args.start_pos[0]).split(","))
        self._goal_pos = list((args.goal_pos[0]).split(","))
        self._waypoints_list = args.waypoints
        self._algorithm = args.algorithm
        self._neo4jDir = os.path.join(_neo4j_root_dir, _neo4j_path)
        with open(self._neo4jDir, 'r', encoding='utf-8') as neo4j:
            neo4jstring = neo4j.read()
            neo4j_obj = yaml.safe_load(neo4jstring)
        self.neo4jData = {
                            "uri": neo4j_obj['uri'],
                            "userName": neo4j_obj['userName'],
                            "password": neo4j_obj['password']
                    }

def __number_list__(self):
    number_list = []
    if (waypoints_list != None):
        for i in (range(len(self._waypoints_list))):
            number_list.append((list(self._waypoints_list[i].split(","))))
    number_list.insert(0,start_pos)
    number_list.insert(len(number_list),goal_pos)
    return number_list

    #return (_id_map,neo4jData,_start_pos,_goal_pos,_waypoints_list,_algorithm,number_list)

def READ_NODES_2EDGES(self,*args): # _id_map, neo4jData
    points = []
    edges  = []
    elevs  = []

    #Neo4j Enterprise
    uri= neo4jData['uri']
    userName= neo4jData['userName']
    password= neo4jData['password']
    #Connect to the neo4j database server
    graphDB_Driver  = GraphDatabase.driver(uri, auth=(userName, password))

    with graphDB_Driver.session() as graphDB_Session:
        for args in id_map: # _id_map
            Obs_cal='MATCH (n) WHERE labels(n)=["GDB_'+ args +'"] AND n.Identifier = "Obs_'+ args +'" RETURN n'
            Ver_cal='MATCH (n)-[r]->(m) WHERE labels(n)=["GDB_'+ args +'"] RETURN n,r,m'
            Ele_cal='MATCH (n) WHERE labels(n)=["GDB_'+ args +'"] AND n.Identifier = "EP_'+ args +'" RETURN n'
            nodeo = graphDB_Session.run(Obs_cal)
            nodes = graphDB_Session.run(Ver_cal)
            nodee = graphDB_Session.run(Ele_cal)
            for node in nodeo:
                #print(str(node[0]['z']), node[0]['y'], node[0]['x'],node[0]['Action'], node[0]['Identifier'], node[0]['Floor'])
                p = (float(node[0]['y']), float(node[0]['x']))
                points.append(p)
            for node in nodes:
                #print(str(node[0]['z']), node[0]['y'], node[0]['x'],node[0]['Action'], node[0]['Identifier'], node[0]['Floor'])
                p1 = (float(node[0]['z']), float(node[0]['y']), float(node[0]['x']))
                p2 = (float(node[2]['z']), float(node[2]['y']), float(node[2]['x']))
                edges.append((p1, p2))
            for node in nodee:
                #print(str(node[0]['z']), node[0]['y'], node[0]['x'],node[0]['Action'], node[0]['Identifier'], node[0]['Floor'])
                e = (float(node[0]['z']), float(node[0]['y']), float(node[0]['x']))
                elevs.append(e)

        #EL_closest
        for x,e in enumerate (elevs):
            dist_e = 1000000
            for i in range(len(edges)):
                for j in (edges[i]):
                    p = j
                    if (p[0]==e[0]):
                        d = heuristic(e, p)
                        if d < dist_e:
                            EL = p
                            dist_e = d
            edges.append((EL,e))
        #for x in itertools.permutations(elevs, r=2):
        for i in range(len(elevs)-1):
            edges.append((elevs[i],elevs[i+1]))

        #WP_closest
        for w in number_list:
            dist_w = 1000000
            W = (float(w[0]),float(w[1]),float(w[2]))
            for i in range(len(edges)):
                for j in (edges[i]):
                    p = j
                    if (p[0]==W[0]):
                        d = heuristic(w, p)
                        if d < dist_w:
                            WP = p
                            dist_w = d
            edges.append((WP,W))
    graphDB_Driver.close()

    # #Robot's width is considered (pixcel)
    # R = 0.0
    # tree = spatial.KDTree(np.asarray(points))
    # for i,e in enumerate(edges):
    #     for j,n in enumerate(e):
    #         nodes = np.asarray((n[1],n[2]))
    #         if (len(tree.query_ball_point(nodes, R)) != 0):
    #             edges.pop(i)
    #             break
    #         else:
    #             pass
                
    return points,edges,elevs    

def create_waypoints_edges(number_list):
    waypoints_edges = []
    for w in number_list:
        i = (float(w[0]),float(w[1]),float(w[2]))
        for j in elevs:
            if (i[0] == j[0]):
                waypoints_edges.append((i, j))
    for x in itertools.permutations(elevs, r= 2):
        waypoints_edges.append((x[0],x[1]))
    for y in itertools.permutations(number_list, r= 2):
        W1 = (float(y[0][0]),float(y[0][1]),float(y[0][2]))
        W2 = (float(y[1][0]),float(y[1][1]),float(y[1][2]))
        if (W1[0] == W2[0]):
            waypoints_edges.append((W1,W2))
    return waypoints_edges

def create_graph(edges):
    graph = nx.Graph()
    for elem in edges:
        p1 = elem[0]
        p2 = elem[1]
        dist = heuristic(p1, p2)
        graph.add_edge(p1, p2, weight=dist)
    return graph

def heuristic(n1, n2):
    return ( (float(n1[0])-float(n2[0]))**2 +(float(n1[1])-float(n2[1]))**2 +(float(n1[2])-float(n2[2]))**2 )**0.5


def a_star_graph(graph, start_pos, goal_pos, h): # graph,_start_pos,_goal_pos, h
    path = []
    path_cost = 0
    queue = PriorityQueue()
    queue.put((0, start_pos))
    visited = set(start_pos)

    branch = {}
    found = False

    while not queue.empty():
        item = queue.get()
        current_node = item[1]
        if current_node == start_pos:
            current_cost = 0.0
        else:
            current_cost = branch[current_node][0]

        if current_node == goal_pos:
            print('Found a path.')
            found = True
            break
        else:
            for next_node in graph[current_node]:
                cost = graph.edges[current_node, next_node]['weight']
                branch_cost = current_cost + cost
                queue_cost = branch_cost + h(next_node, goal_pos)

                if next_node not in visited:
                    visited.add(next_node)
                    branch[next_node] = (branch_cost, current_node)
                    queue.put((queue_cost, next_node))
    if found:
        # retrace steps
        n = goal_pos
        path_cost = branch[n][0]
        path.append(goal_pos)
        while branch[n][1] != start_pos:
            path.append(branch[n][1])
            n = branch[n][1]
        path.append(branch[n][1])
    else:
        print('**********************')
        print('Failed to find a path!')
        print('**********************')
    return path[::-1], path_cost

def optimization_path(pathIndex,path_opt,points):
    while (len(path_opt) > pathIndex + 2):
        A = path_opt[pathIndex]
        B = path_opt[pathIndex+1]
        C = path_opt[pathIndex+2]
        cells = list(bresenham(int(A[1]),int(A[2]),int(C[1]),int(C[2])))
        hit = False
        for p in points:
            for c in cells:
                if (int(p[0])==c[0] and int(p[1])==c[1]):
                    hit = True
                    break
            break
        if not hit:
            path_opt.remove(B)
            pathIndex += 1
    return path_opt


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(sys.argv) == 1:
        print("+++++++++++++++++++++++++++++++++++++++++++++\n")
        print("[********* Please input arguments **********]\n")
        print("+++++++++++++++++++++++++++++++++++++++++++++\n")
        sys.exit()
    neo4jNode = DBnode(args)
    id_map = neo4jNode._id_map
    neo4jData =  neo4jNode.neo4jData
    start_pos = neo4jNode._start_pos
    goal_pos  = neo4jNode._goal_pos
    waypoints_list = neo4jNode._waypoints_list
    algorithm = neo4jNode._algorithm
    number_list = __number_list__(waypoints_list)
    #id_map,neo4jData,start_pos,goal_pos,waypoints_list,algorithm,number_list = __init__(args)
    points,edges,elevs = READ_NODES_2EDGES(id_map,neo4jData)
    print(elevs)
#****************************************************************************************************
    if (algorithm == None):
        graph = create_graph(edges)
        path_WP = []
        for i in (range(len(number_list)-1)):
            WP1 = (float(number_list[i][0]),float(number_list[i][1]),float(number_list[i][2]))
            WP2 = (float(number_list[i+1][0]),float(number_list[i+1][1]),float(number_list[i+1][2]))
            path, cost = a_star_graph(graph, WP1, WP2, heuristic)
            path_WP.extend(path)
        # print(path_WP)
        # plotVoronoiPath(path_WP)
    elif (algorithm != None):
        waypoints_edges = create_waypoints_edges(number_list)
        graph = create_graph(waypoints_edges)
        path_WP = []
        for i in (range(len(number_list)-1)):
            WP1 = (float(number_list[i][0]),float(number_list[i][1]),float(number_list[i][2]))
            WP2 = (float(number_list[i+1][0]),float(number_list[i+1][1]),float(number_list[i+1][2]))
            path, cost = a_star_graph(graph, WP1, WP2, heuristic)
            path_WP.extend(path)
        # print(path_WP)
        # plotVoronoiPath(path_WP)
    else:
        pass
    print("Optimizing path...")
    path_opt = copy.deepcopy(path_WP)
    pathCount = 0
    while pathCount < len(path_opt) - 2:
        # pathCount = 0
        path_opt = optimization_path(pathCount,path_opt,points)
        pathCount += 1
    print("End of path optimization")
    print(path_opt)
    plotVoronoiPath(path_opt)
#****************************************************************************************************
    t0 = time.clock()
    t1 = time.clock()
    total = t1-t0
    print('Compu. time =', total)
