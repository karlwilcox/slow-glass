# standard libraries
from abc import abstractmethod
import matplotlib.colors as colors
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

    def tag_fixup(self, itag, stag):
        """
        return properly named image and sprite tags
        """
        if stag is None:
            stag = itag
        stag = self.scene.make_tag(stag)
        itag = self.scene.resolve_tag(itag, Command.globalData.images.keys())
        return itag, stag

    @abstractmethod
    def do_process(self):
        pass


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
    """
    echo [args...] (prints arguments to console)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/echo|log : */rest"

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
    """
        from folder (look for resources in this folder)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/from|using|with : */rest"

    def do_process(self):
        self.scene.from_folder = self.params.get('rest')


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
    """
        load filename [as] [tag] (loads resource, basename as tag if not given)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/load|upload : +/filename ~/named &/tag ~/split ?/cols ?/by ?/rows"

    def do_process(self):
        filename = os.path.join(self.scene.folder, self.scene.from_folder, self.params.get("filename")).rstrip("/")
        if not os.path.exists(filename):
            print("Resource file not found: %s" % filename)
            return True
        tag = self.params.get("tag")
        if tag is None:
            tag, ext = os.path.splitext(os.path.basename(filename))
        tag = self.scene.make_tag(tag)
        if tag in Command.globalData.images.keys():
            # Silent return, don't reload existing images, used unload first
            return True
        if os.path.isdir(filename):
            Command.globalData.images[tag] = images.ImageFolder(filename)
        elif filename.lower().endswith((".jpg", ".jpeg", ".png", ".svg")):
            rows = self.params.as_int("rows")
            cols = self.params.as_int("cols")
            if rows is not None and cols is not None:
                Command.globalData.images[tag] = images.CellImage(filename, rows, cols)
            else:
                Command.globalData.images[tag] = images.SimpleImage(filename)
        elif filename.lower().endswith((".gif", ".mov", ".mp4")):
            Command.globalData.images[tag] = images.Movie(filename)
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
    """
        unload tag... (unloads resources, deleted from memory)
    """

    def __init__(self):
        super().__init__()
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
    """
        play tag (play sound named tag to the end)
    """

    def __init__(self):
        super().__init__()
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
    """
        [set] volume [of] tag [to] 0-100 (per resource sound level)
    """

    def __init__(self):
        super().__init__()
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
#    ########  ##          ###     ######  ########       ###    ########
#    ##     ## ##         ## ##   ##    ## ##            ## ##      ##
#    ##     ## ##        ##   ##  ##       ##           ##   ##     ##
#    ########  ##       ##     ## ##       ######      ##     ##    ##
#    ##        ##       ######### ##       ##          #########    ##
#    ##        ##       ##     ## ##    ## ##          ##     ##    ##
#    ##        ######## ##     ##  ######  ########    ##     ##    ##
#
# **************************************************************************************************


class PlaceAtCommand(Command):
    """
        place image [as sprite] [at] x,y,z [size w,h] (adds image to display)
        or redefines existing sprite with the same tag
    """

    def __init__(self):
        super().__init__()
        self.format = "=/place : +/itag ~/named &/stag +/at +/x +/y ~/depth +/z |/size|scale ?/w ?/h"

    def do_process(self):
        itag, stag = self.tag_fixup(self.params.get("itag"), self.params.get("stag"))
        if itag is None:
            return True
        sw = None
        sh = None
        x = self.params.as_float("x", "number for x coord")
        y = self.params.as_float("y", "number for y coord")
        if self.params.get("size") is not None and self.params.get("size") == "scale":
            w = None
            h = None
            sw = self.params.as_float("w")
            sh = self.params.as_float("h")
        else:
            w = self.params.as_float("w")
            h = self.params.as_float("h")
        z = self.params.as_float("z") or 0
        existing = Command.globalData.sprites.get_sprite(stag)
        if existing is not None:
            old_depth = existing.depth
            existing.reposition(x, y, w, h, z)
            # depth may have changed, so re-order them
            if z is not None and z != old_depth:
                Command.globalData.sprites.sprite_set_depth(stag, existing.depth)
        else:
            Command.globalData.sprites.sprite_add(sprites.SpriteItem(itag, stag, self.scene, x, y, w, h, z))
        if sw is not None:
            Command.globalData.sprites.get_sprite(stag).scale_to(sw, sh, 0)

# *************************************************************************************************
#
#    ########  ##     ## ########       ###     ######
#    ##     ## ##     ##    ##         ## ##   ##    ##
#    ##     ## ##     ##    ##        ##   ##  ##
#    ########  ##     ##    ##       ##     ##  ######
#    ##        ##     ##    ##       #########       ##
#    ##        ##     ##    ##       ##     ## ##    ##
#    ##         #######     ##       ##     ##  ######
#
# **************************************************************************************************


class PlaceAsCommand(Command):
    """
        place image [as sprite] as location
    """

    def __init__(self):
        super().__init__()
        self.format = "=/put : +/itag ~/named &/stag +/as |/background|top|bottom|left|right|ground|sky ~/depth ?/depth"

    def do_process(self):
        stag = self.params.get("stag")
        location = self.params.get("background")
        if stag is None:
            stag = location
        itag, stag = self.tag_fixup(self.params.get("itag"), stag)
        if itag is None:
            return True
        width = Command.globalData.options["width"]
        height = Command.globalData.options["height"]
        image_width = Command.globalData.images[itag].image_rect.width
        image_height = Command.globalData.images[itag].image_rect.height
        depth = self.params.as_int("depth")
        if location == "background":
            x = width / 2
            y = height / 2
            w = width
            h = height
            z = depth or 1000
        elif location == "bottom" or location == "ground":
            x = width / 2
            w = width
            # Set height to maintain original aspect ratio
            h = image_height * (width / image_width)
            # and move to the bottom
            y = height - (h / 2)
            z = depth or 980
        elif location == "top" or location == "sky":
            x = width / 2
            w = width
            # Set height to maintain original aspect ratio
            h = image_height * (width / image_width)
            # and move to the top
            y = h / 2
            z = depth or 980
        elif location == "left":
            y = height / 2
            h = height
            # Set width to maintain original aspect ratio
            w = image_width * (height / image_height)
            # and move to the left
            x = w /2
            z = depth or 960
        elif location == "left":
            y = height / 2
            h = height
            # Set width to maintain original aspect ratio
            w = image_width * (height / image_height)
            # and move to the right
            x = width - (w /2)
            z = depth or 960
        else:
            print("Unknown location: " + self.params.get("rest"))
            return
        Command.globalData.sprites.sprite_add(sprites.SpriteItem(itag, stag, self.scene, x, y, w, h, z))


# *************************************************************************************************
#
#    ##      ## #### ##    ## ########   #######  ##      ##
#    ##  ##  ##  ##  ###   ## ##     ## ##     ## ##  ##  ##
#    ##  ##  ##  ##  ####  ## ##     ## ##     ## ##  ##  ##
#    ##  ##  ##  ##  ## ## ## ##     ## ##     ## ##  ##  ##
#    ##  ##  ##  ##  ##  #### ##     ## ##     ## ##  ##  ##
#    ##  ##  ##  ##  ##   ### ##     ## ##     ## ##  ##  ##
#     ###  ###  #### ##    ## ########   #######   ###  ###
#
# **************************************************************************************************


class WindowCommand(Command):
    """
        window s-tag at ix, iy, iw, ih - define centre, width and height of the sprite on
        its source image (sprite must exist)
    """

    def __init__(self):
        super().__init__()
        self.format = "=/window : +/stag ~/at +/ix +/iy +/iw +/ih"

    def do_process(self):
        stag = self.params.get("stag")
        tag = self.scene.resolve_tag(stag, Command.globalData.sprites.keys())
        if tag is not None:
            ix = self.params.as_float("ix", "centre x of window")
            iy = self.params.as_float("iy", "centre y of window")
            iw = self.params.as_float("iw", "width of window")
            ih = self.params.as_float("ih", "height of window")
            Command.globalData.sprites.get_sprite(tag).set_window(ix, iy, iw, ih)
        else:
            print("tag %s not found" % stag)

# *************************************************************************************************
#
#    ########  #######   #######  ##     ##
#         ##  ##     ## ##     ## ###   ###
#        ##   ##     ## ##     ## #### ####
#       ##    ##     ## ##     ## ## ### ##
#      ##     ##     ## ##     ## ##     ##
#     ##      ##     ## ##     ## ##     ##
#    ########  #######   #######  ##     ##
#
# **************************************************************************************************


class ZoomCommand(Command):
    """
        zoom tag [to] x,y [in] [time] (changes size of sprite on source window)
    """

    def __init__(self):
        super().__init__()
        self.format = "=/zoom =/window : +/tag ~/to +/iw +/ih ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        iw = self.params.as_float("iw", "new width of window")
        ih = self.params.as_float("ih", "new height of window")
        rate = timing.Duration(self.params.get("time")).as_seconds()
        Command.globalData.sprites.get_sprite(tag).zoom_to(iw, ih, rate)

# *************************************************************************************************
#
#     ######   ######  ########   #######  ##       ##
#    ##    ## ##    ## ##     ## ##     ## ##       ##
#    ##       ##       ##     ## ##     ## ##       ##
#     ######  ##       ########  ##     ## ##       ##
#          ## ##       ##   ##   ##     ## ##       ##
#    ##    ## ##    ## ##    ##  ##     ## ##       ##
#     ######   ######  ##     ##  #######  ######## ########
#
# **************************************************************************************************

# *************************************************************************************************
#
#    ##     ##  #######  ##     ## ########    ##      ## #### ##    ## ########   #######  ##      ##
#    ###   ### ##     ## ##     ## ##          ##  ##  ##  ##  ###   ## ##     ## ##     ## ##  ##  ##
#    #### #### ##     ## ##     ## ##          ##  ##  ##  ##  ####  ## ##     ## ##     ## ##  ##  ##
#    ## ### ## ##     ## ##     ## ######      ##  ##  ##  ##  ## ## ## ##     ## ##     ## ##  ##  ##
#    ##     ## ##     ##  ##   ##  ##          ##  ##  ##  ##  ##  #### ##     ## ##     ## ##  ##  ##
#    ##     ## ##     ##   ## ##   ##          ##  ##  ##  ##  ##   ### ##     ## ##     ## ##  ##  ##
#    ##     ##  #######     ###    ########     ###  ###  #### ##    ## ########   #######   ###  ###
#
# **************************************************************************************************


class MoveWindowCommand(Command):
    """
        scroll window of tag [to] x,y [in] [time] (changes position of sprite on source window)
    """

    def __init__(self):
        super().__init__()
        self.format = "=/move =/window : ~/of +/tag ~/to +/ix +/iy ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        ix = self.params.as_float("ix", "new centre x of window")
        iy = self.params.as_float("iy", "new centre y of window")
        rate = timing.Duration(self.params.get("time")).as_seconds()
        Command.globalData.sprites.get_sprite(tag).scroll_to(ix, iy, rate)


# *************************************************************************************************
#
#    ########  ######## ##     ##  #######  ##     ## ########
#    ##     ## ##       ###   ### ##     ## ##     ## ##
#    ##     ## ##       #### #### ##     ## ##     ## ##
#    ########  ######   ## ### ## ##     ## ##     ## ######
#    ##   ##   ##       ##     ## ##     ##  ##   ##  ##
#    ##    ##  ##       ##     ## ##     ##   ## ##   ##
#    ##     ## ######## ##     ##  #######     ###    ########
#
# **************************************************************************************************


class RemoveCommand(Command):
    """
        remove tag... (remove sprites from the display, does not delete loaded image)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/remove|erase : >/tags"

    def do_process(self):
        for tag in self.params.get("tag"):
            tag = self.scene.resolve_tag(tag, Command.globalData.sprites.keys())
            if tag is not None:
                Command.globalData.sprites.remove(tag)


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
    """
        move tag [to] x,y [in] [time] (moves sprite to new position, whether hidden or visible)
    """

    def __init__(self):
        super().__init__()
        self.format = "=/move : +/tag |/to|by +/x +/y |/in|at */rest"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        x = self.params.as_float("x", "new x coord")
        y = self.params.as_float("y", "new y coord")
        in_or_at = self.params.get("in")
        relative = self.params.get("to") == "by"
        if in_or_at == "in":
            rate = timing.Duration(self.params.get("rest")).as_seconds()
            Command.globalData.sprites.get_sprite(tag).move_in_time(x, y, rate, relative)
        elif in_or_at == "at":
            rate = timing.Speed(self.params.get("rest")).as_pps()
            Command.globalData.sprites.get_sprite(tag).move_at_rate(x, y, rate, relative)
        else:
            Command.globalData.sprites.get_sprite(tag).move_in_time(x, y, 0, relative)

