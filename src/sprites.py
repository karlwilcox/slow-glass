import pygame
from defaults import *
from timing import Timer


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


class SpriteItem:
    globalData = None

    class Adjustable:

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

        def update_value(self):
            if abs(self.current_value - self.target_value) > abs(self.delta_value):
                self.current_value += self.delta_value
            else:
                self.delta_value = 0

    # End inner class

    def __init__(self, itag, stag, scene, centre_x, centre_y, width=None, height=None, depth=0):
        self.tag = stag
        self.scene = scene
        self.depth = depth
        self.x = self.Adjustable(centre_x)
        self.y = self.Adjustable(centre_y)
        self.image = SpriteItem.globalData.images[itag]
        self.image_rect = self.image.get_frame_number(0)
        w = width if width is not None else self.image_rect.width
        h = height if height is not None else self.image_rect.height
        self.w = self.Adjustable(w)
        self.h = self.Adjustable(h)
        self.rot = self.Adjustable(0, -360, 360)
        self.alpha = self.Adjustable(0, 0, 100)
        self.visible = True
        self.paused = False
        self.animation_rate = self.Adjustable(0)
        self.last_frame_millis = Timer.millis()

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

    def trans(self, value, seconds):
        self.alpha.set_target_value(value, seconds)

    def rate(self, value, seconds):
        self.animation_rate.set_target_value(value, seconds)

    def update(self):
        if self.paused:
            return
        for name, value in vars(self).items():
            if value.__class__.__name__ == "Adjustable":
                value.update_value()
        if self.animation_rate.value() > 0:
            if Timer.millis() - self.last_frame_millis > self.animation_rate.value() * 1000:
                self.last_frame_millis = Timer.millis()
                self.image_rect = self.image.get_next_frame()

    def display(self, screen):
        if not self.visible:
            return
        surface = pygame.Surface((int(self.image.frame_width), int(self.image.frame_height)))
        surface.blit(self.image.surface, (0, 0), self.image_rect)
        scaled_image = pygame.transform.scale(surface, (self.w.value(), self.h.value()))
        if self.rot.value() != 0:
            scaled_image = pygame.transform.rotate(scaled_image, self.rot.value() * -1)
        if self.alpha.value() > 0:
            # convert transparency 0->100 to alpha 255->0
            scaled_image.set_alpha(int(255 - (255 * self.alpha.value() / 100)))
        position = pygame.Rect(self.x.value() - (self.w.value() / 2),
                               self.y.value() - (self.h.value() / 2),
                               self.w.value(), self.h.value())
        screen.blit(scaled_image, position)

    def dump(self):
        return "%s at %f,%f,%d" % (self.tag,
                                   self.x.value(),
                                   self.y.value(),
                                   self.depth)
