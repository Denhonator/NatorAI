import re
import string
import GenerateSentences  as speak
import SettingsAndPreferences as settings

folder = settings.folder
data = {"Sentences": [], "Definitions": {}}
progress = 0

def load():
    count = 0
    total = 0
    global progress
    try:
        f = open(folder+"/sentences2.txt", encoding='utf-8', mode='r')
        for line in f.readlines():
            try:
                (s, c) = line.split(" -- ")
                if s and s!="TotalAmountOfSentences":                   
                    for i in range(int(c)):
                        add(s)
                    count+=int(c)
                elif s:
                    total = int(c)
            except ValueError:
                pass
            if count and int(100*count/total)>progress:
                progress+=1
                print("Loading sentences2.txt... "+str(progress)+"%", end="\r")
    except IOError:
        settings.levelprint("Couldn't load "+folder+"/sentences2.txt", 0)
    data["TotalSentences"] = count
    #settings.levelprint("\nLearning from data...", 0)
    #firstwords(data["Sentences"])
    #nextwords(data["Sentences"])
    settings.levelprint("Loaded "+str(data.get("TotalSentences",0))+" entries to Sentences", 0)
    settings.levelprint("Creating backup", 0)
    if progress and progress<100:
        progress = 100
    save(".backup")

def add(sentence):
    #print(sentence)
    sentence = sentence.strip()
    if ignoresentence(sentence):
        return
    added = False
    sentences = []
    data["TotalSentences"]=data.get("TotalSentences",0)+1
    for s, c in data["Sentences"]:
        if sentence==s:
            c+=1
            added = True
        sentences.append((s,c))
    if not added:
        sentences.append((sentence, 1))
    data["Sentences"] = sentences
    firstwords([(sentence, 1)])
    nextwords([(sentence, 1)])

def ignoresentence(sentence):
    for word in settings.settings["word"] + settings.settings["call"]:
        if word.lower() in sentence.lower():
            settings.levelprint("Ignored sentence '"+sentence+"' due to ignored word", 4)
            return True
    if sentence[0]=="!" and len(sentence.split())==1:   #Ignore command usage
        settings.levelprint("Ignored learning message with command '"+sentence, 4)
        return True
    return False

def save(backup=""):
    if progress<100 or data["TotalSentences"]==0:
        print(str(progress)+", "+str(data["TotalSentences"]))
        settings.levelprint("Not ready to save",0)
        return
    f = open(folder+"/sentences2.txt"+backup, encoding='utf-8', mode='w')
    output="TotalAmountOfSentences -- "+str(data["TotalSentences"])+"\n"
    count = 0
    for s, c in data["Sentences"]:
        if s[-1]==",":
            output+=s+" "
        elif output[-1]==" ":
            output+=s+" -- 1\n"
            count+=1
        else:
            output+=s+" -- "+str(c)+"\n"
            count+=c
    f.write(output.strip())
    f.close()
    print("Saved "+str(count)+" sentences")

def firstwords(sentences):
    count = 0
    words = data.get("FirstWords",{})
    for s, c in sentences:
        w = s.split()[0].lower()
        words[w]=words.get(w,0)+c
        count+=c
    data["FirstWords"] = words
    data["TotalFirstWords"] = data.get("TotalFirstWords",0)+count
    settings.levelprint("Added "+str(count)+" entries to FirstWords", 4)

def definitions(word):
    if word!=word.lower() or word!=word.upper():
        data["Definitions"] = data.get("Definitions", {})
        (w, c) = data["Definitions"].get(word.lower(), (word, 0))
        if w!=word:
            if c>1:
                data["Definitions"][word.lower()] = (w, c-1)
            else:
                data["Definitions"][word.lower()] = (word, 1)
        else:
            data["Definitions"][word.lower()] = (w, c+1)
        
def nextwords(sentences):
    count = 0
    words = data.get("NextWords",{})
    for s, c in sentences:
        loop=0
        parts = s.strip().split()
        for wo in parts:
            w = wo.lower()
            if loop>0 or (loop==0 and wo.capitalize()!=wo):
                definitions(wo)
            words[w] = words.get(w,{})
            words[w]["Occurances"] = words[w].get("Occurances",0)+c
            words[w]["LastWord"] = words[w].get("LastWord",0)
            try:
                words[w][parts[loop+1].lower()] = words[w].get(parts[loop+1].lower(),0)+c
            except IndexError:
                words[w]["LastWord"] = words[w].get("LastWord",0)+c
            loop+=1
            count+=c
    data["NextWords"] = words
    settings.levelprint("Added "+str(count)+" entries to NextWords", 4)