# *************************************************************************************************
#
#     ######  ########  ######## ######## ########
#    ##    ## ##     ## ##       ##       ##     ##
#    ##       ##     ## ##       ##       ##     ##
#     ######  ########  ######   ######   ##     ##
#          ## ##        ##       ##       ##     ##
#    ##    ## ##        ##       ##       ##     ##
#     ######  ##        ######## ######## ########
#
# **************************************************************************************************


class SpeedCommand(Command):
    """
        [set] speed [of] s-tag [to] <value> [in <time>] - change speed of sprite
    """

    def __init__(self):
        super().__init__()
        self.format = "~/set =/speed ~/of : +/tag ~/to +/speed ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        speed = self.params.as_float("speed", "new speed (pps)")
        rate = timing.Duration(self.params.get("time")).as_seconds()
        Command.globalData.sprites.get_sprite(tag).set_speed(speed, rate)

# *************************************************************************************************
#
#    ########  ##       ##     ## ########
#    ##     ## ##       ##     ## ##     ##
#    ##     ## ##       ##     ## ##     ##
#    ########  ##       ##     ## ########
#    ##     ## ##       ##     ## ##   ##
#    ##     ## ##       ##     ## ##    ##
#    ########  ########  #######  ##     ##
#
# **************************************************************************************************


