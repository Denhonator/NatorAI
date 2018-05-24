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

def findValue(setting, value=None):
    try:
        f = open(folder+"/settings and commands.txt", "r")
    except:
        f = open(folder+"/settings and commands.txt", "w")
        f.close()
        f = open(folder+"/settings and commands.txt", "r")
        
    output = ""
    entries = []
    for line in f.readlines():
        (w, s) = line.split(" ", 1)
        if w.lower().strip()==setting.lower().strip():
            entries.append(s.strip())
            if value:
                s = str(value)
                output += w+" "+s+"\n" 
        elif value:
            output += line.strip()+"\n"
    if not entries and value:
        output += setting+" "+str(value)
    output = output.strip()
    f.close()
    if value:
        f = open(folder+"/settings and commands.txt", "w")
        f.write(output)
        f.close()
    if not value:
        if entries:
            return entries[random.randint(0,len(entries)-1)].strip()
        else:
            print("Add definition for "+setting+" in 'settings and commands.txt'")
            print("Returning 30 instead (this keeps optional features disabled)")
            return "30"
    return value

def userlist(filename, add=None):
    try:
        f = open(folder+"/"+filename, "r")
    except:
        f = open(folder+"/"+filename, "w")
        f.write(add.strip())
        f.close()
        return [add]
    listOfNicks = []
    try:
        for line in f.readlines():
            listOfNicks.append(line.strip().lower())
        f.close()
        if add and add not in listOfNicks:
            listOfNicks.append(add.strip().lower())
            f = open(folder+"/"+filename, "a")
            f.write("\n"+add)
    except:
        print("Couldn't read "+filename)
    return listOfNicks

def commandList(add=None, reply=None):
    filename = "settings and commands.txt"
    try:
        f = open(folder+"/"+filename, "r")
    except:
        f = open(folder+"/"+filename, "w")
        f.close()
        f = open(folder+"/"+filename, "r")
    output = ""
    entries = []
    for line in f.readlines():
        (c, r) = (line[:line.find(" ")],line[line.find(" ")+1:])
        if c.strip().lower()==add.strip().lower():
            entries.append(r)
            if reply and reply!="delete":
                output += c+" "+reply+"\n"
        else:
            output += line
    f.close()
    if entries and not reply:
        return entries[random.randint(0,len(entries)-1)].strip()
    if not entries and reply and reply!="delete":
        output = output.strip()
        output += "\n"+add+" "+reply
    if reply:
        f = open(folder+"/"+filename, "w")
        f.write(output.strip())
    return reply
