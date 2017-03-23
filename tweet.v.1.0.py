import twitter
import json
import ConfigParser
import argparse

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description ='To test different options',
    epilog      = 'comments > /dev/null'
)
#-----------------------------------------------------------------------------------------------------------------------
parser.add_argument('--trends',  "-t", action='store_true', help='To get which it\'s said')
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
VERBOSE = 0
ENVCONFIG = "config/env.ini"
USERCONFIG = "config/userdata.ini"
#-----------------------------------------------------------------------------------------------------------------------
EnvConfig = ConfigParser.ConfigParser()
Config = ConfigParser.ConfigParser()
EnvConfig.read(ENVCONFIG)
Config.read(USERCONFIG)
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
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
WORLD_WOE_ID = 1

world_trends = twitter_api.trends.place(_id=WORLD_WOE_ID)

print json.dumps(world_trends, indent=1)


