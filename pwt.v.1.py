#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf8
import os
from langdetect import detect
import json, csv
#import parser
import argparse
from collections import Counter
import ConfigParser
from py2neo import authenticate, Graph, Node, Relationship

import networkx
from networkx.algorithms.approximation import clique
import matplotlib
matplotlib.use('TkAgg')

from filedata import filedata
from mongodata import mongodata
from speaking import speaking
from twmac import twmac

# En el mongo voy a montar distintas colecciones, unas de catalogo y otras de relacion
# Objetos principales son el twitter y el user
# Una coleccion debe ser users
# La colección friends tendrá dos campos user, friend y el valor será el id
# la coleccion followers tendrá dos campos user, follower y el valor será el id

# ﻿db.getCollection('tweets').find({},{user:1, text:1, retweeted:1, lang:1, created_at:1})
# ﻿db.getCollection('tweets').find({},{text:1, _id:0})

#=======================================================================================================================
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
#=======================================================================================================================
WORLD_WOE_ID = 1
TOP=10
#-----------------------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description ='To test different options',
    epilog      = 'comments > /dev/null'
)

#=======================================================================================================================
parser.add_argument('--print_',  "-p", action='store_true', help='print')
parser.add_argument('--mongodb',  "-db", action='store_true', help='print')
parser.add_argument('--trends',  "-t", action='store_true', help='To get which it\'s said')
parser.add_argument('--trendAvailable',  "-ta", action='store_true', help='trends available, it means, countries speaking, WOEID')
parser.add_argument('--friends',  '-fr', action='store_true', help='get your following contacts')
parser.add_argument('--other_friend',  '-rf', type=str, help='get from other user his "friends" contacts')
parser.add_argument('--followers',  '-fo', action='store_true', help='get your following contacts')
parser.add_argument('--other_follower',  '-of', type=str, help='get from other user his "following" contacts')
parser.add_argument('--lists',  "-l",  type=str, help='lists of a given user (me|screen_name)')
parser.add_argument('--memberships',  "-m", action='store_true', help='print')
parser.add_argument('--tweets',  "-w", action='store_true', help='tweets from home')
parser.add_argument('--users',  "-r", type=str, help='users to find, you can use various names, comma separated without spaces')
parser.add_argument('--tweets_user',  "-u", type=str, help='tweets of a given user (me|screen_name)')
parser.add_argument('--user2csv',  "-u2csv", action='store_true', help='data user to analyze')
parser.add_argument('--data2neo',  "-d2neo", action='store_true', help='data to graph creation')
parser.add_argument('--get_userid',  '-n', type=str, help='get userid by name or screen_name')
parser.add_argument('--get_userid_regex',  '-nr', type=str, help='get userid by name or screen_name but regex based')
parser.add_argument('--get_tweet_user',  '-gtu', type=str, help='get downloaded tweets by name or screen_name')
parser.add_argument('--userstweets',  "-ut", action='store_true', help='return number of teewts by user ordered desc')
parser.add_argument('--get_username',  '-gn', type=str, help='get name or screen_name from userid')
parser.add_argument('--resolve_na',  '-a', action='store_true', help='resolve name or screen_name from userid')
parser.add_argument('--hide',  '-hh', action='store_true', help='hide some exits')
parser.add_argument('--get_tweet_user2analyze',  '-gtua', type=str, help='get downloaded tweets by name or screen_name to analyze, hash, user and words')
parser.add_argument('--user',  '-au', action='store_true', help='users in get_tweet_user2analyze')
parser.add_argument('--hash',  '-ah', action='store_true', help='hashes in get_tweet_user2analyze')
parser.add_argument('--words',  '-aw', action='store_true', help='words in get_tweet_user2analyze')
parser.add_argument('--tweetsxuser',  '-txu', action='store_true', help='shows tweets per user')
parser.add_argument('--top',  '-tt', action='store_true', help='shows top number in searches of get_tweet_user2analyze')
parser.add_argument('--clan',  '-c', type=str, help='clique')
parser.add_argument('--lookup',  '-k', type=str, help='User lookup of a user')

