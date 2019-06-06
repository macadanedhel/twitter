#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf8
import os
#from langdetect import detect
import json, csv
#import parser
import argparse
from collections import Counter
import ConfigParser
#from py2neo import authenticate, Graph, Node, Relationship

from filedata import filedata
from mongodata import mongodata
from speaking import speaking
from twmac import twmac

# _id=77555910
#
# twitt_ = twmac()

# followers = twitt_.followersID(id)
# print ("Followers:{0}").format(followers['num_followers'])
# #mngdb.insert_many_followers(followers)
# for _user in followers:
#     print _user
#
#

import networkx
from networkx.algorithms.approximation import clique
mngdb = mongodata()
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


## relation_graph = { (i['user'], i['friend']) for i in mngdb.get_relationship('followers')}.union( {(i['user'], i['friend']) for i in mngdb.get_relationship('friends') })
##RG_list=[i for i in relation_graph]

def _follower(name):
    if not str(name).isdigit():
        name = mngdb.get_followers(name)



twitt_ = twmac()
#followers=twitt_.followersID(77555910)
mngdb = mongodata()
#followers=mngdb.get_followers('macarionull')
followers=mngdb.get_followers('vespadict')
relation_graph = { (i['user'], i['friend']) for i in followers }
for item in followers:
    print ("Getting data from {}".format(item['friend']))
    followersUser = mngdb.get_followers(item['friend'])
    relation_graph=relation_graph.union({(i['user'], i['friend']) for i in followersUser})

RG_list=[i for i in relation_graph]


#w = 4
#h = 3
#d = 70
#plt.figure(figsize=(w, h), dpi=d)
G = networkx.Graph()

#H = networkx.path_graph(5)
#G.add_edges_from(H.edges())
#G.add_edges_from([(0, 2)])



G = networkx.Graph()
G.add_edges_from(RG_list)
print ("Numero de nodos: {}".format(G.number_of_nodes()))
print ("Numero de vertices:{}".format(G.number_of_edges()))
cliques = networkx.find_cliques(G)
print cliques

for clique in cliques:
    x=len(clique)
    if x > 3:
        print x


#print ("Numero de cliques:{}".format(networkx.graph_number_of_cliques(G)))
#print list(networkx.cliques_containing_node(G,77555910))

# IDEA: Dado un usuario, buscamos los que le siguen en 3 niveles de profundidad


#labels = [0, 1, 2, 3, 4]
#networkx.draw_networkx(G, with_labels=labels)
#networkx.draw_networkx(G, with_labels=False)
# plt.axis ("off")
#
#plt.show()
# plt.savefig("out.png")