class BlurCommand(Command):
    """
        [set] blur [of] s-tag [to] <value> [in <time>] - change blurriness of sprite
    """

    def __init__(self):
        super().__init__()
        self.format = "~/set =/blur ~/of : +/tag ~/to +/blur ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        bluriness = self.params.as_float("blur", "Bluriness (0-100)")
        rate = timing.Duration(self.params.get("time")).as_seconds()
        Command.globalData.sprites.get_sprite(tag).set_blur(bluriness, rate)


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
    """
        resize tag [to] x,y [in] [time] (moves sprite to new position, whether hidden or visible)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/size|resize : +/tag ~/to +/width +/height ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        width = self.params.as_float("width", "new width")
        height = self.params.as_float("height", "new height")
        rate = timing.Duration(self.params.get("time")).as_seconds()
        print("Size of %s to %f in %f" % (tag, width, rate))
        Command.globalData.sprites.get_sprite(tag).resize(width, height, rate)


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
    """
        scale tag [by] x,y [in] [time] (moves sprite to new position, whether hidden or visible)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/scale|rescale : +/tag |/by|to +/xpct #/ypct ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        width_scale = self.params.as_float("xpct", "Percentage to change")
        height_scale = self.params.as_float("ypct")
        if height_scale is None:
            height_scale = width_scale
        rate = timing.Duration(self.params.get("time")).as_seconds()
        if self.params.get("by") == "by":
            Command.globalData.sprites.get_sprite(tag).scale_by(width_scale, height_scale, rate)
        else:
            Command.globalData.sprites.get_sprite(tag).scale_to(width_scale, height_scale, rate)


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
    """
        rotate tag [to] degrees [in] [time] (rotates sprite to new position, whether hidden or visible)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/rotate|turn : +/tag |/to|by #/degrees ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        rotation = self.params.as_float("degrees", "Degrees to turn by/to")
        relative = self.params.get("to").lower() == "by"
        rate = timing.Duration(self.params.get("time")).as_seconds()
        Command.globalData.sprites.get_sprite(tag).turn(rotation, rate, relative)


# *************************************************************************************************
#
#    ########     ###    ####  ######  ########       ## ##        #######  ##      ## ######## ########
#    ##     ##   ## ##    ##  ##    ## ##            ##  ##       ##     ## ##  ##  ## ##       ##     ##
#    ##     ##  ##   ##   ##  ##       ##           ##   ##       ##     ## ##  ##  ## ##       ##     ##
#    ########  ##     ##  ##   ######  ######      ##    ##       ##     ## ##  ##  ## ######   ########
#    ##   ##   #########  ##        ## ##         ##     ##       ##     ## ##  ##  ## ##       ##   ##
#    ##    ##  ##     ##  ##  ##    ## ##        ##      ##       ##     ## ##  ##  ## ##       ##    ##
#    ##     ## ##     ## ####  ######  ######## ##       ########  #######   ###  ###  ######## ##     ##
#
# **************************************************************************************************


class RaiseLowerCommand(Command):
    """
        raise tag by/to depth (sets depth of sprite)
    """

    def __init__(self):
        super().__init__()
        self.format = "~/set |/raise|lower|depth ~/of : +/tag ~/depth |/by|to +/num"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is not None:
            depth = self.params.as_int("num")
            if self.params.get("by") == "by":
                if "lower" in self.params.command:
                    depth *= -1
                Command.globalData.sprites.sprite_change_depth(tag, depth)
            else:
                Command.globalData.sprites.sprite_set_depth(tag, depth)

# *************************************************************************************************
#
#       ###    ########  ##     ##    ###    ##    ##  ######  ########
#      ## ##   ##     ## ##     ##   ## ##   ###   ## ##    ## ##
#     ##   ##  ##     ## ##     ##  ##   ##  ####  ## ##       ##
#    ##     ## ##     ## ##     ## ##     ## ## ## ## ##       ######
#    ######### ##     ##  ##   ##  ######### ##  #### ##       ##
#    ##     ## ##     ##   ## ##   ##     ## ##   ### ##    ## ##
#    ##     ## ########     ###    ##     ## ##    ##  ######  ########
#
# **************************************************************************************************


class AdvanceCommand(Command):
    """
        Get next / previous sprite frame
    """

    def __init__(self):
        super().__init__()
        self.format = "|/advance|reverse : +/tag |/by|to +/num ~/frames"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is not None:
            frame = self.params.as_int("num")
            if frame is None or frame == 0:
                frame = 1
            if self.params.get("by") == "by":
                if "reverse" in self.params.command:
                    frame *= -1
                Command.globalData.sprites.get_sprite(tag).next_frame(frame)
            else:
                Command.globalData.sprites.get_sprite(tag).move_to(frame)


# *************************************************************************************************
#
#    ########     ###    ######## ########
#    ##     ##   ## ##      ##    ##
#    ##     ##  ##   ##     ##    ##
#    ########  ##     ##    ##    ######
#    ##   ##   #########    ##    ##
#    ##    ##  ##     ##    ##    ##
#    ##     ## ##     ##    ##    ########
#
# **************************************************************************************************


class RateCommand(Command):
    """
    set frame rate of tag to value [in duration]
    Sets the frame update rate to value [in seconds per frame], over the given duration
    Note that this is independent of the actual display framerate
    """

    def __init__(self):
        super().__init__()
        self.format = "~/set |/frame|animation =/rate ~/of : +/tag ~/to +/value ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        duration = timing.Duration(self.params.get("time")).as_seconds()
        if tag is not None:
            Command.globalData.sprites.get_sprite(tag).set_animation_rate(self.params.as_float("value"), duration)

# *************************************************************************************************
#
#    ########     ###    ########  ##    ##       ## ##       ####  ######   ##     ## ########
#    ##     ##   ## ##   ##     ## ##   ##       ##  ##        ##  ##    ##  ##     ##    ##
#    ##     ##  ##   ##  ##     ## ##  ##       ##   ##        ##  ##        ##     ##    ##
#    ##     ## ##     ## ########  #####       ##    ##        ##  ##   #### #########    ##
#    ##     ## ######### ##   ##   ##  ##     ##     ##        ##  ##    ##  ##     ##    ##
#    ##     ## ##     ## ##    ##  ##   ##   ##      ##        ##  ##    ##  ##     ##    ##
#    ########  ##     ## ##     ## ##    ## ##       ######## ####  ######   ##     ##    ##
#
# **************************************************************************************************


class BrightnessCommand(Command):
    """
        set darkness/lightness of tag to num (make image darker/lighter)
    """

    def __init__(self):
        super().__init__()
        self.format = "~/set |/darken|darkness|lightness|lighten ~/of : +/tag ~/to +/value ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        rate = timing.Duration(self.params.get("time")).as_seconds()
        if tag is not None:
            if ("darken", "darkness") in self.params.command:
                Command.globalData.sprites.get_sprite(tag).darken(self.params.as_int("value"), rate)
            else:
                Command.globalData.sprites.get_sprite(tag).lighten(self.params.as_int("value"), rate)

# *************************************************************************************************
#
#    ######## ########     ###    ##    ##  ######
#       ##    ##     ##   ## ##   ###   ## ##    ##
#       ##    ##     ##  ##   ##  ####  ## ##
#       ##    ########  ##     ## ## ## ##  ######
#       ##    ##   ##   ######### ##  ####       ##
#       ##    ##    ##  ##     ## ##   ### ##    ##
#       ##    ##     ## ##     ## ##    ##  ######
#
# **************************************************************************************************


class TransCommand(Command):
    """
        set trans of tag to num (Set transparency of sprite from 0 to 100)
    """

    def __init__(self):
        super().__init__()
        self.format = "~/set |/trans|transparency ~/of : +/tag ~/to +/value ~/in */time"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        rate = timing.Duration(self.params.get("time")).as_seconds()
        if tag is not None:
            Command.globalData.sprites.get_sprite(tag).trans(self.params.as_int("value"), rate)


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
    """
        start scene... (start running a named scene)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/start|run : >/list"

    def do_process(self):
        for scene_name in self.params.get("list"):
            for scene_key in Command.globalData.scenes.keys():
                if scene_key == scene_name:
                    Command.globalData.scenes[scene_name].start()
                    break


