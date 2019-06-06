import ConfigParser
import datetime

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
    def users(self, data):
        USERS = self.EnvConfig.get('path', 'data') + '/' + self.EnvConfig.get('prefix',
                                                                               'users') + '_' + self.DATETIME + ".json"
        self.write_(USERS, data)