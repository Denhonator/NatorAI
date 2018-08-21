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
        settings.levelprint(folder+"sentencedata.p not found",0)
        data["Sentences"] = []
    save(".backup")
    try:
        with open(folder+'/pregen.p', 'rb') as fp:
            speak.pregen = pickle.load(fp)
        settings.levelprint("Loaded pregen",0)
    except FileNotFoundError:
        settings.levelprint("Couldn't load pregen from file",0)
    if "FirstWords" in data:
        Reconstruct()

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
    sentence = sentence.strip()
    if ignoresentence(sentence):
        return
    data["TotalSentences"]=data.get("TotalSentences",0)+count
    data["Sentences"].append(sentence)

def ignoresentence(sentence):
    for word in settings.settings["word"] + settings.settings["call"]:
        if word.lower() in sentence.lower():
            settings.levelprint("Ignored sentence '"+sentence+"' due to ignored word", 4)
            return True
    if sentence[0]=="!" and len(sentence.split())==1:   #Ignore command usage
        settings.levelprint("Ignored learning message with command '"+sentence, 4)
        return True
    return False

def Reconstruct():
    settings.levelprint("Reconstructing data...",0)
    global data
    sentences = []
    for s in data["Sentences"]:
        try:
            (s,c) = s
        except:
            pass
        if not ignoresentence(s):
            sentences.append(s)
    data = {}
    data["Sentences"] = sentences
    data["TotalSentences"] = len(sentences)
    speak.pregen = []
    settings.levelprint("Reconstructed!",0)

##def firstwords(sentences):
##    count = 0
##    words = data.get("FirstWords",{})
##    for s, c in sentences:
##        w = s.split()[0].lower()
##        words[w]=words.get(w,0)+c
##        count+=c
##    data["FirstWords"] = words
##    data["TotalFirstWords"] = data.get("TotalFirstWords",0)+count
##    settings.levelprint("Added "+str(count)+" entries to FirstWords", 4)
##
##def definitions(word):
##    if word!=word.lower() or word!=word.upper():
##        data["Definitions"] = data.get("Definitions", {})
##        (w, c) = data["Definitions"].get(word.lower(), (word, 0))
##        if w!=word:
##            if c>1:
##                data["Definitions"][word.lower()] = (w, c-1)
##            else:
##                data["Definitions"][word.lower()] = (word, 1)
##        else:
##            data["Definitions"][word.lower()] = (w, c+1)
##        
##def nextwords(sentences):
##    count = 0
##    words = data.get("NextWords",{})
##    for s, c in sentences:
##        loop=0
##        parts = s.strip().split()
##        for wo in parts:
##            w = wo.lower()
##            if loop>0 or (loop==0 and wo.capitalize()!=wo):
##                definitions(wo)
##            words[w] = words.get(w,{})
##            words[w]["Occurances"] = words[w].get("Occurances",0)+c
##            words[w]["LastWord"] = words[w].get("LastWord",0)
##            try:
##                words[w][parts[loop+1].lower()] = words[w].get(parts[loop+1].lower(),0)+c
##            except IndexError:
##                words[w]["LastWord"] = words[w].get("LastWord",0)+c
##            loop+=1
##            count+=c
##    data["NextWords"] = words
##    settings.levelprint("Added "+str(count)+" entries to NextWords", 4)
