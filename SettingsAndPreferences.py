import random
try:
    f = open("folder.txt", "r")
    folder = f.readlines()[0].strip()
    print("Using folder "+folder)
except IOError as e:
    print("Couldn't read folder name from folder.txt")
    print("Folder name should be on first line of folder.txt")
    print("And all other files than that and .py files should be under the folder")
    raise e

settings = {}
use = ["NICK",
    "JOIN",
    "SENDTO",
    "oauth",
    "MessagePrefix",
    "cooldown",
    "longerCooldown",
    "autoCooldown",
    "commandCooldown",
    "call",
    "printLevel",
    "NewGeneration",
    "lengthMod",
    "MaxEdits",
    "EditLoopRepetition",
    "PregenAmount",
    "PregenStartupSpeed",
    "PregenRefreshSpeed",
    "enableLearning",
    "enableTalking",
    "autosave",
    "APIOauth",
    "ClientID",
    "UserID",
    "FollowCheckCooldown",
    "FollowReply",
    "SubReply",
    "ResubReply",
    "SubgiftReply"]

def load(file):
    try:
        f = open(folder+"/"+file, encoding='utf-8', mode='r')
        for line in f.readlines():
            try:
                (w, s) = line.split(" ", 1)
                s=s.strip()
                if file!="settings and commands.txt" or w in use or w[0]=="!":
                    try:
                        settings[w].append(s)
                    except KeyError:
                        settings[w]=[s]
                else:
                    print("\""+line.strip()+"\" wasn't recognized as a valid setting or command")
            except ValueError:
                if line.strip():
                    try:
                        settings[file.split()[0].replace(".txt","")].append(line.strip())
                    except KeyError:
                        settings[file.split()[0].replace(".txt","")]=[line.strip()]
        f.close()
        print("Loaded "+file)
    except IOError:
        print(folder+"/"+file+" does not exist")

def loadall():
    settings["approved"] = []
    load("approved users.txt")
    
    settings["ignore"] = []
    load("ignore list.txt")
    
    settings["whitelist"] = []
    load("whitelist.txt")
    
    settings["word"] = []
    load("word ignore list.txt")
    
    load("settings and commands.txt")

loadall()

def save(file):
    key = file.split()[0].replace(".txt","")
    output=""
    try:
        if "settings" in file:
            for (w, s) in settings.items():
                if w != "word" and w != "whitelist" and w != "ignore" and w != "approved":
                    for e in s:
                        output+=w+" "+e+"\n"
        else:
            for v in settings.get(key, []):
                output+=v+"\n"
    except KeyError:
        print("Key error with "+file)
    f = open(folder+"/"+file, encoding='utf-8', mode='w')
    f.write(output.strip())
    f.close()
    print("Saved to "+file)

def saveall():
    save("approved users.txt")
    save("ignore list.txt")
    save("settings and commands.txt")
    save("whitelist.txt")
    save("word ignore list.txt")

def findValue(setting, value=None, replace=False):
    key = setting.split()[0]
    global settings
    if value:
        if settings.get(key, None) and not replace:
            settings[key].append(value)
        else:
            settings[key]=[value]
        return value
    elif replace and key in settings:
        del settings[key]
        return "Removed command "+key
    try:
        return settings[key][random.randint(0,len(settings[key])-1)]
    except KeyError:
        if setting[0]!="!":
            print("Couldn't find value for "+key+", returning 30 instead and saving it")
            print("This keeps toggleable features off")
            settings[key]=["30"]
        return "30"

def userlist(filename, add=None):
    key = filename.split()[0].replace(".txt","")
    try:
        return [name.lower() for name in settings[key]]
    except KeyError:
        return []

def levelprint(text, level):
    try:
        if str(level) in findValue("printLevel"):
            print(text)
    except Exception as e:
        for c in text:
            try:
                print(c, end='')
            except:
                print("?", end='')

for s in use:
    findValue(s)