class StopCommand(Command):
    """
        stop scene... (stop running named scene, or the current scene if not given & removes all sprites
                    for this scene from display)
    """

    def __init__(self):
        super().__init__()
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

class ShowHideCommand(Command):
    """
        show/hide sprites... (hides sprite, but still active and updating)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/show|hide : +/tag ~/for */time"

    def do_process(self):
        tag = self.params.get("tag")
        s_tag = self.scene.resolve_tag(tag, Command.globalData.sprites.keys())
        if s_tag is None:
            return
        my_sprite = Command.globalData.sprites.get_sprite(s_tag)
        my_sprite.visible = "show" in self.params.command
        time_param = self.params.get("time")
        if time_param is not None:
            duration = timing.Duration(time_param).as_seconds()
            my_sprite.set_visibility_duration(duration)
        else:
            my_sprite.visibilityTimer = None


# *************************************************************************************************
#
#    ########     ###    ##     ##  ######  ########       ## ########  ########  ######  ##     ## ##     ## ########
#    ##     ##   ## ##   ##     ## ##    ## ##            ##  ##     ## ##       ##    ## ##     ## ###   ### ##
#    ##     ##  ##   ##  ##     ## ##       ##           ##   ##     ## ##       ##       ##     ## #### #### ##
#    ########  ##     ## ##     ##  ######  ######      ##    ########  ######    ######  ##     ## ## ### ## ######
#    ##        ######### ##     ##       ## ##         ##     ##   ##   ##             ## ##     ## ##     ## ##
#    ##        ##     ## ##     ## ##    ## ##        ##      ##    ##  ##       ##    ## ##     ## ##     ## ##
#    ##        ##     ##  #######   ######  ######## ##       ##     ## ########  ######   #######  ##     ## ########
#
# **************************************************************************************************


class PauseCommand(Command):
    """
        pause sprites... (pause sprite, freeze changes)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/pause|freeze : >/list"

    def do_process(self):
        tag_list = self.params.get("list")
        for tag in tag_list:
            s_tag = self.scene.resolve_tag(tag, Command.globalData.sprites.keys())
            if s_tag is not None:
                Command.globalData.sprites.get_sprite(s_tag).paused = True


