from collections.abc import Iterable
import pygame
from script.state import state

SideClue = list[list[str]]
BetweenClue = list[list[str]]


class Cell(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, x: int, y: int, number: int = 0, note: str = ""):
        super().__init__(group)
        self.image = pygame.Surface((state.unit + 4, state.unit + 4))
        self.rect = self.image.get_rect()

        self.x, self.y = x, y
        self.number = number
        self.note = note
        self.fixed = bool(number)
        self.selected = False
        self.last_selected = False
        self.error = False
        self.corner_memo: set[int] = set()
        self.center_memo: set[int] = set()

    def update(self):
        self.image = pygame.Surface((state.unit + 2, state.unit + 2))
        self.image.fill((127, 0, 0) if self.error else (0, 0, 0))
        pos = (state.left + state.unit * self.x - 1, state.top + state.unit * self.y - 1)
        self.rect = self.image.get_rect(topleft=pos)

        pygame.draw.rect(self.image, (168, 168, 168), (0, 0, state.unit + 2, state.unit + 2), width=2)
        if self.selected:
            color = (70, 180, 255) if self.last_selected else (0, 100, 200)
            pygame.draw.rect(self.image, color, (4, 4, state.unit - 6, state.unit - 6), width=2)

        if self.number:
            color = (255, 255, 255) if self.fixed else (255, 255, 0)
            text_image = state.number_font.render(str(self.number), True, color)
            text_rect = text_image.get_rect(center=(state.unit // 2 + 1, state.unit // 2 + 2))
            self.image.blit(text_image, text_rect)
        else:
            center_text = "".join(map(str, sorted(self.center_memo)))
            text_image = state.memo_font.render(center_text, True, (255, 255, 0))
            text_rect = text_image.get_rect(center=(state.unit // 2 + 1, state.unit // 2 + 2))
            self.image.blit(text_image, text_rect)
            corner_text = "".join(map(str, sorted(self.corner_memo)))
            text_image = state.memo_font.render(corner_text, True, (255, 255, 0))
            text_rect = text_image.get_rect(topleft=(state.unit // 10, state.unit // 8))
            self.image.blit(text_image, text_rect)

        if self.note:
            text_image = state.note_font.render(self.note, True, (255, 255, 255))
            text_rect = text_image.get_rect(center=(state.unit // 6 * 5, state.unit // 5 * 4))
            self.image.blit(text_image, text_rect)


class GridType(Iterable[list[Cell]]):
    def __init__(self, grid: list[list[Cell]]):
        self.grid = grid
        self.top: SideClue = [[] for _ in [0] * 9]
        self.left: SideClue = [[] for _ in [0] * 9]
        self.between: BetweenClue = [[""] * 8 for _ in [0] * 9]
        self.index = 0

    def __getitem__(self, item: tuple[int, int]) -> Cell:
        return self.grid[item[1]][item[0]]

    def __iter__(self):
        return self

    def __next__(self) -> list[Cell]:
        if self.index >= len(self.grid):
            raise StopIteration
        row = self.grid[self.index]
        self.index += 1
        return row

    def row_number(self, i: int, /) -> list[int]:
        return [self.grid[i][j].number for j in range(9)]

    def column_number(self, j: int, /) -> list[int]:
        return [self.grid[i][j].number for i in range(9)]
