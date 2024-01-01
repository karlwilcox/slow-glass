import glob

from abc import abstractmethod
import pygame
import cv2

# *************************************************************************************************
#
#    #### ##     ##    ###     ######   ######## #### ######## ######## ##     ##
#     ##  ###   ###   ## ##   ##    ##  ##        ##     ##    ##       ###   ###
#     ##  #### ####  ##   ##  ##        ##        ##     ##    ##       #### ####
#     ##  ## ### ## ##     ## ##   #### ######    ##     ##    ######   ## ### ##
#     ##  ##     ## ######### ##    ##  ##        ##     ##    ##       ##     ##
#     ##  ##     ## ##     ## ##    ##  ##        ##     ##    ##       ##     ##
#    #### ##     ## ##     ##  ######   ######## ####    ##    ######## ##     ##
#
# **************************************************************************************************


class ImageItem:

    def __init__(self):
        self.surface = None
        self.image_rect = None

    @abstractmethod
    def move_to_frame(self, number):
        pass

    @abstractmethod
    def next_frame(self, advance_by=1):
        pass

# *************************************************************************************************
#
#     ######  #### ##     ## ########  ##       ######## #### ##     ##    ###     ######   ########
#    ##    ##  ##  ###   ### ##     ## ##       ##        ##  ###   ###   ## ##   ##    ##  ##
#    ##        ##  #### #### ##     ## ##       ##        ##  #### ####  ##   ##  ##        ##
#     ######   ##  ## ### ## ########  ##       ######    ##  ## ### ## ##     ## ##   #### ######
#          ##  ##  ##     ## ##        ##       ##        ##  ##     ## ######### ##    ##  ##
#    ##    ##  ##  ##     ## ##        ##       ##        ##  ##     ## ##     ## ##    ##  ##
#     ######  #### ##     ## ##        ######## ######## #### ##     ## ##     ##  ######   ########
#
# **************************************************************************************************


class SimpleImage(ImageItem):

    def __init__(self, filename, rows=1, columns=1):
        super().__init__()
        self.surface = pygame.image.load(filename)
        self.image_rect = pygame.Rect(0, 0, self.surface.get_width(), self.surface.get_height())

    def move_to_frame(self, number):
        pass

    def next_frame(self, advance_by=1):
        pass

# *************************************************************************************************
#
#     ######  ######## ##       ##       #### ##     ##    ###     ######   ########
#    ##    ## ##       ##       ##        ##  ###   ###   ## ##   ##    ##  ##
#    ##       ##       ##       ##        ##  #### ####  ##   ##  ##        ##
#    ##       ######   ##       ##        ##  ## ### ## ##     ## ##   #### ######
#    ##       ##       ##       ##        ##  ##     ## ######### ##    ##  ##
#    ##    ## ##       ##       ##        ##  ##     ## ##     ## ##    ##  ##
#     ######  ######## ######## ######## #### ##     ## ##     ##  ######   ########
#
# **************************************************************************************************


