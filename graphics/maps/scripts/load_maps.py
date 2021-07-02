import json
import time
import os
from graphics.sprites.Sprites.Sprites import get_sprite_from_group

def load_map_data(map: str):
    """
    Takes in the map name, adds in " meta.json" and then returns all values we want
    :param map: the name of the map used
    :return: map data from the json

    The function allows one to enter multiple different values as map.
    Examples:
        load_map_data("twinleaf"):
        >>> map = "./graphics/maps/twinleaf meta.json"

        load_map_data("twinleaf meta"):
        >>> map = "./graphics/maps/twinleaf meta.json"

        load_map_data("twinleaf meta.json"):
        >>> map = "./graphics/maps/twinleaf meta.json"

    todo:
        rn allow it to squeeze in the addons in any order. also maybe allow it to load in maps from any dir?

    """
    path = "./graphics/maps/" #the parent folder

    if " meta" not in map: # adds in " meta" if not already in map
        map+= " meta"
    if ".json" not in map: # adds in ".json" if not already in map
        map +=".json"
    path+= map # adds on the parent directory
    with open(f"{path}", "r") as map_data: #opens the folder
        map_data=json.load(map_data)
    return map_data

def get_meta_files():
    """Searches for all json files in the /graphics/maps directory.

    when switching maps, we need to use their meta data files. these are all json files. this function looks through all
    files in the graphics/maps directory, takes the json files and returns them.

    Example:
        get_meta_files():
        >>> return ["map1 meta.json", "map2 meta.json", "map3 meta.json"]

    """
    path = os.getcwd()
    path+="/graphics/maps"
    path = os.listdir(path)
    meta_files = []
    for file in path:
        dot = file.rfind(".")
        ext = file[dot:]
        if ext == ".json":
            meta_files.append(file)
    return meta_files

def load_tiles(backdrop_coords, sprite_group,tiles = None, animated = False, is_player =False):
    """
    Function to load in instances of tiles from the metadata json.

    takes in the index of tiles of said type(npc, obstacle etc) and a
    sprite group, then, for every element in the index, set their coordinates
    relative to the backdrop location, their image and then adds them to
    the sprite group and an array containing all instances of said
    sprite group. depending on the value of animated, it will set the sprite as animated or static. False by default.
    returns the array

    The reason why this entire function is necessary is so that each map
    can have a dynamic amount of tiles and npc's etc

    Also allows creating an instance of the player. This is because the player is a tile in a group that is manipulated
    extensively, so being able to manipulate that groups is invaluable.
    Only difference is it draws a single sprite into player_group and draws it at the centre of the screen as an
    instance of Animated_Sprite().

    :param backdrop_coords: the coordinates of the backdrop. a tuple
    :param tiles: the index of tiles from the meta json
    :param sprite_group: the given spritegroup
    :param animated: determines if the created sprites will be animated or not
    :param is_player: determines if the sprite group consists of the player
    :return: tile_list, the list containing all instances

    Examples:
        >>> load_tiles((0,0), npc_group, NPCs, True)
        sets all npc's from the npc index in metadata, draws them relative to (0,0) adds them to the npc sprite group,
        and gives them animated sprites.

        >>> load_tiles((0,0), obstacle_group, obstacles, False)
        sets all obstacles from the obstacle index in metadata, main difference here is these are not animated

        >>> load_tiles((500,500),npc_group, NPCs, True)
        here, the backdrop is at (500,500), so draw all npc's with their coordinates relative to (500,500)

        >>> load_tiles((0,0), player_group, animated=True, is_player=True)
        creates an instance of the player that is drawn on the centre of the screen in player_group

    """
    from graphics.sprites.Sprites.Sprites import Animated_Sprite, Static_Sprite

    if is_player:
        from main import mid_x, mid_y
        new_tile = Animated_Sprite(mid_x, mid_y, "graphics/sprites/overworld/player movement.png")
        sprite_group.add(new_tile)
        return sprite_group

    for tile in tiles:
        tile_data = tiles[tile]
        # x and y coordinates of the sprite which is relative to the pos of backdrop
        x = tile_data["coords"]["x"]; x+= backdrop_coords[0]
        y = tile_data["coords"]["y"]; y+= backdrop_coords[1]

        image = tile_data["image"] #image path

        # if animated, creeate an animated sprite, if not a static sprite
        if animated:
            new_tile = Animated_Sprite(x,y,image)
        if not animated:
            new_tile = Static_Sprite(x,y,image)

        sprite_group.add(new_tile) #adds the new sprite to the group

    return sprite_group

