#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf8
import os, re
import twitter
import json, csv
import ConfigParser
import parser
import argparse
import datetime, time
import pymongo
from py2neo import authenticate, Graph, Node, Relationship


from recipe__make_twitter_request import make_twitter_request

# En el mongo voy a montar distintas colecciones, unas de catalogo y otras de relacion
# Objetos principales son el twitter y el user
# Una coleccion debe ser users
# La colección friends tendrá dos campos user, friend y el valor será el id
# la coleccion followers tendrá dos campos user, follower y el valor será el id

# ﻿db.getCollection('tweets').find({},{user:1, text:1, retweeted:1, lang:1, created_at:1})
# ﻿db.getCollection('tweets').find({},{text:1, _id:0})

#=======================================================================================================================
class filedata:
    ENVCONFIG = "config/env.ini"
    EnvConfig = ConfigParser.ConfigParser()
    Config = ConfigParser.ConfigParser()
    EnvConfig.read(ENVCONFIG)
    DATETIME = ""

    def __init__(self):
        self.EnvConfig = ConfigParser.ConfigParser()
        self.EnvConfig.read(self.ENVCONFIG)
        self.DATETIME = str(datetime.datetime.isoformat(datetime.datetime.now()))
    def write_ (self, file_, data):
        #print ("output:{0}").format(file_)
        f = open(file_, 'w')
        f.write(data)
        f.close()
    def trends (self, data):
        TRENDS = self.EnvConfig.get('path', 'data') + '/' + self.EnvConfig.get('prefix', 'trends') + '_' + self.DATETIME + ".json"
        self.write_( TRENDS, data )
    def trendAvailable (self, data):
        TRENDS = self.EnvConfig.get('path', 'data') + '/' + self.EnvConfig.get('prefix',
                                                                               'trendsavailable') + '_' + self.DATETIME + ".json"
        self.write_(TRENDS, data)
    def friends(self, data):
        FRIENDS = self.EnvConfig.get('path', 'data') + '/' + self.EnvConfig.get('prefix',
                                                                               'friends') + '_' + self.DATETIME + ".json"
        self.write_(FRIENDS, data)
    def followers(self, data):
        FOLLOWERS = self.EnvConfig.get('path', 'data') + '/' + self.EnvConfig.get('prefix',
                                                                               'followers') + '_' + self.DATETIME + ".json"
        self.write_(FOLLOWERS, data)
    def tweets(self, data):
        TWEETS = self.EnvConfig.get('path', 'data') + '/' + self.EnvConfig.get('prefix',
                                                                               'tweets') + '_' + self.DATETIME + ".json"
        self.write_(TWEETS, data)
    def users(self, data):
        USERS = self.EnvConfig.get('path', 'data') + '/' + self.EnvConfig.get('prefix',
                                                                               'users') + '_' + self.DATETIME + ".json"
        self.write_(USERS, data)
    def user2csv (self, data):
        u2_c_s_v = self.EnvConfig.get('path', 'data') + '/' + self.EnvConfig.get('prefix',
                                                                               'user2csv') + '_' + self.DATETIME + ".csv"
        f=open(u2_c_s_v,"w")
        f.write ("_id,screen_name,location,name,followers_count,friends_count,created_at,url,lang,screen_name,retweet_count,verified,listed_count,statuses_count,default_profile,withheld_in_countries,description,time_zone,utc_offset,lang\n")
        for row in data:
            f.write (
                "{_id},'{screen_name}','{location}','{name}',{followers_count},{friends_count},{created_at},'{url}','{lang}','{screen_name}',{retweet_count}, {verified}, {listed_count},{statuses_count}, {default_profile},{withheld_in_countries},'{description}',{time_zone},{utc_offset},'{lang}'".format(
                    **row))
            f.write("\n")
        f.close()
    def data2neo (self, users, followers, friends):
        filenameU =  self.EnvConfig.get('neo4j','userfile') + '_' + self.DATETIME + ".csv"
        u2l = self.EnvConfig.get('neo4j', 'datapath') + '/' + filenameU
        f = open(u2l, "w")

        filenameG = self.EnvConfig.get('neo4j','lang') + '_' + self.DATETIME + ".csv"
        l2_c_s_v = self.EnvConfig.get('neo4j', 'datapath') + '/'  +filenameG
        ff = open(l2_c_s_v, "w")

        filenameL = self.EnvConfig.get('neo4j','location') + '_' + self.DATETIME + ".csv"
        tz2_csv = self.EnvConfig.get('neo4j', 'datapath') + '/' + filenameL
        fff = open(tz2_csv, "w")

        filenameF = self.EnvConfig.get('neo4j', 'followers') + '_' + self.DATETIME + ".csv"
        f2_csv = self.EnvConfig.get('neo4j', 'datapath') + '/' + filenameF
        ffff = open(f2_csv, "w")

        filenameR = self.EnvConfig.get('neo4j', 'friends') + '_' + self.DATETIME + ".csv"
        r2_csv = self.EnvConfig.get('neo4j', 'datapath') + '/' + filenameR
        fffff = open(r2_csv, "w")


        files={'user':u2l,'lang':l2_c_s_v,'location':tz2_csv,'followers':f2_csv,'friends':r2_csv,
               'remote_user': self.EnvConfig.get('neo4j','remotepath') + '/' + filenameU,
               'remote_lang': self.EnvConfig.get('neo4j', 'remotepath') + '/' + filenameG,
               'remote_location': self.EnvConfig.get('neo4j', 'remotepath') + '/' + filenameL,
               'remote_followers': self.EnvConfig.get('neo4j', 'remotepath') + '/' + filenameF,
               'remote_friends': self.EnvConfig.get('neo4j', 'remotepath') + '/' + filenameR
               }

        userkeys = (self.EnvConfig.get('neo4j','user_key'))
        langkeys = (self.EnvConfig.get('neo4j', 'lang_key'))
        locationkeys = (self.EnvConfig.get('neo4j', 'location_key'))
        followerskey = (self.EnvConfig.get('neo4j', 'followers_key'))
        friendskey = (self.EnvConfig.get('neo4j', 'friends_key'))

        f.write("_id,")
        ff.write("_id,")
        fff.write("_id,")

        f.write( userkeys )
        ff.write( langkeys )
        fff.write( locationkeys )
        ffff.write(followerskey)
        fffff.write(friendskey)

        f.write( "\n" )
        ff.write( "\n" )
        fff.write( "\n" )
        ffff.write( "\n" )
        fffff.write( "\n" )

        userkeys=userkeys.split(',')
        langkeys = langkeys.split(',')
        locationkeys = locationkeys.split(',')
        followerskey = followerskey.split(',')
        friendskey = friendskey.split(',')

        for i in followers:
            ffff.write( "{0},{1}\n".format(i[0],i[1]) )
        for i in friends:
            fffff.write("{0},{1}\n".format(i[0], i[1]) )
        for i in users:
            #user
            key = i.keys()[0]
            f.write( "{0},{1},{2},{3},{4}\n".format(key,i[key][0][userkeys[0]],i[key][0][userkeys[1]],i[key][0][userkeys[2]],
                                           i[key][0][userkeys[3]]) )
            ff.write( "{0},{1}\n".format(key,i[key][1][langkeys[0]]) )
            if i[key][2][locationkeys[2]] <> '':
                fff.write( "{0},{1},{2},{3}\n".format(key,i[key][2][locationkeys[0]],i[key][2][locationkeys[1]],i[key][2][locationkeys[2]]) )
        f.close()
        ff.close()
        fff.close()
        ffff.close()
        fffff.close()
        return(files)
