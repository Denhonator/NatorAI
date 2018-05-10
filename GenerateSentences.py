from random import randint
import re
import SettingsAndPreferences as settings

folder = settings.folder

def firstword(feed):
    f = open(folder+"/firstwords.txt", "r")
    lines = f.readlines()
    linenumber = 0
    total = 0
    selection = 0
    current = 0
    chosenword = None
    feedword = None
    foundselection = False
    for line in lines:
        (w, c) = line.split()
        if linenumber == 0:
            total = int(c)
            try:
                selection = randint(1,total)
            except ValueError:
                selection = 1
        else:
            current += int(c)
            if current >= selection and not foundselection:
                foundselection = True
                if not feed:
                    f.close()
                    return w
                else:
                    chosenword = w
            if w in feed:
                if len(feed)>1 and randint(1,100) < int(int(settings.findValue("FeedInFirstWord"))/len(feed)):
                    print("Feed word "+w+" used")
                    return w
                if len(feed)==1:
                    feedword = w
        linenumber += 1
    f.close()
    if feedword and randint(1,100) < int(settings.findValue("FeedInFirstWord")):
        print("Feed word "+w+" used")
        return feedword
    if chosenword:
        return chosenword
    return feedword

def nextword(word, feed, length=1):
    try:
        f = open(folder+"/words/"+word+".txt","r")
    except:
        return ""
    lines = f.readlines()
    linenumber = 0
    total = 0
    selection = 0
    current = 0
    occurances = 0
    chosenword = None
    feedword = None
    foundselection = False
    for line in lines:
        (w, c) = line.split()
        if linenumber == 0:
            occurances = int(c)
        if linenumber == 2:
            total = occurances-(int(c)-(int((int(c)*length*0.1)/int(settings.findValue("msgLengthModifier")))))
            current += int((int(c)*length*0.1)/int(settings.findValue("msgLengthModifier")))
            try:
                selection = randint(1,total)
            except ValueError:
                selection = 1
            if current >= selection:
                f.close()
                return ""
        if linenumber > 2:
            current += int(c)
            if current >= selection and not foundselection:
                foundselection = True
                if not feed:
                    f.close()
                    return w
                else:
                    chosenword = w
            if w in feed:
                if len(feed)>1 and randint(1,100) < int(int(settings.findValue("FeedInNextWord"))/len(feed)):
                    print("Feed word "+w+" used")
                    return w
                if len(feed)==1:
                    feedword = w
        linenumber += 1
    f.close()
    if current==0:
        print("No next words for "+word)
        return ""
    if feedword and randint(1,100) < int(settings.findValue("FeedInNextWord")):
        print("Feed word "+w+" used")
        return feedword
    if chosenword:
        return chosenword
    return ""

def findSentence(sentence):
    f = open(folder+"/sentences2.txt", "r")
    lines = f.readlines()
    total = 0
    linenumber = 0
    matches = []
    for line in lines:
        (w, c) = line.split(" -- ")
        if w.lower().strip().find(sentence.lower().strip())>-1:
            matches.append(linenumber)
        linenumber += 1
    if matches:
        return lines[matches[randint(0,len(matches)-1)]].split(" -- ")[0]
    return ""

def findThreeWords(sentence):
    f = open(folder+"/threewords.txt", "r")
    matches = []
    total = 0
    loop = 0
    for line in f.readlines():
        (w, c) = line.split(" -- ")
        if loop>0:
            threewords = w.split()
            words = list(reversed(sentence.split()))
            try:
                if words[0]==threewords[1] and words[1]==threewords[0] and sentence.find(w)==-1:
                    matches.append((threewords[2],int(c)))
                    total+=int(c)
            except IndexError:
                print("Index error from " + sentence + " at " + line.strip())
        loop+=1
    if matches:
        current = 0
        selection = randint(1,total)
        for w, c in matches:
            current+=c
            if current >= selection:
                return w
    return ""

def customFormatting(sentence):
    specialwords = []
    try:
        f = open(folder+"/definitions.txt", "r")
    except:
        print("Couldn't read definitions.txt")
        return sentence
    for line in f.readlines():
        try:
            specialwords.append(line.strip().split()[0])
        except IndexError:
            pass
    f.close()

    words = sentence.split()
    output = ""
    for word in words:
        for specialword in specialwords:
            if word.strip().lower()==specialword.strip().lower():
                word = specialword
        output += word + " "
    return output.strip()

def generateSentence(feed):
    currentword = firstword(feed)
    output = currentword
    words = 1
    endsentence = False
    while words < 100:
        if currentword in feed:
            feed.remove(currentword)
        if currentword != "":
            try:
                currentword = nextword(currentword, feed, len(output))
            except:
                currentword = ""
        if currentword == "" and words == 1:    #second attempt if at first word
            currentword = nextword(output, feed)
        if currentword == "" and len(output)<int(settings.findValue("maxContinuationLength")):
            r = randint(8*int(settings.findValue("msgContinuationModifier"))-(words*20),100)
            if r>60:
                try:
                    if r>92:
                        currentword = firstword("")
                    elif r>84:
                        f = open(folder+"/words/or.txt","r")
                        f.close()
                        currentword = "or"
                    elif r>76:
                        f = open(folder+"/words/and.txt","r")
                        f.close()
                        currentword = "and"
                    elif r>68:
                        f = open(folder+"/words/i.txt","r")
                        f.close()
                        currentword = "i"
                    elif r>60:
                        f = open(folder+"/words/but.txt","r")
                        f.close()
                        currentword = "but"
                    #print("Message Continuation")
                except:
                    print("or, and, i or but words missing")
        if currentword != "" and len(output)<int(settings.findValue("maxMessageLength")):
            words += 1
            output += " " + currentword
##            temp = findSentence(output) #chance to pull out a sentence
##            if temp != "" and (words > 2 or (randint(1,100)<int(settings.findValue("sentenceChance")) and words > 1)):
##                output = temp
##                try:
##                    currentword = re.sub('[^A-Za-z0-9]+', '', output.split()[-1].translate(str.maketrans('','','\',.-!')))
##                except IndexError:
##                    currentword = ""
##                    print("INDEX ERROR")
##                currentword = currentword.strip()
            addingThirdWords = True
            temp = findThreeWords(output)
            while len(output.split())>1 and temp!="" and addingThirdWords and len(output)<int(settings.findValue("maxMessageLength")):
                temp = findThreeWords(output)   #find word based on previous two words
                if temp!="":
                    output += " "+temp
                    #print("Added "+temp)
                    if "!" in temp or "?" in temp or "." in temp:
                        currentword = ""
                        #print("Ending sentence")
                        endsentence = True
                    elif randint(1,100)>int(settings.findValue("sentenceChance")):
                        addingThirdWords = False
                    else:
                        currentword = temp
            if not endsentence:
                try:
                    currentword = re.sub('[^A-Za-z0-9]+', '', output.split()[-1].translate(str.maketrans('','','\',.-!')))
                    currentword = currentword.strip()
                except IndexError:
                    currentword = ""
            
        else:
            return customFormatting(output.capitalize())
    print("Couldn't make a sentence, output was " + output)
    return ""
