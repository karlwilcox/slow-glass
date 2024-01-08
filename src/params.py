from defaults import *
import re


class ParamList:
    # parameter specifications are of the form:
    # <TYPE><SEPARATOR><VALUE>
    SEPARATOR = "/"
    # Where type is one of those listed below, and VALUE is either the string to match,
    # or the name to use for the matched parameter
    ARGUMENT_MARKER = ":"   # marks end of commands, start of arguments
    OPTIONAL = "?"          # optional argument, at end of list only, value used as name
    REQUIRED = "+"          # argument must exist, value used as name
    MUSTMATCH = "="         # command or argument word must be present and match value, no parameter created
    CANMATCH = "~"          # if word matches value then a flag is set for IFMATCHED, no parameter created
    IFMATCHED = "&"         # if previous CANMATCH was matched then argument must exist, value is name, else ignore
    GETREST = "*"           # All remaining arguments concatenated as string, value  used as name
    GETLIST = ">"           # All remaining arguments saved as list, value used as name
    CHOICE = "|"            # Like MUSTMATCH but with a list of alternative values
    NUMBER = '#'            # match numbers only, otherwise None, value used as name

    COMMANDS = 1
    ARGUMENTS = 2

    def __init__(self, words, format_spec):
        self.params = {}
        self.command = []
        self.valid = False
        if len(words) < 1:
            return
        if format_spec is None or format_spec == "":
            return
        # First get the format parts
        format_pairs = re.split(WORD_SPLIT, format_spec)
        arg_pos = 0
        match_found = False
        state = ParamList.COMMANDS
        for format_pair in format_pairs:
            if format_pair == ParamList.ARGUMENT_MARKER:
                state = ParamList.ARGUMENTS
                continue
            parts = re.split(ParamList.SEPARATOR, format_pair)
            if len(parts) != 2:
                print("Bad parameter format %s" % format_pair)
                continue
            optionality = parts[0]
            name = parts[1]
            choices = None
            if optionality == ParamList.GETREST:
                self.params[name] = " ".join(words[arg_pos:])
                if len(self.params[name]) < 1:
                    self.params[name] = None
                continue
            if optionality == ParamList.GETLIST:
                self.params[name] = words[arg_pos:]
                continue
            if optionality == ParamList.IFMATCHED and not match_found:
                # only look for this if previous CANMATCH was found
                self.params[name] = None
                continue
            if optionality == ParamList.CHOICE:
                choices = name.split(ParamList.CHOICE)
                name = choices[0]
            step = 1
            if arg_pos < len(words):  # argument is present
                arg = words[arg_pos]
                if state == ParamList.COMMANDS:
                    self.command.append(arg)
                if optionality == ParamList.OPTIONAL or \
                        optionality == ParamList.REQUIRED or \
                        optionality == ParamList.IFMATCHED:
                    match_found = False
                    self.params[name] = arg
                elif optionality == ParamList.MUSTMATCH:
                    match_found = False
                    if not arg == name:
                        if state == ParamList.COMMANDS:
                            return  # not an error, this is not the command you were looking for
                        else:
                            print("Expected: %s" % name)
                    # else do nothing
                elif optionality == ParamList.CANMATCH:
                    if arg == name:
                        match_found = True
                    else:
                        step = 0
                elif optionality == ParamList.CHOICE:
                    choice_found = False
                    for choice in choices:
                        if arg == choice:
                            self.params[name] = choice
                            choice_found = True
                            break
                    if not choice_found:
                        if state == ParamList.COMMANDS:
                            return  # Not an error, this command wasn't found
                        else:
                            print("Expected one of: %s" % ", ".join(choices))
                elif optionality == ParamList.NUMBER:
                    # Always create param, but only match if value is float
                    try:
                        float(words[arg_pos])
                        self.params[name] = words[arg_pos]
                    except ValueError:
                        self.params[name] = None
                        step = 0
                else:
                    print("Bad optionality: %s" % optionality)
                arg_pos += step
            else:  # no input found
                match_found = False
                if optionality == ParamList.REQUIRED or \
                        optionality == ParamList.IFMATCHED:
                    print("Expected value for: %s" % name)
                    self.params[name] = None
                elif optionality == ParamList.MUSTMATCH:
                    if state == ParamList.COMMANDS:
                        return  # not an error, this is not the command you were looking for
                    else:
                        print("Expected word: %s" % name)
                elif optionality == ParamList.CANMATCH:
                    pass
                elif optionality == ParamList.OPTIONAL or \
                        optionality == ParamList.CHOICE:
                    self.params[name] = None
                elif optionality == ParamList.NUMBER:
                    self.params[name] = None
        self.valid = True

    def get(self, key):
        if key in self.params.keys():
            return self.params[key]
        else:
            print("(script) Param key value not found %s" % key)
            return None

    def exists(self, key):
        return key in self.params.keys()

    def as_float(self, key, message=None):
        value = None
        if key in self.params.keys():
            value = self.params[key]
            if value is not None:
                try:
                    value = float(self.params[key])
                    return float(value)
                except ValueError:
                    pass
        if message is not None:
            print("Expected %s: %s" % (message, self.params[key]))
        return None

    def as_int(self, key, message=None):
        value = self.as_float(key, message)
        if value is not None:
            return int(value)
        else:
            return None

    def dump(self):
        for key, value in self.params.items():
            print("%s -> %s" % (key, value))
