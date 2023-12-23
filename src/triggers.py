# From standard libraries

import timing

# *************************************************************************************************
#
#    ######## ########  ####  ######    ######   ######## ########
#       ##    ##     ##  ##  ##    ##  ##    ##  ##       ##     ##
#       ##    ##     ##  ##  ##        ##        ##       ##     ##
#       ##    ########   ##  ##   #### ##   #### ######   ########
#       ##    ##   ##    ##  ##    ##  ##    ##  ##       ##   ##
#       ##    ##    ##   ##  ##    ##  ##    ##  ##       ##    ##
#       ##    ##     ## ####  ######    ######   ######## ##     ##
#
# **************************************************************************************************


class Trigger:
    """
    Any number of triggers can be associated with any number of commands. Trigger types are
    described below. The type of trigger which caused the command to be run is available
    in the variable $TRIGGER
    """
    key_pressed = False
    keycode = None
    mouse_clicked = False
    click_x = 0
    click_y = 0
    variables = None
    next_update = 0

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

    def test_update(self, millis):
        if self.next_update < millis:
            self.update(millis)

    def update(self, millis):
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
    """
    begin
    All associated commands are run once only when the scene starts (or the program starts, if this
    trigger is not in a scene.
    No arguments
    """

    def update(self, millis):
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
    """
    on key <key>
    The associated commands are run when the <key> is pressed (strictly speaking, sometime during the
    second following the key press. Commands are run every time the key is pressed, but never more than
    once per second. The actual key pressed is available in the variable $LASTKEY
    Arguments: Any printable key (the space bar cannot be used a key at the moment)
    """
    trigger_key = None

    def __init__(self, words, scene):
        super().__init__(words, scene)
        self.expand()
        if self.expanded is None or len(self.expanded) < 1:
            self.trigger_key = None
        else:
            self.trigger_key = self.expanded[0]

    def update(self, millis):
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
    """
    after <duration>
    Commands are run once, when <duration> seconds have elapsed after the scene has started
    Arguments: See Duration
    """

    def __init__(self, words, scene):
        super().__init__(words, scene)
        self.timer = timing.Timer()
        self.expand()
        self.time_value = timing.Duration(self.expanded)

    def update(self, millis):
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
    """
    at <time-of-day>
    Commands are run once when time the clock face time matches the time of day given
    """

    def __init__(self, words, scene):
        super().__init__(words, scene)
        self.timer = timing.Now()
        self.expand()
        self.time_value = timing.TimeOfDay(self.expanded)

    def update(self, millis):
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
    """
    each <time-of-day-pattern>
    Commands are run each time the clock face time matches the time of day pattern
    Arguments: see TimeMatch
    """

    def __init__(self, words, scene):
        super().__init__(words, scene)
        self.timer = timing.Now()
        self.expand()
        self.time_value = timing.TimeMatch(self.expanded)

    def update(self, millis):
        self.timer.update()
        self.triggered = (self.time_value.hour == "*" or self.timer.hour == int(self.time_value.hour)) and \
                         (self.time_value.minute == "*" or self.timer.minute == int(self.time_value.minute)) and \
                         (self.time_value.second == "*" or self.timer.second == int(self.time_value.second))
        if self.triggered:
            # Only need to check this once per second
            self.next_update = millis + 1000


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
    """
    every <duration>
    Commands are run every <duration> seconds after the scene is started
    Arguments: See Duration
    """

    def __init__(self, words, scene):
        super().__init__(words, scene)
        self.timer = timing.Timer()
        self.expand()
        self.time_value = timing.Duration(self.expanded)

    def update(self, millis):
        self.timer.update()
        self.triggered = self.timer.millisecond > self.time_value.as_millis()
        if self.triggered:
            self.timer.reset()
            if self.time_value.as_seconds() >= 1:
                self.next_update = millis + self.time_value.as_millis()


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
    """
    onclick
    Commands are run any mouse button is clicked (might be changed later...). Commands are never
    run more often than once per second. The coordinates of the mouse at the moment it was clicked
    are available in the variables $CLICKX and $CLICKY (absolute window coordinates)
    Arguments: None at present
    """
    rect = None

    def __init__(self, words, scene):
        super().__init__(words, scene)
        self.expand()

    def update(self, millis):
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
    """
    when (expression)
    Commands are run when expression evaluates to True. The expression is evaluated once per second
    Expression is any valid Python code but must be fully enclosed in round brackets (may be restricted later)
    Slow glass variables will be substituted before the expression is evaluated.
    """

    def __init__(self, words, scene):
        super().__init__(words, scene)

    def update(self, millis):
        self.expand()
        if self.variables.true_or_false(self.expanded):
            self.triggered = True
