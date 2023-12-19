import pygame


class ImageItem:

    def __init__(self, filename, rows=1, columns=1):
        self.surface = pygame.image.load(filename)
        self.rows = rows if rows is not None else 1
        self.columns = columns if columns is not None else 1
        self.num_frames = self.rows * self.columns
        self.frame_width = self.surface.get_width() / self.columns
        self.frame_height = self.surface.get_height() / self.rows
        self.current_frame = 0

    def limit_row(self, row):
        if row > self.rows:
            row = self.rows
        elif row < 1:
            row = 1
        return row

    def limit_column(self, column):
        if column > self.columns:
            column = self.columns
        elif column < 1:
            column = 1
        return column

    def get_frame_rect(self, row, column):
        row = self.limit_row(row)
        column = self.limit_column(column)
        return pygame.Rect((row - 1) * self.frame_width,
                           (column - 1) * self.frame_height,
                           self.frame_width, self.frame_height)

    def get_frame_number(self, number):
        if self.num_frames == 1:
            return pygame.Rect(0, 0, self.surface.get_width(), self.surface.get_height())
        # else
        number = (number % self.num_frames) - 1
        column = (number % self.rows) + 1
        row = (number // self.rows) + 1
        return self.get_frame_rect(row, column)

    def get_next_frame(self):
        self.current_frame += 1
        if self.current_frame >= self.num_frames:
            self.current_frame = 0
        return self.get_frame_number(self.current_frame)


class ImageFolder(ImageItem):

    def __init__(self, folder_name):
        self.folder_name = folder_name
        self.current_image = 0
        # need to set self.image to the first file, frames to the number of files, w & h to the
        # size of the first file
        super().__init__(self.folder_name)

    def get_next_frame(self):
        pass
        # need to update self.image with the next file in order
