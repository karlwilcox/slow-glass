import re, time
from datetime import datetime
from math import floor

import wordtypes
from defaults import *


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


class Duration:
    the_same_time = None

    def __init__(self, time_string):
        # the small parts are strings, if you want a number use as_float
        self.total = 0
        words = re.split(WORD_SPLIT, time_string.lower())
        if "same" in words:
            self.total = Duration.the_same_time
            return
        # look for any number of num / unit pairs
        number = None
        for word in words:
            # words that can before the number
            if number is None:
                if word.lower() in ["and", "&"]:
                    continue
                if word.isnumeric():
                    number = float(word)
                else:
                    number = wordtypes.NumberFromWord(word).value
                if number is None:
                    number = 1
                    continue
            else:  # got a number, look for a unit
                # look for a qualifier first
                fraction = wordtypes.FractionFromWord(word).value
                if fraction is not None:
                    number *= fraction
                    continue
                # words that can go before the unit
                if word.lower() in ["a", "an", "of"]:
                    continue
                unit = wordtypes.UnitFromWord(word).value
                if unit is None:
                    print("Expected a unit: %s" % word)
                    unit = 1
                self.total += number * unit
                number = None
        # if number isn't None we had one left without a unit
        if number is not None:
            self.total += number
        Duration.the_same_time = self.total

    def as_seconds(self):
        return self.total


class Timer:

    def __init__(self):
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.start_time = self.millis()

    @staticmethod
    def millis():
        return time.time() * 1000

    def reset(self):
        self.start_time = self.millis()

    def update(self):
        elapsed = self.millis() - self.start_time
        self.hour = floor(elapsed / (1000 * 60 * 60))
        elapsed -= self.hour * 1000 * 60 * 60
        self.minute = floor(elapsed / (1000 * 60))
        elapsed -= self.minute * 1000 * 60
        self.second = elapsed / 1000

    def as_seconds(self):
        return (self.hour * 60 * 60) + (self.minute * 60) + self.second


class Now(Timer):

    def reset(self):
        pass

    def update(self):
        now = datetime.now()
        self.hour = now.hour
        self.minute = now.minute
        self.second = now.second
