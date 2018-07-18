import re
import string
import pickle
import GenerateSentences  as speak
import SettingsAndPreferences as settings

folder = settings.folder
data = {}
progress = 0

def load():
    global data
    data = {}
    try:
        with open(folder+'/sentencedata.p', 'rb') as fp:
            data = pickle.load(fp)
        global progress
        progress = 100
        settings.levelprint("Loaded data with "+str(data["TotalSentences"])+" messages",0)
    except FileNotFoundError:
        settings.levelprint("Loading from sentences2.txt instead",0)
        oldload()
    save(".backup")
    try:
        with open(folder+'/pregen.p', 'rb') as fp:
            speak.pregen = pickle.load(fp)
        settings.levelprint("Loaded pregen",0)
    except FileNotFoundError:
        settings.levelprint("Couldn't load pregen from file",0)

def oldload():
    data["Sentences"] = []
    data["Definitions"] = {}
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
    settings.levelprint("Loaded "+str(data.get("TotalSentences",0))+" entries to Sentences", 0)
    if progress and progress<100:
        progress = 100

def save(backup=""):
    if progress<100 or data["TotalSentences"]==0:
        print(str(progress)+", "+str(data["TotalSentences"]))
        settings.levelprint("Not ready to save",0)
        return
    with open(folder+'/sentencedata.p'+backup, 'wb') as fp:
        pickle.dump(data, fp, protocol=pickle.HIGHEST_PROTOCOL)
        settings.levelprint("Saved data to sentencedata.p"+backup,0)
    if speak.pregen:
        with open(folder+'/pregen.p','wb') as fp:
            pickle.dump(speak.pregen, fp, protocol=pickle.HIGHEST_PROTOCOL)
            settings.levelprint("Saved pregen",0)

def add(sentence, count=1):
    #print(sentence)
    sentence = sentence.strip()
    if ignoresentence(sentence):
        return
    added = False
    sentences = []
    data["TotalSentences"]=data.get("TotalSentences",0)+count
    for s, c in data["Sentences"]:
        if sentence==s:
            c+=1
            added = True
        sentences.append((s,c))
    if not added:
        sentences.append((sentence, count))
    data["Sentences"] = sentences
    firstwords([(sentence, count)])
    nextwords([(sentence, count)])

def ignoresentence(sentence):
    for word in settings.settings["word"] + settings.settings["call"]:
        if word.lower() in sentence.lower():
            settings.levelprint("Ignored sentence '"+sentence+"' due to ignored word", 4)
            return True
    if sentence[0]=="!" and len(sentence.split())==1:   #Ignore command usage
        settings.levelprint("Ignored learning message with command '"+sentence, 4)
        return True
    return False

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
