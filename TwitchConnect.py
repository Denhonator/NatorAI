import socket
import time
import threading
from threading import Thread
import SettingsAndPreferences as settings
import TextInput as AI
import GenerateSentences as speak
import TwitchAPI as api
import UI

HOST = "irc.chat.twitch.tv"
PORT = 6667

s = socket.socket()

def parseMessage(tags):
    msginfo = {}
    for line in tags[1:].split(";"):
        try:
            (key, value) = line.split("=")
            msginfo[key] = value
        except:
            pass
    return msginfo

def send_message(rep, addprefix = True):
    MSGPR = settings.findValue("MessagePrefix")
    if MSGPR != "30" and addprefix:
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
    s.send(bytes('CAP REQ :twitch.tv/commands\r\n', 'UTF-8'))
    s.send(bytes("JOIN #" + JOIN + " \r\n", "UTF-8"))
    while True:
        line = (s.recv(1024)).decode("utf-8","replace")
        for text in line.split('\\r\\n'):
            if text:
                print(text)
        if "End of /NAMES list" in line:
            UI.go = False
            break

class AddWords(Thread):
    def __init__(self, message=None):
        Thread.__init__(self)
        self.message = message

    def run(self):
        if messageGenThread.is_alive():
            messageGenThread.join()
        if self.message:
            if self.message==1:
                AI.load()
            else:
                AI.add(self.message)
        else:
            settings.levelprint("No words received", 4)

class GenerateMessage(Thread):
    def __init__(self, message=None):
        Thread.__init__(self)
        self.message = message

    def run(self):
        if wordAddingThread.is_alive():
            wordAddingThread.join()
        feed = []
        if self.message:
            #pregen
            if self.message==1:
                pregenAmount = int(settings.findValue("PregenAmount"))
                pregenStart = 0.5-(0.05*min(max(0.2*int(settings.findValue("PregenStartupSpeed")),0),10))
                pregenRefresh = (10.0/(min(max(0.2*int(settings.findValue("PregenRefreshSpeed")),1),10))-0.5)
                if pregenAmount>99:
                    progress = 0
                    if pregenAmount-len(speak.pregen)<2:
                        progress = 100
                    while self.message==1:
                        if len(speak.pregen)>=pregenAmount:
                            del speak.pregen[0]
                            time.sleep(pregenRefresh)
                        else:
                            time.sleep(pregenStart)
                        if settings.findValue("NewGeneration")=="1":
                            speak.pregen.append(speak.GenerateSentence([],False))
                        else:
                            speak.pregen.append(speak.newGenerateSentence([], 10))
                        if int(100*len(speak.pregen)/pregenAmount)>progress:
                            progress=int(100*len(speak.pregen)/pregenAmount)
                            settings.levelprint("Pre-generating... "+str(progress)+"%",0)
                return
            try:
                feed = self.message.lower().replace(settings.findValue("call"), "").strip().split()
            except Exception as e:
                feed = self.message.lower().strip().split()
                print(e)
        else:
            feed = []
        reply = ""
        if speak.pregen:
            reply = speak.findPregen(feed)
        hasFeed = False
        for w in feed:
            if reply and w in reply.lower().split():
                hasFeed = True
        if not reply or (feed and not hasFeed):
            reply = speak.GenerateSentence(feed)
        send_message(reply)
        if hasFeed:
            settings.levelprint("PREGEN MESSAGE: " + reply, 1)
            try:
                speak.pregen.remove(reply)
            except:
                settings.levelprint("Couldn't remove from pregen",2)
        else:
            settings.levelprint("GENERATED MESSAGE: " + reply, 1)

