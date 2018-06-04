import socket
import time
import threading
from threading import Thread
import TextInput as AI
import GenerateSentences as speak
import SettingsAndPreferences as settings
import TwitchAPI as api
from tkinter import *
from tkinter import scrolledtext
import os

HOST = "irc.chat.twitch.tv"
PORT = 6667
NICK = settings.findValue("NICK")
JOIN = settings.findValue("JOIN")
SENDTO = settings.findValue("SENDTO")
PASS = settings.findValue("oauth")
MSGPR = settings.findValue("MessagePrefix")

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

    def run(self):
        self.window = Tk()
        self.window.title(settings.folder)
        self.window.geometry('650x350')
        def save():     
            AI.save()
            txt.insert(INSERT,'Saved AI!\n')
        def saveset():     
            settings.saveall()
            txt.insert(INSERT,'Saved settings!\n')
        def nosave():
            self.save = False
            self.window.quit()
        def onselect(evt):
            if entry.get() and entry.get()!="-":
                print("Updating "+self.key+str(self.index)+" with "+entry.get())
                try:
                    settings.settings[self.key][self.index]=entry.get()
                except IndexError:
                    settings.settings[self.key].append(entry.get())
            try:
                index = int(evt.widget.curselection()[0])
                entry.delete(0,len(entry.get()))
                entries.delete(1,entries.size()-1)
                loop=0
                self.key = evt.widget.get(index)
                for e in settings.settings[self.key]:
                    loop+=1
                    entries.insert(loop, str(loop))
            except IndexError:
                pass
                
        def subselect(evt):
            if entry.get() and entry.get()!="-":
                print("Updating "+self.key+str(self.index)+" with "+entry.get())
                try:
                    settings.settings[self.key][self.index]=entry.get()
                except IndexError:
                    settings.settings[self.key].append(entry.get())
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
        save.grid(column=0, row=1,sticky=N)
        saveset = Button(self.window, text="Save settings", command=saveset, height=2, width=45)
        saveset.grid(column=0, row=2,sticky=N)
        nosave = Button(self.window, text="Quit without saving", command=nosave, height=2, width=45)
        nosave.grid(column=0, row=4,sticky=N)
        savequit = Button(self.window, text="Save and quit", command=self.window.quit, height=2, width=45)
        savequit.grid(column=0, row=3,sticky=N)
        txt = scrolledtext.ScrolledText(self.window,width=40,height=5)
        txt.grid(column=0,row=0,sticky=N)
        entry = Entry(self.window)
        entry.grid(row=1,column=2)
        entries = Listbox(self.window,height=5)
        entries.bind('<<ListboxSelect>>',subselect)
        entries.insert(0, "0")
        entries.grid(column=2,row=0)
        sets = Listbox(self.window,height=20)
        sets.bind('<<ListboxSelect>>', onselect)
        loop=0
        for w in settings.settings.keys():
            loop+=1
            sets.insert(loop, w)
        sets.grid(column=1,row=0,rowspan=5)
        try:
            self.window.mainloop()
            if self.save:
                AI.save()
                settings.saveall()
            os._exit(1)
        except:
            print("UI crash, saving... program should still run")
            AI.save()

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

connectToTwitch()
print("Talking set to "+settings.findValue("enableTalking"))
print("Learning set to "+settings.findValue("enableLearning"))
ohno = 0
timeOfReply = 0
cooldown = int(settings.findValue("cooldown"))
longerCooldown = int(settings.findValue("longerCooldown"))
autoCooldown = int(settings.findValue("autoCooldown"))
s.settimeout(10)
call = settings.findValue("call")

wordAddingThread = AddWords()
wordAddingThread.setName('Word adding')

messageGenThread = GenerateMessage()
messageGenThread.setName('Message generation')

getinput = getInput()
getinput.start()

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
            
            #learning
            if not username in settings.userlist("ignore list.txt") and settings.findValue("enableLearning")=="1":
                if (MSGPR=="30" and username!=NICK) or (MSGPR!="30" and message.find(MSGPR)!=0):
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
                    print("COMMAND RESPONSE: " + reply)
                    send_message(reply)
            except IndexError:
                print(message+" caused index error")
                
            #talking
            if settings.findValue("enableTalking")=="1" and (message.lower().find(call)>-1 or abs(time.clock()-timeOfReply) > autoCooldown):
                if (abs(time.clock()-timeOfReply)>cooldown and approved) or abs(time.clock()-timeOfReply)>longerCooldown:
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
