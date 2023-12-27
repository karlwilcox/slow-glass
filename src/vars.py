import re
from datetime import datetime

import pygame

from defaults import *
import random

from lib.simpleeval import simple_eval


class Variables:
    safe = True

    def __init__(self, data):
        # set up some variables that might not be populated until later
        self.vars = {"KEY": None, "LASTKEY": None, "CLICKX": 0, "CLICKY": 0, "TRIGGER": None, "HEMISPHERE" : HEMISPHERE}
        self.data = data
        Variables.safe = SAFE_EVALUATION

    def set_var(self, name, value, scene=TOP_LEVEL):
        # check for writable built-ins first
        # none at present
        if name[0] == ":":  # reference to top level variable
            scene = TOP_LEVEL
            name = name[1:]
        if scene != TOP_LEVEL:
            name = "%s:%s" % (scene, name)
        self.vars[name] = value

    def get_var(self, in_name, scene):
        height = self.data.options["height"]
        width = self.data.options["width"]
        prop = None
        if "." in in_name:
            name, prop = in_name.split(".")
        else:
            name = in_name
        value = None
        now = datetime.now()
        # Built-ins first
        if name == "SECOND":
            value = now.second
        elif name == "MINUTE":
            value = now.minute
        elif name == "HOUR":
            value = now.hour
        elif name == "DAY":
            value = now.day
        elif name == "DAYNAME":
            value = now.strftime("%A")
        elif name == "WEEKDAY":
            value = now.weekday()
        elif name == "MONTH":
            value = now.month
        elif name == "MONTHNAME":
            value = now.strftime("%B")
        elif name == "YEAR":
            value = now.year
        elif name == "SEASON":
            mon = now.month
            northern = self.vars["hemisphere"].lower().startswith("n")
            if mon <= 2 or mon >= 12:
                value = "winter" if northern else "summer"
            elif mon <= 5:
                value = "spring" if northern else "autumn"
            elif mon <= 8:
                value = "summer" if northern else "winter"
            else:
                value = "autumn" if northern else "spring"
        elif name.startswith("MOUSE"):
            x, y = pygame.mouse.get_pos()
            if name.endswith("X"):
                value = x
            elif name.endswith("Y"):
                value = y
        elif name == "FRAMERATE":
            value = FRAMERATE
        elif name == "WIDTH":
            value = width
        elif name == "HEIGHT":
            value = height
        elif name in ["CENTERX", "CENTREX"]:
            value = width / 2
        elif name in ["CENTERY", "CENTREY"]:
            value = height / 2
        elif name == "PERCENT":
            value = random.randint(0, 100)
        elif name == "CHANCE":
            value = random.random()
        elif name == "RANDOMX":
            value = random.randrange(0, width - 1)
        elif name == "RANDOMY":
            value = random.randrange(0, height - 1)
        # OK, let's see if it is a sprite
        if prop is not None:
            tag = self.data.scenes[scene].resolve_tag(name, scene.sprites.keys())
            if tag is not None:
                if prop.startswith("x"):
                    value = self.data.sprites.get_sprite(tag).x.value()
                elif prop.startswith("y"):
                    value = self.data.sprites.get_sprite(tag).y.value()
                elif prop.startswith("w"):
                    value = self.data.sprites.get_sprite(tag).w.value()
                elif prop.startswith("h"):
                    value = self.data.sprites.get_sprite(tag).h.value()
                elif prop.startswith("s"):
                    value = self.data.sprites.get_sprite(tag).get_speed()
        # None of the above, look for a user variable
        if value is None:
            if name[0] == ":":
                scene = TOP_LEVEL
                name = name[1:]
            if ":" not in name and scene != TOP_LEVEL:  # name already qualified
                name = "%s:%s" % (scene, name)
            if name in self.vars.keys():
                value = self.vars[name]
        if value is None:
            print("Variable not found: %s" % name)
            string_value = "???"
        else:
            string_value = f"{value}"
        return value is not None, string_value

    def purge(self, scene):
        for var_name in self.vars.keys():
            if var_name.startswith(scene + ":"):
                del self.vars[var_name]

    def expand_all(self, line, scene):
        can_eval = True
        if len(line) < 2:
            return line
        var_name = ""
        new_line = ""
        pos = 0
        reading_name = False
        in_braces = False
        while pos < len(line):
            char = line[pos]
            valid = True
            lookahead = None if pos + 1 >= len(line) else line[pos + 1]
            if char == "\\":  # only special before $
                if lookahead == "$":
                    new_line += "$"
                    pos += 1
                else:
                    new_line += char
            elif char == "$":
                reading_name = True
            elif reading_name and char == "{":
                in_braces = True
            elif in_braces and char == "}":
                valid, value = self.get_var(var_name, scene)
                new_line += value
                in_braces = False
                reading_name = False
                var_name = ""
            elif reading_name and not (char.isalnum() or char in "._"):
                valid, value = self.get_var(var_name, scene)
                new_line += value
                new_line += char
                reading_name = False
                var_name = ""
            elif reading_name:
                var_name += char
            else:
                new_line += char
            pos += 1
            if not valid:
                can_eval = False
        if len(var_name) > 0:
            valid, value = self.get_var(var_name, scene)
            new_line += value
            if not valid:
                can_eval = False
        return can_eval, new_line

    @staticmethod
    def evaluate(line):
        if len(line) < 2:
            return line
        new_line = ""
        in_expression = False
        expression = ""
        bracket_count = 0
        pos = 0
        while pos < len(line):
            char = line[pos]
            lookahead = None if pos + 1 >= len(line) else line[pos + 1]
            if char == "\\":  # only special before brackets
                if lookahead in "()":
                    new_line += lookahead
                    pos += 1
                else:
                    new_line += char
            elif char == "(":
                in_expression = True
                expression += char
                bracket_count += 1
            elif in_expression and char == ")":
                bracket_count -= 1
                expression += char
                if bracket_count == 0:
                    in_expression = False
                    if Variables.safe:
                        result = simple_eval(expression)
                    else:
                        result = eval(expression)
                    new_line += f"{result}"
                    expression = ""
            elif in_expression:
                expression += char
            else:
                new_line += char
            pos += 1
        return new_line

    @staticmethod
    def true_or_false(word):
        if word is None:
            return False
        return not (word.lower() in ["false", "none", "no"] or word[0] == "0")

    @staticmethod
    def conditional(line):
        if len(line) < 4:
            return line
        if line.lower().startswith("if "):
            if_statement, condition, rest = re.split(WORD_SPLIT, line, 2)
            if Variables.true_or_false(condition):
                return rest
            else:
                return None
        return line

    def dump(self, scene=TOP_LEVEL):
        print("vars in scene: %s" % scene)
        for var_name in self.vars.keys():
            if scene == TOP_LEVEL:  # dump everything
                print("%s => %s" % (var_name, self.vars[var_name]))
            elif var_name.startswith(scene + ":"):  # only this scene
                print("%s => %s" % (var_name, self.vars[var_name]))
