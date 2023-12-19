import re
from datetime import datetime

import pygame

from defaults import *
import random


# from lib.simpleeval import simple_eval


class Variables:

    def __init__(self, data):
        # set up some variables that might not be populated until later
        self.vars = {"KEY": None, "LASTKEY": None, "CLICKX": 0, "CLICKY": 0, "TRIGGER": None}
        self.data = data

    def set_var(self, name, value, scene=TOP_LEVEL):
        # check for writable built-ins first
        # none at present
        if name[0] == ":":  # reference to top level variable
            scene = TOP_LEVEL
            name = name[1:]
        if scene != TOP_LEVEL:
            name = "%s:%s" % (scene, name)
        self.vars[name] = value

    def get_var(self, name, scene):
        height = self.data.options["height"]
        width = self.data.options["width"]
        value = "???"
        now = datetime.now()
        # Built-ins first
        if name == "SECOND":
            value = now.second
        elif name == "MINUTE":
            value = now.minute
        elif name == "HOUR":
            value = now.hour
            # TODO add more date variables
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
        # None of the above, look for a user variable
        else:
            if name[0] == ":":
                scene = TOP_LEVEL
                name = name[1:]
            if ":" not in name and scene != TOP_LEVEL:  # name already qualified
                name = "%s:%s" % (scene, name)
            if name in self.vars.keys():
                value = self.vars[name]
            else:
                print("Variable not found: %s" % name)
        string_value = f"{value}"
        return string_value

    def purge(self, scene):
        for var_name in self.vars.keys():
            if var_name.startswith(scene + ":"):
                del self.vars[var_name]

    def expand_all(self, line, scene):
        if len(line) < 2:
            return line
        var_name = ""
        new_line = ""
        pos = 0
        reading_name = False
        in_braces = False
        while pos < len(line):
            char = line[pos]
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
                new_line += self.get_var(var_name, scene)
                in_braces = False
                reading_name = False
                var_name = ""
            elif reading_name and not char.isidentifier():
                new_line += self.get_var(var_name, scene)
                new_line += char
                reading_name = False
                var_name = ""
            elif reading_name:
                var_name += char
            else:
                new_line += char
            pos += 1
        if len(var_name) > 0:
            new_line += self.get_var(var_name, scene)
        return new_line

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
                    # result = simple_eval(expression)
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
