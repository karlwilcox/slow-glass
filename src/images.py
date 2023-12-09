import pygame


class ImageItem:

    def __init__(self, filename, rows=1, columns=1):
        self.surface = pygame.image.load(filename)
        self.rows = rows if rows is not None else 1
        self.columns = columns if columns is not None else 1
        self.num_frames = self.rows * self.columns
        self.frame_width = self.surface.get_width() / self.rows
        self.frame_height = self.surface.get_height() / self.columns

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

    def get_frame(self, row, column):
        row = self.limit_row(row)
        column = self.limit_column(column)
        return pygame.Rect( (row - 1) * self.frame_width,
                            (column - 1) * self.frame_height,
                            self.frame_width, self.frame_height)

    def get_frame(self, number):
        if self.num_frames == 1:
            return pygame.Rect(0, 0, self.surface.get_width(), self.surface.get_height())
        # else
        number = (number % self.num_frames) - 1
        column = (number % self.rows) + 1
        row = (number // self.rows) + 1
        return self.get_frame(row, column)


