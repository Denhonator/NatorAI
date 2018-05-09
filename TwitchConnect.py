import socket
import time
import threading
from threading import Thread
import TextInput as AI
import GenerateSentences as speak
import SettingsAndPreferences as settings
import TwitchAPI as api

HOST = "irc.chat.twitch.tv"
PORT = 6667
NICK = settings.findValue("NICK")
JOIN = settings.findValue("JOIN")
SENDTO = settings.findValue("SENDTO")
PASS = settings.findValue("oauth")
MSGPR = settings.findValue("MessagePrefix")

s = socket.socket()

def send_message(rep):
    if MSGPR != "30":
        prefix = MSGPR+" "
    else:
        prefix = ""
    s.send(bytes("PRIVMSG #" + SENDTO + " :" + prefix + rep + "\r\n", "UTF-8"))

def connectToTwitch():
    s.connect((HOST, PORT))
    s.send(bytes("PASS " + PASS + "\r\n", "UTF-8"))
    s.send(bytes("NICK " + NICK + "\r\n", "UTF-8"))
    s.send(bytes("JOIN #" + JOIN + " \r\n", "UTF-8"))
    while True:
        line = str(s.recv(1024))
        for text in line.split('\\r\\n'):
            if len(text)>1:
                print(text)
        if "End of /NAMES list" in line:
            break

class AddWords(Thread):
    def __init__(self, message=None):
        Thread.__init__(self)
        self.message = message

    def run(self):
        if messageGenThread.is_alive():
            messageGenThread.join()
        if self.message:
            AI.altSentences(self.message)
            AI.addWords(AI.findWords(self.message.split()))
        else:
            print("No words received")

class GenerateMessage(Thread):
    def __init__(self, message=None):
        Thread.__init__(self)
        self.message = message

    def run(self):
        if wordAddingThread.is_alive():
            wordAddingThread.join()
        if self.message:
            try:
                feed = self.message.lower().split("nator,")[1].strip().split()
                if feed[0]=="":
                    feed = []
            except:
                #print("No feed")
                feed = []
        else:
            #print("No feed")
            feed = []
        if feed:
            print(feed)
        reply = speak.generateSentence(feed)
        print("GENERATED MESSAGE: " + reply)
        send_message(reply)

class SubWatch(Thread):
    def __init__(self):
        Thread.__init__(self)
        try:
            self.subs = api.totalSubs()
            for name in api.subs():
                settings.userlist("approved users.txt", name)
        except Exception as e:
            print("Couldn't look up subs")
            print(e)

    def run(self):
        try:
            self.subs2 = api.totalSubs()
            if self.subs2 != self.subs:
                if self.subs2>self.subs:
                    replywords = settings.findValue("SubReply")
                    reply = ""
                    for word in replywords:
                        if word=="{}":
                            reply+=api.subs()[0]+" "
                        else:
                            reply+= word+" "
                    reply += speak.generateSentence(settings.findValue("SubFeed").strip().split())
                    print("SUB REPLY: " + reply)
                    send_message(reply)
                self.subs = self.subs2
                for name in api.subs():
                    settings.userlist("approved users.txt", name)
                    print("Updated sublist")
        except Exception as e:
            print("Couldn't look up subs")
            print(e)
        time.sleep(int(settings.findValue("SubCheckCooldown")))

class FollowWatch(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.followers = api.totalFollowers()

    def run(self):
        try:
            self.followers2 = api.totalFollowers()
            if self.followers2 > self.followers and settings.findValue("FollowReply")!="30":
                replywords = settings.findValue("FollowReply")
                reply = ""
                for word in replywords:
                    if word=="{}":
                        reply+=api.followers()[0]+" "
                    else:
                        reply+= word+" "
                reply += speak.generateSentence(settings.findValue("FollowFeed").strip().split())
                print("FOLLOW REPLY: " + reply)
                send_message(reply)
            self.followers = self.followers2
        except Exception as e:
            print("Couldn't update follower count")
            print(e)
        time.sleep(int(settings.findValue("FollowCheckCooldown")))

connectToTwitch()
print("Talking set to "+settings.findValue("enableTalking"))
print("Learning set to "+settings.findValue("enableLearning"))
ohno = 0
timeOfReply = 0
cooldown = int(settings.findValue("cooldown"))
longerCooldown = int(settings.findValue("longerCooldown"))
autoCooldown = int(settings.findValue("autoCooldown"))
s.settimeout(1)
call = settings.findValue("call")
skip = False

wordAddingThread = AddWords()
wordAddingThread.setName('Word adding')

messageGenThread = GenerateMessage()
messageGenThread.setName('Message generation')

if settings.findValue("enableSubCheck")=="1":
    subChecker = SubWatch()
    subChecker.setName('Sub checker')
    subChecker.start()

if settings.findValue("enableFollowCheck")=="1":
    followChecker = FollowWatch()
    followChecker.setName('Follow checker')
    followChecker.start()

message = ""

while True:
    try:
        for line in str(s.recv(1024)).split('\\r\\n'):
            if line=="b''":
                ohno+=1
                if ohno > 30:
                    s.shutdown()
                    s.close()
                    print("Disconnected")
                    connectToTwitch()
                    print("Reconnected")
                    break
            if line.find("PING")!=-1:
                print("PING")
            if line.find("PING")==2:    #making sure ping pong works
                s.send(bytes("PONG\r\n", "UTF-8"))
                print("PONG")
            parts = line.split(':', 2) 
            if len(parts) < 3:
                continue

            if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
                message = parts[2][:len(parts[2])]
            else:
                print(line)

            usernamesplit = parts[1].split("!")
            username = usernamesplit[0]
            
            #print(username+": "+message)
            
            if not username in settings.userlist("ignore list.txt") and settings.findValue("enableLearning")=="1":
                if (MSGPR=="30" and username!=NICK) or (MSGPR!="30" and message.find(MSGPR)!=0):
                    if wordAddingThread.is_alive():
                        print("Skipping because adding previous words")
                    else:
                        wordAddingThread = AddWords(message)
                        wordAddingThread.start()
                else:
                    print("Ignored itself")

            try:
                if message.split()[0][0]=='!' and (len(message.strip().split())==1 and settings.commandList(message.strip().split()[0].lower()) or (username in settings.userlist("whitelist.txt") and len(message.strip().split())>1)):
                    if len(message.strip().split())>1:
                        reply = settings.commandList(message.strip().split()[0], message[message.find(" ")+1:])
                    else:
                        reply = settings.commandList(message.split()[0])
                    print("COMMAND RESPONSE: " + reply)
                    send_message(reply)
            except IndexError:
                print(message+" caused index error")

            if settings.findValue("enableTalking")=="1" and (message.lower().find(call)>-1 or abs(time.clock()-timeOfReply) > autoCooldown):
                if (abs(time.clock()-timeOfReply)>cooldown and username in settings.userlist("approved users.txt")) or abs(time.clock()-timeOfReply)>longerCooldown:
                    if (MSGPR=="30" and username!=NICK) or (MSGPR!="30" and message.find(MSGPR)!=0):    #don't reply to yourself
                        if messageGenThread.is_alive():
                            print("Skipping because generating another message")
                        else:
                            timeOfReply = time.clock()
                            messageGenThread = GenerateMessage(message)
                            messageGenThread.start()
                    
    except socket.timeout:
        if settings.findValue("enableTalking")=="1" and abs(time.clock()-timeOfReply) > autoCooldown:
            if messageGenThread.is_alive():
                print("Skipping because generating another message")
            else:
                timeOfReply = time.clock()
                messageGenThread = GenerateMessage()
                messageGenThread.start()
