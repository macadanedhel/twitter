#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, re
import twitter
import json, csv
import ConfigParser
import parser
import argparse
import datetime, time
import pymongo
from recipe__make_twitter_request import make_twitter_request

# En el mongo voy a montar distintas colecciones, unas de catalogo y otras de relacion
# Objetos principales son el twitter y el user
# Una coleccion debe ser users
# La colección friends tendrá dos campos user, friend y el valor será el id
# la coleccion followers tendrá dos campos user, follower y el valor será el id


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
        self.BBDD.tweets.insert_many(ALLDATA['tweets']).inserted_ids

    def insert_many_trends(self, ALLDATA):
        self.BBDD.trends.insert_many(ALLDATA).inserted_ids


    def insert_many_trendAvailable(self, ALLDATA):
        self.BBDD.trendAvailable.insert_many(ALLDATA).inserted_ids

    def list_users (self):
        return (list(self.BBDD.users.find({}, {"id": 1, "screen_name": 1, "location": 1, "name": 1, "followers_count": 1,
                                              "friends_count": 1, "created_at": 1, "url": 1, "lang": 1,
                                              "screen_name": 1, "retweet_count": 1, "verified": 1, "listed_count": 1,
                                              "statuses_count": 1, "default_profile": 1, "withheld_in_countries": 1,
                                              "_id": 0})))

    def get_users_from_tweets(self):
        return (list(self.BBDD.tweets.find({}, {"id": 1, "user": 1,
                                              "_id": 0})))

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
            print 2
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
                line['_id']=line.pop('id')
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
parser.add_argument('--users_tweets',  "-ut", action='store_true', help='user from tweets')
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
    if args.print_:
        fwrite = filedata()
        fwrite.friends(json.dumps(friends, indent=1))
    elif args.mongodb:
        mngdb = mongodata()
        mngdb.insert_many_friends(friends)
    else:
        print (json.dumps(friends, indent=1))
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
    if args.print_ and followers['num_followers']:
        fwrite = filedata()
        fwrite.followers(json.dumps(followers, indent=1))
    elif args.mongodb and followers['num_followers']:
        mngdb = mongodata()
        mngdb.insert_many_followers(followers)
    else:
        print (json.dumps(followers, indent=1))
elif args.test:
    mngdb = mongodata()
    myself = mngdb.list_users()
    print myself[0].keys()
    for row in myself:
        try:
            if not row["retweet_count"] or row["withheld_in_countries"]:
                row["retweet_count"]=0
        except:
            row["retweet_count"] = 0
            row["withheld_in_countries"] = 0
        print ("{id},{screen_name},{location},{name},{followers_count},{friends_count},\
        {created_at},{url},{lang},{screen_name},{retweet_count}, {verified}, {listed_count},\
        {statuses_count}, {default_profile},{withheld_in_countries}".format(**row))

    #print (json.dumps(myself, indent=1))
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
        print (json.dumps(tweets, indent=1))

elif args.users_tweets:
    mngdb = mongodata()
    tweets = mngdb.get_users_from_tweets()
    for i in tweets:
        print ("{1}->{0}").format(i['id'],i['user']['id'])