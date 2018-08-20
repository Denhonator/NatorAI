from tkinter import *
from tkinter import scrolledtext
import os
import time
from threading import Thread
import SettingsAndPreferences as settings
import TextInput as AI

go = False

class getInput(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.save = True
        self.key = "MessagePrefix"
        self.index = 0
        self.description = {"word": "Word ignore list. The AI will not learn from messages with these words",
                            "approved": "Users who can use the base cooldown without being a subscriber",
                            "whitelist": "Users who are allowed to change commands via twitch chat",
                            "ignore": "The AI will not learn from these users",
                            "NICK": "Account nick for the bot",
                            "JOIN": "Channel to read messages from",
                            "SENDTO": "Channel to send messages to",
                            "oauth": "IRC oauth token for the bot's account",
                            "MessagePrefix": "Characters at the start of every message the bot sends",
                            "printLevel": "Add 0 for basic info, 1 for generated messages, 2 for its debug, 3 for learning info, 4 for its debug,"+
                            " 5 for UI debug, 6 for general debug. For example: 013 or 0123456",
                            "PregenAmount": "How many messages are pre-generated in memory at a time. Must be at least 100 to be active, recommended max 10000",
                            "PregenStartupSpeed": "Reduce startup CPU usage by lowering this value (1-100)",
                            "PregenRefreshSpeed": "Frequency at which oldest pre-generated message is removed and a new one is generated (1-100)",
                            "cooldown": "Bot call cooldown for subs and approved users",
                            "longerCooldown": "Bot call cooldown for other users",
                            "autoCooldown": "Time after which the bot will send a message on its own",
                            "commandCooldown": "Cooldown for using commands for all users",
                            "call": "Characters used to provoke a random message from the bot. Following words will be used as feed",
                            "enableLearning": "Allow the AI to learn from twitch chat (0,1)",
                            "enableTalking": "Allow the AI to generate and send messages to twitch chat (0,1)",
                            "autosave": "Enable autosave for AI and settings every time Twitch pings the bot (0,1)",
                            "APIOauth": "Twitch API oauth token, used for checking for follows. Connected to ClientID",
                            "ClientID": "ClientID from your created twitch app for the bot",
                            "FollowCheckCooldown": "How often in seconds followers will be checked",
                            "FollowReply": "What the bot will say when someone follows. {} will be replaced by the nick, () with a generated message",
                            "FollowFeed": "Feed that the AI will use for generating a random message in response to a follow",
                            "SubReply": "What the bot will say when someone subscribes. {} will be replaced by the nick, () with a generated message",
                            "SubFeed": "Feed that the AI will use for generating a random message in response to a subscription",
                            "ResubReply": "Same as SubReply, but for resubs. Additionally, [] will be replaced with sub months",
                            "ResubFeed": "Feed that the AI will use for generating a random message in response to a resub"}

    def run(self):
        self.window = Tk()
        self.window.title(settings.folder)
        self.window.geometry('640x420')
        
        def save():     
            AI.save()
            txt.insert(INSERT,'Saved AI!\n')
            txt.see("end")
            
        def saveset():
            if entry.get() and entry.get()!="-":
                settings.levelprint("Updating "+self.key+str(self.index)+" with "+entry.get(), 5)
                try:
                    settings.settings[self.key][self.index]=entry.get()
                except IndexError:
                    settings.settings[self.key].append(entry.get())
            settings.saveall()
            txt.insert(INSERT,'Saved settings!\n')
            txt.see("end")
            
        def nosave():
            self.save = False
            self.window.quit()

        def Reconstruct():
            AI.Reconstruct()
            
        def connect():
            global go
            if go:
                return
            go = True
            timeout = 0
            while go and timeout<2:
                time.sleep(0.1)
                timeout+=0.1
            if timeout<2:
                txt.insert(INSERT, "Connected!\n")
            else:
                txt.insert(INSERT, "Failed to connect\n")
            txt.see("end")

        def buildsets():
            self.entryamount=0
            first = False
            if not sets.size():
                first = True
            sets.delete(0,sets.size())
            for w in settings.settings.keys():  #sort commands to the end of the list
                if w[0]!="!":
                    sets.insert(self.entryamount, w)
                    self.entryamount+=1
            for w in settings.settings.keys():
                if w[0]=="!":
                    sets.insert(self.entryamount, w)
                    self.entryamount+=1
            index = 0
            if not first:
                index = max(self.entryamount-1,0)
                sets.see("end")
            sets.select_set(index)
            onselect(None, index)
                    
        def addentry():
            name = newentry.get()
            settings.settings[name] = ["EditMe"]
            sets.insert(self.entryamount, name)
            self.entryamount+=1
            sets.select_set(self.entryamount-1)
            onselect(None, self.entryamount-1)
            sets.see("end")
            
        def entriesupdate():
            entry.delete(0,len(entry.get()))
            entries.delete(0,entries.size()-1)
            if not settings.settings.get(self.key, None):
                return
            loop=0
            for e in settings.settings[self.key]:
                loop+=1
                entries.insert(loop, e)
            entries.insert(loop+1, "new")
            try:
                entry.insert(INSERT,settings.settings[self.key][self.index])
            except IndexError:
                entry.insert(INSERT,"-")

        def entryupdate():
            if entry.get() and entry.get()!="-":
                settings.levelprint("Updating "+self.key+str(self.index)+" with "+entry.get(), 5)
                try:
                    settings.settings[self.key][self.index]=entry.get()
                except IndexError:
                    settings.settings[self.key].append(entry.get())
            elif entry.get():
                settings.levelprint("Removing "+self.key+str(self.index), 5)
                try:
                    del settings.settings[self.key][self.index]
                    if not settings.settings[self.key]:
                        del settings.settings[self.key]
                        buildsets()
                except (IndexError, KeyError) as e:
                    settings.levelprint("Nothing to delete at this point", 5)
                    
        def onselect(evt, index=0):
            entryupdate()
            try:
                if not index:
                    index = sets.curselection()[0]
                self.key = sets.get(index)
                entriesupdate()
                message = self.description.get(self.key, "")
                if message:
                    txt.insert(INSERT, message+"\n\n")
                txt.see("end")
                entries.select_set(0)
            except IndexError:
                pass
                
        def subselect(evt):
            entryupdate()
            try:
                self.index = entries.curselection()[0]
                entriesupdate()
                entries.select_set(self.index)
            except IndexError as e:
                pass
            
        save = Button(self.window, text="Save AI", command=save, height=2, width=45)
        save.grid(column=0, row=2,sticky=N)
        saveset = Button(self.window, text="Save settings", command=saveset, height=2, width=45)
        saveset.grid(column=0, row=3,sticky=N)
        nosave = Button(self.window, text="Quit without saving", command=nosave, height=2, width=45)
        nosave.grid(column=0, row=6,sticky=N)
        savequit = Button(self.window, text="Save and quit", command=self.window.quit, height=2, width=45)
        savequit.grid(column=0, row=4,sticky=N)
        connect = Button(self.window, text="Connect", command=connect, height=2, width=45)
        connect.grid(column=0, row=1,sticky=N)
        reconstruct = Button(self.window, text="Reconstruct", command=Reconstruct, height=2, width=45)
        reconstruct.grid(column=0, row=5,sticky=N)
        txt = scrolledtext.ScrolledText(self.window,width=40,height=10)
        txt.grid(column=0,row=0,sticky=N)
        txt.insert(INSERT, "Change, add, remove settings/commands/values. Choose one from the left menu, then add a value to 0, "
                            "unless you want to have multiple values. Insert '-' to remove an entry. Only way to not save AI/settings "
                            "is to select 'Quit without saving'. If you want to change the AI folder, edit folder.txt and relaunch the program\n\n")
        entry = Entry(self.window)
        entry.grid(row=1,column=2)
        newentry = Entry(self.window)
        newentry.grid(row=6, column=1)
        add = Button(self.window, text="Add", command=addentry, height=1, width=5)
        add.grid(row=6, column=2, sticky=W)
        entries = Listbox(self.window,height=9)
        entries.bind('<<ListboxSelect>>',subselect)
        #entries.insert(0, "0")
        entries.grid(column=2,row=0)
        sets = Listbox(self.window,height=22)
        sets.bind('<<ListboxSelect>>', onselect)
        buildsets()
        sets.grid(column=1,row=0,rowspan=6)
        try:
            self.window.mainloop()
            if self.save:
                AI.save()
                settings.saveall()
            os._exit(1)
        except:
            print("UI crash, saving... program should still run")
            AI.save()
            settings.saveall()
