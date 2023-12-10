#!/usr/bin/python
# standard libraries
import random

import pygame, sys
from pygame.locals import *
from datetime import datetime
# local modules
import script, globals, sprites, timing
import commands, args, triggers
from defaults import *


def do_actions(data):
    for name, scene in data.scenes.items():
        if scene.enabled:
            scene.update_triggers()  # update all triggers once this frame
            for current_action in scene.action_list:
                # because one trigger may cause multiple actions
                if not current_action.complete and current_action.triggered():
                    if current_action.conditional(data.vars, scene.name):
                        data.command_dispatcher.dispatch(current_action, scene)
            # then clear them ready for next time
            scene.clear_triggers()


def handle_events(data):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            triggers.Trigger.keycode = event.unicode
            triggers.Trigger.key_pressed = True
            data.vars.set_var("LASTKEY", event.unicode)
            data.vars.set_var("KEY", event.unicode)
        elif event.type == pygame.KEYUP:
            data.vars.set_var("KEY", None)
        elif event.type == pygame.MOUSEBUTTONUP:
            triggers.Trigger.mouse_clicked = True
            triggers.Trigger.click_x, triggers.Trigger.click_y = event.pos
            data.vars.set_var("CLICKX", event.pos[0])
            data.vars.set_var("CLICKY", event.pos[1])


def main():
    # Initialisation coda
    random.seed()
    globalData = globals.Globals()
    args.parse_args(globalData)
    commands.Command.globalData = globalData
    sprites.SpriteItem.globalData = globalData
    triggers.Trigger.variables = globalData.vars
    script.read(globalData)
    globalData.scenes[TOP_LEVEL].start()
    pygame.init()
    pygame.mixer.init()
    if globalData.options["rotate"]:
        screen = pygame.display.set_mode((globalData.options["height"],
                                          globalData.options["width"]))
    else:
        screen = pygame.display.set_mode((globalData.options["width"],
                                          globalData.options["height"]))
    grey = pygame.Color(127, 127, 127)
    # Main loop
    last_second = 0
    then = 0
    tick_rate = 1000 / FRAMERATE
    while True:
        screen.fill(grey)
        handle_events(globalData)
        this_second = datetime.now().second
        if this_second != last_second:
            last_second = this_second
            do_actions(globalData)
        now = timing.Timer.millis()
        if now - then >= tick_rate:
            globalData.sprites.display_all(screen)
            pygame.display.update()
            then = now


# Processing starts here
main()
