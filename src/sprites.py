import pygame
from defaults import *


class SpriteItem:
    globalData = None

    class Adjustable:
        instances = []

        def __init__(self, in_value, min_value=float('-inf'), max_value=float('inf')):
            self.current_value = in_value
            self.target_value = in_value
            self.delta_value = 0.0
            self.lower_limit = min_value
            self.upper_limit = max_value

        def value(self):
            return self.current_value

        def set_target_value(self, target_value, seconds=0):
            if target_value is None:
                return
            target_value = target_value if target_value > self.lower_limit else self.lower_limit
            target_value = target_value if target_value < self.upper_limit else self.upper_limit
            self.target_value = target_value
            if seconds is None or seconds < 0.001:
                self.current_value = target_value
                self.delta_value = 0
            else:
                self.delta_value = (target_value - self.current_value) / (seconds * FRAMERATE)
            self.instances.append(self)

        def update_value(self):
            if abs(self.current_value - self.target_value) > abs(self.delta_value):
                self.current_value += self.delta_value
            else:
                self.delta_value = 0

    # End inner class

    def __init__(self, tag, scene, centre_x, centre_y, width=None, height=None, depth=0):
        self.tag = tag
        self.scene = scene
        self.x = self.Adjustable(centre_x)
        self.y = self.Adjustable(centre_y)
        self.image = SpriteItem.globalData.images[tag]
        w = width if width is not None else self.image.surface.get_width()
        h = height if height is not None else self.image.surface.get_height()
        self.w = self.Adjustable(w)
        self.h = self.Adjustable(h)
        self.rot = self.Adjustable(0, -360, 360)
        self.visible = False

    def move(self, new_x, new_y, seconds):
        self.x.set_target_value(new_x, seconds)
        self.y.set_target_value(new_y, seconds)

    def resize(self, new_width, new_height, seconds):
        self.w.set_target_value(new_width, seconds)
        self.h.set_target_value(new_height, seconds)

    def scale(self, width_pct, height_pct, seconds):
        self.w.set_target_value(self.w.value() * (width_pct / 100), seconds)
        self.h.set_target_value(self.h.value() * (height_pct / 100), seconds)

    def turn_to(self, angle, seconds):
        self.rot.set_target_value(angle, seconds)

    def turn_by(self, angle, seconds):
        self.rot.set_target_value(self.rot.value() + angle, seconds)

    def display(self, screen):
        if not self.visible:
            return
        scaled_image = pygame.transform.scale(self.image.surface, (self.w.value(), self.h.value()))
        if self.rot.value() != 0:
            scaled_image = pygame.transform.rotate(scaled_image, self.rot.value() * -1)
        if self.globalData.options["rotate"]:
            position = pygame.Rect(screen.get_width() - (self.y.value() - (self.h.value() / 2)),
                                   self.x.value() - (self.w.value() / 2),
                                   self.h.value(), self.w.value())
            screen.blit(pygame.transform.rotate(scaled_image, -90), position)
        else:
            position = pygame.Rect(self.x.value() - (self.w.value() / 2),
                                   self.y.value() - (self.h.value() / 2),
                                   self.w.value(), self.h.value())
            screen.blit(scaled_image, position)

    def update(self):  # Must be called not more than once per FRAMERATE
        for item in self.Adjustable.instances:
            item.update_value()