def set_map(name):
    """
    Loads map metadata.

    Loads in the image, and gates and backdrop, npc_group, obstacle_group and other groups including the player_group
    put it all into an array, that is returned and each variable will be called upon.

    :param name: name of the map
    :return:

    todo:
        maybe include backdrop groups as load_tiles()???

    """
    from main import npc_group, obstacle_group, background_group, player_group
    from graphics.sprites.Sprites.Sprites import Static_Sprite, Animated_Sprite

    map_data = [] #array that we will return
    map = load_map_data(name)
    gate = map["gates"]["gate 1"]; map_data.append(gate)
    backdrop_x = gate["coords"]["x"] #coordinates of the backdrop
    backdrop_y = gate["coords"]["y"]

    backdrop = Static_Sprite(backdrop_x, backdrop_y, map["image"]); map_data.append(backdrop)
    background_group.add(backdrop)

    NPCs = map["NPC's"]
    npc_group = load_tiles((backdrop_x, backdrop_y), npc_group, NPCs, True); map_data.append(npc_group)
    obstacles = map["Obstacles"]
    obstacle_group = load_tiles((backdrop_x, backdrop_y), obstacle_group, obstacles); map_data.append(obstacle_group)

    player_group = load_tiles((0,0), player_group, animated=True, is_player=True)

    return map_data

def link_gates(id):
    """
    Links 2 gates by id's.

    Takes the id of the given gate and then looks through all meta files in the maps folder using get_meta_files()
    looks through all of them, looks through all their gates and looks in those gate id's for one that matches.
    it then pairs both gates together and loads in the new map from that gate.

    todo:
        this returns the name of the map, idk if it will load in the new map by the proper id. might need to return
        both id and map name and then load in according to both respectively.
    """
    from main import name #gets the name of the current map
    meta_files = get_meta_files() #loads in all the meta data files
    for file in meta_files:
        map = load_map_data(file)
        map_name = map["name"] #gets the name of the meta file we want. if its name = global map name, we skip it
        if name != map_name:
            gates = map["gates"]
            for gate in gates:
                gate = gates[gate]
                gate_id = gate["id"] #for all the gates in meta data, look for the one who's id = the id we want
                if gate_id == id: name = map_name; return map_name

def kill_group(group):
    """
    Kills a group.

    Loops through all sprites in a group and rmoves each instance.

    Examples:
        kill_group(npc_group)
        >>> npc_group("0 sprites")
    """
    for sprite in group:
        group.remove(sprite)

    return group

def return_gate_coords(pr, gr):
    """
    Returns the difference between the coordinates of 2 sprites.

    This is horrible. does not collide properly. work on improving this or rmove it for the other collison method.

    :param pr: player rect
    :param gr: gate rect
    :return: an array of the differences
    """
    return [(abs(pr.left-gr.right)),(abs(pr.right-gr.left)),(abs(pr.top-gr.bottom)),(abs(pr.bottom-gr.top))]

def is_at_gate(now, init):
    """
    Checks if the player is at a gate and loads in a new map at the corresponding gate.

    Checks if the player is at the given map. it will ignore if the player is currently standing still in said gate or
    if the player recently entered through the gates. once the player has entered the gate, it will kill all sprite
    instances in the given group using kill_group(sprite_group). then links the current gate with the corresponding gate
    using link_gates(id) and then use the returned map name to create the new map using set_map(name).

    Examples:
        is_at_gate(0,1000) //first time entering a gate
        loads in a new map

        is_at_gate(1000,1000) //runs when the player has just entered a gate
        ignores and returns None

        is_at_gate(1001, 1000) //after 1 second of previously entering a gate
        loads in a new map

    todo:
        make it check for all gates in gate group
        load maps based on id's. confirm this
    """

    from main import \
        (gayte, col_tol,background_group, obstacle_group, npc_group, gate_group, player_group, map,gate, name)

    player = get_sprite_from_group(player_group)
    print(player.last_posx, player.pos_x, player.last_posy, player.pos_y)

    if (player.last_posx == player.pos_x) and (player.last_posy == player.pos_y) or (now-init<1): return

    coords_diff = return_gate_coords(player.rect, gayte.rect)
    if (coords_diff[0] <=col_tol or coords_diff[1] <=col_tol) and (coords_diff[2]<=col_tol or coords_diff[3]<=col_tol):

        #kills all instances in all groups
        npc_group = kill_group(npc_group)
        obstacle_group = kill_group(obstacle_group)
        gate_group = kill_group(gate_group)
        player_group = kill_group(player_group)
        background_group = kill_group(background_group)

        #pairs the new maps by thei id's
        new_map = link_gates(gate["id"])

        #sets the name value to the new map name
        name = new_map
        #loads in the new map using that name
        map = set_map(new_map)
        return name #return the new name so we can switch again later
