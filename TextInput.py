import re
import string
import GenerateSentences  as speak
import SettingsAndPreferences as settings

folder = settings.folder

def addDefinition(specialword):
    found = False
    output = ""
    sorting = []
    try:
        f = open(folder+"/definitions.txt", "r")
    except:
        print("Created new definitions.txt")
        f = open(folder+"/definitions.txt", "w")
        f.write(specialword+" 1")
        f.close()
        f = open(folder+"/definitions.txt", "r")
    for line in f.readlines():
        sorting.append(line)
    sorting = sorted(sorting, key=lambda v: v.upper())  #alphabetical order
    for line in sorting:
        try:
            (w, c) = line.split()
        except:
            w = line.strip()
            c = 1
        if specialword.strip().lower()==w.strip().lower():
            found = True
            if specialword.strip() != w.strip():
                if int(c)-1>0:
                    output += w.strip()+" "+str(int(c)-1)   #start unlearning if different
            else:
                output += w.strip()+" "+str(int(c)+1)   #confirm what it knows
            output += "\n"
        elif line!="\n":
            output += line.strip()+"\n"
    f.close()
    if not found:
        output += specialword+" 1"
    f = open(folder+"/definitions.txt", "w")
    f.write(output.strip())
    f.close()
        
def findWords(words):
    final = []
    loop = 0
    commonchar = 0
    for word in words:
        delete = False
        word = word.strip()
        scan = re.sub('[^A-Za-z0-9]+', '¤', word.translate(str.maketrans('','','\',.-!')))
        if scan.find('¤') > -1:
            delete = True
        elif word.find('"')>-1:
            if not word.find('"',word.find('"'))>-1:
                delete = True
        if not delete and word.lower()!=settings.findValue("call").lower() and word.lower() not in settings.userlist("word ignore list.txt"):
            if word[0]!="!":
                final.append(word.lower())
            commonchar = 0
            searchloop = 0
            hasletter = False
            for c in word:
                if c.isalpha():
                    hasletter = True
                if c.isalpha() or c.isdigit():
                    if c!=c.lower() and (searchloop>0 or loop>0):
                        commonchar+=1
                    searchloop+=1
            if commonchar > 0 and (searchloop-commonchar>1 or len(word)<4):
                addDefinition(word)
            elif settings.findValue("AddAllToDefinitions")=="1" and loop>0 and hasletter:
                addDefinition(word)
            elif speak.customFormatting(word)!=word and loop>0:
                addDefinition(word)
        loop = loop+1
    return final

def firstwordlist(word):
    try:
        f = open(folder+"/firstwords.txt", "r")
    except IOError:
        f = open(folder+"/firstwords.txt", "w")
        f.write("TotalAmountOfFirstWords 0")
        f.close()
        f = open(folder+"/firstwords.txt", "r")

    lines = f.readlines()
    linenumber = 0
    output = ""
    foundEntry = False
    for line in lines:
        try:
            (w,c) = line.split()
            if linenumber == 0:
                output = w + " " + str(int(c)+1)
            elif w==word:
                output = output + w + " " + str(int(c)+1)
                foundEntry = True
            else:
                output = output + line.strip()
            output = output + "\n"
        except:
            pass
        linenumber = linenumber+1
    if not foundEntry:
        output = output + word + " 1"
    f.close()
    f = open(folder+"/firstwords.txt", "w")
    f.write(output)
    f.close()

def orgSentences(sentence):
    try:
        f = open(folder+"/sentences.txt", "r")
    except IOError:
        f = open(folder+"/sentences.txt", "w")
        f.write("TotalAmountOfSentences -- 0")
        f.close()
        f = open(folder+"/sentences.txt", "r")

    lines = f.readlines()
    linenumber = 0
    output = ""
    foundEntry = False
    for line in lines:
        try:
            (w,c) = line.split(" -- ")
            if linenumber == 0:
                output = w + " -- " + str(int(c)+1)
            elif w.strip()==sentence.strip():
                output = output + w + " -- " + str(int(c)+1)
                foundEntry = True
            else:
                output = output + line.strip()
            output = output + "\n"
        except:
            pass
        linenumber = linenumber+1
    if not foundEntry:
        output = output + sentence + " -- 1"
        
    f.close()
    f = open(folder+"/sentences.txt", "w")
    f.write(output)
    f.close()