#parser.add_argument('--test',  "-test", action='store_true', help='print')
parser.add_argument('--test',  "-test", type=str, help='print')
parser.add_argument('--ptest',  "-ptest", type=str, help='print')
#-----------------------------------------------------------------------------------------------------------------------
args = parser.parse_args()
#-----------------------------------------------------------------------------------------------------------------------

def clan(user, temp=False):
    twitt_ = twmac()
    mngdb = mongodata()
    if str(user).isdigit():
        followers=twitt_.followersID(user)
    else:
        followers = twitt_.followers(user)
    print ("Getting data from {}".format(user))
    # Info Usuarios
    followersItems = followers['ids']
    # Insert info usuarios + relaciones
    mngdb.insert_many_followers(followers)
    # Temporal usuarios
    if temp:
        mngdb.insert_temp_users(followersItems)
    # conjunto de usuarios
    relation_graph = {(i['user'], i['friend']) for i in followers['followers']}
    print ("Num relationships :{} ".format(len(relation_graph)))
    return relation_graph


if args.trends:
    twitt_ = twmac()
    world_trends = twitt_.trends(WORLD_WOE_ID)
    if args.print_:
         fwrite = filedata()
         fwrite.trends(json.dumps(world_trends, indent=1))
    elif args.mongodb:
        mngdb = mongodata()
        mngdb.insert_many_trends(world_trends)
    else:
        print (json.dumps(world_trends, indent=1))
elif args.lookup:
    twitt_ = twmac()
    print twitt_.get_user_lookup(args.lookup)
elif args.trendAvailable:
    twitt_ = twmac()
    world_trends = twitt_.trendAvailable(WORLD_WOE_ID)
    if args.print_:
         fwrite = filedata()
         fwrite.trendAvailable(json.dumps(world_trends, indent=1))
    elif args.mongodb:
        mngdb = mongodata()
        mngdb.insert_many_trendAvailable(world_trends)
    else:
        print(json.dumps(world_trends, indent=1))
elif args.friends or args.other_friend:
    twitt_ = twmac()
    some = args.other_friend
    friends = twitt_.friends(some)
    print ("Friends:{0}").format(friends['num_friends'])
    if args.print_ and friends['num_friends']:
        fwrite = filedata()
        fwrite.friends(json.dumps(friends, indent=1))
    elif args.mongodb and friends['num_friends']:
        mngdb = mongodata()
        mngdb.insert_many_friends(friends)
    elif friends['num_friends']:
        print (json.dumps(friends, indent=1))
    else:
        print ("{0} Not found !!!\n").format("Friends")
elif args.lists:
    twitt_ = twmac()
    lists = twitt_.lists(args.lists)
    print (json.dumps(lists, indent=1))
elif args.memberships:
    twitt_ = twmac()
    lists = twitt_.memberships()
elif args.users:
    twitt_ = twmac()
    users = twitt_.users(args.users)
    if args.print_:
        fwrite = filedata()
        fwrite.users(json.dumps(users, indent=1))
    elif args.mongodb :
        mngdb = mongodata()
        mngdb.insert_many_users(users)
    else:
        print (json.dumps(users, indent=1))
elif args.followers or args.other_follower:
    twitt_ = twmac()
    some=args.other_follower
    followers = twitt_.followers(some)
    print ("Followers:{0}").format(followers['num_followers'])
    if args.print_ and followers['num_followers']:
        fwrite = filedata()
        fwrite.followers(json.dumps(followers, indent=1))
    elif args.mongodb and followers['num_followers']:
        mngdb = mongodata()
        mngdb.insert_many_followers(followers)
    elif followers['num_followers']:
        print (json.dumps(followers, indent=1))
    else:
        print ("{0} Not found !!!\n").format("Followers")