class ResumeCommand(Command):
    """
        resume sprites... (resume changing sprites)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/resume|unfreeze : >/list"

    def do_process(self):
        tag_list = self.params.get("list")
        for tag in tag_list:
            s_tag = self.scene.resolve_tag(tag, Command.globalData.sprites.keys())
            if s_tag is not None:
                Command.globalData.sprites.get_sprite(s_tag).paused = False

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
    """
        make name [be] value (can be accessed as $name in other commands)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/make|let|put : +/name ~/be ~/as ~/= */rest"

    def do_process(self):
        name = self.params.get("name")
        content = self.params.get("rest")
        # check for writable built-ins first
        # none at present
        Command.globalData.vars.set_var(name, content, self.scene.name)

# *************************************************************************************************
#
#     ######  ########  ########    ###    ######## ########
#    ##    ## ##     ## ##         ## ##      ##    ##
#    ##       ##     ## ##        ##   ##     ##    ##
#    ##       ########  ######   ##     ##    ##    ######
#    ##       ##   ##   ##       #########    ##    ##
#    ##    ## ##    ##  ##       ##     ##    ##    ##
#     ######  ##     ## ######## ##     ##    ##    ########
#
# **************************************************************************************************


class CreateItemCommand(Command):

    def __init__(self):
        super().__init__()
        self.format = "=/create |/group|text : +/item_name |/from|size */content"

    def do_process(self):
        item_type = self.params.get("group")
        item_name = self.params.get("item_name")
        content = self.params.get("content")
        if item_type == "group":
            if content is not None and content != "":
                size = timing.Size(content).as_tuple()
                image_rect = pygame.Rect(0, 0, size[0], size[1])
                self.scene.data.images[item_name] = images.GroupImage(self.scene, item_name, image_rect)
            else:
                self.scene.data.images[item_name] = images.GroupImage(self.scene, item_name)
        elif item_type == "text":
            self.scene.data.images[item_name] = images.TextImage()
            if content is not None:
                self.scene.data.images[item_name].content = content
                self.scene.data.images[item_name].next_frame()