def altSentences(message):
    try:
        f = open(folder+"/sentences2.txt", "r")
    except IOError:
        f = open(folder+"/sentences2.txt", "w")
        f.write("TotalAmountOfSentences -- 0")
        f.close()
        f = open(folder+"/sentences2.txt", "r")

    sentences = []
    sentences.append("")
    amessage = list(message)
    sentencenumber = 0
    for c in amessage:
        sentences[sentencenumber]+=c
        if c == ',' or c == '.' or c == '!' or c == '?':
            sentences[sentencenumber]=sentences[sentencenumber].strip()
            sentencenumber += 1
            sentences.append("")

    if sentences[-1] == '':
        sentences = sentences[:-1]
    else:
        sentences[-1] = sentences[-1].strip()
            
    linenumber = 0
    sentencenumber = 0
    output = ""
    for sentence in sentences:
        if sentence.strip().find(" ")>-1:
            lines = f.readlines()
            foundEntry = False
            for line in lines:
                try:
                    (w,c) = line.split(" -- ")
                    if linenumber==0:
                        output = w + " -- " + str(int(c)+1)
                    elif w.strip()==sentence.strip():
                        output = output + w + " -- " + str(int(c)+1)
                        foundEntry = True
                    else:
                        output = output + line.strip()
                    output = output + "\n"
                except:
                    pass
                linenumber = linenumber+1
            if not foundEntry:
                output = output + sentence + " -- 1"
            f.close()
            f = open(folder+"/sentences2.txt", "w")
            f.write(output)
            f.close()
            f = open(folder+"/sentences2.txt", "r")
            output = ""
            linenumber = 0
        sentencenumber = sentencenumber+1
    f.close()

def threewords(w1,w2,w3):
    filename = "threewords.txt"
    try:
        f = open(folder+"/"+filename, "r")
    except IOError:
        f = open(folder+"/"+filename, "w")
        f.write("TotalAmountOfThreeWords -- 0")
        f.close()
        f = open(folder+"/"+filename, "r")
    loop = 0
    output = ""
    entryFound = False
    for line in f.readlines():
        try:
            (w, c) = line.split(" -- ")
            if loop==0:
                output += "TotalAmountOfThreeWords -- "+str(int(c)+1)
            else:
                if w.strip()==w1+" "+w2+" "+w3:
                    output += "\n"+w+" -- "+str(int(c)+1)
                    entryFound = True
                else:
                    output += "\n"+line.strip()
        except:
            pass
        loop+=1
    if not entryFound:
        output += "\n"+w1+" "+w2+" "+w3+" -- 1"
    f = open(folder+"/"+filename, "w")
    f.write(output)
    f.close()

def sentencesToThreeWords():
    filename = "sentences2.txt"
    f = open(folder+"/"+filename, "r")
    for line in f.readlines():
        (s, c) = line.split(" -- ")
        words = s.split()
        if len(words)>2:
            loop=0
            for word in words:
                try:
                    if loop>0:
                        threewords(words[loop-1],word,words[loop+1])
                except:
                    pass
                loop+=1
    
def addWords(words):
    loop = 0
    lineWords = []
    isFirst = True
    occurances = 0
    firstword = 0
    lastWord = False
    output = ""
    nextWord = ""
    sentence = ""
    for word in words:
        if isFirst:
            firstwordlist(word)
        sentence = sentence.strip() + " " + word
        lastWord = False
        entryAdded = False
        occurances = 0
        firstword = 0
        if not word.endswith(".") and not word.endswith("!"):
            try:
                nextWord = words[loop+1]
                if not isFirst and loop>0:
                    try:
                        threewords(words[loop-1],word,words[loop+1])
                    except:
                        print("Invalid three words")
            except:
                nextWord = ""
                lastWord = True
                if sentence.strip().find(" ")>-1:
                    orgSentences(sentence)
                sentence = ""
        else:
            nextWord = ""
            lastWord = True
        try:
            file = open(folder+"/words/"+word+".txt", "r")
            lines = file.readlines()
            lineNumber = 0
            for line in lines:
                try:
                    lineWords = line.split()
                    if lineNumber == 0:
                        occurances = int(lineWords[1])+1    #Occurances
                    elif lineNumber == 1:
                        firstword = int(lineWords[1])       #Firstword count
                        if isFirst:
                            firstword = firstword + 1
                        output = "Occurances: " + str(occurances) + "\nFirstWord: " + str(firstword)
                    elif lineNumber == 2:                   #Lastword count
                        if lastWord:
                            output = output + "\nLastWord: " + str(int(lineWords[1])+1)
                        else:
                            output = output + "\nLastWord: " + lineWords[1]
                    elif lineNumber > 2:                    #Next words
                        if lineWords[0].strip()==nextWord:
                            output = output + "\n" + lineWords[0] + " " + str(int(lineWords[1])+1)
                            entryAdded = True
                        else:
                            output = output + "\n" + lineWords[0] + " " + lineWords[1]
                except IndexError:
                    pass           
                
                lineNumber = lineNumber+1
                
            if not nextWord == "" and not entryAdded:       #add next word entry if not found
                output = output + "\n" + nextWord + " 1"        
            file.close()

        except IOError:                                     #new file if not found
            #print(word + " does not exist, creating new")
            if isFirst:
                output = "Occurances: 1\nFirstWord: 1"
            else:
                output = "Occurances: 1\nFirstWord: 0"
            if lastWord:
                output = output + "\nLastWord: 1"
            else:
                output = output + "\nLastWord: 0"
            if not nextWord=="":
                output = output + "\n" + nextWord + " 1"
                
        file = open(folder+"/words/"+word+".txt", "w")
        file.write(output)
        file.close()
        loop = loop+1
        if word.endswith(".") or word.endswith("!") or word.endswith(","):
            isFirst = True
            if sentence.strip().find(" ")>-1:
                orgSentences(sentence)
            sentence = ""
        else:
            isFirst = False
