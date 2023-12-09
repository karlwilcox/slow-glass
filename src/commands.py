# standard libraries
from abc import abstractmethod
import os, re

import pygame.mixer

import params, images, sprites, timing
from defaults import *


class Command:
    globalData = None

    def __init__(self):
        self.format = None
        self.scene = None
        self.keywords = []
        self.params = None
        self.help = "(No help provided)"

    def invoked(self, words):
        words = re.split(WORD_SPLIT, words)
        self.params = params.ParamList(words, self.format)
        return self.params.valid

    def process(self, this_scene):
        self.scene = this_scene
        result = self.do_process()
        if result is None:
            return False
        else:
            return result

    @abstractmethod
    def do_process(self):
        pass

# TODO implement read file (add scene items on demand, like include but triggered)

# TODO implement fade command for transparency

# TODO how to change center of rotation? (Not urgent)
# *************************************************************************************************
#
#    ########  ######  ##     ##  #######
#    ##       ##    ## ##     ## ##     ##
#    ##       ##       ##     ## ##     ##
#    ######   ##       ######### ##     ##
#    ##       ##       ##     ## ##     ##
#    ##       ##    ## ##     ## ##     ##
#    ########  ######  ##     ##  #######
#
# **************************************************************************************************


class EchoCommand(Command):

    def __init__(self):
        super().__init__()
        self.format = "|/echo|say|print : */rest"
        self.help = "echo [args...]"

    def do_process(self):
        print(self.params.get("rest"))

# *************************************************************************************************
#
#    ######## ########   #######  ##     ##
#    ##       ##     ## ##     ## ###   ###
#    ##       ##     ## ##     ## #### ####
#    ######   ########  ##     ## ## ### ##
#    ##       ##   ##   ##     ## ##     ##
#    ##       ##    ##  ##     ## ##     ##
#    ##       ##     ##  #######  ##     ##
#
# **************************************************************************************************


class FromCommand(Command):

    def __init__(self):
        super().__init__()
        self.format = "|/from|using|with : */rest"
        self.help = "from folder"

    def do_process(self):
        self.scene.from_folder = self.params.get('rest')

# *************************************************************************************************
#
# *************************************************************************************************
#
#    ##        #######     ###    ########
#    ##       ##     ##   ## ##   ##     ##
#    ##       ##     ##  ##   ##  ##     ##
#    ##       ##     ## ##     ## ##     ##
#    ##       ##     ## ######### ##     ##
#    ##       ##     ## ##     ## ##     ##
#    ########  #######  ##     ## ########
#
# **************************************************************************************************


class LoadCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "load filename [as] [tag] (loads resource, basename as tag if not given)"
        self.format = "|/load|upload : +/filename ~/as ?/tag ~/split ?/cols ?/by ?/rows"

    def do_process(self):
        filename = os.path.join(self.scene.folder, self.scene.from_folder, self.params.get("filename"))
        if not os.path.exists(filename):
            print("Resource file not found: %s" % filename)
            return True
        tag = self.scene.make_tag(self.params.get("tag"))
        if filename.lower().endswith((".jpg", ".jpeg", "png", "gif")):
            rows = self.params.as_int("rows")
            cols = self.params.as_int("cols")
            Command.globalData.images[tag] = images.ImageItem(filename, rows, cols)
        elif filename.lower().endswith((".wav", ".ogg")):
            Command.globalData.sounds[tag] = pygame.mixer.Sound(filename)
            Command.globalData.sounds[tag].set_volume(0.5)
        else:
            print("Unrecognised resource file type: %s" % filename)
        return True  # Only run this command once


# *************************************************************************************************
#
#    ##     ## ##    ## ##        #######     ###    ########
#    ##     ## ###   ## ##       ##     ##   ## ##   ##     ##
#    ##     ## ####  ## ##       ##     ##  ##   ##  ##     ##
#    ##     ## ## ## ## ##       ##     ## ##     ## ##     ##
#    ##     ## ##  #### ##       ##     ## ######### ##     ##
#    ##     ## ##   ### ##       ##     ## ##     ## ##     ##
#     #######  ##    ## ########  #######  ##     ## ########
#
# **************************************************************************************************


class UnloadCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "unload tag... (unloads resources)"
        self.format = "|/unload|purge : >/tags"

    def do_process(self):
        for tag in self.params.get("tags"):
            i_tag = self.scene.resolve_tag(tag, Command.globalData.images.keys())
            for key in Command.globalData.images.keys():
                if key == i_tag:
                    del Command.globalData.images[i_tag]
            s_tag = self.scene.resolve_tag(tag, Command.globalData.images.keys())
            for key in Command.globalData.sounds.keys():
                if key == s_tag:
                    del Command.globalData.sounds[s_tag]
        return True  # Only run this command once


# *************************************************************************************************
#
#    ########  ##          ###    ##    ##
#    ##     ## ##         ## ##    ##  ##
#    ##     ## ##        ##   ##    ####
#    ########  ##       ##     ##    ##
#    ##        ##       #########    ##
#    ##        ##       ##     ##    ##
#    ##        ######## ##     ##    ##
#
# **************************************************************************************************


class PlayCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "play sound"
        self.format = "=/play : >/tags"

    def do_process(self):
        for tag in self.params.get("tags"):
            r_tag = self.scene.resolve_tag(tag, Command.globalData.sounds.keys())
            if r_tag is None:
                continue
            for s_tag in Command.globalData.sounds.keys():
                if r_tag == s_tag:
                    Command.globalData.sounds[r_tag].play()
        return True

# *************************************************************************************************
#
#    ##     ##  #######  ##       ##     ## ##     ## ########
#    ##     ## ##     ## ##       ##     ## ###   ### ##
#    ##     ## ##     ## ##       ##     ## #### #### ##
#    ##     ## ##     ## ##       ##     ## ## ### ## ######
#     ##   ##  ##     ## ##       ##     ## ##     ## ##
#      ## ##   ##     ## ##       ##     ## ##     ## ##
#       ###     #######  ########  #######  ##     ## ########
#
# **************************************************************************************************


class VolumeCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "[set] volume [of] tag [to] 0-100"
        self.format = "~/set |/volume|vol : ~/of +/tag ~/to +/value"

    def do_process(self):
        tag = self.params.get("tag")
        r_tag = self.scene.resolve_tag(tag, Command.globalData.sounds.keys())
        if r_tag is None:
            return True
        volume = self.params.as_int("value") / 100
        for s_tag in Command.globalData.sounds.keys():
            if r_tag == s_tag:
                Command.globalData.sounds[r_tag].set_volume(volume)
                break
        return True

# *************************************************************************************************
#
#    ########  ##          ###     ######  ########
#    ##     ## ##         ## ##   ##    ## ##
#    ##     ## ##        ##   ##  ##       ##
#    ########  ##       ##     ## ##       ######
#    ##        ##       ######### ##       ##
#    ##        ##       ##     ## ##    ## ##
#    ##        ######## ##     ##  ######  ########
#
# **************************************************************************************************
# TODO implement remove/delete as opposite of place (deletes sprite from active list)


class PlaceCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "place image [as sprite] [at] x,y,z [size w,h] (adds to active list but DOES not show sprite)"
        self.format = "|/place|put : +/itag ~/as &/stag ~/at +/x +/y ~/depth +/z ~/size ?/w ?/h"

    def do_process(self):
        # TODO Implement sprite depth and the raise/lower commands
        itag = self.params.get("itag")
        stag = self.params.get("stag")
        if stag is None:
            stag = itag
        stag = self.scene.make_tag(stag)
        itag = self.scene.resolve_tag(itag, Command.globalData.images.keys())
        if itag is None:
            return True
        Command.globalData.sprites[stag] = sprites.SpriteItem(itag, self.scene,
                                                              self.params.as_float("x", "number for x coord"),
                                                              self.params.as_float("y", "number for y coord"),
                                                              self.params.as_float("w"),
                                                              self.params.as_float("h"))


# *************************************************************************************************
#
#    ##     ##  #######  ##     ## ########
#    ###   ### ##     ## ##     ## ##
#    #### #### ##     ## ##     ## ##
#    ## ### ## ##     ## ##     ## ######
#    ##     ## ##     ##  ##   ##  ##
#    ##     ## ##     ##   ## ##   ##
#    ##     ##  #######     ###    ########
#
# **************************************************************************************************


class MoveCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "move tag [to] x,y [in] [time] (moves sprite to new position, whether hidden or visible)"
        self.format = "=/move : +/tag ~/to +/x +/y ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        x = self.params.as_float("x", "new x coord")
        y = self.params.as_float("y", "new y coord")
        rate = timing.Duration(self.params.get("time")).as_seconds()
        Command.globalData.sprites[tag].move(x, y, rate)