elif args.user2csv:
    mngdb = mongodata()
    myself = mngdb.list_users()
    if not args.print_:
        print myself[0].keys()
    users=[]
    for row in myself:
        try:
            if not row["retweet_count"] or row["withheld_in_countries"]:
                row["retweet_count"]=0
        except:
            row["retweet_count"] = 0
            row["withheld_in_countries"] = 0
        rowaux = {}
        for w in row.keys():
            if type(row[w]) is unicode:
                rowaux[w] = row[w].encode('utf-8')
            elif str(row[w]).isdigit():
                rowaux[w] = row[w]
            else:
                rowaux[w] = row[w]
            if type(rowaux[w]) is 'str' :
                rowaux[w] = rowaux[w].replace("\r\n", " ")
                rowaux[w]=rowaux[w].replace("\n"," ")
        if args.print_:
            users.append(rowaux)
        else:
            print (
                "{_id},{screen_name},{location},{name},{followers_count},{friends_count},{created_at},{url},{lang},{screen_name},{retweet_count}, {verified}, {listed_count},{statuses_count}, {default_profile},{withheld_in_countries},{description},{time_zone},{utc_offset},{lang}".format(
                    **rowaux))

    if args.print_:
        fwrite = filedata()
        fwrite.user2csv(users)
elif args.tweets or args.tweets_user:
    twitt_ = twmac()
    if args.tweets:
        tweets = twitt_.get_tweet_timeline('home')
    elif args.tweets_user == 'me':
        tweets = twitt_.get_tweet_timeline()
    else:
        tweets = twitt_.get_tweet_timeline('user',args.tweets_user )

    if tweets<0:
        print "ERROR"
        exit (0)
    elif args.mongodb and tweets['num_tweets']:
        print ('Fetched {} tweets').format(tweets['num_tweets'])
        if args.mongodb and tweets['num_tweets']:
            mngdb = mongodata()
            mngdb.insert_many_tweets(tweets)
    elif args.print_:
            fwrite = filedata()
            fwrite.tweets(json.dumps(tweets['tweets'], indent=1))
            fwrite.users(json.dumps(tweets['users'], indent=1))
    else:
        print (json.dumps(tweets['tweets'], indent=1))
        print (json.dumps(tweets['users'], indent=1))