#=======================================================================================================================
class mongodata:
    ENVCONFIG = "config/env.ini"
    EnvConfig = ConfigParser.ConfigParser()
    Config = ConfigParser.ConfigParser()
    EnvConfig.read(ENVCONFIG)
    DATETIME = ""
    BBDD = ""

    def __init__(self):
        self.EnvConfig = ConfigParser.ConfigParser()
        self.EnvConfig.read(self.ENVCONFIG)
        self.DATETIME = str(datetime.datetime.isoformat(datetime.datetime.now()))
        host = self.EnvConfig.get('mongodb', 'ip')
        port = int(self.EnvConfig.get('mongodb', 'port'))
        client = pymongo.MongoClient(host, port)
        self.BBDD = client.twitter

    def insert_many_users (self,  ALLDATA):
        try:
            self.BBDD.users.insert_many(ALLDATA, ordered=False).inserted_ids
        except pymongo.errors.BulkWriteError as e:
                    #print("Error:{0}").format(e.details['writeErrors'])
                    print "Error, duplicate data"

    def insert_many_friends (self,ALLDATA):
        self.insert_many_users(ALLDATA['ids'])
        self.BBDD.friends.insert_many(ALLDATA['friends']).inserted_ids
        #cpeddbb.twitter.friends.create_index([('title', pymongo.TEXT)], name='title', default_language='english')

    def insert_many_followers (self,ALLDATA):
        self.insert_many_users(ALLDATA['ids'])
        self.BBDD.followers.insert_many(ALLDATA['followers']).inserted_ids
        #cpeddbb.twitter.friends.create_index([('title', pymongo.TEXT)], name='title', default_language='english')
    def insert_many_tweets (self,ALLDATA):
        self.insert_many_users(ALLDATA['users'])
        try:
            self.BBDD.tweets.insert_many(ALLDATA['tweets']).inserted_ids
        except self.BBDD.tweets.BulkWriteError as exc:
            exc.details

    def insert_many_trends(self, ALLDATA):
        self.BBDD.trends.insert_many(ALLDATA).inserted_ids


    def insert_many_trendAvailable(self, ALLDATA):
        self.BBDD.trendAvailable.insert_many(ALLDATA).inserted_ids

    def list_users (self):
        return (list(self.BBDD.users.find({}, {"_id": 1, "screen_name": 1, "location": 1, "name": 1, "followers_count": 1,
                                              "friends_count": 1, "created_at": 1, "url": 1, "lang": 1,
                                              "retweet_count": 1, "verified": 1, "listed_count": 1,
                                              "statuses_count": 1, "default_profile": 1, "withheld_in_countries": 1,
                                              "description" :1, "time_zone" :1, "utc_offset":1})))
    def data2neo  (self):
        return (list(self.BBDD.users.find({}, {"_id": 1, "screen_name": 1, "location": 1, "name": 1, "lang": 1,
                                              "verified": 1,  "default_profile":1, "time_zone" :1, "utc_offset":1 })))

    def get_users_from_tweets(self):
        return (list(self.BBDD.tweets.find({}, {"id": 1, "user": 1})))

    def get_users (self):
        return (list(self.BBDD.users.find({}, {"_id": 1, "screen_name": 1})))

    def get_relationship(self, relation):
        if relation == 'friends':
            return (list(self.BBDD.friends.find({}, {"_id": 0, "friend": 1, "user":1})))
        elif relation == 'followers':
            return (list(self.BBDD.followers.find({}, {"_id": 0, "friend": 1, "user": 1})))
        else:
            print "ERROR: No relationship"
    def get_userid (self, name):
        users=list(self.BBDD.users.find({ "$or": [ {"screen_name":name}, {"name":name} ] },{"_id":1}))
        if len(users)<1:
            result=0
        else:
            result=users[0]['_id']
        return (result)
    def get_username (self, id):
        users=list(self.BBDD.users.find({ "id_str" : id } ,{ "_id":0, "name":1, "screen_name":1 } ))
        if len(users)<1:
            result=0
        else:
            result=users[0]
        return (result)

    def get_tweets_byuserid (self, uid):
        return (self.BBDD.tweets.find({"user": uid}, {"text":1, "_id": 0}))
    def get_userid_regex (self, name):
        #users=list(self.BBDD.users.find({"name":{"$regex":name, "$options":"i"} },{"_id":1, "name":1}))
        users = list(self.BBDD.users.find(
            {"$or": [{"screen_name": {"$regex": name, "$options": "i"}}, {"name": {"$regex": name, "$options": "i"}}]},
            {"_id": 1, "name": 1, "screen_name":1 }))
        if len(users)<1:
            result=0
        else:
            result=users
        return (result)
    def get_tweets_users (self):
        tweets = self.BBDD.tweets.aggregate(
            [
                {
                    "$group": {
                    "_id": {"user": "$user"},
                    "count": { "$sum":1}
                }
            },
            { "$sort": {"count": -1}}])
        return (tweets)
    def get_tweets_db (self, name=None, limit=None):
        str1=""
        str2=""
        if name and limit:
            result = list(self.BBDD.tweets.find({}, {"text": 1, "user": 1, "lang": 1}).limit(limit))
        elif name:
            result = list(self.BBDD.tweets.find({ "name" : name }, {"text": 1, "user": 1, "lang": 1}))
        elif limit:
            result=list(self.BBDD.tweets.find({}, {"text": 1, "user": 1, "lang":1}).limit(limit))
        else:
            result = list(self.BBDD.tweets.find({str1}, {"text": 1, "user": 1, "lang": 1}).limit(limit))
        return (result)
