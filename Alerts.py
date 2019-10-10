import vlc
import time

player = vlc.MediaPlayer('C:/Users/Elmeri/Desktop/Untitled Project.mp4')

player.play()

time.sleep(0.1)

time.sleep(player.get_length()/1000)

player.set_position(0)
