import dispatcher
import vars
from defaults import *


class Globals:

    def __init__(self):
        # global data structures
        self.scenes = {}
        self.sprites = {}
        self.sounds = {}
        self.images = {}
        self.vars = vars.Variables(self)
        self.command_dispatcher = dispatcher.Dispatcher()
        self.options = {"width": 1080, "height": 1920, "fullscreen": False,
                        "rotate": False, "dir": DEFAULT_FOLDER, "file": DEFAULT_FILENAME}

    def dump_options(self):
        for key, value in self.options.items():
            print("%s +> %s" % (key, value))
