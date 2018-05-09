import urllib.request
import json
import SettingsAndPreferences as settings
import sys

oauth = settings.findValue("APIOauth")
clientid = settings.findValue("ClientID")

def parseInfo(url, lookfor):
    headers={
    'Client-ID': clientid,
    'Accept': 'application/vnd.twitchtv.v5+json',
    'Authorization': 'OAuth '+oauth,
    'Content-Type': 'application/json'
    }
    req = urllib.request.Request(url, None, headers)
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode("utf-8"))
    userlist = []
    while lookfor=="follows" or lookfor=="subscriptions":
        try:
            cursor = data["_cursor"]
        except KeyError:
            print("End of list")
            return userlist
        for follower in data[lookfor]:
            userlist.append(follower["user"]["name"])
        req = urllib.request.Request(url+"?cursor="+cursor, None, headers)
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode("utf-8"))
    return data[lookfor]

#Getting your own ID at the start
ID = parseInfo("https://api.twitch.tv/kraken/channel", "_id")

def getUserID(user):
    url = "https://api.twitch.tv/kraken/users?login="+user
    return parseInfo(url, "_id")

def followers():
    url = "https://api.twitch.tv/kraken/channels/"+ID+"/follows"
    return parseInfo(url, "follows")

def totalFollowers():
    url = "https://api.twitch.tv/kraken/channels/"+ID+"/follows"
    return parseInfo(url, "_total")

def subs():
    url = "https://api.twitch.tv/kraken/channels/"+ID+"/subscriptions"
    return parseInfo(url, "subscriptions")

def totalSubs():
    url = "https://api.twitch.tv/kraken/channels/"+ID+"/subscriptions"
    return parseInfo(url, "_total")

def isSubbed(userid):
    url = 'https://api.twitch.tv/kraken/channels/'+ID+'/subscriptions/'+userid
    try:
       parseInfo(url, "sub_plan")
    except urllib.error.HTTPError as e:
        print("Couldn't get subscription status")
        print(str(e.code) + " " + e.reason)
