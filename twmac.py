import ConfigParser
import twitter
from recipe__make_twitter_request import make_twitter_request


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
        _FRIENDS = 0
        NAME_ = ""
        ID_ = ""
        if not user:
            NAME_ = self.Config.get('secuser', 'owner')
            ID_ = self.ID
        else:
            aux = self.twitter_api.users.lookup(screen_name=user)
            NAME_ = user
            ID_ = long(aux[0]['id'])
        data = []
        relationship = []
        result = {}

        next_cursor = "-1"

        while (int(next_cursor) != 0):
            if int(next_cursor) < 0:
                query = self.twitter_api.friends.ids(screen_name=NAME_)
            else:
                query = self.twitter_api.friends.ids(screen_name=NAME_, cursor=next_cursor)
            next_cursor = query["next_cursor"]
            if query["ids"] and len(query["ids"]) > 0:
                _FRIENDS = _FRIENDS + (len(query["ids"]))
                print ("found {} friends").format(_FRIENDS)
                for n in range(0, len(query["ids"]) - 1, 100):
                    ids = query["ids"][n:n + 100]
                    try:
                        subquery = self.twitter_api.users.lookup(user_id=ids)
                        for line in subquery:
                            aux = {}
                            aux['user'] = self.ID
                            aux['friend'] = line['id']
                            relationship.append(aux)
                            line['_id'] = line.pop('id')
                            data.append(line)
                    except twitter.TwitterHTTPError as e:
                        print("Error:{0}\n\nUSER ID:{1}\n").format(e, ids)

        result['num_friends'] = _FRIENDS
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
        ID_ = ""
        _FRIENDS = 0
        NAME_ = ""

        if not user:
            # query = self.twitter_api.friends.ids(screen_name=self.Config.get('secuser', 'owner'))
            NAME_ = self.Config.get('secuser', 'owner')
            ID_ = self.ID
        else:
            # query = self.twitter_api.friends.ids(screen_name=user)
            aux = self.twitter_api.users.lookup(screen_name=user)
            NAME_ = user
            ID_ = long(aux[0]['id'])
        data = []
        relationship = []
        result = {}

        next_cursor = "-1"

        while (int(next_cursor) != 0):
            if int(next_cursor) < 0:
                try:
                    query = self.twitter_api.followers.ids(screen_name=NAME_)
                except twitter.TwitterHTTPError as e:
                    print("Error:{0}\n\nUSER ID:{1}\n").format(e, NAME_)
                    query = False
            else:
                query = self.twitter_api.followers.ids(screen_name=NAME_, cursor=next_cursor)
            if query:
                next_cursor = query["next_cursor"]
                if query["ids"] and len(query["ids"]) > 0:
                    _FRIENDS = _FRIENDS + (len(query["ids"]))
                    for n in range(0, len(query["ids"]) - 1, 100):
                        ids = query["ids"][n:n + 100]
                        try:
                            subquery = self.twitter_api.users.lookup(user_id=ids)
                            for line in subquery:
                                aux = {}
                                aux['user'] = ID_
                                aux['friend'] = line['id']
                                relationship.append(aux)
                                line['_id'] = line.pop('id')
                                data.append(line)
                        except twitter.TwitterHTTPError as e:
                            print("Error:{0}\n\nUSER ID:{1}\n").format(e, ids)
            else:
                next_cursor=0

        result['num_followers'] = _FRIENDS
        result['ids'] = data
        result['followers'] = relationship
        print ("found {} followers").format(_FRIENDS)
        return (result)
#-----------------------------------------------------------------------------------------------------------------------
    def users (self,users):
        data=[]
        USERS=self.twitter_api.users.lookup(screen_name=users)
        for line in USERS:
            line['_id'] = line.pop('id')
            data.append(line)
        return(data)
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
#-----------------------------------------------------------------------------------------------------------------------
    def followersID (self,id=None):
        ID_ = ""
        _FRIENDS = 0
        NAME_ = ""
        ID_ = ""
        # query = self.twitter_api.friends.ids(screen_name=user)
        aux = self.twitter_api.users.lookup(user_id=id)
        NAME_ = aux[0]['screen_name']
        print NAME_
        ID_ = id
        data = []
        relationship = []
        return (self.followers(NAME_))
#-----------------------------------------------------------------------------------------------------------------------
    def get_user_lookup (self,user=None):
        user_ = ""

        if not user:
            user_ = self.twitter_api.users.lookup(user_id=self.ID)
        elif str(user).isdigit():
            user_ = self.twitter_api.users.lookup(user_id=user)
        else:
            user_ = self.twitter_api.users.lookup(screen_name=user)
        return (user_)
#-----------------------------------------------------------------------------------------------------------------------