#=======================================================================================================================
class twmac:
    USERCONFIG = "config/userdata.ini"
    Config = ConfigParser.ConfigParser()
    Config.read(USERCONFIG)
    ID=""
    twitter_api = ""

    def __init__(self):
        consumer_key = self.Config.get('secuser', 'consumer_key')
        consumer_secret = self.Config.get('secuser', 'consumer_secret')
        access_key = self.Config.get('secuser', 'access_key')
        access_secret = self.Config.get('secuser', 'access_secret')
        auth = twitter.oauth.OAuth(access_key, access_secret,
                                   consumer_key, consumer_secret)
        self.twitter_api = twitter.Twitter(auth=auth,retry=True)
        aux = self.twitter_api.users.lookup(screen_name=self.Config.get('secuser', 'owner'))
        self.ID= long(aux[0]['id'])

# -----------------------------------------------------------------------------------------------------------------------
    def trends (self, id):
        return(self.twitter_api.trends.place(_id=id))
#-----------------------------------------------------------------------------------------------------------------------
    def trendAvailable (self, id):
        return(self.twitter_api.trends.available(_id=id))
#-----------------------------------------------------------------------------------------------------------------------
    def friends (self,user=None):
        ID_ = ""
        if not user:
            query=  self.twitter_api.friends.ids(screen_name = self.Config.get('secuser','owner'))
            ID_ = self.ID
        else :
            query= self.twitter_api.friends.ids(screen_name=user)
            aux = self.twitter_api.users.lookup(screen_name=user)
            ID_ = long(aux[0]['id'])
        data =[]
        relationship=[]
        result={}
        if query["ids"] and len(query["ids"]) > 0:
            print "found %d friends" % (len(query["ids"]) - 1)
            cont = 0
            for n in range(0, len(query["ids"])-1, 100):
                ids = query["ids"][n:n + 100]
                try:
                    subquery = self.twitter_api.users.lookup(user_id = ids)
                    for line in subquery:
                        aux = {}
                        aux['user']=self.ID
                        aux['friend']=line['id']
                        relationship.append(aux)
                        line['_id'] = line.pop('id')
                        data.append(line)
                except twitter.TwitterHTTPError as e:
                    print("Error:{0}\n\nUSER ID:{1}\n").format(e, ids)
            result['num_friends']=len(query["ids"])-1
            result['ids']=data
            result['friends']=relationship
        else:
            result['num_friends'] = 0
            result['ids'] = data
            result['friends'] = relationship
        return (result)
