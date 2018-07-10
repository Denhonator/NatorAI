from random import randint
import re
import SettingsAndPreferences as settings
import TextInput

folder = settings.folder

pregen = []

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

def word(data, feed, output):
    try:
        ignorelast=int(settings.findValue("msgLengthModifier"))*20-len(output)
        outputwords = output.lower().split()
    except:
        ignorelast=int(settings.findValue("msgLengthModifier"))*output
        outputwords = []
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
                #reroll chance
                if randint(1,100)<ignorelast and ((w=="LastWord" and len(items)>2) or (len(outputwords)>1 and w==outputwords[-1])):
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
    words = words.strip().lower()
    words = words.split()[-2]+" "+words.split()[-1]
    for s, c in sentences:
        if words in s.lower():
            try:
                cont = s[s.lower().find(words)+len(words):]
                if cont.lower().strip().split()[0] in s.lower().split():
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

def findPregen(feed):
    msgs = pregen
    matches = []
    total = 0
    for msg in msgs:
        match = 0
        for w in feed:
            if w.lower() in msg.lower().split():
                match+=max(20, match*20)
        if match:
            total+=match
            matches.append((msg, match))
    try:
        if(matches):
            return entryfromlist(matches, total)
        return msgs[randint(0,len(msgs)-1)]
    except Exception as e:
        print(e)
        return ""

def newGenerateSentence(feed=[]):
    if feed:
        settings.levelprint(feed, 1)
    data = TextInput.data
    currentword = word(data, feed, "")
    output = currentword+" "
    usedwords = []
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
                if temp and (temp not in usedwords or temp.lower()==output.lower().strip().split()[-1]):
                    if temp=="LastWord":
                        settings.levelprint("Third word was final", 2)
                        break
                    currentword = temp
                    #chance to end
                    if word(data["NextWords"][currentword.lower()], feed, len(output))=="LastWord":
                        if (lengthmax-5)-len(output)<randint(1,100):
                            output+=currentword
                            break
                    usedwords.append(currentword)
            if not temp or (temp and currentword!=temp):
                currentword = word(data["NextWords"][currentword.lower()], feed, output)
                #continuation
                if currentword=="LastWord" and len(output)<contmax:
                    r = randint(8*contmod-(len(output)*2),100)
                    if r>90:
                        currentword = word(data, feed, output)
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
