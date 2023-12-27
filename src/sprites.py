import math
from io import UnsupportedOperation

import pygame
from defaults import *
from timing import Timer

# *************************************************************************************************
#
#     ######  ########  ########  #### ######## ######## ##       ####  ######  ########
#    ##    ## ##     ## ##     ##  ##     ##    ##       ##        ##  ##    ##    ##
#    ##       ##     ## ##     ##  ##     ##    ##       ##        ##  ##          ##
#     ######  ########  ########   ##     ##    ######   ##        ##   ######     ##
#          ## ##        ##   ##    ##     ##    ##       ##        ##        ##    ##
#    ##    ## ##        ##    ##   ##     ##    ##       ##        ##  ##    ##    ##
#     ######  ##        ##     ## ####    ##    ######## ######## ####  ######     ##
#
# **************************************************************************************************


class SpriteList:

    def __init__(self):
        self.sprite_list = []
        self.tag_list = []

    def get_list(self):
        return self.sprite_list

    def get_sprite(self, sprite_tag):
        for sprite in self.sprite_list:
            if sprite.tag == sprite_tag:
                return sprite
        return None

    def get_sprite_index(self, sprite_tag):
        for sprite_pos in range(0, len(self.sprite_list)):
            if self.sprite_list[sprite_pos].tag == sprite_tag:
                return sprite_pos
        return None

    def sprite_add(self, in_sprite):
        # Maintain an ordered list of sprites, order by sprite.depth
        sprite_pos = 0
        while sprite_pos < len(self.sprite_list):
            if in_sprite.depth > self.sprite_list[sprite_pos].depth:
                break
            sprite_pos += 1
        self.sprite_list.insert(sprite_pos, in_sprite)
        self.tag_list.append(in_sprite.tag)

    def sprite_remove(self, sprite_tag):
        index = self.get_sprite_index(sprite_tag)
        if index is not None:
            self.sprite_list.pop(index)
            self.tag_list.remove(sprite_tag)

    def sprite_set_depth(self, sprite_tag, new_depth):
        index = self.get_sprite_index(sprite_tag)
        if index is not None:
            current = self.sprite_list[index]
            self.sprite_list.pop(index)
            current.depth = new_depth
            self.sprite_add(current)

    def sprite_change_depth(self, sprite_tag, change):
        index = self.get_sprite_index(sprite_tag)
        # This only makes sense if there are at least 2 sprites
        if index is not None and len(self.sprite_list) > 1:
            current = self.sprite_list[index]
            self.sprite_list.pop(index)
            new_index = index + change
            new_depth = 0
            if new_index >= len(self.sprite_list):
                new_index = len(self.sprite_list) - 1
                new_depth = self.sprite_list[len(self.sprite_list) - 1].depth + 1
            elif new_index < 0:
                new_index = 0
            else:
                new_depth = self.sprite_list[new_index].depth - 1
            current.depth = new_depth
            self.sprite_list.insert(new_index, current)

    def display_all(self, screen):
        # Update values of all current sprites (visible or not)
        # for adjustable in SpriteItem.Adjustable.instances:
        #     adjustable.update_value()
        # And paint them to the screen
        for sprite in self.sprite_list:
            sprite.update()
            sprite.display(screen)

    def keys(self):
        return self.tag_list

    def dump(self):
        result = ""
        count = 0
        for sprite in self.sprite_list:
            result = "%d - %s\n" % (count, sprite.dump())
            count += 1
        return result

# *************************************************************************************************
#
#     ######  ########  ########  #### ######## ######## #### ######## ######## ##     ##
#    ##    ## ##     ## ##     ##  ##     ##    ##        ##     ##    ##       ###   ###
#    ##       ##     ## ##     ##  ##     ##    ##        ##     ##    ##       #### ####
#     ######  ########  ########   ##     ##    ######    ##     ##    ######   ## ### ##
#          ## ##        ##   ##    ##     ##    ##        ##     ##    ##       ##     ##
#    ##    ## ##        ##    ##   ##     ##    ##        ##     ##    ##       ##     ##
#     ######  ##        ##     ## ####    ##    ######## ####    ##    ######## ##     ##
#
# **************************************************************************************************


