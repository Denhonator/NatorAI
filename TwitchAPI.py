import urllib.request
import json
import SettingsAndPreferences as settings
import sys

oauth = settings.findValue("APIOauth").strip()
clientid = settings.findValue("ClientID").strip()
nick = settings.findValue("JOIN").strip()
lastData = {}

def parseInfo(url, lookfor):
    headers={
    'Accept': 'application/vnd.twitchtv.v5+json',
    'Client-ID': clientid,
    'Authorization': 'OAuth '+oauth,
    }
    req = urllib.request.Request(url, None, headers)
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode("utf-8"))
    global lastData
    lastData = data
##    userlist = []   
##    try:
##        while lookfor=="data":
##            cursor = data["pagination"]["cursor"]
##            userlist+=data["data"]    
##            req = urllib.request.Request(url+"?cursor="+cursor, None, headers)
##            resp = urllib.request.urlopen(req)
##            data = json.loads(resp.read().decode("utf-8"))
##    except Exception as e:
##        print(e)
##        return userlist
    if "6" in settings.findValue("printLevel"):
        print(data)    
    return data[lookfor]

def getUserID(user):
    url = "https://api.twitch.tv/kraken/user"
    return parseInfo(url, "_id")

def NewFollower(refresh=True):
    url = "https://api.twitch.tv/kraken/channels/"+ID+"/follows"
    users = parseInfo(url, "follows")
    return users[0]["user"]["display_name"]

def totalFollowers(refresh=True):
    if refresh:
        url = "https://api.twitch.tv/kraken/channels/"+ID+"/follows"
        return parseInfo(url, "_total")
    return lastData["_total"]

def totalSubs(refresh=True):
    url = "https://api.twitch.tv/kraken/channels/"+ID+"/subscriptions"
    total = parseInfo(url, "_total")
    for sub in lastData["subscriptions"]:
        if sub["user"]["_id"]==ID:
            total-=1
        elif sub["sub_plan"] == "2000":
            total+=1
        elif sub["sub_plan"] == "3000":
            total+=5
    return total

try:
    ID = getUserID(nick)
except Exception as e:
    print(e)
    print("Can't automatically fetch ID, using manual value")
    ID = settings.findValue("UserID")

followers = totalFollowers()
subs = totalSubs()
if(followers):
    settings.levelprint("API working, "+str(followers)+" followers, most recent: "+NewFollower(False),0)
else:
    settings.levelprint("API not working (followers)",0)
if(subs):
    settings.levelprint("API working, "+str(subs)+" sub points",0)
else:
    settings.levelprint("API not working (subs)",0)
