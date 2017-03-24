import os, re
import twitter
import json
import ConfigParser
import argparse
import datetime

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description ='To test different options',
    epilog      = 'comments > /dev/null'
)
#-----------------------------------------------------------------------------------------------------------------------
parser.add_argument('--trends',  "-t", action='store_true', help='To get which it\'s said')
parser.add_argument('--Gfollowing',  '-Gg', action='store_true', help='get your following contacts')
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
args = parser.parse_args()
VERBOSE = 0
ENVCONFIG = "config/env.ini"
USERCONFIG = "config/userdata.ini"
EnvConfig = ConfigParser.ConfigParser()
Config = ConfigParser.ConfigParser()
EnvConfig.read(ENVCONFIG)
Config.read(USERCONFIG)
DATETIME=str(datetime.datetime.isoformat(datetime.datetime.now()))
TRENDS=EnvConfig.get('path','data')+'/'+EnvConfig.get('prefix','trends')+'_'+DATETIME

#-----------------------------------------------------------------------------------------------------------------------
EnvConfig = ConfigParser.ConfigParser()
Config = ConfigParser.ConfigParser()
EnvConfig.read(ENVCONFIG)
Config.read(USERCONFIG)
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
if not os.path.exists(EnvConfig.get('path','data')):
    os.makedirs(EnvConfig.get('path','data'))


consumer_key = Config.get('secuser','consumer_key')
consumer_secret = Config.get('secuser','consumer_secret')
access_key = Config.get('secuser','access_key')
access_secret = Config.get('secuser','access_secret')
if VERBOSE:
    print("consumer_key ={0}\nconsumer_secret = {1}\naccess_key = {2}\naccess_secret = {3}").\
        format(consumer_key,consumer_secret,access_key, access_secret)
try:
    auth = twitter.oauth.OAuth(access_key, access_secret,
                               consumer_key, consumer_secret)
except:
    print("consumer_key ={0}\nconsumer_secret = {1}\naccess_key = {2}\naccess_secret = {3}"). \
        format(consumer_key, consumer_secret, access_key, access_secret)

twitter_api = twitter.Twitter(auth=auth)
if args.trends:
    WORLD_WOE_ID = 1
    world_trends = twitter_api.trends.place(_id=WORLD_WOE_ID)
    f = open(TRENDS, 'w')
    f.write(json.dumps(world_trends, indent=1))
    f.close()
if args.Gfollowing:
    query = twitter_api.friends.ids(screen_name = Config.get('secuser','owner'))
    print "found %d friends" % (len(query["ids"]))
    for n in range(0, len(query["ids"]), 100):
         ids = query["ids"][n:n+100]
         subquery = twitter_api.users.lookup(user_id = ids)
         print (json.dumps(subquery, indent=1))

         #     print "verified\tscreen_name\tlocaltion\tcreated_at\tfollowers_count\tgeo_enabled\tdefault_profile\tstatuses_count\tdescription"
    #     for user in subquery:
    #         straux=re.sub('\n', " ",user["description"]).strip()
    #         straux = re.sub('\t', " ", user["description"]).strip()
    #         print " %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % ("1" if user["verified"] else "0", user["screen_name"], \
    #                                                user["location"], user["created_at"], user["followers_count"], \
    #                                                user["geo_enabled"], user["default_profile"],\
    #                                                user["statuses_count"], re.sub('\n', " ",straux))

