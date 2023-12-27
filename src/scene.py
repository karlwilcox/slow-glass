import re, pygame
from defaults import *
import action, params, sprites
from collections import namedtuple
from triggers import *  # IMPORTANT - Keep this line, required for globals()


class Scene:

    def __init__(self, in_name, in_folder, in_content, in_data):
        self.name = in_name
        self.content = in_content
        self.data = in_data
        self.enabled = False
        self.action_list = []
        self.folder = in_folder
        self.from_folder = ""
        self.trigger_list = []
        self.surface = None
        self.sprites = sprites.SpriteList()
        self.images = {}
        self.sounds = {}
        self.depth = 0

    def start(self, depth=None):
        trigger_map = {"Start": "=/begin : */rest",
                       "After": "=/after : */rest",
                       "OnKey": "=/on |/key|keypress ~/press : */rest",
                       "OnClick": "=/on ~/mouse =/click : */rest",
                       "AtTime": "=/at ~/time : */rest",
                       "EachTime": "=/each ~/time: */rest",
                       "Every": "=/every : */rest",
                       "When": "=/when : */rest",
                       "While": "=/while : */rest",
                       }
        self.enabled = True
        if depth is not None:
            self.depth = depth
        self.surface = pygame.Surface((self.data.options["width"], self.data.options["height"]), pygame.SRCALPHA)
        self.from_folder = ""  # clear each time
        found_action = False
        found_trigger = False
        # We go through the whole textual content of the scene
        # to build "action groups" consisting of a list of one or more
        # triggers and a list of one or more actions.
        # When we have all the groups we go through each one:
        # if any of the triggers is start:
        #     run all the actions now
        #     remove the start trigger from the list
        # if the trigger list still contains triggers:
        #    add the triggers to the scene-wide list of triggers
        #    add the actions to the scene-wide list of actions
        ActionGroup = namedtuple("ActionGroup", ("triggers", "actions"))
        action_group = ActionGroup([], [])
        run_now = False
        for content_line in self.content:
            words = re.split(WORD_SPLIT, content_line)
            for klass_name, trigger_format in trigger_map.items():
                trigger_params = params.ParamList(words, trigger_format)
                if trigger_params.valid:  # This is a trigger
                    if found_action:
                        if len(action_group.triggers) > 0 and len(action_group.actions) > 0:
                            self.trigger_list += action_group.triggers
                            self.action_list += action_group.actions
                        action_group = ActionGroup([], [])
                        run_now = False
                        found_action = False
                    if klass_name == "Start":
                        run_now = True
                    else:
                        klass = globals()[klass_name]
                        trigger = klass(trigger_params.get("rest"), self.name)
                        action_group.triggers.append(trigger)
                    found_trigger = True
                    break
            if found_trigger:
                found_trigger = False
                continue
            # else, assume this is an action
            found_action = True
            # Remove any initial syntactic sugar...
            if content_line.startswith("and "):
                content_line = content_line[4:]
            this_action = action.Action(content_line)
            if run_now:
                if this_action.conditional(self.data.vars, self.name):
                    self.data.command_dispatcher.dispatch(this_action, self)
            else:
                this_action.triggers = action_group.triggers
                action_group.actions.append(this_action)
        # deal with the last group (if present)
        if len(action_group.triggers) > 0 and len(action_group.actions) > 0:
            self.trigger_list += action_group.triggers
            self.action_list += action_group.actions

    def update_triggers(self, millis):
        for trigger in self.trigger_list:
            trigger.test_update(millis)

    def clear_triggers(self):
        for trigger in self.trigger_list:
            trigger.clear()

    def stop(self):
        if self.name == TOP_LEVEL:
            # never stop this one! (Use exit command instead)
            return
        else:
            self.enabled = False  # stop running (duh)
            self.action_list = []  # discard all our action objects
            # and remove all our sprites
            for key, sprite in self.data.sprites.items():
                if sprite.scene == self.name:
                    del self.data.sprites[key]
            # however, sounds play to the end. TODO, is this OK?
            # And clear all variables
            self.data.vars.purge(self.name)
            self.surface = None

    def add_content(self, more_content):
        self.content.append(more_content)

    def make_tag(self, in_tag):
        if ":" in in_tag:  # we have a fully-qualified tag, return it
            return in_tag
        if self.name != TOP_LEVEL:
            return "%s:%s" % (self.name, in_tag)
        return in_tag

    def resolve_tag(self, in_tag, key_list):
        if in_tag is None or in_tag == "":
            return None
        if ":" in in_tag:  # we have a fully-qualified tag, return it
            return in_tag
        # first, look for a local tag in the key_list
        elif in_tag in key_list:
            return in_tag
        print("Sprite %s not found in scene %s" % (in_tag, self.name))
        return None

    def dump(self):
        print("Scene %s (%s) contains:" % (self.name, "enabled" if self.enabled else "disabled"))
        for line in self.content:
            print(line)

