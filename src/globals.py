import dispatcher
import vars, sprites
from defaults import *


class Globals:

    def __init__(self):
        # global data structures
        self.scenes = {}
        self.sprites = sprites.SpriteList()
        self.sounds = {}
        self.images = {}
        self.groups = []
        self.vars = vars.Variables(self)
        self.command_dispatcher = dispatcher.Dispatcher()
        self.options = {"width": 1080, "height": 1920, "fullscreen": False,
                        "rotate": False, "dir": DEFAULT_FOLDER, "file": DEFAULT_FILENAME,
                        "help": False, "safe": SAFE_EVALUATION}

    def dump_options(self):
        for key, value in self.options.items():
            print("%s +> %s" % (key, value))
