SETUP:
- Install python 3.6.5+ if you don't have it yet
- Get your oauth token at https://twitchapps.com/tmi/ using the account the bot will use
- Launch TwitchConnect and change settings

MessagePrefix adds characters before the bot's messages. If the bot uses your personal
account (which is useful so the bot won't get kicked out or anything), this can be used to
make it clear when the bot is speaking and when it's actually you.

cooldown is the time that needs to pass in seconds between bot reply's 
for users in "approved users.txt"
longerCooldown is the cooldown for all other users
autoCooldown is the time it takes for the bot to generate a message regardless

call determines what chat users must type at the start of their message to make
the bot reply. Anything written after that is more likely to make an appaerance in the reply

enableLearning enables learning words from the chat that has been joined. 1 or 0.
enableTalking is the same, but for sending messages. When starting out, you should
set this to 0, as the program can crash if it tries to form sentences without knowing anything

Commands:
A commands are single words starting with '!', that will trigger specific responses.
Commands can be added and edited through the UI or chat.
In chat, a user with their name on "whitelist.txt" can edit commands.
!add !command=Response will add a new response to the command. when !command is called, a random
response will be chosen. This works whether the command already exists or not.
!edit !command=Response will set the command to only have the given response.
!del !command will remove the command entirely.

Multiple memories:
You can define a new folder for data in folder.txt, to use in a different channel for example.
Just edit folder.txt any time you want to switch between different folders.

Sub and follower interaction:
Requires you to create an app at https://dev.twitch.tv/ and take the client ID and head to
https://twitchapps.com/tokengen/ and add scopes 
channel_subscriptions channel_check_subscription channel_read
Then you have the client-id and oauth to access subs and followers
Add:
APIOauth youroauth
ClientID yourclientid

You can enable follow and sub replies by adding SubReply, ResubReply and FollowReply
For these you can also set the feed for the message generation that will follow with
SubFeed, ResubFeed and FollowFeed

You can also set:
FollowCheckCooldown timeinseconds

If you add:
FollowReply Thank you for the follow {}, 
The AI will send that message to new followers, {} being replaced with their name
You can also place a randomly generated message with (). You can give feedwords to it too.
Example for follow: FollowFeed why
The same applies to Subs and Resubs, but in ResubReply you can also add [], which will be replaced 
with the amount of sub months