# *************************************************************************************************
#
#    ######## ######## ##     ## ########
#       ##    ##        ##   ##     ##
#       ##    ##         ## ##      ##
#       ##    ######      ###       ##
#       ##    ##         ## ##      ##
#       ##    ##        ##   ##     ##
#       ##    ######## ##     ##    ##
#
# **************************************************************************************************


class TextCommand(Command):

    def __init__(self):
        super().__init__()
        self.format = "=/set |/content|text ~/of : +/text_item ~/to */rest"

    def do_process(self):
        text_name = self.params.get("text_item")
        if text_name not in self.scene.data.images.keys():
            print("Text image %s does not exist" % text_name)
        else:
            text_item = self.scene.data.images[text_name]
            if text_item.__class__.__name__ != "TextImage":
                print("Image %s is not a TextImage" % text_name)
            else:
                text_item.content = self.params.get("rest")
                text_item.next_frame()

# *************************************************************************************************
#
#    ########  #######  ##    ## ########
#    ##       ##     ## ###   ##    ##
#    ##       ##     ## ####  ##    ##
#    ######   ##     ## ## ## ##    ##
#    ##       ##     ## ##  ####    ##
#    ##       ##     ## ##   ###    ##
#    ##        #######  ##    ##    ##
#
# **************************************************************************************************