#-----------------------------------------------------------------------------------------------------------------------
    def lists (self,user=None):
        if not user:
            data=  self.twitter_api.lists.list(screen_name = self.Config.get('secuser','owner'))
        else :
            data= self.twitter_api.lists.list(screen_name=user)
        return data
#-----------------------------------------------------------------------------------------------------------------------
    def memberships(self, user=None):
        if not user:
            data=  self.twitter_api.lists.memberships(screen_name = self.Config.get('secuser','owner'))
        else :
            data= self.twitter_api.lists.memberships(screen_name=user)
#-----------------------------------------------------------------------------------------------------------------------
    def followers (self,user=None):
        ID_=""
        if not user:
            query = self.twitter_api.followers.ids(screen_name=self.Config.get('secuser', 'owner'))
            ID_ = self.ID
        else :
            query = self.twitter_api.followers.ids(screen_name=user)
            aux = self.twitter_api.users.lookup(screen_name=user)
            ID_ = long(aux[0]['id'])
        data = []
        result = {}
        followers_ = []
        if query["ids"] and len(query["ids"])>0:
            print "found %d followers" % (len(query["ids"])-1)
            cont = 0
            for n in range(0, len(query["ids"])-1, 100):
                ids = query["ids"][n:n + 100]
                try:
                    subquery = self.twitter_api.users.lookup(user_id = ids)
                    for line in subquery:
                        aux = {}
                        aux['user'] = ID_
                        aux['friend'] = line['id']
                        line['_id']=line.pop('id')
                        data.append(line)
                        followers_.append(aux)
                except twitter.TwitterHTTPError as e:
                    print("Error:{0}\n\nUSER ID:{1}\n").format(e,ids)
            result['num_followers']=len(query["ids"])-1
            result['ids']=data
            result['followers'] = followers_
        else:
            result['num_followers'] = 0
            result['ids'] = data
            result['followers'] = followers_
        return (result)
