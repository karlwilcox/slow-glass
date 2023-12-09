import re
from defaults import *
import action, params
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

    def start(self):
        trigger_map = {"Start": "=/begin : */rest",
                       "After": "=/after : */rest",
                       "OnKey": "=/on |/key|keypress ~/press : */rest",
                       "OnClick": "=/on ~/mouse =/click : */rest",
                       "AtTime": "=/at : */rest",
                       "EachTime": "=/each : */rest",
                       "Every": "=/every : */rest",
                       "When": "=/when : */rest",
                       }
        self.enabled = True
        trigger = None
        self.from_folder = ""  # clear each time
        triggers_for_action = []
        found_action = False
        found_trigger = False
        # Build list of actions (everytime, in case variables have changed)
        for content_line in self.content:
            words = re.split(WORD_SPLIT, content_line)
            for klass_name, trigger_format in trigger_map.items():
                trigger_params = params.ParamList(words, trigger_format)
                if trigger_params.valid:  # This is a trigger
                    if found_action:
                        triggers_for_action = []
                        found_action = False
                    klass = globals()[klass_name]
                    trigger = klass(trigger_params.get("rest"), self.name)
                    self.trigger_list.append(trigger)
                    triggers_for_action.append(trigger)
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
            # But actions are only expanded once triggered
            this_action = action.Action(content_line)
            this_action.triggers = triggers_for_action
            self.action_list.append(this_action)
        # And carry out any immediate actions
        for current_action in self.action_list:
            for current_trigger in current_action.triggers:
                current_trigger.reset()
            if current_action.triggered():
                self.data.command_dispatcher.dispatch(current_action, self)

    def update_triggers(self):
        for trigger in self.trigger_list:
            trigger.update()

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
        else:  # first, look for a local tag in the key_list
            new_tag = "%s:%s" % (self.name, in_tag)
            if new_tag in key_list:
                return new_tag
            elif in_tag in key_list:
                return in_tag
        print("Sprite %s not found in scene %s" % (in_tag, self.name))
        return None

    def dump(self):
        print("Scene %s (%s) contains:" % (self.name, "enabled" if self.enabled else "disabled"))
        for line in self.content:
            print(line)