elif args.data2neo:
    mngdb = mongodata()
    myself = mngdb.data2neo()
    if not args.print_:
        print myself[0].keys()
    users=[]
    followers=[]
    friends=[]
    for row in myself:
        tmp={}
        try:
            if not row["retweet_count"] or row["withheld_in_countries"]:
                row["retweet_count"]=0
        except:
            row["retweet_count"] = 0
            row["withheld_in_countries"] = 0
        rowaux = {}
        for w in row.keys():
            if type(row[w]) is unicode:
                rowaux[w] = row[w].encode('utf-8')
            elif str(row[w]).isdigit():
                rowaux[w] = row[w]
            else:
                rowaux[w] = row[w]
        t = {str(rowaux["_id"]): [
            {'screen_name': rowaux["screen_name"], 'name': rowaux["name"], 'verified': rowaux["verified"],
             "default_profile": rowaux["default_profile"]}, {'lang': rowaux["lang"]},
            {'location': rowaux["location"], 'time_zone': rowaux["time_zone"], 'utc_offset': rowaux["utc_offset"]}]}
        if args.print_:
            users.append(t)
        else:
            print (t)

    relation = mngdb.get_relationship('followers')
    for i in relation:
        if args.print_:
            followers.append([i['friend'], i['user']])
        else:
            print ("{0},{1}").format(i['friend'], i['user'])


    relation = mngdb.get_relationship('friends')
    for i in relation:
        if args.print_:
            friends.append([i['user'], i['friend']])
        else:
            print ("{0},{1}").format(i['user'], i['friend'])

    if args.print_:
        fwrite = filedata()
        files=fwrite.data2neo(users,followers,friends)
        ENVCONFIG = "config/env.ini"
        EnvConfig = ConfigParser.ConfigParser()
        Config = ConfigParser.ConfigParser()
        EnvConfig.read(ENVCONFIG)

        g = Graph(host=EnvConfig.get('neo4j', 'ip'),
                  user=EnvConfig.get('neo4j', 'user'),
                  password=EnvConfig.get('neo4j', 'password'),
                  bolt=False,
                  secure=False,
                  bolt_port=int(EnvConfig.get('neo4j', 'bolt')),
                  http_port=int(EnvConfig.get('neo4j', 'http')),
                  https_port=int(EnvConfig.get('neo4j', 'https'))
                  )

        query = """
                 USING PERIODIC COMMIT
                 LOAD CSV WITH HEADERS FROM "file:///{0}" AS userline 
                 CREATE (:User {{ _id: userline._id, verified: userline.verified,
                 screen_name: userline.screen_name, default_profile: userline.default_profile,
                 name: userline.name }} )
                 
                 """.format(files['remote_user'])
        g.run(query)
        g.run("CREATE INDEX ON :User(_id)")
        print ("File {0} loaded !!!").format(files['user'])
        os.remove(files['user'])
        print ("\tFile {0} removed !!!\n").format(files['user'])


        query = """
                 USING PERIODIC COMMIT
                 LOAD CSV WITH HEADERS FROM "file:///{0}" AS langline 
                 CREATE (:Language {{ _id: langline._id, name:  langline.lang }} )

                 """.format( files['remote_lang'] )

        g.run(query)
        g.run("CREATE INDEX ON :Language(_id)")
        print ("File {0} loaded !!!").format(files['lang'])
        os.remove(files['lang'])
        print ("\tFile {0} removed !!!\n").format(files['lang'])


        query = """
                 USING PERIODIC COMMIT
                 LOAD CSV WITH HEADERS FROM "file:///{0}" AS locline
                 CREATE (:Location {{ name : locline.location, time_zone: locline.time_zone, utc_offset: locline.utc_offset }} )
                 
                 """.format( files['remote_location'])
        g.run("CREATE INDEX ON :Location(name)")
        g.run(query)
        print ("File {0} loaded !!!").format(files['location'])
        os.remove(files['location'])
        print ("\tFile {0} removed !!!\n").format(files['location'])

        query = """
                         LOAD CSV WITH HEADERS FROM "file:///{0}" AS row
                         MATCH (user:User {{ _id: row.user  }} )
                         MATCH (friend:User {{ _id: row.friend }} )
                         MERGE (user)-[:ISFRIEND]->(friend)

                         """.format(files['remote_friends'])
        g.run(query)
        print ("File {0} loaded !!!").format(files['friends'])
        os.remove(files['friends'])
        print ("\tFile {0} removed !!!\n").format(files['friends'])

        query = """
                                 LOAD CSV WITH HEADERS FROM "file:///{0}" AS row
                                 MATCH (user:User {{ _id: row.user  }} )
                                 MATCH (friend:User {{ _id: row.friend }} )
                                 MERGE (friend)-[:ISFOLLOWER]->(user)

                                 """.format(files['remote_followers'])
        g.run(query)
        print ("File {0} loaded !!!").format(files['followers'])
        os.remove(files['followers'])
        print ("\tFile {0} removed !!!\n").format(files['followers'])
elif args.get_userid:
    mngdb = mongodata()
    user_id = mngdb.get_userid(args.get_userid)
    print user_id
elif args.get_tweet_user:
    mngdb = mongodata()
    user_id = mngdb.get_userid(args.get_tweet_user)
    if user_id:
        tweets=mngdb.get_tweets_byuserid(user_id)
        for line in tweets:
            print line['text']
    else:
        print ("User not found !!!")
elif args.get_userid_regex:
    mngdb = mongodata()
    user_id = mngdb.get_userid_regex(args.get_userid_regex)
    if user_id:
        for user in user_id:
            print ("name: {0}\tscreen_name: {1}").format(user['name'].encode('utf-8'),
                                                       user['screen_name'].encode('utf-8'))