class SpriteItem:
    globalData = None

# *************************************************************************************************
#
#       ###    ########        ## ##     ##  ######  ########    ###    ########  ##       ########
#      ## ##   ##     ##       ## ##     ## ##    ##    ##      ## ##   ##     ## ##       ##
#     ##   ##  ##     ##       ## ##     ## ##          ##     ##   ##  ##     ## ##       ##
#    ##     ## ##     ##       ## ##     ##  ######     ##    ##     ## ########  ##       ######
#    ######### ##     ## ##    ## ##     ##       ##    ##    ######### ##     ## ##       ##
#    ##     ## ##     ## ##    ## ##     ## ##    ##    ##    ##     ## ##     ## ##       ##
#    ##     ## ########   ######   #######   ######     ##    ##     ## ########  ######## ########
#
# **************************************************************************************************
    class Adjustable:

        def __init__(self, in_value, min_value=float('-inf'), max_value=float('inf')):
            # set limits, if given
            self.lower_limit = min_value
            self.upper_limit = max_value
            # data for constant motion
            self.current_value = in_value
            self.target_value = in_value
            self.delta_value = 0.0
            # data for acceleration
            self.time_to_run = 0.0
            self.time_counter = 0.0
            self.accel_value = 0.0
            self.initial_value = 0.0
            self.changed = False

        def value(self):
            return self.current_value

        def get_delta(self):
            """
            return rate of change in pixels per second
            """
            return self.delta_value * FRAMERATE

        def set_delta(self, delta, rate):
            """
            set rate of change in pixels per second
            accelerating or slowing if rate is non-zero
            """
            if rate <= 0:
                self.delta_value = delta / FRAMERATE
                return
            # need to accelerate to the new value in rate seconds
            self.time_to_run = rate
            self.time_counter = 0.0
            self.initial_value = self.get_delta()
            self.accel_value = (delta - self.get_delta()) / rate
            self.changed = True

        def get_accel(self):
            return self.accel_value * FRAMERATE

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
            self.changed = True

        def update_value(self):
            try:
                if abs(self.current_value - self.target_value) > abs(self.delta_value):
                    self.changed = True
                    self.current_value += self.delta_value
                    # accelerate or slow down to the target value?
                    if self.time_counter < self.time_to_run:
                        self.delta_value = (self.initial_value + (self.accel_value * self.time_counter)) / FRAMERATE
                        self.time_counter += 1 / FRAMERATE
                    else:
                        self.time_to_run = 0
                else:
                    self.current_value = self.target_value
                    self.delta_value = 0
                    self.accel_value = 0
            except TypeError as e:
                print(f"from {self.target_value} to {self.current_value} by {self.delta_value}")
            return_value = self.changed
            self.changed = False
            return return_value

    # End inner class

    def __init__(self, itag, stag, scene, centre_x, centre_y, width=None, height=None, depth=0):
        self.tag = stag
        self.scene = scene
        self.depth = depth
        self.x = self.Adjustable(centre_x)
        self.y = self.Adjustable(centre_y)
        self.image = scene.images[itag]
        w = width or self.image.image_rect.width
        h = height or self.image.image_rect.height
        self.w = self.Adjustable(w)
        self.h = self.Adjustable(h)
        self.rot = self.Adjustable(0, -360, 360)
        self.alpha = self.Adjustable(0, 0, 100)
        self.dark = self.Adjustable(0, 0, 100)
        self.light = self.Adjustable(0, 0, 100)
        self.blur = self.Adjustable(0, 0, 100)
        self.visible = True
        self.paused = False
        self.animation_rate = self.Adjustable(0)
        self.last_frame_millis = Timer.millis()
        self.windowed = False
        self.ix = self.Adjustable(0)
        self.iy = self.Adjustable(0)
        self.ih = self.Adjustable(0)
        self.iw = self.Adjustable(0)
        self.updated = True
        self.previous = None
        self.transition = None
        self.groups = []

    def reposition(self, centre_x, centre_y, width=None, height=None, depth=None):
        self.x = self.Adjustable(centre_x)
        self.y = self.Adjustable(centre_y)
        if width is not None:
            self.w = self.Adjustable(width)
        if height is not None:
            self.h = self.Adjustable(height)
        if depth is not None:
            self.depth = depth

    def move_in_time(self, new_x, new_y, seconds):
        self.x.set_target_value(new_x, seconds)
        self.y.set_target_value(new_y, seconds)

    def move_at_rate(self, new_x, new_y, rate):
        """
        Move to new location at  rate pixels per second
        """
        # need the distance to work our the travel time
        x_distance = new_x - self.x.value()
        y_distance = new_y - self.y.value()
        distance = math.sqrt(x_distance ** 2 + y_distance ** 2)
        seconds = distance / rate
        self.x.set_target_value(new_x, seconds)
        self.y.set_target_value(new_y, seconds)

    def resize(self, new_width, new_height, seconds):
        self.w.set_target_value(new_width, seconds)
        self.h.set_target_value(new_height, seconds)

    def scale_to(self, width_pct, height_pct, seconds):
        if height_pct is None or height_pct < 0:
            height_pct = width_pct
        # This sets the scale as a percentage of the original image value
        self.w.set_target_value(self.image.image_rect.width * (width_pct / 100), seconds)
        self.h.set_target_value(self.image.image_rect.height * (height_pct / 100), seconds)

    def scale_by(self, width_pct, height_pct, seconds):
        if height_pct is None or height_pct < 0:
            height_pct = width_pct
        # This sets the scale as a percentage of its current size - take your pick...
        self.w.set_target_value(self.w.value() * (width_pct / 100), seconds)
        self.h.set_target_value(self.h.value() * (height_pct / 100), seconds)

    def turn_to(self, angle, seconds):
        self.rot.set_target_value(angle, seconds)

    def turn_by(self, angle, seconds):
        self.rot.set_target_value(self.rot.value() + angle, seconds)

    def trans(self, value, seconds):
        self.alpha.set_target_value(value, seconds)

    def lighten(self, value, seconds):
        self.light.set_target_value(value, seconds)

    def darken(self, value, seconds):
        self.dark.set_target_value(value, seconds)

    def set_animation_rate(self, value, seconds):
        self.animation_rate.set_target_value(value, seconds)

    def set_blur(self, value, seconds):
        self.blur.set_target_value(value, seconds)

    def get_speed(self) -> float:
        x_speed = self.x.get_delta()
        y_speed = self.y.get_delta()
        return math.sqrt(x_speed ** 2 + y_speed ** 2)

    def set_speed(self, speed, rate):
        current_speed: float = self.get_speed()
        if current_speed <= 0:
            print("Sprite %s is not moving, set direction first" % self.tag)
            return
        scale = speed / current_speed
        final_x_delta = self.x.get_delta() * scale
        final_y_delta = self.y.get_delta() * scale
        self.x.set_delta(final_x_delta, rate)
        self.y.set_delta(final_y_delta, rate)

    def set_window(self, ix, iy, iw, ih):
        self.windowed = True
        self.ix.set_target_value(ix)
        self.iy.set_target_value(iy)
        self.iw.set_target_value(iw)
        self.ih.set_target_value(ih)

    def set_transition(self, type):
        pass

    def zoom_to(self, width, height, seconds):
        if not self.windowed:
            print("%s is not windowed" % self.tag)
            return
        self.iw.set_target_value(width, seconds)
        self.ih.set_target_value(height, seconds)

    def scroll_to(self, new_ix, new_iy, seconds):
        if not self.windowed:
            print("%s is not windowed" % self.tag)
            return
        self.ix.set_target_value(new_ix, seconds)
        self.iy.set_target_value(new_iy, seconds)

    def advance(self, num_of_frames):
        self.image.next_frame(num_of_frames)
        self.updated = True

    def get_frame(self, frame_num):
        self.image.move_to_frame(frame_num)
        self.updated = True

    def update(self):
        if self.paused:
            return
        for name, value in vars(self).items():
            if value.__class__.__name__ == "Adjustable":
                if value.update_value():
                    self.updated = True
        if self.animation_rate.value() > 0:
            if Timer.millis() - self.last_frame_millis > self.animation_rate.value() * 1000:
                self.last_frame_millis = Timer.millis()
                self.image.next_frame()
                self.updated = True

    def display(self, screen):
        if not self.visible:
            return
        if self.updated:
            # Get the source image onto surface
            if self.windowed:
                target_width = self.iw.value()
                target_height = self.ih.value()
                surface = pygame.Surface((int(self.iw.value()), int(self.ih.value())), pygame.SRCALPHA)
                image_rect = pygame.Rect(self.ix.value() - target_width / 2,
                                         self.iy.value() - target_height / 2,
                                         target_width, target_height)
            else:
                target_width = self.w.value()
                target_height = self.h.value()
                surface = pygame.Surface((int(self.image.image_rect.width), int(self.image.image_rect.height)), pygame.SRCALPHA)
                image_rect = self.image.image_rect
            surface.blit(self.image.surface, (0, 0), image_rect)
            # Scale surface to the required size on screen
            surface = pygame.transform.scale(surface, (self.w.value(), self.h.value()))
            # If rotated, turn the image and re-calculate width and height
            if self.rot.value() != 0:
                surface = pygame.transform.rotate(surface, self.rot.value() * -1)
                new_rect = surface.get_rect(center=(target_width / 2, target_height / 2))
                target_height = new_rect.height
                target_width = new_rect.width
            if self.light.value() > 0:
                # Make sprite darker
                tmp = pygame.Surface((int(target_width), int(target_height)), pygame.SRCALPHA)
                lightness = int(255 * self.light.value() / 100)
                tmp.fill((lightness, lightness, lightness))
                surface.blit(tmp, (0, 0), special_flags=pygame.BLEND_MAX)
            # If the whole sprite has transparency, add that to the existing alpha channel
            if self.dark.value() > 0:
                # Make sprite darker
                tmp = pygame.Surface((int(target_width), int(target_height)), pygame.SRCALPHA)
                darkness = int(255 - (255 * self.dark.value() / 100))
                tmp.fill((darkness, darkness, darkness))
                surface.blit(tmp, (0, 0), special_flags=pygame.BLEND_MIN)
            if self.blur.value() > 0:
                tmp = pygame.Surface((int(target_width), int(target_height)), pygame.SRCALPHA)
                bluriness = int(self.blur.value() / 4)
                pygame.transform.gaussian_blur(surface, bluriness, True, tmp)
                surface.blit(tmp, (0, 0))
            # If the whole sprite has transparency, add that to the existing alpha channel
            if self.alpha.value() > 0:
                # convert transparency 0->100 to alpha 255->0
                tmp = pygame.Surface((int(target_width), int(target_height)), pygame.SRCALPHA)
                tmp.fill((255, 255, 255, int(255 - (255 * self.alpha.value() / 100))))
                surface.blit(tmp, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            position = pygame.Rect(self.x.value() - (self.w.value() / 2),
                                   self.y.value() - (self.h.value() / 2),
                                   target_width, target_height)
            # if transition is not None:
            #     transition.between(self.previous, (surface,position))
            self.previous = surface, position
            self.updated = False
        elif self.transition is not None:
            surface, position = self.previous
            # surface, position = transition.update()
        else:
            surface, position = self.previous
        screen.blit(surface, position)

    def dump(self):
        return "%s at %f,%f,%d" % (self.tag,
                                   self.x.value(),
                                   self.y.value(),
                                   self.depth)
