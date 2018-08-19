import urllib.request
import json
import SettingsAndPreferences as settings
import sys

oauth = settings.findValue("APIOauth").strip()
clientid = settings.findValue("ClientID").strip()
nick = settings.findValue("NICK").strip()

def parseInfo(url, lookfor):
    headers={
    'Accept': 'application/vnd.twitchtv.v5+json',
    'Client-ID': clientid,
    'Authorization': 'Bearer '+oauth,
    'Content-Type': 'application/json'
    }
    req = urllib.request.Request(url, None, headers)
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode("utf-8"))
    
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
    
    return data[lookfor]

def getUserID(user):
    url = "https://api.twitch.tv/helix/users?login="+user
    return parseInfo(url, "data")[0]["id"]

def NewFollower():
    url = "https://api.twitch.tv/helix/users/follows?to_id="+ID
    users = parseInfo(url, "data")
    url = "https://api.twitch.tv/helix/users?id="+users[0]["from_id"]
    return parseInfo(url, "data")[0]["display_name"]

def totalFollowers():
    url = "https://api.twitch.tv/helix/users/follows?to_id="+ID
    return parseInfo(url, "total")

try:
    ID = getUserID(nick)
except Exception as e:
    print(e.read())
    print("Can't automatically fetch ID, using manual value")
    ID = settings.findValue("UserID")

followers = totalFollowers()
if(followers):
    settings.levelprint("API working, "+str(followers)+" followers, most recent: "+NewFollower(),0)
else:
    settings.levelprint("API not working",0)
