SETUP:
- Install python 3.6.5 if you don't have it yet
- Get your oauth token at https://twitchapps.com/tmi/ using the account the bot will use
- Open up "settings and commands.txt"
- All entries must be on different lines
- Don't change or remove the left word on any line except MessagePrefix if you want to remove that
- Add your account name to NICK
- Add the channels for reading (JOIN) and sending messages (SENDTO). Usually your own channel
- Add the oauth token

It should look something like this:
NICK denhonator
JOIN denhonator
SENDTO denhonator
oauth oauth:xxxxxxxxxxxxxxxx

TwitchConnect.py is the main file to launch, but hold on, check your settings

Then for the settings

MessagePrefix adds characters before the bot's messages. If the bot uses your personal
account (which is useful so the bot won't get kicked out or anything), this can be used to
make it clear when the bot is speaking and when it's actually you.

cooldown is the time that needs to pass in seconds between bot reply's 
for users in "approved users.txt"
longerCooldown is the cooldown for all other users
autoCooldown is the time it takes for the bot to generate a message regardless

call determines what chat users must type at the start of their message to make
the bot reply. Anything written after that is more likely to make an appaerance in the reply

FeedInFirstWord and FeedInNextWord are chances in percentage for something from the feed
to appear in the first word and the following words correspondingly. Good values are generally
between 50 and 100

msgLengthModifier affects how long the messages tend to be. 1 is a good value, but can be
increased slightly if longer replies are wanted

Once the reply length hits maxMessageLength, no more words will be added

msgContinuationModifier affects the chance to continue the reply even though a sentence
has been chosen to be finished. 4 seems good in my experience.
maxContinuationLength determines how long the message can be to use this forementioned
message continuation

sentenceChance is a percentage value for the chance to continue the two last words with some
known third word. This tends to generate fuller sentences, sometimes even repeating
what someone has at some point said. I recommend 70-100 for this

enableLearning enables learning words from the chat that has been joined. 1 or 0.
enableTalking is the same, but for sending messages. When starting out, you should
set this to 0, as the program can crash if it tries to form sentences without knowing anything

Commands:
In chat, a user with their name on "whitelist.txt" can add a command by typing
!command textYouWantAsAreplyWhenSomeoneTypesTheCommand
Then any user can type !command and get the same reply
Commands can be deleted by typing !command delete in chat, or by removing them
from "settings and commands.txt". You can also add commmands by typing them out there
the same way.

Emotes and other special capitalization:
The bot keeps track of special capitalization. Each time a word is typed differently than
what the bot currently knows, it will unlearn an entry. In the end, the most common
capitalization should be learned. These can manually be edited in "definitions.txt"

Multiple memories:
You can define a new folder for word data in folder.txt

Sub and follower interaction:
Requires you to create an app at https://dev.twitch.tv/ and take the client ID and head to
https://twitchapps.com/tokengen/ and add scopes 
channel_subscriptions channel_check_subscription channel_read
Then you have the client-id and oauth to access subs and followers
Add:
APIOauth youroauth
ClientID yourclientid

You can then enable features by adding
enableFollowCheck 1
enableSubCheck 1

By default this will update your "approved users.txt" with current subs

You can also set:
FollowCheckCooldown timeinseconds
SubCheckCooldown timeinseconds

If you add:
FollowReply Thank you for the follow {}, 
The AI will send that message to new followers, {} being replaced with their name
After that the AI will generate a message, for which you can give words as feed with:
FollowFeed why
The same apply to subs with SubReply and SubFeed
