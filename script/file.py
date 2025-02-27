from os import listdir

from script.cell import *
from script.check import has_side


def get_level_list() -> list[str]:
    return [file[:-7] for file in listdir("level/")]


def get_level(file: str, group: pygame.sprite.Group) -> tuple[GridType, list[str]]:
    with open(file, 'r', encoding="UTF-8") as f:
        data = f.read().strip()
    v, *b = data.splitlines()
    variants: list[str] = v.split()
    board: list[str] = b[1:4] + b[5:8] + b[9:12]
    additional: list[str] = [""] * 9
    for i in range(9):
        row = board[i]
        board[i] = row[2:8:2] + row[10:16:2] + row[18:24:2]
        board[i] = board[i].replace("•", "0")
        additional[i] = row[3:9:2] + row[11:17:2] + row[19:25:2]
        if "LI" in variants:
            for a, b in zip("123456789", "①②③④⑤⑥⑦⑧⑨"):
                board[i] = board[i].replace(a, b)

    grid = GridType([[] for _ in [0] * 9])

    for y, row in enumerate(grid):
        for x in range(9):
            cell = board[y][x]
            number = int(cell) if cell.isdecimal() else 0
            note = cell if not cell.isdecimal() else ""
            row.append(Cell(group, x, y, number, note))

    for y, row in enumerate(additional):
        for x in range(9):
            if additional[y][x] in "^□":
                grid[x, y].note = additional[y][x]
            if additional[y][x] in "-":
                grid.between[y][x] = additional[y][x]

    state.side_clue = has_side(variants)
    for i, row in enumerate(b[1:4] + b[5:8] + b[9:12]):
        side = row[26:]
        grid.left[i] = side.split()
    for row in b[13:]:
        side = row[2:8:2] + row[10:16:2] + row[18:24:2] + " " * 9
        for i in range(9):
            if side[i] != " ":
                grid.top[i].append(side[i])

    return grid, variants