# *************************************************************************************************
#
#    ########  ########  ######  #### ######## ########
#    ##     ## ##       ##    ##  ##       ##  ##
#    ##     ## ##       ##        ##      ##   ##
#    ########  ######    ######   ##     ##    ######
#    ##   ##   ##             ##  ##    ##     ##
#    ##    ##  ##       ##    ##  ##   ##      ##
#    ##     ## ########  ######  #### ######## ########
#
# **************************************************************************************************


class ResizeCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "resize tag [to] x,y [in] [time] (moves sprite to new position, whether hidden or visible)"
        self.format = "|/size|resize : +/tag ~/to +/width +/height ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        width = self.params.as_float("width", "new width")
        height = self.params.as_float("height", "new height")
        rate = timing.Duration(self.params.get("time")).as_seconds()
        Command.globalData.sprites[tag].resize(width, height, rate)

# *************************************************************************************************
#
#     ######   ######     ###    ##       ########
#    ##    ## ##    ##   ## ##   ##       ##
#    ##       ##        ##   ##  ##       ##
#     ######  ##       ##     ## ##       ######
#          ## ##       ######### ##       ##
#    ##    ## ##    ## ##     ## ##       ##
#     ######   ######  ##     ## ######## ########
#
# **************************************************************************************************


class ScaleCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "scale tag [by] x,y [in] [time] (moves sprite to new position, whether hidden or visible)"
        self.format = "|/scale|rescale : +/tag ~/by +/xpct #/ypct ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        width_scale = self.params.as_float("xpct", "Percentage to change")
        height_scale = self.params.as_float("ypct")
        if height_scale is None:
            height_scale = width_scale
        rate = timing.Duration(self.params.get("time")).as_seconds()
        Command.globalData.sprites[tag].scale(width_scale, height_scale, rate)

# *************************************************************************************************
#
#    ########   #######  ########    ###    ######## ########
#    ##     ## ##     ##    ##      ## ##      ##    ##
#    ##     ## ##     ##    ##     ##   ##     ##    ##
#    ########  ##     ##    ##    ##     ##    ##    ######
#    ##   ##   ##     ##    ##    #########    ##    ##
#    ##    ##  ##     ##    ##    ##     ##    ##    ##
#    ##     ##  #######     ##    ##     ##    ##    ########
#
# **************************************************************************************************


class RotateCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "rotate tag [to] degrees [in] [time] (rotates sprite to new position, whether hidden or visible)"
        self.format = "|/rotate|turn : +/tag |/to|by #/degrees ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        rotation = self.params.as_float("degrees", "Degrees to turn by/to")
        to_by = self.params.get("to").lower()
        rate = timing.Duration(self.params.get("time")).as_seconds()
        if to_by == "to":
            Command.globalData.sprites[tag].turn_to(rotation, rate)
        else:
            Command.globalData.sprites[tag].turn_by(rotation, rate)


# *************************************************************************************************
#
#     ######  ########    ###    ########  ########       ##  ######  ########  #######  ########
#    ##    ##    ##      ## ##   ##     ##    ##         ##  ##    ##    ##    ##     ## ##     ##
#    ##          ##     ##   ##  ##     ##    ##        ##   ##          ##    ##     ## ##     ##
#     ######     ##    ##     ## ########     ##       ##     ######     ##    ##     ## ########
#          ##    ##    ######### ##   ##      ##      ##           ##    ##    ##     ## ##
#    ##    ##    ##    ##     ## ##    ##     ##     ##      ##    ##    ##    ##     ## ##
#     ######     ##    ##     ## ##     ##    ##    ##        ######     ##     #######  ##
#
# **************************************************************************************************


class StartCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "start scene... (start running a named scene)"
        self.format = "|/start|run : >/list"

    def do_process(self):
        for scene_name in self.params.get("list"):
            for scene_key in Command.globalData.scenes.keys():
                if scene_key == scene_name:
                    Command.globalData.scenes[scene_name].start()
                    break


class StopCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "stop scene... (stop running named scene, or the current scene if not given & removes all sprites " \
                    "from active list)"
        self.format = "|/stop|disable : >/list"

    def do_process(self):
        for scene_name in self.params.get("list"):
            for scene_key in Command.globalData.scenes.keys():
                if scene_key == scene_name:
                    Command.globalData.scenes[scene_name].stop()
                    break


