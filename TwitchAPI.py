import urllib.request
import json
import SettingsAndPreferences as settings

user = "FairD"
userid = 0
myuser = "denhonator"
myid = 0
oauth = settings.findValue("APIOauth")
clientid = settings.findValue("ClientID")

#own ID
def getownid(myuser):
    channelIdUrl = "https://api.twitch.tv/kraken/users?login=denhonator"
    headers2={
    'Client-ID': 'lxnmq2fya9fq511vh3d2dbcmasqgra',
    'Accept': 'application/vnd.twitchtv.v5+json',
    'Content-Type': 'application/json'
    }
    req2 = urllib.request.Request(channelIdUrl, None, headers2)
    resp2 = urllib.request.urlopen(req2)
    info = str(resp2.read()).split("\"")
    loop = 0
    for text in info:
        if text=="_id":
            myid = info[loop+2]
            break
        loop+=1
    return myid

#ID of some user
def getuserid(user):
    channelIdUrl = "https://api.twitch.tv/kraken/users?login="+user
    headers2={
    'Client-ID': clientid,
    'Accept': 'application/vnd.twitchtv.v5+json',
    'Authorization': 'OAuth '+oauth,
    'Content-Type': 'application/json'
    }
    req2 = urllib.request.Request(channelIdUrl, None, headers2)
    resp2 = urllib.request.urlopen(req2)
    info = str(resp2.read()).split("\"")
    loop = 0
    for text in info:
        if text=="_id":
            userid = info[loop+2]
            break
        loop+=1
    return userid

#subscription status of user
def usersub(userid):
    url = 'https://api.twitch.tv/kraken/channels/'+myid+'/subscriptions/'+userid
    headers = {'Accept': 'application/vnd.twitchtv.v5+json',
               'Client-ID': clientid,
               'Authorization': 'OAuth '+oauth,
               'Content-Type': 'application/json'
               }
    req = urllib.request.Request(url, None, headers)
    try:
        resp = urllib.request.urlopen(req)
        info = str(resp2.read()).split("\"")
        print(info)
    except urllib.error.HTTPError as e:
        print("Couldn't get subscription status")
        print(str(e.code) + " " + e.reason)

myid = getownid(myuser)
userid = getuserid(user)
print(myid)
print(userid)
usersub(userid)
