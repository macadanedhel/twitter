import re
from bs4 import BeautifulSoup

file = "trapi2.txt"

f = open(file, 'r')
doc=f.read()
f.close()


userdata={
        "background_image" : "",
        "name" : "",
        "screen_name" : "",
        "url_user_home" : "",
        "tweets" : 0,
        "following" : 0,
        "followers" : 0,
        "protected_tweets" : False,
        "verified_account" : False,
        "likes" : 0,
        "lists" : 0,
        "joined": ""

}
html = BeautifulSoup(doc, "html.parser")
all_tweets = []
#for i in res:
#    print i

# timeline = html.select('#timeline li.stream-item')
# for tweet in timeline:
#     tweet_id = tweet['data-item-id']
#     tweet_text = tweet.select('p.tweet-text')[0].get_text()
#     all_tweets.append({"id": tweet_id, "text": tweet_text})
#     print(all_tweets)
# res=html.find("div", "ProfileCard js-actionable-user ProfileCard--wide")
# bi=res.find("a", "ProfileCard-bg js-nav")
# print bi['style'].split('(')[0]
user=html.find("div","ProfileCard js-actionable-user ProfileCard--wide")
if user is None:
    user=html.find("div","ProfileHeaderCard")
    userdata['background_image'] = html.find("div","ProfileCanopy-headerBg").find("img")["src"]
    userdata['name'] = user.find("a", "ProfileHeaderCard-nameLink u-textInheritColor js-nav").text
    accountType = user.find("span","ProfileHeaderCard-badges")
    if not type(accountType) is 'NoneType' :
        if user.find("span","Icon Icon--verified"):
            userdata['verified_account'] = True
        if user.find("span","Icon Icon--protected"):
            userdata['protected_tweets'] = True

    userdata['screen_name'] = re.sub('\n\s*', '',
                         user.find("b", "u-linkComplex-target").text)
    userdata['url_user_home']=html.find("span","ProfileHeaderCard-urlText u-dir").find('a', 'u-textUserColor')['title']
    userdata['image'] =  html.find("img","ProfileAvatar-image")['src']

    infotweets=html.find("div","ProfileCanopy-nav").find("div","ProfileNav")
    userdata['tweets'] = int(infotweets.find("li","ProfileNav-item ProfileNav-item--tweets is-active").find("span","ProfileNav-value")['data-count'])
    userdata['following'] = int(infotweets.find("li","ProfileNav-item ProfileNav-item--following").find("span","ProfileNav-value")['data-count'])
    userdata['followers'] = int(infotweets.find("li","ProfileNav-item ProfileNav-item--followers").find("span","ProfileNav-value")['data-count'])
    userdata['likes'] = int(infotweets.find("li","ProfileNav-item ProfileNav-item--favorites").find("span","ProfileNav-value")['data-count'])
    userdata['lists'] = int(infotweets.find("li","ProfileNav-item ProfileNav-item--lists").find("span","ProfileNav-value").text)
    userdata['joined'] = user.find("div","ProfileHeaderCard-joinDate").find("span","ProfileHeaderCard-joinDateText js-tooltip u-dir")['title']
    userdata['description'] = user.find("p","ProfileHeaderCard-bio u-dir").text

else:
    background_image=user.find("a", "ProfileCard-bg js-nav")['style'].split('(')[1].rstrip(');')
    userdata['name']=user.find("b", "u-linkComplex-target").text
    userdata['screen_name']=re.sub('\n\s*', '', user.find("a", "fullname ProfileNameTruncated-link u-textInheritColor js-nav").text)
    userdata['url_user_home']=user.find("p", "ProfileCard-locationAndUrl").find("a","u-textUserColor")['title']
    userdata['image']=user.find("img","ProfileCard-avatarImage js-action-profile-avatar")['src']
    userdata['tweets']=user.find("span","ProfileCardStats-statValue").text

    userdata['tweets']=following=follower=num=0
    #if user.find("span","ProfileHeaderCard-badges"):
    # CHECK
    accountType = user.find("span", "ProfileHeaderCard-badges")
    if not type(accountType) is 'NoneType' :
        if user.find("span","Icon Icon--verified"):
            userdata['verified_account'] = True
        if user.find("span","Icon Icon--protected"):
            userdata['protected_tweets'] = True

        userdata['protected_tweets'] = True
    for i in user.find("div","ProfileCardStats").find_all("span","ProfileCardStats-statValue"):
        if num == 0:
            userdata['tweets'] = i.text
        elif num == 1:
            userdata['following'] = i.text
        elif num == 2:
            userdata['followers'] = i.text
        num=num+1

for key, value in userdata.items():
    print ("{0}:\t{1}".format(key,value))