class SubWatch(Thread):
    def __init__(self, user, months, user2):
        Thread.__init__(self)
        self.user = user
        self.months = months
        self.user2 = user2

    def run(self):
        subtype = "Sub"
        if self.months!="0":
            subtype = "Resub"
        if self.user2:
            subtype = "Subgift"
        subreply = settings.findValue(subtype+"Reply")
        if subreply and subreply!="30" and settings.findValue("enableTalking"):
            if subreply.find("()")>-1:
                gen = speak.newGenerateSentence()
            reply=subreply.replace("{}", self.user).replace("[]", self.months).replace("()", gen)
            reply=reply.replace("{from}", self.user).replace("{to}", self.user2).strip()
            send_message(reply)
            settings.levelprint("SUB REPLY: " + reply, 1)

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
                    gen = ""
                    if followreply.find("()")>-1:
                        gen = speak.newGenerateSentence()
                    time.sleep(1) #ensure the new username is in before fetching
                    reply=followreply.replace("{}", api.NewFollower(True)).replace("()", gen).strip()
                    send_message(reply)
                    settings.levelprint("FOLLOW REPLY: " + reply, 1)
                self.followers = self.followers2
            except Exception as e:
                settings.levelprint("Couldn't update follower count", 0)
                settings.levelprint(e, 0)
            time.sleep(int(settings.findValue("FollowCheckCooldown")))

