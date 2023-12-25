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
        self.format = "|/echo|say|print : */rest"

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
        self.format = "|/load|upload : +/filename ~/name ~/named &/tag ~/split ?/cols ?/by ?/rows"

    def do_process(self):
        filename = os.path.join(self.scene.folder, self.scene.from_folder, self.params.get("filename")).rstrip("/")
        if not os.path.exists(filename):
            print("Resource file not found: %s" % filename)
            return True
        tag = self.params.get("tag")
        if tag is None:
            tag, ext = os.path.splitext(os.path.basename(filename))
        tag = self.scene.make_tag(tag)
        if os.path.isdir(filename):
            Command.globalData.images[tag] = images.ImageFolder(filename)
        elif filename.lower().endswith((".jpg", ".jpeg", "png", "gif")):
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
        self.format = "=/place : +/itag ~/named &/stag +/at +/x +/y ~/depth +/z ~/size ?/w ?/h"

    def do_process(self):
        itag, stag = self.tag_fixup(self.params.get("itag"), self.params.get("stag"))
        if itag is None:
            return True
        x = self.params.as_float("x", "number for x coord")
        y = self.params.as_float("y", "number for y coord")
        w = self.params.as_float("w")
        h = self.params.as_float("h")
        z = self.params.as_float("z")
        existing = Command.globalData.sprites.get_sprite(stag)
        if existing is not None:
            old_depth = existing.depth
            existing.reposition(x, y, w, h, z)
            # depth may have changed, so re-order them
            if z is not None and z != old_depth:
                Command.globalData.sprites.sprites_set_depth(stag, existing.depth)
        else:
            Command.globalData.sprites.sprite_add(sprites.SpriteItem(itag, stag, self.scene, x, y, w, h, z))

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
        self.format = "=/put : +/itag ~/named &/stag +/as |/background|top|bottom|left|right|ground|sky */rest"

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
        image_width = Command.globalData.images[itag].frame_width
        image_height = Command.globalData.images[itag].frame_height
        image_ar = image_width / image_height
        if location == "background":
            x = width / 2
            y = height / 2
            w = width
            h = height
            z = 1000
        elif location == "bottom" or location == "ground":
            x = width / 2
            w = width
            # Set height to maintain original aspect ratio
            h = image_height * (width / image_width)
            # and move to the bottom
            y = height - (h / 2)
            z = 980
        elif location == "top" or location == "sky":
            x = width / 2
            w = width
            # Set height to maintain original aspect ratio
            h = image_height * (width / image_width)
            # and move to the top
            y = h / 2
            z = 980
        elif location == "left":
            y = height / 2
            h = height
            # Set width to maintain original aspect ratio
            w = image_width * (height / image_height)
            # and move to the left
            x = w /2
            z = 960
        elif location == "left":
            y = height / 2
            h = height
            # Set width to maintain original aspect ratio
            w = image_width * (height / image_height)
            # and move to the right
            x = width - (w /2)
            z = 960
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
        self.format = "=/zoom : +/tag ~/to +/iw +/ih ~/in */time"

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


class ScrollCommand(Command):
    """
        scroll tag [to] x,y [in] [time] (changes position of sprite on source window)
    """

    def __init__(self):
        super().__init__()
        self.format = "=/scroll : +/tag ~/to +/ix +/iy ~/in */time"

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
        self.format = "=/move : +/tag ~/to +/x +/y |/in|at */rest"

    def do_process(self):
        tag = self.scene.resolve_tag(self.params.get("tag"), Command.globalData.sprites.keys())
        if tag is None:
            return True
        x = self.params.as_float("x", "new x coord")
        y = self.params.as_float("y", "new y coord")
        in_or_at = self.params.get("in")
        if in_or_at == "in":
            rate = timing.Duration(self.params.get("rest")).as_seconds()
            Command.globalData.sprites.get_sprite(tag).move_in_time(x, y, rate)
        elif in_or_at == "at":
            rate = timing.Speed(self.params.get("rest")).as_pps()
            Command.globalData.sprites.get_sprite(tag).move_at_rate(x, y, rate)
        else:
            Command.globalData.sprites.get_sprite(tag).move_in_time(x, y, 0)

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
        Command.globalData.sprites.get_sprite(tag).scale(width_scale, height_scale, rate)


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
        to_by = self.params.get("to").lower()
        rate = timing.Duration(self.params.get("time")).as_seconds()
        if to_by == "to":
            Command.globalData.sprites.get_sprite(tag).turn_to(rotation, rate)
        else:
            Command.globalData.sprites.get_sprite(tag).turn_by(rotation, rate)


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
                Command.globalData.sprites.get_sprite(tag).get_next_frame(frame)
            else:
                Command.globalData.sprites.get_sprite(tag).get_frame(frame)


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
#    ########    ###    ########  ########
#    ##         ## ##   ##     ## ##
#    ##        ##   ##  ##     ## ##
#    ######   ##     ## ##     ## ######
#    ##       ######### ##     ## ##
#    ##       ##     ## ##     ## ##
#    ##       ##     ## ########  ########
#
# **************************************************************************************************


class FadeCommand(Command):
    """
        fade tag to num (Set transparency of sprite from 0 to 100)
    """

    def __init__(self):
        super().__init__()
        self.format = "~/set |/fade|transparency ~/of : +/tag ~/to +/value ~/in */time"

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

class HideCommand(Command):
    """
        hide sprites... (hides sprite, but still active and updating)
    """

    def __init__(self):
        super().__init__()
        self.format = "=/hide : >/list"

    def do_process(self):
        tag_list = self.params.get("list")
        for tag in tag_list:
            s_tag = self.scene.resolve_tag(tag, Command.globalData.sprites.keys())
            if s_tag is not None:
                Command.globalData.sprites.get_sprite(s_tag).visible = False


class ShowCommand(Command):
    """
        show sprites... (reveals sprites in active list)
    """

    def __init__(self):
        super().__init__()
        self.format = "|/show|reveal : >/list"

    def do_process(self):
        tag_list = self.params.get("list")
        for tag in tag_list:
            s_tag = self.scene.resolve_tag(tag, Command.globalData.sprites.keys())
            if s_tag is not None:
                Command.globalData.sprites.get_sprite(s_tag).visible = True

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