class FontCommand(Command):

    def __init__(self):
        super().__init__()
        self.format = "=/set =/font : +/feature ~/of +/text_item ~/to */rest"

    def do_process(self):
        text_name = self.params.get("text_item")
        if text_name not in self.scene.data.images.keys():
            print("Text image %s does not exist" % text_name)
        else:
            text_item = self.scene.data.images[text_name]
            feature_name = self.params.get("feature")
            if feature_name.startswith("col") or feature_name.startswith("back"):
                colour_name = self.params.get("rest").lower().replace(" ", "")
                if colour_name in colors.cnames.keys():
                    if feature_name.startswith("c"):
                        text_item.color = colors.cnames[colour_name]
                    else:
                        text_item.background_color = colors.cnames[colour_name]
                else:
                    print("Unknown colour %s" % colour_name)
            elif feature_name == "style":
                style_item = self.params.get("rest")
                if style_item == "bold":
                    text_item.text_font.bold = True
                elif style_item == "italic":
                    text_item.text_font.italic = True
                elif style_item == "underline":
                    text_item.text_font.underline = True
                else:
                    print("Unknown style %s" % style_item)
            elif feature_name == "size":
                text_item.text_font.point_size = int(self.params.get("rest"))
            text_item.next_frame()  # Force re-rendering


