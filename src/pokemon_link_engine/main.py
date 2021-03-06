import os; print(os.getcwd())
import time
from audio import dialogue_sys
from mechanics.load_userdata import User_Config     #gets the user info specific to the specific account/player
from utils.pygame_utils import *
from utils.system.sys_info import *
from utils.directories import get_project_dir, get_user_dir
from utils.json_utils import load_json
from graphics.maps.scripts.load_maps import is_at_gate, Map
from graphics.sprites.Sprites.Sprites import Window

#GLOBAL VARIABLES======================================================================================================#
game_dir = get_project_dir()
user = "loona"
user_home = get_user_dir(user, game_dir)
conf = User_Config(user)
current_map = Map("twinleaf")#; print(current_map)
pid = os.getpid() #gets the process id of main so we can monitor its resource usage (RAM, CPU usage etc)
Game_Running = True #so long as the application is running
Intro = False #the intro screen
Main_Menu = False #menu outside of the game. aka, choosing which save file, settings etc
In_Game = True #in the main game
Game_Menu = False #game menu if it will be fullscreen. not finalized
Dialogue = True
In_Battle = False #in battle


#FPS AND ANIMATIONS
prev_time = time.time() #for limiting fps. remove
counter_limit = int((FPS/1.875) / conf.base_speed) #how many frames an animation period is. based on the current fps and base_speed. debatable where this will be stored
conversation = load_json("./audio/conversation.json"); conversation = conversation["conversation"] #loads in the convo

#loads up a window=====================================================================================================#
window = create_window(sc_w, sc_h, resizable=True, icon="Dump stuff/server-icon.jpg", caption="Pokemon Link Engine")

text_x, text_y = 10,10 #make these diff depending on which text. each text will have locations to load em from a json config

#Main Game loop========================================================================================================#
frame_counter = 0 #keeps track of the frames. used for sprite animations
map_change_init = 0 #time when the map is changed. used for time delays between map changes.
prev = 0 #previous time. called when
while True:
    exit_conditions(conf.exit)
    now = time.time()  # sets the current time

    Window.draw_to_screen() #draws all sprite groups to the screen

    inputs = Window.get_inputs() #gets inputs
    x, y = inputs[0], inputs[1]

    conf.draw_hud = Window.toggle_hud() #hud

    new_map = is_at_gate(now, map_change_init) #checks if at gate
    #print(new_map)

    #if at a gate, it changes the map. also sets an init time
    if new_map is not None: print(new_map);current_map = new_map; map_change_init = time.time()

    dialogue_sys.show_lines() #draws dialogue

    Window.update_screen(x, y) #updates the screen

    dialogue_sys.clear_lines() #clears the dialogue

    #fps incrementer. this helps with things that arent meant to be updated every frame
    frame_counter+=1
    if frame_counter == 75: frame_counter=0
