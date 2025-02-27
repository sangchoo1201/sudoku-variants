from collections import defaultdict
from itertools import product
from typing import Callable

from script.cell import GridType

Point = tuple[int, int]
CheckerType = Callable[[GridType], set[Point]]


def v_check(grid: GridType, disable: tuple[bool, ...]) -> set[Point]:
    s = set()
    numbers: dict[int, list[Point]]
    if not disable[0]:
        # Horizontal
        for y in range(9):
            numbers = {i: [] for i in range(10)}
            for x in range(9):
                numbers[grid[x, y].number].append((x, y))
            s |= {cell for i in range(1, 10) for cell in numbers[i] if len(numbers[i]) > 1}
    if not disable[1]:
        # Vertical
        for x in range(9):
            numbers = {i: [] for i in range(10)}
            for y in range(9):
                numbers[grid[x, y].number].append((x, y))
            s |= {cell for i in range(1, 10) for cell in numbers[i] if len(numbers[i]) > 1}
    if not disable[2]:
        # Box
        for i in range(9):
            numbers = {k: [] for k in range(10)}
            for j in range(9):
                x, y = (i // 3) * 3 + j // 3, (i % 3) * 3 + j % 3
                numbers[grid[x, y].number].append((x, y))
            s |= {cell for j in range(1, 10) for cell in numbers[j] if len(numbers[j]) > 1}
    return s


def dt_check(grid: GridType) -> set[Point]:
    s = set()
    for x, y in product(range(8), repeat=2):
        if grid[x, y].number == grid[x + 1, y + 1].number != 0:
            s |= {(x, y), (x + 1, y + 1)}
        if grid[x, y + 1].number == grid[x + 1, y].number != 0:
            s |= {(x, y + 1), (x + 1, y)}
    return s


def tp_check(grid: GridType) -> set[Point]:
    s = set()
    # Horizontal
    for x, y in product(range(7), range(9)):
        a, b, c = grid[x, y].number, grid[x + 1, y].number, grid[x + 2, y].number
        if 0 not in (a, b, c) and (a + 1 == b == c - 1 or a - 1 == b == c + 1):
            s |= {(x, y), (x + 1, y), (x + 2, y)}
    # Vertical
    for x, y in product(range(9), range(7)):
        a, b, c = grid[x, y].number, grid[x, y + 1].number, grid[x, y + 2].number
        if 0 not in (a, b, c) and (a + 1 == b == c - 1 or a - 1 == b == c + 1):
            s |= {(x, y), (x, y + 1), (x, y + 2)}
    # Diagonal
    for x, y in product(range(7), range(7)):
        a, b, c = grid[x, y].number, grid[x + 1, y + 1].number, grid[x + 2, y + 2].number
        if 0 not in (a, b, c) and (a + 1 == b == c - 1 or a - 1 == b == c + 1):
            s |= {(x, y), (x + 1, y + 1), (x + 2, y + 2)}
        a, b, c = grid[x + 2, y].number, grid[x + 1, y + 1].number, grid[x, y + 2].number
        if 0 not in (a, b, c) and (a + 1 == b == c - 1 or a - 1 == b == c + 1):
            s |= {(x + 2, y), (x + 1, y + 1), (x, y + 2)}
    return s


def cr_check(grid: GridType) -> set[Point]:
    s = set()
    # Positive
    numbers = {i: [] for i in range(10)}
    for i in range(9):
        numbers[grid[i, i].number].append((i, i))
    s |= {cell for i in range(1, 10) for cell in numbers[i] if len(numbers[i]) > 1}
    # Negative
    numbers = {i: [] for i in range(10)}
    for i in range(9):
        numbers[grid[i, 8 - i].number].append((i, 8 - i))
    s |= {cell for i in range(1, 10) for cell in numbers[i] if len(numbers[i]) > 1}
    return s


def ro_check(grid: GridType) -> set[Point]:
    s = set()
    for pos in product(range(9), range(9)):
        note, number = grid[pos].note, grid[pos].number
        if any((note == "L" and number not in (0, 1, 2, 3),
                note == "M" and number not in (0, 4, 5, 6),
                note == "H" and number not in (0, 7, 8, 9))):
            s.add(pos)
    return s


def sd_check(grid: GridType) -> set[Point]:
    s = set()
    # Horizontal
    for i in range(9):
        if not grid.left[i]:
            continue
        row = grid.row_number(i)
        if row.count(1) != 1 or row.count(9) != 1:
            continue
        one, nine = row.index(1), row.index(9)
        clue = grid.left[i][0]
        low, high = (int(clue),) * 2 if clue.isdigit() else {"L": (1, 3), "M": (4, 6), "H": (7, 9)}[clue]
        if not low <= abs(one - nine) - 1 <= high:
            s |= {(one, i), (nine, i)}
    # Vertical
    for i in range(9):
        if not grid.top[i]:
            continue
        column = grid.column_number(i)
        if column.count(1) != 1 or column.count(9) != 1:
            continue
        one, nine = column.index(1), column.index(9)
        clue = grid.top[i][0]
        low, high = (int(clue),) * 2 if clue.isdigit() else {"L": (1, 3), "M": (4, 6), "H": (7, 9)}[clue]
        if not low <= abs(one - nine) - 1 <= high:
            s |= {(i, one), (i, nine)}
    return s


def fx_check(grid: GridType) -> set[Point]:
    s = set()
    # Horizontal
    for i in range(9):
        side = grid.left[i]
        row = grid.row_number(i)
        if not all(row.count(int(j)) <= 1 for j in side):
            continue
        indices = [row.index(int(j)) for j in side if j in row]
        if indices != sorted(indices):
            s |= {(j, i) for j in indices}
    # Vertical
    for i in range(9):
        side = grid.top[i]
        column = grid.column_number(i)
        if not all(column.count(int(j)) <= 1 for j in side):
            continue
        indices = [column.index(int(j)) for j in side if j in column]
        if indices != sorted(indices):
            s |= {(i, j) for j in indices}
    return s


def as_check(grid: GridType) -> set[Point]:
    s = set()
    # Horizontal
    for i in range(9):
        row = grid.row_number(i)
        if row.count(1) != 1 or row.count(9) != 1:
            continue
        one, nine = row.index(1), row.index(9)
        reverse = (1, -1)[one > nine]
        end = nine + reverse if nine else None
        sublist = [j for j in row[one: end: reverse] if j]
        if sublist != sorted(sublist):
            s |= {(j, i) for j in range(one, nine + reverse, reverse) if row[j]}
    # Vertical
    for i in range(9):
        column = grid.column_number(i)
        if column.count(1) != 1 or column.count(9) != 1:
            continue
        one, nine = column.index(1), column.index(9)
        reverse = (1, -1)[one > nine]
        end = nine + reverse if nine else None
        sublist = [j for j in column[one: end: reverse] if j]
        if sublist != sorted(sublist):
            s |= {(i, j) for j in range(one, nine + reverse, reverse) if column[j]}
    return s


def qt_check(grid: GridType) -> set[Point]:
    s = set()
    # Horizontal
    for i in range(9):
        if not grid.left[i]:
            continue
        row = grid.row_number(i)
        a, b = map(int, grid.left[i])
        if row.count(a) == 1 and row.count(b) == 1 and row[a - 1] != b and row[b - 1] != a:
            s |= {(row.index(a), i), (row.index(b), i)}
            continue
        if row[a - 1] == a:
            s.add((a - 1, i))
        if row[b - 1] == b:
            s.add((b - 1, i))
        if row[a - 1] == 0 or row[b - 1] == 0:
            continue
        if (row[a - 1] == b) + (row[b - 1] == a) != 1:
            s |= {(a - 1, i), (b - 1, i)}
    # Vertical
    for i in range(9):
        if not grid.top[i]:
            continue
        column = grid.column_number(i)
        a, b = map(int, grid.top[i])
        if column.count(a) == 1 and column.count(b) == 1 and column[a - 1] != b and column[b - 1] != a:
            s |= {(i, column.index(a)), (i, column.index(b))}
            continue
        if column[a - 1] == a:
            s.add((i, a - 1))
        if column[b - 1] == b:
            s.add((i, b - 1))
        if column[a - 1] == 0 or column[b - 1] == 0:
            continue
        if (column[a - 1] == b) + (column[b - 1] == a) != 1:
            s |= {(i, a - 1), (i, b - 1)}
    return s


def li_check(grid: GridType) -> set[Point]:
    s = set()
    for pos in product(range(9), range(9)):
        note, number = grid[pos].note, grid[pos].number
        if not note or number == 0:
            continue
        note_number = ord(note) - 9311
        if abs(number - note_number) != 1:
            s.add(pos)
    return s


def rm_check(grid: GridType) -> set[Point]:
    s = set()
    # Horizontal
    for x, y in product(range(8), range(9)):
        a, b = grid[x, y].number, grid[x + 1, y].number
        if a and b and abs(a - b) == 1:
            s |= {(x, y), (x + 1, y)}
    # Vertical
    for x, y in product(range(9), range(8)):
        a, b = grid[x, y].number, grid[x, y + 1].number
        if a and b and abs(a - b) == 1:
            s |= {(x, y), (x, y + 1)}
    return s


def qd_check(grid: GridType) -> set[Point]:
    s = set()
    for x, y in product(range(8), repeat=2):
        n = [grid[i, j].number for i, j in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1))]
        if all(n) and not (16 <= sum(n) < 25):
            s |= {(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)}
    return s