class CellImage(ImageItem):

    def __init__(self, filename, rows=1, columns=1):
        super().__init__()
        self.surface = pygame.image.load(filename)
        self.current_frame = 0
        self.rows = rows if rows is not None else 1
        self.columns = columns if columns is not None else 1
        self.num_frames = self.rows * self.columns
        self.frame_width = self.surface.get_width() / self.columns
        self.frame_height = self.surface.get_height() / self.rows

    def move_to_frame(self, number):
        if number > self.num_frames:
            number = 0
        elif number < 0:
            number = self.num_frames - 1
        number = (number % self.num_frames) - 1
        column = (number % self.rows) + 1
        row = (number // self.rows) + 1
        self.image_rect = pygame.Rect((row - 1) * self.frame_width,
                           (column - 1) * self.frame_height,
                           self.frame_width, self.frame_height)

    def next_frame(self, advance_by=1):
        self.move_to_frame(self.current_frame + advance_by)

# *************************************************************************************************
#
#    #### ##     ##    ###     ######   ######## ########  #######  ##       ########  ######## ########
#     ##  ###   ###   ## ##   ##    ##  ##       ##       ##     ## ##       ##     ## ##       ##     ##
#     ##  #### ####  ##   ##  ##        ##       ##       ##     ## ##       ##     ## ##       ##     ##
#     ##  ## ### ## ##     ## ##   #### ######   ######   ##     ## ##       ##     ## ######   ########
#     ##  ##     ## ######### ##    ##  ##       ##       ##     ## ##       ##     ## ##       ##   ##
#     ##  ##     ## ##     ## ##    ##  ##       ##       ##     ## ##       ##     ## ##       ##    ##
#    #### ##     ## ##     ##  ######   ######## ##        #######  ######## ########  ######## ##     ##
#
# **************************************************************************************************


class ImageFolder(ImageItem):

    def __init__(self, folder_name):
        super().__init__()
        self.file_list = sorted(glob.glob(folder_name + "/*.png"))
        self.current_file = 0
        self.surface = pygame.image.load(self.file_list[0])
        self.image_rect = pygame.Rect(0, 0, self.surface.get_width(), self.surface.get_height())

    def move_to_frame(self, number):
        if number > len(self.file_list):
            number = 0
        elif number < 0:
            number = len(self.file_list) - 1
        self.current_file = number
        self.surface = pygame.image.load(self.file_list[self.current_file])

    def next_frame(self, advance_by=1):
        self.move_to_frame(self.current_file + advance_by)

# *************************************************************************************************
#
#     ######   ########   #######  ##     ## ########  #### ##     ##    ###     ######   ########
#    ##    ##  ##     ## ##     ## ##     ## ##     ##  ##  ###   ###   ## ##   ##    ##  ##
#    ##        ##     ## ##     ## ##     ## ##     ##  ##  #### ####  ##   ##  ##        ##
#    ##   #### ########  ##     ## ##     ## ########   ##  ## ### ## ##     ## ##   #### ######
#    ##    ##  ##   ##   ##     ## ##     ## ##         ##  ##     ## ######### ##    ##  ##
#    ##    ##  ##    ##  ##     ## ##     ## ##         ##  ##     ## ##     ## ##    ##  ##
#     ######   ##     ##  #######   #######  ##        #### ##     ## ##     ##  ######   ########
#
# **************************************************************************************************


class GroupImage(ImageItem):

    def __init__(self, scene, group_name):
        super().__init__()
        self.group_name = group_name
        self.scene = scene
        self.image_rect = pygame.Rect(0, 0, self.scene.data.options["width"], self.scene.data.options["height"])

    def move_to_frame(self, number):
        self.surface = pygame.Surface((self.scene.data.options["width"], self.scene.data.options["height"]), pygame.SRCALPHA)
        self.scene.data.sprites.display_all(self.surface, self.group_name)

    def next_frame(self, advance_by=1):
        self.move_to_frame(0)

# *************************************************************************************************
#
#    ######## ######## ##     ## ########
#       ##    ##        ##   ##     ##
#       ##    ##         ## ##      ##
#       ##    ######      ###       ##
#       ##    ##         ## ##      ##
#       ##    ##        ##   ##     ##
#       ##    ######## ##     ##    ##
#
# **************************************************************************************************


class TextImage(ImageItem):

    def __init__(self):
        super().__init__()
        if not pygame.font.get_init():
            pygame.font.init()
        self.font_face = pygame.font.get_default_font()
        self.size = 24
        self.text_font = None
        self.content = ""
        self.color = (255, 255, 255)
        self.background_color = None
        self.rebuild_font()

    def move_to_frame(self, number):
        self.surface = self.text_font.render(self.content, True, self.color, self.background_color)
        self.image_rect = self.surface.get_rect()

    def next_frame(self, advance_by=1):
        self.move_to_frame(advance_by)

    def rebuild_font(self):
        self.text_font = pygame.font.Font(self.font_face, self.size)

# *************************************************************************************************
#
#    ##     ##  #######  ##     ## #### ########
#    ###   ### ##     ## ##     ##  ##  ##
#    #### #### ##     ## ##     ##  ##  ##
#    ## ### ## ##     ## ##     ##  ##  ######
#    ##     ## ##     ##  ##   ##   ##  ##
#    ##     ## ##     ##   ## ##    ##  ##
#    ##     ##  #######     ###    #### ########
#
# **************************************************************************************************


class Movie(ImageItem):

    def __init__(self, movie_file):
        super().__init__()
        self.movie_file = movie_file
        self.video = None
        self.init_video()

    def move_to_frame(self, number):  # not supported, just gets next frame
        self.next_frame(number)

    def next_frame(self, advance_by=1):
        success = True
        advance_by = abs(advance_by)
        while success:
            success, image = self.video.read()
            self.surface = pygame.Surface(image)
            if --advance_by <= 0:
                return
        # run out of frames, go back to the start
        self.init_video()

    def init_video(self):
        self.video = cv2.VideoCapture(self.movie_file)
        success, image = self.video.read()
        self.surface = pygame.Surface(image)
        self.image_rect = self.surface.get_rect()

    def __del__(self):
        self.video.release()