# *************************************************************************************************
#
#       ###    ########  ########     ########  #######      ######   ########   #######  ##     ## ########
#      ## ##   ##     ## ##     ##       ##    ##     ##    ##    ##  ##     ## ##     ## ##     ## ##     ##
#     ##   ##  ##     ## ##     ##       ##    ##     ##    ##        ##     ## ##     ## ##     ## ##     ##
#    ##     ## ##     ## ##     ##       ##    ##     ##    ##   #### ########  ##     ## ##     ## ########
#    ######### ##     ## ##     ##       ##    ##     ##    ##    ##  ##   ##   ##     ## ##     ## ##
#    ##     ## ##     ## ##     ##       ##    ##     ##    ##    ##  ##    ##  ##     ## ##     ## ##
#    ##     ## ########  ########        ##     #######      ######   ##     ##  #######   #######  ##
#
# **************************************************************************************************


class AddGroupCommand(Command):

    def __init__(self):
        super().__init__()
        self.format = "=/add ~/to =/group : +/group >/list"

    def do_process(self):
        group_name = self.params.get("group")
        if group_name is None or group_name not in Command.globalData.images.keys():
            print("No such group: %s" % group_name)
            return
        for item in self.params.get("list"):
            item = self.scene.resolve_tag(item, Command.globalData.sprites.keys())
            if item is not None:
                Command.globalData.sprites.get_sprite(item).group = group_name

# *************************************************************************************************
#
#    ########  ######## ##       ######## ######## ########     ######   ########   #######  ##     ## ########
#    ##     ## ##       ##       ##          ##    ##          ##    ##  ##     ## ##     ## ##     ## ##     ##
#    ##     ## ##       ##       ##          ##    ##          ##        ##     ## ##     ## ##     ## ##     ##
#    ##     ## ######   ##       ######      ##    ######      ##   #### ########  ##     ## ##     ## ########
#    ##     ## ##       ##       ##          ##    ##          ##    ##  ##   ##   ##     ## ##     ## ##
#    ##     ## ##       ##       ##          ##    ##          ##    ##  ##    ##  ##     ## ##     ## ##
#    ########  ######## ######## ########    ##    ########     ######   ##     ##  #######   #######  ##
#
# **************************************************************************************************


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
    """
        dump vars|scenes|sprites
    """

    def __init__(self):
        super().__init__()
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
    """
    exit - ends program
    """

    def __init__(self):
        super().__init__()
        self.format = "|/exit|quit :"

    def do_process(self):
        exit(0)