elif args.userstweets:
    mngdb = mongodata()
    tweets = mngdb.get_tweets_users()
    total=0
    for t in tweets:
        if args.resolve_na:
            aux=mngdb.get_username(str(t['_id']['user']))
            print ("Name:{0}\tscreen_name:{1}\t{2}").format(aux["name"].encode('utf-8'),aux["screen_name"].encode('utf-8'),t['count'])
        else:
            print ("User:{0}\t{1}").format(t['_id']['user'], t['count'])
        total=total+t['count']
    print("Total tweets {}").format(total)
elif args.get_username:
    mngdb = mongodata()
    user = mngdb.get_username(args.get_username)
    print ("Name:{0}\tscreen_name:{1}").format(user["name"],user["screen_name"])
elif args.get_tweet_user2analyze:

    mngdb = mongodata()
    highlight = {'user':[],'words':[],'hash':[]}
    _users=None
    if args.user:
        _users=True
    _words=None
    if args.words:
        _words=True
    _hash=None
    if args.hash:
        _hash = True
    if not( _users or _hash or _words ):
        _users=_hash=_words=True
    user_id = mngdb.get_userid(args.get_tweet_user2analyze)
    if user_id:
        tweets = mngdb.get_tweets_byuserid(user_id)
        words = speaking()

        for line in tweets:
            #print line['text']
            try:
                lang = detect(line['text'])
            except:
                #print ("Language no detected\n using english")
                lang='en'
            datos = words.lang_process(line['text'], lang, _users, _hash, _words)
            #print datos
            for key in datos.keys():
                if len(datos[key])>0:
                    if not args.hide:
                        print ("[{0}]").format(key)
                    else:
                        print ".",
                    totaldata=datos[key]
                    for value in totaldata:
                        highlight[key].append(value)
                        if not args.hide:
                            print ("\t{0}").format(value.encode('utf8'))
                        else:
                            print ".",
        # [term for term in self.preprocess(s, True) if term not in stop and term.startswith('@')]
        print
        if args.top:
            print "TOP 10 of items found !!!"
            for item in [highlight[key] for key in highlight.keys()]:
                c = Counter(item)
                print c.most_common()[:10]  # top 10 print
    else:
        print ("User not found !!!")
elif args.tweetsxuser:
    mngdb = mongodata()
    tweets = mngdb.tweets_per_user()
    for id,count in sorted(tweets.iteritems(),key=lambda (k,v):v, reverse=True):
        if args.resolve_na:
            aux = mngdb.get_username(str(id))
            print ("[{0:20}]\t{1} {2}\t{3}").format(id,aux["screen_name"].encode('utf-8'),aux["name"].encode('utf-8'), count)
        else:
            print ("[{0:20}]\t{1}").format(id, count)
elif args.clan:
    mngdb = mongodata()
    followersItems = clan(args.clan,True)
    relation_graph = followersItems
    for item in [i[1] for i in followersItems]:
        print item
        print ("Getting data from {}".format(item))
        followersFriend = clan(item)
        relation_graph = relation_graph.union(followersFriend)
        print ("Num relationships :{} ".format(len(relation_graph)))
        mngdb.delete_temp_users(item)
    RG_list = [i for i in relation_graph]
    G = networkx.Graph()
    G.add_edges_from(RG_list)
    print ("Numero de nodos: {}".format(G.number_of_nodes()))
    print ("Numero de vertices:{}".format(G.number_of_edges()))

elif args.test:
     # mngdb = mongodata()
     # tweet = mngdb.get_tweets_db("",100)
     # words = speaking()
     # for i in tweet:
     #     print i['text'].encode('utf-8')
     #     lang=detect(i['text'])
     #     print "language:{0}".format(lang)
     #     print words.lang_process(i['text'],lang)
     twitt_ = twmac()
     p=twitt_.users(args.test)
     print (json.dumps(p, indent=1))

#elif args.ptest: