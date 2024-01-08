import re, time
from datetime import datetime
from math import floor

import wordtypes
from defaults import *

# *************************************************************************************************
#
#    ######## #### ##     ## ########  #######  ######## ########     ###    ##    ##
#       ##     ##  ###   ### ##       ##     ## ##       ##     ##   ## ##    ##  ##
#       ##     ##  #### #### ##       ##     ## ##       ##     ##  ##   ##    ####
#       ##     ##  ## ### ## ######   ##     ## ######   ##     ## ##     ##    ##
#       ##     ##  ##     ## ##       ##     ## ##       ##     ## #########    ##
#       ##     ##  ##     ## ##       ##     ## ##       ##     ## ##     ##    ##
#       ##    #### ##     ## ########  #######  ##       ########  ##     ##    ##
#
# **************************************************************************************************


class TimeOfDay:

    def __init__(self, time_string):
        self.second = 0
        self.minute = 0
        self.hour = 0
        try:
            parts = re.split("\\s*:\\s*", time_string)
            if len(parts) == 1:  # assume this means on the hour
                self.hour = int(parts[0])
            elif len(parts) == 2:  # assume hh:mm
                self.hour = int(parts[0])
                self.minutes = int(parts[1])
            else:  # 3 or more, assume hh:mm:ss + ignore rest
                self.hour = int(parts[0])
                self.minute = int(parts[1])
                self.second = int(parts[2])
        except ValueError as e:
            print("Invalid time format %s" % time_string)

# *************************************************************************************************
#
#    ######## #### ##     ## ######## ##     ##    ###    ########  ######  ##     ##
#       ##     ##  ###   ### ##       ###   ###   ## ##      ##    ##    ## ##     ##
#       ##     ##  #### #### ##       #### ####  ##   ##     ##    ##       ##     ##
#       ##     ##  ## ### ## ######   ## ### ## ##     ##    ##    ##       #########
#       ##     ##  ##     ## ##       ##     ## #########    ##    ##       ##     ##
#       ##     ##  ##     ## ##       ##     ## ##     ##    ##    ##    ## ##     ##
#       ##    #### ##     ## ######## ##     ## ##     ##    ##     ######  ##     ##
#
# **************************************************************************************************


class TimeMatch:

    def __init__(self, time_string):
        self.hour = "*"
        self.minute = "*"
        self.second = "*"
        parts = re.split("\\s*:\\s*", time_string)
        if len(parts) == 1:  # assume this means every minute on the second value
            self.second = parts[0]
        elif len(parts) == 2:  # assume this means every hour on the minute & second
            self.second = parts[1]
            self.minute = parts[0]
        else:  # at least 3
            self.second = parts[2]
            self.minute = parts[1]
            self.hour = parts[0]
            if len(parts) > 3:
                print("Unexpected timecode value: %s" % time_string)

# *************************************************************************************************
#
#    ########  ##     ## ########     ###    ######## ####  #######  ##    ##
#    ##     ## ##     ## ##     ##   ## ##      ##     ##  ##     ## ###   ##
#    ##     ## ##     ## ##     ##  ##   ##     ##     ##  ##     ## ####  ##
#    ##     ## ##     ## ########  ##     ##    ##     ##  ##     ## ## ## ##
#    ##     ## ##     ## ##   ##   #########    ##     ##  ##     ## ##  ####
#    ##     ## ##     ## ##    ##  ##     ##    ##     ##  ##     ## ##   ###
#    ########   #######  ##     ## ##     ##    ##    ####  #######  ##    ##
#
# **************************************************************************************************


class Duration:
    the_same_time = None

    def __init__(self, time_string):
        # the small parts are strings, if you want a number use as_float
        self.total = 0
        if len(time_string) == 0:
            return
        words = re.split(WORD_SPLIT, time_string.lower())
        if "same" in words:
            self.total = Duration.the_same_time
            return
        # look for any number of num / unit pairs
        number = None
        unit = 1
        word_count = 0
        while word_count < len(words):
            word = words[word_count]
            increment = 1
            # words that can before the number
            if number is None:
                if word.lower() in ["and", "&"]:
                    pass
                elif re.match("[0-9]+\\.?[0-9]*", word.lower()):
                    number = float(word)
                else:
                    number = wordtypes.NumberFromWord(word).value
                if number is None:
                    number = 1
                    increment = 0
            else:  # got a number, look for a unit
                # look for a qualifier first
                fraction = wordtypes.FractionFromWord(word).value
                if fraction is not None:
                    number *= fraction
                # words that can go before the unit
                elif word.lower() in ["a", "an", "of"]:
                    pass
                else:
                    unit = wordtypes.UnitFromWord(word).value
                    if unit is None:
                        print("Expected a unit: %s" % word)
                        unit = 1
                self.total += number * unit
                number = None
            word_count += increment
        # if number isn't None we had one left without a unit
        if number is not None:
            self.total += number
        Duration.the_same_time = self.total

    def as_seconds(self):
        return self.total

    def as_millis(self):
        return self.total * 1000

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


class Speed:
    the_same_speed = None

    def __init__(self, speed_string):
        words = re.split(WORD_SPLIT, speed_string.lower())
        if "same" in words:
            self.total = Speed.the_same_speed
            return
        # look for a number
        number = None
        word_count = 0
        if words[word_count].isnumeric():
            number = float(words[word_count])
        else:
            number = wordtypes.NumberFromWord(words[word_count]).value
        if number is None:
            print("Expected a number: %s" % words[word_count])
            number = 0
        # Got a number, look for units
        unit_divisor = 1  # assume pixels per second
        if ("pps", "secs", "s", "seconds", "second") in words:
            unit_divisor = 1
        elif ("ppm", "min", "minutes", "minute", "m") in words:
            unit_divisor = 60
        elif ("pph", "hr", "hours", "hour", "h") in words:
            unit_divisor = 3600
        self.speed = number / unit_divisor

    def as_pps(self):
        return self.speed

# *************************************************************************************************
#
#    ######## #### ##     ## ######## ########
#       ##     ##  ###   ### ##       ##     ##
#       ##     ##  #### #### ##       ##     ##
#       ##     ##  ## ### ## ######   ########
#       ##     ##  ##     ## ##       ##   ##
#       ##     ##  ##     ## ##       ##    ##
#       ##    #### ##     ## ######## ##     ##
#
# **************************************************************************************************


class Timer:

    def __init__(self):
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.millisecond = 0
        self.start_time = self.millis()

    @staticmethod
    def millis():
        return time.time() * 1000

    def reset(self):
        self.start_time = self.millis()

    def update(self):
        elapsed = self.millis() - self.start_time
        self.millisecond = elapsed
        self.hour = floor(elapsed / (1000 * 60 * 60))
        elapsed -= self.hour * 1000 * 60 * 60
        self.minute = floor(elapsed / (1000 * 60))
        elapsed -= self.minute * 1000 * 60
        self.second = elapsed / 1000

    def as_seconds(self):
        return (self.hour * 60 * 60) + (self.minute * 60) + self.second

# *************************************************************************************************
#
#    ##    ##  #######  ##      ##
#    ###   ## ##     ## ##  ##  ##
#    ####  ## ##     ## ##  ##  ##
#    ## ## ## ##     ## ##  ##  ##
#    ##  #### ##     ## ##  ##  ##
#    ##   ### ##     ## ##  ##  ##
#    ##    ##  #######   ###  ###
#
# **************************************************************************************************


class Now(Timer):

    def reset(self):
        pass

    def update(self):
        now = datetime.now()
        self.hour = now.hour
        self.minute = now.minute
        self.second = now.second

# *************************************************************************************************
#
#     ######  #### ######## ########
#    ##    ##  ##       ##  ##
#    ##        ##      ##   ##
#     ######   ##     ##    ######
#          ##  ##    ##     ##
#    ##    ##  ##   ##      ##
#     ######  #### ######## ########
#
# **************************************************************************************************


class Size:
    the_same_width = None
    the_same_height = None

    def __init__(self, size_string):
        self.width = None
        self.height = None
        words = re.split(WORD_SPLIT, size_string.lower())
        if "same" in words:
            self.width = Size.the_same_width
            self.height = Size.the_same_height
            return
        # look for a number
        word_count = 0
        measure = "width"
        while word_count < len(words):
            if words[word_count].startswith("h"):
                measure = "height"
            elif words[word_count].startswith("w"):
                measure = "width"
            elif words[word_count] in ("by", "and"):
                pass
            elif words[word_count].isnumeric():
                if measure == "width":
                    self.width = int(words[word_count])
                    measure = "height"
                else:
                    self.height = int(words[word_count])
                    self.measure = "width"
            word_count += 1

    def as_tuple(self):
        return self.width, self.height
