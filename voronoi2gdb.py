#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import os,sys,yaml,argparse
from neo4j import GraphDatabase
from PIL import Image
import numpy as np
from scipy.spatial import Voronoi
from bresenham import bresenham
import cv2

#class NODE():
_image_root_dir = os.getcwd()+"/map/"
_neo4j_root_dir = os.getcwd()+"/Neo4j_setting/"

def __init__(self,*args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--id_map', help='map ID', nargs='+', required=True)
    parser.add_argument('-f', '--floor_map', help='which floor', nargs='+', required=True)
    parser.add_argument('-p', '--pgm_file', help='pgm file', nargs='+', required=True)
    parser.add_argument('-y', '--yaml_file', help='yaml file', nargs='+', required=True)
    parser.add_argument('-s', '--neo4j_file', help='neo4j setting file', nargs='+', required=True)
    args = parser.parse_args()

    _id_map = args.id_map[0]
    _floor_map = args.floor_map[0]
    _pgm_path = args.pgm_file[0]
    _yaml_path = args.yaml_file[0]
    _neo4j_path = args.neo4j_file[0]

    _imageDir = os.path.join(_image_root_dir, _yaml_path)
    _neo4jDir = os.path.join(_neo4j_root_dir, _neo4j_path)

    with open(_neo4jDir, 'r', encoding='utf-8') as neo4j:
        neo4jstring = neo4j.read()
        neo4j_obj = yaml.safe_load(neo4jstring)
    neo4jData = {
                        "uri": neo4j_obj['uri'],
                        "userName": neo4j_obj['userName'],
                        "password": neo4j_obj['password']
                }

    with open(_imageDir, 'r', encoding='utf-8') as yml:
        ymlstring = yml.read()
        yaml_obj = yaml.safe_load(ymlstring)
    yamlData = {
                        "origin": {"x": yaml_obj['origin'][0], "y": yaml_obj['origin'][1]},
                        "resolution": {"x": yaml_obj['resolution'], "y": yaml_obj['resolution']},
                        "direction": {"x": 1, "y": -1}
                }
    return (_id_map,_floor_map,neo4jData,_pgm_path,yamlData)

def create_vertices(_pgm_path):
    '''
    Create a vertice database by reading a PNG image
    '''
    map = cv2.imread (os.path.join(_image_root_dir, _pgm_path))

    #minimum and maximum north coordinates
    north_min = 0
    north_max = map.shape[0]

    #minimum and maximum east coordinates
    east_min = 0
    east_max = map.shape[1]

    #given the minimum and maximum coordinates we can
    #calculate the size of the grid
    north_size = int(north_max - north_min)
    east_size = int(east_max - east_min)

    #Initialize an empty grid
    grid = np.zeros((north_size, east_size))
    #Initialize an empty list for Voronoi points
    points = []

    #white in RGB
    pixel = (0,0,0)
    best = (0, 0, 0)
    for x in range (map.shape [0] ):
        for y in range (map.shape [1] ):
                ipixel = map [ (x, y) ]
                if (tuple(ipixel) == pixel):
                    best = (0, x, y)
                    x, y = best [1:]

                    #Populate the grid with obstacles
                    grid[x, y] = 1
                    #add center of obstacles to points list
                    points.append([x, y])

    #create a voronoi graph based on location of obstacle centres
    graph = Voronoi(points)

    #check each edge from graph.ridge_vertices for collision
    edges = []
    for v in graph.ridge_vertices:
        p1 = graph.vertices[v[0]]
        p2 = graph.vertices[v[1]]
        cells = list(bresenham(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1])))
        hit = False

        for c in cells:
            #First check if we're off the map
            if np.amin(c) < 0 or c[0] >= grid.shape[0] or c[1] >= grid.shape[1]:
                hit = True
                break
            #Next check if we're in collision
            if grid[c[0], c[1]] == 1:
                hit = True
                break

        #If the edge does not hit on obstacle
        #add it to the list
        if not hit:
            #array to tuple for future graph creation step
            p1 = (p1[0], p1[1])
            p2 = (p2[0], p2[1])
            edges.append((p1, p2))
    return points, edges