# *************************************************************************************************
#
#     ######  ##     ##  #######  ##      ##       ## ##     ## #### ########  ########
#    ##    ## ##     ## ##     ## ##  ##  ##      ##  ##     ##  ##  ##     ## ##
#    ##       ##     ## ##     ## ##  ##  ##     ##   ##     ##  ##  ##     ## ##
#     ######  ######### ##     ## ##  ##  ##    ##    #########  ##  ##     ## ######
#          ## ##     ## ##     ## ##  ##  ##   ##     ##     ##  ##  ##     ## ##
#    ##    ## ##     ## ##     ## ##  ##  ##  ##      ##     ##  ##  ##     ## ##
#     ######  ##     ##  #######   ###  ###  ##       ##     ## #### ########  ########
#
# **************************************************************************************************

class HideCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "hide sprites... (hides sprite, but still active and updating)"
        self.format = "=/hide : >/list"

    def do_process(self):
        tag_list = self.params.get("list")
        for tag in tag_list:
            s_tag = self.scene.resolve_tag(tag, Command.globalData.sprites.keys())
            if s_tag is not None:
                Command.globalData.sprites[s_tag].visible = False


class ShowCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "show sprites... (reveals sprites in active list) / "
        self.format = "|/show|reveal : >/list"

    def do_process(self):
        tag_list = self.params.get("list")
        for tag in tag_list:
            s_tag = self.scene.resolve_tag(tag, Command.globalData.sprites.keys())
            if s_tag is not None:
                Command.globalData.sprites[s_tag].visible = True

# *************************************************************************************************
#
#    ##     ##    ###    ##    ## ########       ## ##       ######## ########       ## ########  ##     ## ########
#    ###   ###   ## ##   ##   ##  ##            ##  ##       ##          ##         ##  ##     ## ##     ##    ##
#    #### ####  ##   ##  ##  ##   ##           ##   ##       ##          ##        ##   ##     ## ##     ##    ##
#    ## ### ## ##     ## #####    ######      ##    ##       ######      ##       ##    ########  ##     ##    ##
#    ##     ## ######### ##  ##   ##         ##     ##       ##          ##      ##     ##        ##     ##    ##
#    ##     ## ##     ## ##   ##  ##        ##      ##       ##          ##     ##      ##        ##     ##    ##
#    ##     ## ##     ## ##    ## ######## ##       ######## ########    ##    ##       ##         #######     ##
#
# **************************************************************************************************


class MakeCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "make name [be] value (can be accessed as $name in other commands)"
        self.format = "|/make|let|put : +/name ~/be ~/as */rest"

    def do_process(self):
        name = self.params.get("name")
        content = self.params.get("rest")
        # check for writable built-ins first
        # none at present
        Command.globalData.vars.set_var(name, content, self.scene.name)


# *************************************************************************************************
#
#    ########  ##     ## ##     ## ########
#    ##     ## ##     ## ###   ### ##     ##
#    ##     ## ##     ## #### #### ##     ##
#    ##     ## ##     ## ## ### ## ########
#    ##     ## ##     ## ##     ## ##
#    ##     ## ##     ## ##     ## ##
#    ########   #######  ##     ## ##
#
# **************************************************************************************************


class DumpCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "dump vars|scenes|sprites"
        self.format = "=/dump : >/list"

    def do_process(self):
        dump_list = self.params.get("list")
        for dump in dump_list:
            if dump.startswith("var"):
                Command.globalData.vars.dump()
            elif dump.startswith("scene"):
                for key, value in Command.globalData.scenes.items():
                    Command.globalData.scenes[key].dump()
            elif dump.startswith("action"):
                for key, value in Command.globalData.scenes.items():
                    if value.enabled:
                        print("Actions in scene %s" % key)
                        for action in value.action_list:
                            action.dump()


# *************************************************************************************************
#
#    ######## ##     ## #### ########
#    ##        ##   ##   ##     ##
#    ##         ## ##    ##     ##
#    ######      ###     ##     ##
#    ##         ## ##    ##     ##
#    ##        ##   ##   ##     ##
#    ######## ##     ## ####    ##
#
# **************************************************************************************************


class ExitCommand(Command):

    def __init__(self):
        super().__init__()
        self.help = "Ends program"
        self.format = "|/exit|quit :"

    def do_process(self):
        exit(0)
