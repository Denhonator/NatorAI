import socket
import time
import threading
from threading import Thread
import SettingsAndPreferences as settings
import TextInput as AI
import GenerateSentences as speak
import TwitchAPI as api
from tkinter import *
from tkinter import scrolledtext
import os

HOST = "irc.chat.twitch.tv"
PORT = 6667
go = False

s = socket.socket()

def parseMessage(parts):
    msginfo = {}
    for line in parts[0].split(";"):
        try:
            (key, value) = line.split("=")
            msginfo[key] = value
        except:
            pass
    return msginfo

def send_message(rep):
    MSGPR = settings.findValue("MessagePrefix")
    if MSGPR != "30":
        prefix = MSGPR+" "
    else:
        prefix = ""
    while len(prefix+rep)>=500: #hard cap
        rep=rep[:-1]
    s.send(bytes("PRIVMSG #" + SENDTO + " :" + prefix + rep + "\r\n", "UTF-8"))

def connectToTwitch():
    s.connect((HOST, PORT))
    s.send(bytes("PASS " + PASS + "\r\n", "UTF-8"))
    s.send(bytes("NICK " + NICK + "\r\n", "UTF-8"))
    s.send(bytes('CAP REQ :twitch.tv/tags\r\n', 'UTF-8'))
    s.send(bytes("JOIN #" + JOIN + " \r\n", "UTF-8"))
    while True:
        line = str(s.recv(1024))
        for text in line.split('\\r\\n'):
            if len(text)>1:
                print(text)
        if "End of /NAMES list" in line:
            global go
            go = False
            break

class AddWords(Thread):
    def __init__(self, message=None):
        Thread.__init__(self)
        self.message = message

    def run(self):
        if messageGenThread.is_alive():
            messageGenThread.join()
        if self.message:
            AI.add(self.message)
        else:
            print("No words received")

