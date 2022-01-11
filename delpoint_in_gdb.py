#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import os,sys,yaml,argparse
from neo4j import GraphDatabase

#class NODE():
_image_root_dir = os.getcwd()+"/map/"
_neo4j_root_dir = os.getcwd()+"/Neo4j_setting/"

def __init__(self,*args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--id_map', help='map ID', nargs='+', required=True)
    parser.add_argument('-ie', '--identifier', help='identifier', nargs='+', required=True)
    parser.add_argument('-s', '--neo4j_file', help='neo4j setting file', nargs='+', required=True)
    args = parser.parse_args()

    _id_map = args.id_map
    _identifier = args.identifier[0]
    _neo4j_path = args.neo4j_file[0]

    _neo4jDir = os.path.join(_neo4j_root_dir, _neo4j_path)

    with open(_neo4jDir, 'r', encoding='utf-8') as neo4j:
        neo4jstring = neo4j.read()
        neo4j_obj = yaml.safe_load(neo4jstring)
    neo4jData = {
                        "uri": neo4j_obj['uri'],
                        "userName": neo4j_obj['userName'],
                        "password": neo4j_obj['password']
                }
    return (_id_map,_identifier,neo4jData)

def CREATE_NODES(_id_map,_identifier,neo4jData,):
 
    #Neo4j Enterprise
    uri= neo4jData['uri']
    userName= neo4jData['userName']
    password= neo4jData['password']

    #Connect to the neo4j database server
    graphDB_Driver  = GraphDatabase.driver(uri, auth=(userName, password))
    
    with graphDB_Driver.session() as graphDB_Session:
        identifier = _identifier
        for args in _id_map:
            clean = 'MATCH (n) WHERE labels(n)=["GDB_'+ args +'"] AND n.Identifier = "'+ identifier +''+ args +'" DETACH DELETE n'
            clean_nodes = graphDB_Session.run(clean)
        print("All nodes and relationships are cleaned...")
    graphDB_Driver.close()

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(sys.argv) == 1:
        print("+++++++++++++++++++++++++++++++++++++++++++++\n")
        print("[********* Please input arguments **********]\n")
        print("+++++++++++++++++++++++++++++++++++++++++++++\n")
        sys.exit()
    _id_map,_identifier,neo4jData = __init__(args)
    CREATE_NODES(_id_map,_identifier,neo4jData)
