# From standard libraries

import timing


class Trigger:
    key_pressed = False
    keycode = None
    mouse_clicked = False
    click_x = 0
    click_y = 0
    variables = None

    def __init__(self, content_line, scene_name):
        self.triggered = False
        self.content_line = content_line
        self.scene_name = scene_name
        self.expanded = None
        self.expired = False

    # expand trigger conditions when needed (mostly when we set them up)
    def expand(self):
        temp = self.variables.expand_all(self.content_line, self.scene_name)
        self.expanded = self.variables.evaluate(temp)

    def clear(self):
        self.triggered = False

    def reset(self):
        pass

    def update(self):
        pass


# *************************************************************************************************
#
#     ######  ########    ###    ########  ########
#    ##    ##    ##      ## ##   ##     ##    ##
#    ##          ##     ##   ##  ##     ##    ##
#     ######     ##    ##     ## ########     ##
#          ##    ##    ######### ##   ##      ##
#    ##    ##    ##    ##     ## ##    ##     ##
#     ######     ##    ##     ## ##     ##    ##
#
# **************************************************************************************************


class Start(Trigger):
    def update(self):
        if not self.expired:
            self.triggered = True
            # Only triggers once
            self.expired = True


# *************************************************************************************************
#
#     #######  ##    ## ##    ## ######## ##    ##
#    ##     ## ###   ## ##   ##  ##        ##  ##
#    ##     ## ####  ## ##  ##   ##         ####
#    ##     ## ## ## ## #####    ######      ##
#    ##     ## ##  #### ##  ##   ##          ##
#    ##     ## ##   ### ##   ##  ##          ##
#     #######  ##    ## ##    ## ########    ##
#
# **************************************************************************************************


class OnKey(Trigger):
    trigger_key = None

    def __init__(self, words, scene):
        super().__init__(words, scene)
        self.expand()
        if self.expanded is None or len(self.expanded) < 1:
            self.trigger_key = None
        else:
            self.trigger_key = self.expanded[0]

    def update(self):
        if Trigger.key_pressed:
            if self.trigger_key is None:  # trigger on every key press
                self.triggered = True
                # Consume this keypress
                Trigger.key_pressed = False
            else:  # only trigger if matched
                if self.trigger_key == self.keycode:
                    self.triggered = True
                    # Consume this keypress
                    Trigger.key_pressed = False

# *************************************************************************************************
#
#       ###    ######## ######## ######## ########
#      ## ##   ##          ##    ##       ##     ##
#     ##   ##  ##          ##    ##       ##     ##
#    ##     ## ######      ##    ######   ########
#    ######### ##          ##    ##       ##   ##
#    ##     ## ##          ##    ##       ##    ##
#    ##     ## ##          ##    ######## ##     ##
#
# **************************************************************************************************


class After(Trigger):

    def __init__(self, words, scene):
        super().__init__(words, scene)
        self.timer = timing.Timer()
        self.expand()
        self.time_value = timing.Duration(self.expanded)

    def update(self):
        if not self.expired:
            self.timer.update()
            # Note the condition, we trigger After the second has elapsed
            self.triggered = self.timer.as_seconds() > self.time_value.as_seconds()
            if self.triggered:
                # Only triggers once
                self.expired = True


# *************************************************************************************************
#
#       ###    ######## ######## #### ##     ## ########
#      ## ##      ##       ##     ##  ###   ### ##
#     ##   ##     ##       ##     ##  #### #### ##
#    ##     ##    ##       ##     ##  ## ### ## ######
#    #########    ##       ##     ##  ##     ## ##
#    ##     ##    ##       ##     ##  ##     ## ##
#    ##     ##    ##       ##    #### ##     ## ########
#
# **************************************************************************************************


class AtTime(Trigger):

    def __init__(self, words, scene):
        super().__init__(words, scene)
        self.timer = timing.Now()
        self.expand()
        self.time_value = timing.TimeOfDay(self.expanded)

    def update(self):
        if not self.expired:
            self.timer.update()
            self.triggered = self.timer.hour == self.time_value.hour and \
                             self.timer.minute == self.time_value.minute and \
                             self.timer.second >= self.time_value.second
            if self.triggered:
                self.expired = True  # only happens once


# *************************************************************************************************
#
#    ########    ###     ######  ##     ##
#    ##         ## ##   ##    ## ##     ##
#    ##        ##   ##  ##       ##     ##
#    ######   ##     ## ##       #########
#    ##       ######### ##       ##     ##
#    ##       ##     ## ##    ## ##     ##
#    ######## ##     ##  ######  ##     ##
#
# **************************************************************************************************


class EachTime(Trigger):

    def __init__(self, words, scene):
        super().__init__(words, scene)
        self.timer = timing.Now()
        self.expand()
        self.time_value = timing.TimeMatch(self.expanded)

    def update(self):
        self.timer.update()
        self.triggered = (self.time_value.hour == "*" or self.timer.hour == int(self.time_value.hour)) and \
                         (self.time_value.minute == "*" or self.timer.minute == int(self.time_value.minute)) and \
                         (self.time_value.second == "*" or self.timer.second == int(self.time_value.second))


# *************************************************************************************************
#
#    ######## ##     ## ######## ########  ##    ##
#    ##       ##     ## ##       ##     ##  ##  ##
#    ##       ##     ## ##       ##     ##   ####
#    ######   ##     ## ######   ########     ##
#    ##        ##   ##  ##       ##   ##      ##
#    ##         ## ##   ##       ##    ##     ##
#    ########    ###    ######## ##     ##    ##
#
# **************************************************************************************************


class Every(Trigger):

    def __init__(self, words, scene):
        super().__init__(words, scene)
        self.timer = timing.Timer()
        self.expand()
        self.time_value = timing.Duration(self.expanded)

    def update(self):
        self.timer.update()
        self.triggered = self.timer.as_seconds() > self.time_value.as_seconds()
        if self.triggered:
            self.timer.reset()

# *************************************************************************************************
#
#     #######  ##    ##  ######  ##       ####  ######  ##    ##
#    ##     ## ###   ## ##    ## ##        ##  ##    ## ##   ##
#    ##     ## ####  ## ##       ##        ##  ##       ##  ##
#    ##     ## ## ## ## ##       ##        ##  ##       #####
#    ##     ## ##  #### ##       ##        ##  ##       ##  ##
#    ##     ## ##   ### ##    ## ##        ##  ##    ## ##   ##
#     #######  ##    ##  ######  ######## ####  ######  ##    ##
#
# **************************************************************************************************


class OnClick(Trigger):
    rect = None

    def __init__(self, words, scene):
        super().__init__(words, scene)
        self.expand()

    def update(self):
        if Trigger.mouse_clicked:
            self.triggered = True
            # Consume this keypress
            Trigger.mouse_clicked = False

# *************************************************************************************************
#
#    ##      ## ##     ## ######## ##    ##
#    ##  ##  ## ##     ## ##       ###   ##
#    ##  ##  ## ##     ## ##       ####  ##
#    ##  ##  ## ######### ######   ## ## ##
#    ##  ##  ## ##     ## ##       ##  ####
#    ##  ##  ## ##     ## ##       ##   ###
#     ###  ###  ##     ## ######## ##    ##
#
# **************************************************************************************************


class When(Trigger):

    def __init__(self, words, scene):
        super().__init__(words, scene)

    def update(self):
        self.expand()
        if self.variables.true_or_false(self.expanded):
            # print("it was true")
            self.triggered = True
