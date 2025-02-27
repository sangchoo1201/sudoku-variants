import pygame


class State:
    number_font: pygame.font.Font
    note_font: pygame.font.Font
    memo_font: pygame.font.Font

    def __init__(self):
        self.fps = 60
        self.side_clue = False

        self.level = ""
        self.level_selection = 0
        self.level_offset = 0

    @property
    def width(self) -> int:
        return pygame.display.get_window_size()[0]

    @property
    def height(self) -> int:
        return pygame.display.get_window_size()[1]

    @property
    def unit(self) -> int:
        return min(self.width // 12, self.height // 12)

    @property
    def left(self) -> int:
        return self.width // 2 - self.unit * 9 // 2 + self.unit * self.side_clue

    @property
    def top(self) -> int:
        return self.height // 2 - self.unit * 9 // 2 + self.unit * self.side_clue

    @property
    def right(self) -> int:
        return self.width // 2 + self.unit * 9 // 2 + self.unit * self.side_clue

    @property
    def bottom(self) -> int:
        return self.height // 2 + self.unit * 9 // 2 + self.unit * self.side_clue


state = State()
