#!/usr/bin/python
# standard libraries
import random
import inspect

import pygame, sys
from pygame.locals import *

import action
# local modules
import script, globals, sprites, timing
import commands, args, triggers
from defaults import *


def do_actions(data, millis):
    for name, scene in data.scenes.items():
        if scene.enabled:
            scene.update_triggers(millis)  # update all triggers once this frame
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


def is_relevant(obj):
    """Filter for the inspector to filter out non user defined functions/classes"""
    if hasattr(obj, '__name__') and obj.__name__ == 'type':
        return False
    if hasattr(obj, '__name__') and obj.__name__ == '__init__':
        return False
    if inspect.isfunction(obj) or inspect.isclass(obj) or inspect.ismethod(obj):
        return True


def print_docs(module):
    flag = True

    for child in inspect.getmembers(module, is_relevant):
        if not flag:
            print('\n')
        flag = False  # To avoid the newlines at top of output
        doc = inspect.getdoc(child[1])
        if doc:
            print(child[0], doc, sep='\n')

        if inspect.isclass(child[1]):
            for grandchild in inspect.getmembers(child[1], is_relevant):
                doc = inspect.getdoc(grandchild[1])
                if doc:
                    doc = doc.replace('\n', '\n    ')
                    print('\n    ' + grandchild[0], doc, sep='\n    ')


def print_help(data):
    print_docs(triggers)
    print_docs(commands)


def main():
    # Initialisation coda
    random.seed()
    globalData = globals.Globals()
    args.parse_args(globalData)
    if globalData.options["help"]:
        print_help(globalData)
        exit(0)
    commands.Command.globalData = globalData
    sprites.SpriteItem.globalData = globalData
    triggers.Trigger.variables = globalData.vars
    action.Action.variables = globalData.vars
    script.read(globalData)
    globalData.scenes[TOP_LEVEL].start()
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((globalData.options["width"],
                                      globalData.options["height"]))
    window = pygame.Surface((globalData.options["width"], globalData.options["height"]))
    grey = pygame.Color(127, 127, 127)
    clock = pygame.time.Clock()
    # Main loop
    while True:
        window.fill(grey)
        handle_events(globalData)
        do_actions(globalData, timing.Timer.millis())
        clock.tick(FRAMERATE)
        globalData.sprites.display_all(window)
        screen.blit(window, (0, 0))
        pygame.display.update()


# Processing starts here
main()