def ct_check(grid: GridType) -> set[Point]:
    s = set()
    for x, y in product(range(9), repeat=2):
        if grid[x, y].note != '^':
            continue
        n = grid[x, y].number
        if not n:
            continue
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < 9 and 0 <= ny < 9):
                continue
            if grid[nx, ny].number > n:
                s.add((x, y))
                break
    return s


def lk_check(grid: GridType) -> set[Point]:
    s = set()
    for x, y in product(range(8), range(9)):
        if grid.between[y][x] != '-':
            continue
        a, b = grid[x, y].number, grid[x + 1, y].number
        if not a * b:
            continue
        if a + b != 10 and abs(a - b) != 1:
            s |= {(x, y), (x + 1, y)}
    return s


def bx_check(grid: GridType) -> set[Point]:
    s = set()
    for x, y in product(range(9), repeat=2):
        if grid[x, y].note != "□":
            continue
        numbers = {i: [] for i in range(10)}
        for dx, dy in product(range(-1, 2), repeat=2):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < 9 and 0 <= ny < 9):
                continue
            numbers[grid[nx, ny].number].append((nx, ny))
            s |= {cell for j in range(1, 10) for cell in numbers[j] if len(numbers[j]) > 1}
    return s


def vr_check(grid: GridType) -> set[Point]:
    s = set()
    numbers = defaultdict(lambda: {i: [] for i in range(10)})
    for pos in product(range(9), range(9)):
        cell = grid[pos]
        if not cell.note:
            continue
        numbers[cell.note][cell.number].append(pos)
    for d in numbers.values():
        s |= {cell for i in range(1, 10) for cell in d[i] if len(d[i]) > 1}
    return s


def none_check(_: GridType) -> set[Point]:
    return set()


def has_side(variants: list[str]) -> bool:
    return any(v in side_variant for v in variants)


side_variant = {"SD", "FX", "QT"}
checkers: dict[str, CheckerType] = {
    "V": none_check,
    "DT": dt_check,
    "TP": tp_check,
    "CR": cr_check,
    "RO": ro_check,
    "SD": sd_check,
    "FX": fx_check,
    "AS": as_check,
    "QT": qt_check,
    "LI": li_check,
    "RM": rm_check,
    "QD": qd_check,
    "CT": ct_check,
    "LK": lk_check,
    "BX": bx_check,
    "VR": vr_check,
    "A?R": none_check
}
