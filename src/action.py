# standard libraries
# local modules
import re
from defaults import *


class Action:
    variables = None

    def __init__(self, content_line):
        self.content_line = content_line
        self.expanded_line = ""
        self.task = ""
        self.args = ""
        self.triggers = []
        self.complete = False

    def triggered(self):
        for trigger in self.triggers:
            Action.variables.set_var("TRIGGER", trigger.__class__.__name__)
            if trigger.triggered:
                return True
        return False

    def conditional(self, variables, scene_name):
        expanded_args = variables.expand_all(self.content_line, scene_name)
        # Expand expressions
        evaluated_args = variables.evaluate(expanded_args)
        # Test conditionals
        conditional_args = variables.conditional(evaluated_args)
        if conditional_args is not None:
            self.expanded_line = conditional_args
            # if " " in conditional_args:
            #     self.task, self.args = re.split(WORD_SPLIT, conditional_args, 1)
            # else:
            #     self.task = conditional_args
            return True
        else:
            return False

    def dump(self):
        status = "(completed)" if self.complete else "(available)"
        trigger_list = ""
        for trigger in self.triggers:
            trigger_list += trigger.__class__.__name__ + " "
        print("%s: %s %s" % (self.content_line, status, trigger_list))