class getInput(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.save = True
        self.key = "MessagePrefix"
        self.index = 0
        self.description = {"word": "Word ignore list. The AI will not learn from messages with these words",
                            "approved": "Users who can use the base cooldown without being a subscriber",
                            "whitelist": "Users who are allowed to change commands via twitch chat",
                            "ignore": "The AI will not learn from these users",
                            "NICK": "Account nick for the bot",
                            "JOIN": "Channel to read messages from",
                            "SENDTO": "Channel to send messages to",
                            "oauth": "IRC oauth token for the bot's account",
                            "MessagePrefix": "Characters at the start of every message the bot sends",
                            "cooldown": "Bot call cooldown for subs and approved users",
                            "longerCooldown": "Bot call cooldown for other users",
                            "autoCooldown": "Time after which the bot will send a message on its own",
                            "call": "Characters used to provoke a random message from the bot. Following words will be used as feed",
                            "FeedInFirstWord": "Chance to start a message with a word from given feed",
                            "FeedInNextWord": "Chance to use a word from given feed in a next word",
                            "msgLengthModifier": "Affects the typical length of random messages. Default: 5 Recommended: 1-10",
                            "maxMessageLength": "Character limit after which no more words will be added. Recommended: 200 or more",
                            "msgContinuationModifier": "Chance to continue a message if it would otherwise end. Default: 4 Recommended: 1-10",
                            "maxContinuationLength": "Character threshold after which continuation will not be used anymore",
                            "sentenceChance": "Chance to look for next words using the previous two words rather than one. Recommended: 100",
                            "SpamLimit": "Limit to how many times a word can be repeated. Mainly to avoid potential emote spamming",
                            "enableLearning": "Allow the AI to learn from twitch chat (0,1)",
                            "enableTalking": "Allow the AI to generate and send messages to twitch chat (0,1)",
                            "APIOauth": "Twitch API oauth token, used for checking for follows. Connected to ClientID",
                            "ClientID": "ClientID from your created twitch app for the bot",
                            "FollowCheckCooldown": "How often in seconds followers will be checked",
                            "FollowReply": "What the bot will say when someone follows. {} will be replaced by the nick, () with a generated message",
                            "FollowFeed": "Feed that the AI will use for generating a random message in response to a follow",
                            "SubReply": "What the bot will say when someone subscribes. {} will be replaced by the nick, () with a generated message",
                            "SubFeed": "Feed that the AI will use for generating a random message in response to a subscription",
                            "ResubReply": "Same as SubReply, but for resubs. Additionally, [] will be replaced with sub months",
                            "ResubFeed": "Feed that the AI will use for generating a random message in response to a resub"}

    def run(self):
        self.window = Tk()
        self.window.title(settings.folder)
        self.window.geometry('640x420')
        def save():     
            AI.save()
            txt.insert(INSERT,'Saved AI!\n')
        def saveset():
            if entry.get() and entry.get()!="-":
                print("Updating "+self.key+str(self.index)+" with "+entry.get())
                try:
                    settings.settings[self.key][self.index]=entry.get()
                except IndexError:
                    settings.settings[self.key].append(entry.get())
            settings.saveall()
            txt.insert(INSERT,'Saved settings!\n')
            txt.see("end")
        def nosave():
            self.save = False
            self.window.quit()
        def connect():
            global go
            go = True
            timeout = 0
            while go and timeout<3:
                time.sleep(0.1)
                timeout+=0.1
            if timeout<3:
                txt.insert(INSERT, "Connected!")
            else:
                txt.insert(INSERT, "Failed to connect")
            txt.see("end")
        def addentry():
            self.entryamount
            name = newentry.get()
            settings.settings[name] = ["EditMe"]
            sets.insert(self.entryamount, name)
        def onselect(evt):
            if entry.get() and entry.get()!="-":
                print("Updating "+self.key+str(self.index)+" with "+entry.get())
                try:
                    settings.settings[self.key][self.index]=entry.get()
                except IndexError:
                    settings.settings[self.key].append(entry.get())
            elif entry.get():
                print("Removing "+self.key+str(self.index))
                try:
                    del settings.settings[self.key][self.index]
                except IndexError:
                    print("Nothing to delete")
            try:
                index = int(evt.widget.curselection()[0])
                entry.delete(0,len(entry.get()))    #On select, (not select out)
                entries.delete(1,entries.size()-1)
                loop=0
                self.key = evt.widget.get(index)
                for e in settings.settings[self.key]:
                    loop+=1
                    entries.insert(loop, str(loop))
                entries.select_set(0)
                entries.event_generate("<<ListboxSelect>>")
                message = self.description.get(self.key, "")
                if message:
                    txt.insert(INSERT, message+"\n\n")
                txt.see("end")
            except IndexError:
                pass
                
        def subselect(evt):
            if entry.get() and entry.get()!="-":
                print("Updating "+self.key+str(self.index)+" with "+entry.get())
                try:
                    settings.settings[self.key][self.index]=entry.get()
                except IndexError:
                    settings.settings[self.key].append(entry.get())
            elif entry.get():
                print("Removing "+self.key+str(self.index))
                try:
                    del settings.settings[self.key][self.index]
                except IndexError:
                    print("Nothing to delete")
            try:
                subindex = int(evt.widget.curselection()[0])
                self.index = subindex
                entry.delete(0,len(entry.get()))
                try:
                    entry.insert(INSERT,settings.settings[self.key][subindex])
                except IndexError:
                    entry.insert(INSERT,"-")
            except IndexError as e:
                pass
            
        save = Button(self.window, text="Save AI", command=save, height=2, width=45)
        save.grid(column=0, row=2,sticky=N)
        saveset = Button(self.window, text="Save settings", command=saveset, height=2, width=45)
        saveset.grid(column=0, row=3,sticky=N)
        nosave = Button(self.window, text="Quit without saving", command=nosave, height=2, width=45)
        nosave.grid(column=0, row=5,sticky=N)
        savequit = Button(self.window, text="Save and quit", command=self.window.quit, height=2, width=45)
        savequit.grid(column=0, row=4,sticky=N)
        connect = Button(self.window, text="Connect", command=connect, height=2, width=45)
        connect.grid(column=0, row=1,sticky=N)
        txt = scrolledtext.ScrolledText(self.window,width=40,height=10)
        txt.grid(column=0,row=0,sticky=N)
        txt.insert(INSERT, "Change, add, remove settings/commands/values. Choose one from the left menu, then add a value to 0, "
                            "unless you want to have multiple values. Insert '-' to remove an entry. Only way to not save AI/settings "
                            "is to select 'Quit without saving'. If you want to change the AI folder, edit folder.txt and relaunch the program\n\n")
        entry = Entry(self.window)
        entry.grid(row=1,column=2)
        newentry = Entry(self.window)
        newentry.grid(row=6, column=1)
        add = Button(self.window, text="Add", command=addentry, height=1, width=5)
        add.grid(row=6, column=2, sticky=W)
        entries = Listbox(self.window,height=5)
        entries.bind('<<ListboxSelect>>',subselect)
        entries.insert(0, "0")
        entries.grid(column=2,row=0)
        sets = Listbox(self.window,height=22)
        sets.bind('<<ListboxSelect>>', onselect)
        self.entryamount=0
        for w in settings.settings.keys():  #sort commands to the end of the list
            if w[0]!="!":
                self.entryamount+=1
                sets.insert(self.entryamount, w)
        for w in settings.settings.keys():
            if w[0]=="!":
                self.entryamount+=1
                sets.insert(self.entryamount, w)
        sets.grid(column=1,row=0,rowspan=6)
        try:
            self.window.mainloop()
            if self.save:
                AI.save()
                settings.saveall()
            os._exit(1)
        except:
            print("UI crash, saving... program should still run")
            AI.save()
            settings.saveall()

class GenerateMessage(Thread):
    def __init__(self, message=None):
        Thread.__init__(self)
        self.message = message

    def run(self):
        if wordAddingThread.is_alive():
            wordAddingThread.join()
        if self.message:
            try:
                feed = self.message.lower().split(settings.findValue("call"))[1].strip().split()
                if feed[0]=="":
                    feed = []
            except:
                #print("No feed")
                feed = []
        else:
            #print("No feed")
            feed = []
        reply = speak.newGenerateSentence(feed)
        print("GENERATED MESSAGE: " + reply)
        send_message(reply)

class SubWatch(Thread):
    def __init__(self, user, months=0):
        Thread.__init__(self)
        self.user = user
        self.months = months

    def run(self):
        subtype = "Sub"
        if self.months!="0":
            subtype = "Resub"     
        subreply = settings.findValue(subtype+"Reply")
        if subreply and subreply!="30" and settings.findValue("enableTalking"):
            feed = []
            subfeed = settings.findValue(subtype+"Feed").strip()
            if subfeed!="30":
                feed = subfeed.split()
            if subreply.find("()")>-1:
                gen = speak.newGenerateSentence(feed)
            reply=subreply.replace("{}", "@"+self.user).replace("[]", self.months).replace("()", gen).strip()
            print("SUB REPLY: " + reply)
            send_message(reply)

class FollowWatch(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.followers = api.totalFollowers()

    def run(self):
        followreply = settings.findValue("FollowReply")
        while followreply!="30" and followreply:
            try:
                self.followers2 = api.totalFollowers()               
                if self.followers2>self.followers and followreply!="30" and settings.findValue("enableTalking")=="1":
                    followreply = settings.findValue("FollowReply")
                    feed = []
                    gen = ""
                    followfeed = settings.findValue("FollowFeed").strip()
                    if followfeed!="30":
                        feed = followfeed.split()
                    if followreply.find("()")>-1:
                        gen = speak.newGenerateSentence(feed)
                    reply=followreply.replace("{}", "@"+api.followers()[0]).replace("()", gen).strip()
                    print("FOLLOW REPLY: " + reply)
                    send_message(reply)
                self.followers = self.followers2
            except Exception as e:
                print("Couldn't update follower count")
                print(e)
            time.sleep(int(settings.findValue("FollowCheckCooldown")))

getinput = getInput()
getinput.start()
while not go:
    time.sleep(0.1)
NICK = settings.findValue("NICK")
JOIN = settings.findValue("JOIN")
SENDTO = settings.findValue("SENDTO")
PASS = settings.findValue("oauth")
connectToTwitch()
print("Talking set to "+settings.findValue("enableTalking"))
print("Learning set to "+settings.findValue("enableLearning"))
ohno = 0
timeOfReply = 0
s.settimeout(10)

wordAddingThread = AddWords()
wordAddingThread.setName('Word adding')

messageGenThread = GenerateMessage()
messageGenThread.setName('Message generation')

if settings.findValue("FollowReply")!="30":
    followChecker = FollowWatch()
    followChecker.setName('Follow checker')
    followChecker.start()

print("All systems go")
message = ""

while True:
    try:
        for line in str(s.recv(1024)).split('\\r\\n'):
            if line=="b''":
                ohno+=1
                if ohno > 10:
                    s.shutdown(socket.SHUT_WR)
                    s.close()
                    print("Disconnected")
                    connectToTwitch()
                    print("Reconnected hopefully")
                    ohno=0
                    break
            else:
                ohno=0
            if line.find("PING")!=-1:
                print("PING")
            if line.find("PING")==2:    #making sure ping pong works
                s.send(bytes("PONG\r\n", "UTF-8"))
                print("PONG")
                continue
            if len(line)<5:
                continue
            parts = line.split(" :", 2)
            if len(parts) > 2:
                message = parts[2].strip()
            else:
                print(line)
                message = ""
                print("Not a usual message, ignoring")

            msginfo = parseMessage(parts)
            username = msginfo.get("display-name","").lower()
            if not username:
                print("No display-name found")
                
            approved = False
            if msginfo.get("subscriber","0")!="0":
                approved = True
                #print(username+" is a subscriber!")
            elif username in settings.userlist("approved users.txt"):
                approved = True

            if msginfo.get("msg-id", ""):
                print(msginfo["msg-id"]+" happened!")
                msgid = msginfo["msg-id"]
                if msgid=="sub" or msgid=="resub":
                    if settings.findValue("enableTalking")=="1":
                        months = msginfo.get("msg-param-months","0")
                        subChecker = SubWatch(username, months)
                        subChecker.setName('Sub message')
                        subChecker.start()               

            if "PRIVMSG" not in parts[1] and message:
                print("Non PRIVMSG message: "+message)

            if not message:
                continue
            
            #update settings
            cooldown = int(settings.findValue("cooldown"))
            longerCooldown = int(settings.findValue("longerCooldown"))
            autoCooldown = int(settings.findValue("autoCooldown"))
            prefix = settings.findValue("MessagePrefix")
            call = settings.findValue("call")
            #learning
            if not username in settings.userlist("ignore list.txt") and settings.findValue("enableLearning")=="1":
                if (prefix=="30" and username!=NICK) or (prefix!="30" and message.find(prefix)!=0):
                    if wordAddingThread.is_alive():
                        print("Skipping because adding previous words")
                    else:
                        wordAddingThread = AddWords(message)
                        wordAddingThread.start()
                    
            #commands
            try:
                if message.split()[0]=="!save" and username in settings.userlist("whitelist.txt"):
                    AI.save()
                elif message[0]=='!' and (len(message.strip().split())==1 and settings.commandList(message.strip().split()[0].lower()) or (username in settings.userlist("whitelist.txt") and len(message.strip().split())>1)):
                    if len(message.strip().split())>1:
                        reply = settings.commandList(message.strip().split()[0], message[message.find(" ")+1:])
                    else:
                        reply = settings.commandList(message.split()[0])
                    if reply!="30":
                        print("COMMAND RESPONSE: " + reply)
                        send_message(reply)
            except IndexError:
                print(message+" caused index error")
                
            #talking
            if settings.findValue("enableTalking")=="1" and (message.lower().find(call)>-1 or abs(time.clock()-timeOfReply) > autoCooldown):
                if (abs(time.clock()-timeOfReply)>cooldown and approved) or abs(time.clock()-timeOfReply)>longerCooldown:
                    if (prefix=="30" and username!=NICK) or (prefix!="30" and message.find(prefix)!=0):    #don't reply to yourself
                        if messageGenThread.is_alive():
                            print("Skipping because generating another message")
                        else:
                            timeOfReply = time.clock()
                            messageGenThread = GenerateMessage(message)
                            messageGenThread.start()
                    
    except socket.timeout:
        autoCooldown = int(settings.findValue("autoCooldown"))
        if settings.findValue("enableTalking")=="1" and abs(time.clock()-timeOfReply) > autoCooldown:
            if messageGenThread.is_alive():
                print("Skipping because generating another message")
            else:
                timeOfReply = time.clock()
                messageGenThread = GenerateMessage()
                messageGenThread.start()
