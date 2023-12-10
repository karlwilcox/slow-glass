# standard libraries
import os
import re
# local files
from scene import Scene
from defaults import *


def read(data, filename=None, folder=None):
    if filename is None:
        if "args" in data.options.keys() and len(data.options["args"]) > 0:
            filename = data.options["args"][0]  # TODO read file, or if folder read that
        else:
            filename = DEFAULT_FILENAME
    if folder is None:
        if "dir" in data.options.keys() and data.options["dir"] is not None:
            folder = data.options["dir"]
        else:
            folder = DEFAULT_FOLDER
    line_count = 0
    in_comment = False
    current_scene = None
    holding = []
    top_level = []
    filename = os.path.join(folder, filename)
    try:
        script_file = open(filename)
    except FileNotFoundError:
        print("No script file file at: %s" % filename)
        exit(-1)
    else:
        with script_file as file:
            while line := file.readline():
                line_count += 1
                line = line.strip()
                # Ignore comment lines
                if len(line) < 2 or line.startswith('#'):
                    continue
                if in_comment and line.endswith("*/"):
                    in_comment = False
                    continue
                if line.startswith("/*"):
                    in_comment = True
                    continue
                if in_comment:
                    continue
                # Any line without alphabetic characters can be ignored
                if not re.match('[a-zA-Z]+', line):
                    continue
                # Actual processing starts here
                words = re.split(WORD_SPLIT, line.lower())
                # Ignore any initial and
                if words[0] == "and":
                    words.pop(0)
                # Scene management commands
                command = words[0]
                argument = None if len(words) < 2 else words[1]
                if command == "scene":
                    if argument is None:
                        print("Expected scene name on line %d" % line_count)
                    else:
                        current_scene = argument
                elif command == "end":
                    if argument == "scene":
                        if len(holding) > 0:
                            data.scenes[current_scene] = Scene(current_scene, folder, holding, data)
                            holding = []
                        current_scene = None
                    elif argument == "file":  # same as finish
                        break
                    else:
                        print ("end must be followed by scene or file")
                elif command == "include":
                    if argument is None:
                        print("Expected filename for include on line %d" % line_count)
                    else:
                        read(argument, data)
                elif command == "finish":
                    break
                else:  # must be an action, trigger or condition
                    if current_scene is None:
                        top_level.append(line)
                    else:
                        holding.append(line)
            # end while
            # Add any incomplete scene
            if len(holding) > 0:
                data.scenes[current_scene] = Scene(current_scene, folder, holding, data)
            # and the top_level
            if len(top_level) > 0:
                data.scenes[TOP_LEVEL] = Scene(TOP_LEVEL, folder, top_level, data)
            else:
                print("No top level actions, nothing will happen!")
