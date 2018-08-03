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

def findPregen(feed, sentence=False):
    if sentence:
        msgs = TextInput.data["Sentences"]
    else:
        msgs = pregen
    matches = []
    total = 0
    for msg in msgs:
        if sentence:
            msg = msg[0]
        match = 0
        for w in feed:
            if w.lower() in msg.lower().split():
                match+=max(50, match*50)
        if match:
            total+=match
            matches.append((msg, match))
    try:
        if(matches):
            return entryfromlist(matches, total)
        if sentence:
            return msgs[randint(0,len(msgs)-1)][0]
        return msgs[randint(0,len(msgs)-1)]
    except Exception as e:
        print(e)
        return ""

def newGenerateSentence(feed=[], pr=2):
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
            settings.levelprint(currentword+" from feed", pr)
        try:
            temp = ""
            if output.strip()!=currentword and randint(1,100) < sentchance:
                temp = thirdword(data["Sentences"], output.strip(), feed)
                if temp and (temp not in usedwords or temp.lower()==output.lower().strip().split()[-1]):
                    if temp=="LastWord":
                        settings.levelprint("Third word was final", pr)
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

if __name__ == "__main__":
    TextInput.load()

def ReplaceThird(s1,s2, threshold=2, skip=0, feed=[], pr=True):
    s1w = s1.lower().split()
    s2w = s2.lower().split()
    S1W = s1.split()
    S2W = s2.split()
    loop = 0
    found = False
    if feed:
        for w in feed:
            if w in s1w:
                found = True
                break
        if not found:
            return None
    for word in s1w:
        if loop<=skip:
            loop+=1
            continue
        if word in s2w:
            index1 = loop+1
            index2 = s2w.index(word)+1
            matches = 1
            while index1<len(s1w) and index2<len(s2w):
                if s1w[index1]==s2w[index2]:
                    matches+=1
                else:
                    if matches>=threshold:
                        if pr:
                            settings.levelprint("USED: "+s1,2)
                        S1W[index1]=S2W[index2]
                        SW = S1W[:index1]+S2W[index2:]
                        return " ".join(SW)
                    break
                index1+=1
                index2+=1
        loop+=1
    return None

def GenerateSentence(feed=[], pr=True):
    size = len(TextInput.data["Sentences"])-1
    loops = size
    output = ""
    r = 0
    if feed and not feed[0]:
        feed = []
    if feed:
        output = findPregen(feed, True)
    while len(output.split())<2:
        r = randint(0,size)
        output = TextInput.data["Sentences"][r][0]
    if pr:
        settings.levelprint("USED: "+output,2)
    current = r
    edits = 0
    loop = 0
    while edits<5 and loop < loops:
        current+=randint(1,10)
        if current>size:
            current-=size
        t = 2
        if loop>loops/2:
            t = 1
        temp = ReplaceThird(TextInput.data["Sentences"][current][0], output, t, edits, feed, pr)
        if temp:
            output = temp
            edits += 1
        loop += 1
    return output