class SubcountWatch(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            try:
                self.subs = api.totalSubs()               
                subfile = open(settings.folder+"/subgoal.txt","w")
                subgoaltext = settings.findValue("SubGoal").replace("{}", str(self.subs))
                subfile.write(subgoaltext)
                subfile.close()
            except Exception as e:
                settings.levelprint("Couldn't update sub count", 0)
                settings.levelprint(e, 0)
            time.sleep(int(settings.findValue("FollowCheckCooldown")))

getinput = UI.getInput()
getinput.start()

wordAddingThread = AddWords(1)
wordAddingThread.setName('Word adding')

messagePreGen = GenerateMessage(1)
messagePreGen.setName('Message pre-generation')

messageGenThread = GenerateMessage()
messageGenThread.setName('Message generation')

wordAddingThread.start()
messagePreGen.start()

while not UI.go:
    time.sleep(0.1)
    
NICK = settings.findValue("NICK")
JOIN = settings.findValue("JOIN")
SENDTO = settings.findValue("SENDTO")
PASS = settings.findValue("oauth")
connectToTwitch()
print("Talking set to "+settings.findValue("enableTalking"))
print("Learning set to "+settings.findValue("enableLearning"))
timeOfReply = 0
timeOfAuto = 0
timeOfCommand = 0
s.settimeout(10)

if settings.findValue("FollowReply")!="30":
    followChecker = FollowWatch()
    followChecker.setName('Follow checker')
    followChecker.start()

subChecker = SubcountWatch()
subChecker.setName('Subcount checker')
subChecker.start()

print("All systems go")
message = ""

while True:
    try:
        for line in (s.recv(1024)).decode("utf-8","replace").split('\\r\\n'):
            if line.strip()=="PING :tmi.twitch.tv":
                s.send(bytes("PONG\r\n", "UTF-8"))
                settings.levelprint("PING PONG", 0)
                if settings.findValue("autosave")=="1":
                    AI.save()
                    settings.saveall()
                continue
            settings.levelprint(line.strip(),6)
            if len(line)<5:
                continue
            
            parts = line.split(" :", 2)
            if "tmi.twitch.tv" in parts[1] and len(parts)>2:
                message = parts[2].strip()
            else:
                message = ""
                settings.levelprint("Couldn't parse message", 0)
                settings.levelprint(line, 0)
                continue
                
            msginfo = parseMessage(parts[0])
            settings.levelprint(msginfo,4)
            
            username = msginfo.get("display-name","")
            if not username:
                settings.levelprint("No display-name found", 6)
                
            approved = False
            if "subscriber" in msginfo.get("badges","") or "mod" in msginfo.get("badges",""):
                approved = True
            elif username.lower() in settings.userlist("approved users.txt"):
                approved = True
            if approved:
                settings.levelprint(username+" is approved!", 6)

            if msginfo.get("msg-id", ""):
                settings.levelprint(msginfo["msg-id"]+" happened!", 0)
                msgid = msginfo["msg-id"]
                if "sub" in msgid and settings.findValue("enableTalking")=="1":
                    months = msginfo.get("msg-param-months","0")
                    user2 = msginfo.get("msg-param-recipient-display-name", None)
                    subChecker = SubWatch(username, months, user2)
                    subChecker.setName('Sub message')
                    subChecker.start()

            msgtype = "WHISPER" if "WHISPER" in parts[1] else "-"

            if not "PRIVMSG" in parts[1] and not "WHISPER" in parts[1] and message:
                settings.levelprint("Non PRIVMSG message: "+message, 3)
            else:
                settings.levelprint(msgtype+" "+username+": "+message, 3)
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                server_address = ('localhost', 55555)
                color = msginfo.get("color", "")
                emotes = msginfo.get("emotes", "")
                sent = sock.sendto(bytes(username+' '+color+' '+emotes+' '+msgtype+' '+message, 'UTF-8'), server_address)
                sock.close()

            if not "PRIVMSG" in parts[1]:
                continue
            
            #update settings
            cooldown = int(settings.findValue("cooldown"))
            longerCooldown = int(settings.findValue("longerCooldown"))
            autoCooldown = int(settings.findValue("autoCooldown"))
            prefix = settings.findValue("MessagePrefix")
            call = settings.findValue("call")
                    
            #commands
            if message[0]=='!':
                white = username.lower() in settings.userlist("whitelist.txt")
                if white or abs(time.perf_counter()-timeOfCommand) > int(settings.findValue("commandCooldown")):
                    cmdparts = message.strip().split(" ", 1)
                    reply = settings.findValue(message)
                    if white:
                        try:
                            if cmdparts[1][0]!="!":
                                cmdparts[1] = "!"+cmdparts[1]
                            if cmdparts[0]=="!del":
                                reply = settings.findValue(cmdparts[1], None, True)
                            cmd = cmdparts[1].split("=")[0].strip()
                            val = cmdparts[1].split("=")[1].strip()
                            if len(cmdparts)>=2:
                                if cmdparts[0]=="!edit":
                                    reply = settings.findValue(cmd, val, True)   
                                if cmdparts[0]=="!add":
                                    reply = settings.findValue(cmd, val)
                        except IndexError as e:
                            pass
                    if reply!="30":
                        settings.levelprint("COMMAND RESPONSE: " + reply, 1)
                        send_message(reply, False)
                        timeOfCommand = time.perf_counter()

            #learning
            elif username.lower() not in settings.userlist("ignore list.txt") and settings.findValue("enableLearning")=="1":
                if wordAddingThread.is_alive():
                    settings.levelprint("Skipping because adding previous words", 6)
                else:
                    wordAddingThread = AddWords(message)
                    wordAddingThread.start()
                
            #talking
            if settings.findValue("enableTalking")=="1" and (message.lower().find(call)>-1 or abs(time.perf_counter()-timeOfAuto) > autoCooldown and autoCooldown > 0):
                if (abs(time.perf_counter()-timeOfReply)>cooldown and approved) or abs(time.perf_counter()-timeOfReply)>longerCooldown:
                    if messageGenThread.is_alive():
                        settings.levelprint("Skipping because generating another message", 6)
                    else:
                        if message.lower().find(call)>-1:
                            timeOfReply = time.perf_counter()
                        else:
                            timeOfAuto = time.perf_counter()
                        messageGenThread = GenerateMessage(message)
                        message = ""
                        messageGenThread.start()
                    
    except socket.timeout:
        autoCooldown = int(settings.findValue("autoCooldown"))
        if settings.findValue("enableTalking")=="1" and abs(time.perf_counter()-timeOfAuto) > autoCooldown and autoCooldown > 0:
            if messageGenThread.is_alive():
                settings.levelprint("Skipping because generating another message", 6)
            else:
                timeOfAuto = time.perf_counter()-min(3, int(settings.findValue("autoCooldown"))-3)
                if message:
                    messageGenThread = GenerateMessage()
                    message = ""
                else:
                    messageGenThread = GenerateMessage()
                messageGenThread.start()
    except ConnectionResetError:
        s.shutdown(socket.SHUT_WR)
        s.close()
        settings.levelprint("Trying to reconnect", 0)
        connectToTwitch()
        settings.levelprint("Reconnected hopefully", 0)
