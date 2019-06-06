import datetime, os
import pymongo
import ConfigParser


from py2neo import authenticate, Graph, Node, Relationship
class mongodata:
    ENVCONFIG = "config/env.ini"
    EnvConfig = ConfigParser.ConfigParser()
    Config = ConfigParser.ConfigParser()
    EnvConfig.read(ENVCONFIG)
    DATETIME = ""
    BBDD = ""

    def __init__(self,userconfig):
        Config = ConfigParser.ConfigParser()
        if os.path.exists(userconfig):
            Config.read(userconfig)
        else:
            print ("{0} file not found !!!")
            exit(0)
        self.DATETIME = str(datetime.datetime.isoformat(datetime.datetime.now()))
        host = Config.get('mongodb', 'ip')
        port = int(Config.get('mongodb', 'port'))
        client = pymongo.MongoClient(host, port)
        self.BBDD = client.twitter
        args={ "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["friends_count", "followers_count", "listed_count", "statuses_count", "favourites_count"],
            "properties": {
                "friends_count": {
                    "bsonType": "long"
                },
                "followers_count": {
                    "bsonType": "long"
                },
                "listed_count": {
                    "bsonType": "long"
                },
                "statuses_count": {
                    "bsonType": "long"
                },
                "favourites_count": {
                    "bsonType": "long"
                }
            }
        }}
        }
        #self.BBDD.create_collection("users",**args)
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

    def tweets_per_user (self, user=None):
        user_ = "$user"
        if user is not None:
            user_ = user

        tweets = self.BBDD.tweets.aggregate(
            [
                {
                    "$group": {
                        "_id": {"user": user_},
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"count": -1}}])
        data={}
        for i in tweets:
            data[i["_id"]["user"]]=i["count"]
        return (data)