def CREATE_NODES(points,edges,_id_map,_floor_map,neo4jData):
 
    #Neo4j Enterprise
    uri= neo4jData['uri']
    userName= neo4jData['userName']
    password= neo4jData['password']

    #Connect to the neo4j database server
    graphDB_Driver  = GraphDatabase.driver(uri, auth=(userName, password))

    #Delete all the nodes and relationships
    clean = """
    MATCH (n)
    DETACH DELETE n
    """
    with graphDB_Driver.session() as graphDB_Session:
        # clean_nodes = graphDB_Session.run(clean)
        # print("All nodes and relationships are cleaned...")
        print("New nodes and relationships are being added...")

        floor = str(_floor_map)
        action = "None"
        identifier = "None"

        z = str(int(_floor_map) * 100)
        for p in enumerate(points):
            x = str(p[1][0])
            y = str(p[1][1])

            #Cypher statement, add variables in the statement
            Obs = 'CREATE (p:GDB_'+ _id_map +'{z:"'+ z +'",y:"'+ y +'",x:"'+ x +'",Floor:"'+ floor +'",Action:"'+ action +'",Identifier:"Obs_'+ _id_map +'"})'
            #Start cypher statement
            create_n_obs = graphDB_Session.run(Obs)

        z1 = z2 = str(int(_floor_map) * 100)
        for e in enumerate(edges):
            x1 = str(e[1][0][0])
            y1 = str(e[1][0][1])
            x2 = str(e[1][1][0])
            y2 = str(e[1][1][1])
            h = ( (float(z1)-float(z2))**2 +(float(y1)-float(y2))**2 +(float(x1)-float(x2))**2 )**0.5
            heuristics = str(h)

            #Cypher statement, add variables in the statement
            Ver = 'CREATE (p1:GDB_'+ _id_map +'{z:"'+ z1 +'",y:"'+ y1 +'",x:"'+ x1 +'",Floor:"'+ floor +'",Action:"'+ action +'",Identifier:"'+ identifier +'"})-[rel:heuristics_'+ _id_map +'{h:"'+ heuristics +'"}]->(p2:GDB_'+ _id_map +'{z:"'+ z2 +'",y:"'+ y2 +'",x:"'+ x2 +'",Floor:"'+ floor +'",Action:"'+ action +'",Identifier:"'+ identifier +'"})'
            #Start cypher statement
            create_n_r = graphDB_Session.run(Ver)

        #Copy all properties
        A = 'MATCH (n:GDB_'+ _id_map +'), (m:GDB_'+ _id_map +') WHERE labels(n)=["GDB_'+ _id_map +'"] AND n.x = m.x AND n.y = m.y AND n.z = m.z AND ID(n)<ID(m) WITH n, m SET n += m'
        #Copy all outgoing relations
        B = 'MATCH (n:GDB_'+ _id_map +'), (m:GDB_'+ _id_map +')-[rel:heuristics_'+ _id_map +']->(endnode) WHERE labels(n)=["GDB_'+ _id_map +'"] AND n.x = m.x AND n.y = m.y AND n.z = m.z AND ID(n)<ID(m) WITH n, collect(endnode) as endnodes FOREACH (x in endnodes | CREATE (n)-[rel:heuristics_'+ _id_map +'{h:'+ str(( (float(z1)-float(z2))**2 +(float(y1)-float(y2))**2 +(float(x1)-float(x2))**2 )**0.5) +'}]->(x))'
        #Copy all incoming relations
        C = 'MATCH (n:GDB_'+ _id_map +'), (m:GDB_'+ _id_map +')<-[rel:heuristics_'+ _id_map +']-(endnode) WHERE labels(n)=["GDB_'+ _id_map +'"] AND n.x = m.x AND n.y = m.y AND n.z = m.z AND ID(n)<ID(m) WITH n, collect(endnode) as endnodes FOREACH (x in endnodes | CREATE (n)<-[rel:heuristics_'+ _id_map +'{h:'+ str(( (float(z1)-float(z2))**2 +(float(y1)-float(y2))**2 +(float(x1)-float(x2))**2 )**0.5) +'}]-(x))'
        #Delete duplicates
        D = 'MATCH (n:GDB_'+ _id_map +'), (m:GDB_'+ _id_map +') WHERE labels(n)=["GDB_'+ _id_map +'"] AND n.x = m.x AND n.y = m.y AND n.z = m.z AND ID(n)<ID(m) detach delete m'

        nodes_A = graphDB_Session.run(A)
        nodes_B = graphDB_Session.run(B)
        nodes_C = graphDB_Session.run(C)
        nodes_D = graphDB_Session.run(D)

    graphDB_Driver.close()

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(sys.argv) == 1:
        print("+++++++++++++++++++++++++++++++++++++++++++++\n")
        print("[********* Please input arguments **********]\n")
        print("+++++++++++++++++++++++++++++++++++++++++++++\n")
        sys.exit()
    _id_map,_floor_map,neo4jData,_pgm_path,yamlData = __init__(args)
    points, edges = create_vertices(_pgm_path)
    CREATE_NODES(points,edges,_id_map,_floor_map,neo4jData)
