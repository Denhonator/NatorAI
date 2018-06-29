from random import randint
import re
import SettingsAndPreferences as settings
import TextInput

folder = settings.folder

def spamfilter(message):
    spamlimit=int(settings.findValue("SpamLimit"))
    prevword = ""
    spam=0
    filtered = ""
    reduced = False
    for word in message.strip().split():
        if word==prevword:
            spam+=1
        else:
            spam=0
        prevword = word
        if not spam>spamlimit:
            filtered+=word+" "
        else:
            reduced = True
    if reduced:
        settings.levelprint("Spam reduced", 2)
    return filtered.strip()

def entryfromlist(data, amount):
    selection = randint(1,amount)
    current=0
    for w, c in data:
        current+=c
        if current >= selection:
            return w

def word(data, feed, ignorelast=0):
    current = 0
    fromfeed = []
    feedwords = 0
    fromfeedsentence = []
    feedsentenceamount = 0
    feedsentencewords = []
    currentword = ""
    if "Occurances" in data.keys():
        pos = "NextWord"
        selection = randint(1,data["Occurances"])
        items = data.items()
    else:
        pos = "FirstWord"
        selection = randint(1,data["TotalFirstWords"])
        items = data["FirstWords"].items()
    if feed:
        for sentence, v in TextInput.data["Sentences"]:
            for word in sentence.lower().split():
                if word in feed:
                    for word in sentence.lower().split():
                        feedsentencewords.append(word)
                    break
                
    for w, c in items:
        if w!="Occurances":
            current+=c
            if current >= selection and not currentword:
                if w=="LastWord" and len(items)>2 and randint(1,100)<ignorelast:
                    selection = randint(current,data["Occurances"])
                else:
                    currentword = w
                    if not feed:
                        break
            if w in feed:
                fromfeed.append((w,c))
                feedwords+=c
            if w in feedsentencewords:
                fromfeedsentence.append((w,c))
                feedsentenceamount+=c
    if fromfeed and randint(1,100)<int(settings.findValue("FeedIn"+pos)):
        currentword = entryfromlist(fromfeed, feedwords)
        settings.levelprint(pos+" from feed", 2)
    elif fromfeedsentence and randint(1,100)<int(settings.findValue("FeedInNextWord")):
        currentword = entryfromlist(fromfeedsentence, feedsentenceamount)
        settings.levelprint(pos+" from sentence with feed", 2)
    return currentword

def thirdword(sentences, words, feed):
    entries = []
    total = 0
    length = len(words)
    words = words.split()[-2]+" "+words.split()[-1]      
    for s, c in sentences:
        if words in s:
            try:
                cont = s[s.find(words)+len(words):]
                if cont.strip().split()[0] in s.split():
                    for w in s.lower().split():
                        if w in feed:
                            c*=int(int(settings.findValue("FeedInNextWord"))*0.05)
                            settings.levelprint("Found sentence with feed words", 2)
                    entries.append((cont.strip().split()[0], c))
                    total+=c
            except IndexError:
                if randint(-70*int(settings.findValue("msgLengthModifier")),100)>((int(settings.findValue("maxMessageLength"))/2)-length):
                    entries.append(("LastWord", c))
                    total+=c
    if entries:
        return entryfromlist(entries, total)
    return ""

def capitalization(data, message):
    msg = message.capitalize().split()
    output = ""
    for word in msg:
        if (word.lower()==word or word==msg[0]) and not (data.get(word.lower(), (word, 1))[0].lower()==data.get(word.lower(), (word, 1))[0]):
            output+=data.get(word.lower(), (word, 1))[0]+" "
        else:
            output+=word+" "
    return output.strip()

def newGenerateSentence(feed=[]):
    settings.levelprint(feed, 2)
    data = TextInput.data
    currentword = word(data, feed)
    output = currentword+" "
    usedwords = []
    lengthmod = int(settings.findValue("msgLengthModifier"))
    sentchance = int(settings.findValue("sentenceChance"))
    contmax = int(settings.findValue("maxContinuationLength"))
    contmod = int(settings.findValue("msgContinuationModifier"))
    lengthmax = int(settings.findValue("maxMessageLength"))
    while(currentword and len(output)<lengthmax):
        if currentword.lower() in feed:
            feed.remove(currentword.lower())
            settings.levelprint(currentword+" from feed", 2)
        try:
            temp = ""
            if output.strip()!=currentword and randint(1,100) < sentchance:
                temp = thirdword(data["Sentences"], output.strip(), feed)
                if temp and temp not in usedwords:
                    if temp=="LastWord":
                        settings.levelprint("Third word was final", 2)
                        break
                    currentword = temp
                    if word(data["NextWords"][currentword.lower()], feed, lengthmod*20-len(output))=="LastWord":
                        if (lengthmax-5)-len(output)<randint(1,100):
                            output+=currentword
                            break
                    usedwords.append(currentword)
            if not temp or (temp and currentword!=temp):
                currentword = word(data["NextWords"][currentword.lower()], feed, lengthmod*20-len(output))
                if currentword=="LastWord" and len(output)<contmax:
                    r = randint(8*contmod-(len(output)*2),100)
                    if r>90:
                        currentword = word(data, feed)
                    elif r>80:
                        currentword = "and"
                    elif r>70:
                        currentword = "or"
                    elif r>60:
                        currentword = "but"
                if currentword=="LastWord":
                    break
            output+=currentword+" "
        except KeyError:
            settings.levelprint("Data not found for "+currentword, 0)
            break
    return spamfilter(capitalization(data["Definitions"], output))