#-----------------------------------------------------------------------------------------------------------------------
    def test (self):
        return (self.twitter_api.users.lookup(screen_name = self.Config.get('secuser', 'owner')))
#-----------------------------------------------------------------------------------------------------------------------
    def get_tweet_timeline(self, user=None, name_=None):
        KW = {  # For the Twitter API call
            'count': 200,
            'skip_users': 'true',
            'include_entities': 'true',
            'since_id': 1,
        }
        TIMELINE_NAME = 'user'
        MAX_PAGES=16
        page_num = 1
        cont=0
        result={}
        data=[]
        users=[]

        if not user:
            KW['screen_name'] = self.Config.get('secuser','owner')
            user= KW['screen_name']
        else :
            if user == 'user':
                if not name_:
                    print "ERROR: user needs a screen_name"
                    return -1
                else:
                    KW['screen_name'] = name_
                    user = KW['screen_name']
            elif user == 'home':
                TIMELINE_NAME = 'home'
                MAX_PAGES = 4
            elif user == 'public':
                # ESTE NO VA
                # AttributeError: twmac instance has no attribute 'account'
                TIMELINE_NAME = 'public'
                MAX_PAGES = 1

        # Usage: $ %s timeline_name [max_pages] [screen_name]' % (sys.argv[0],)
        # timeline_name in [public, home, user]'
        # 0 < max_pages <= 16 for timeline_name in [home, user]'
        # max_pages == 1 for timeline_name == public'
        # Notes:'
        # * ~800 statuses are available from the home timeline.'
        # * ~3200 statuses are available from the user timeline.'
        # * The public timeline updates every 60 secs and returns 20 statuses.'
        # * See the streaming/search API for additional options to harvest tweets.'
        while page_num <= MAX_PAGES:
            KW['page'] = page_num
            api_call = getattr(self.twitter_api.statuses, TIMELINE_NAME + '_timeline')
            tweets = make_twitter_request(self, api_call, **KW)
            for line in tweets:
                aux=line['user']['id']
                line['user']['_id'] = line['user'].pop('id')
                users.append(line['user'])
                line['user']=aux
                #line['_id']=line.pop('id')
                data.append(line)

            cont=cont+len(tweets)
            page_num += 1
        result['num_tweets'] = cont
        result['tweets'] = data
        result['users'] = users
        return (result)
#=======================================================================================================================
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
WORLD_WOE_ID = 1
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
parser.add_argument('--other_friend',  '-rf', type=str, help='get other following contacts')
parser.add_argument('--followers',  '-fo', action='store_true', help='get your following contacts')
parser.add_argument('--other_follower',  '-of', type=str, help='get other following contacts')
parser.add_argument('--lists',  "-l",  type=str, help='lists of a given user (me|screen_name)')
parser.add_argument('--memberships',  "-m", action='store_true', help='print')
parser.add_argument('--tweets',  "-w", action='store_true', help='tweets from home')
parser.add_argument('--tweets_user',  "-u", type=str, help='tweets of a given user (me|screen_name)')
parser.add_argument('--user2csv',  "-u2csv", action='store_true', help='data user to analyze')
parser.add_argument('--data2neo',  "-d2neo", action='store_true', help='data to graph creation')
parser.add_argument('--get_userid',  '-n', type=str, help='get userid by name or screen_name')
parser.add_argument('--get_userid_regex',  '-nr', type=str, help='get userid by name or screen_name but regex based')
parser.add_argument('--get_tweet_user',  '-gtu', type=str, help='get downloaded tweets by name or screen_name')
parser.add_argument('--userstweets',  "-ut", action='store_true', help='return number of teewts by user ordered desc')
parser.add_argument('--get_username',  '-gn', type=str, help='get name or screen_name from userid')
parser.add_argument('--resolve_na',  '-a', action='store_true', help='resolve name or screen_name from userid')
parser.add_argument('--test',  "-test", action='store_true', help='print')

#-----------------------------------------------------------------------------------------------------------------------
args = parser.parse_args()
#-----------------------------------------------------------------------------------------------------------------------

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
elif args.test:
    mngdb = mongodata()
    tweet = mngdb.get_tweets_db("",20)
    for i in tweet:
        print i['text'].encode('utf-8')
# elif args.test:
#     print "test"