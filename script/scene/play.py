from time import perf_counter
from typing import TypedDict

from script.scene import *
from script.cell import *
from script.check import *
from script.text import TextRender
from script.state import state
from script.file import get_level

corner_keys = (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LCTRL, pygame.K_RCTRL)
center_keys = (pygame.K_LALT, pygame.K_RALT)
keymap = {pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1)}


class SingleHistory(TypedDict):
    pos: tuple[int, int]
    before: tuple[int, set[int], set[int]]
    after: tuple[int, set[int], set[int]] | None


HistoryType = list[SingleHistory]


class Play(Scene):
    def __init__(self, screen: pygame.Surface):
        from script.scene.select import Select

        super().__init__(screen)
        self.render = TextRender(screen, state.unit, (255, 255, 255))
        self.select_scene = Select

        self.cell_group = pygame.sprite.Group()
        self.grid, self.variants = get_level(f"level/{state.level}.sudoku", self.cell_group)
        self.selection: set[Point] = set()
        self.last_selection = (-1, -1)
        self.history: list[HistoryType] = []
        self.undo_history: list[HistoryType] = []

        self.click_time = 0
        self.begin_time = perf_counter()
        self.clear_time = -1

    def get_event(self) -> Optional[callback]:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return End
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not (pos := self.get_cell()):
                    self.selection.clear()
                    self.last_selection = (-1, -1)
                    continue
                if not any(keys[k] for k in center_keys + corner_keys):
                    self.selection.clear()
                    if not self.click_time:
                        self.click_time = 30
                self.selection.add(pos)
                double_click = pos == self.last_selection
                self.last_selection = pos
                if not 0 < self.click_time < 30 or not double_click:
                    continue
                number = self.grid[pos].number
                if not number:
                    continue
                for p in product(range(9), repeat=2):  # type: tuple[int, int]
                    if self.grid[p].number == number:
                        self.selection.add(p)
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_BACKSPACE:
                history = self.erase()
                if any(data["before"] != data["after"] for data in history):
                    self.history.append(history)
                    self.undo_history.clear()
            if event.key == pygame.K_z:
                self.undo()
            if event.key == pygame.K_x:
                self.redo()
            if pygame.K_1 <= event.key <= pygame.K_9 or pygame.K_KP1 <= event.key <= pygame.K_KP9:
                key = 0
                if pygame.K_1 <= event.key <= pygame.K_9:
                    key = event.key - pygame.K_0
                if pygame.K_KP1 <= event.key <= pygame.K_KP9:
                    key = event.key - pygame.K_KP_1 + 1
                history = self.write(key)
                if any(data["before"] != data["after"] for data in history):
                    self.history.append(history)
                    self.undo_history.clear()
            if event.key in keymap:
                dx, dy = keymap[event.key]
                nx, ny = self.last_selection
                nx += dx
                ny += dy
                if not (0 <= nx < 9 and 0 <= ny < 9):
                    continue
                if not any(keys[k] for k in center_keys + corner_keys):
                    self.selection.clear()
                self.selection.add((nx, ny))
                self.last_selection = (nx, ny)
            if event.key == pygame.K_ESCAPE:
                return self.select_scene

    def write(self, key: int) -> HistoryType:
        keys = pygame.key.get_pressed()
        selection = {pos for pos in self.selection if not self.grid[pos].fixed}
        history: HistoryType = []
        for pos in selection:
            cell = self.grid[pos]
            history.append({
                "pos": pos,
                "before": (cell.number, cell.center_memo.copy(), cell.corner_memo.copy()),
                "after": None
            })
        memo_selection = {pos for pos in self.selection if not self.grid[pos].number}
        if any(keys[k] for k in center_keys):
            if all(key in self.grid[pos].center_memo for pos in memo_selection):
                for pos in memo_selection:
                    self.grid[pos].center_memo.remove(key)
            else:
                for pos in memo_selection:
                    self.grid[pos].center_memo.add(key)
        elif any(keys[k] for k in corner_keys):
            if all(key in self.grid[pos].corner_memo for pos in memo_selection):
                for pos in memo_selection:
                    self.grid[pos].corner_memo.remove(key)
            else:
                for pos in memo_selection:
                    self.grid[pos].corner_memo.add(key)
        else:
            value = 0 if all(self.grid[pos].number == key for pos in selection) else key
            for pos in selection:
                self.grid[pos].number = value
        for data in history:
            cell = self.grid[data['pos']]
            data["after"] = (cell.number, cell.center_memo.copy(), cell.corner_memo.copy())
        return history

    def erase(self) -> HistoryType:
        selection = {pos for pos in self.selection if not self.grid[pos].fixed}
        history: HistoryType = []
        for pos in selection:
            cell = self.grid[pos]
            history.append({
                "pos": pos,
                "before": (cell.number, cell.center_memo.copy(), cell.corner_memo.copy()),
                "after": None
            })
        if all(self.grid[pos].number for pos in selection):
            for pos in selection:
                self.grid[pos].number = 0
        elif any(self.grid[pos].corner_memo | self.grid[pos].center_memo for pos in selection):
            for pos in selection:
                self.grid[pos].corner_memo.clear()
                self.grid[pos].center_memo.clear()
        else:
            for pos in selection:
                self.grid[pos].number = 0
        for data in history:
            cell = self.grid[data['pos']]
            data["after"] = (cell.number, cell.center_memo.copy(), cell.corner_memo.copy())
        return history

    def undo(self):
        if not self.history:
            return
        history = self.history.pop()
        for data in history:
            cell = self.grid[data['pos']]
            cell.number = data["before"][0]
            cell.center_memo = data["before"][1]
            cell.corner_memo = data["before"][2]
        self.undo_history.append(history)

    def redo(self):
        if not self.undo_history:
            return
        history = self.undo_history.pop()
        for data in history:
            cell = self.grid[data['pos']]
            cell.number = data["after"][0]
            cell.center_memo = data["after"][1]
            cell.corner_memo = data["after"][2]
        self.history.append(history)

    @staticmethod
    def get_cell() -> Optional[Point]:
        mx, my = pygame.mouse.get_pos()
        x, y = (mx - state.left) // state.unit, (my - state.top) // state.unit
        if not (0 <= x < 9 and 0 <= y < 9):
            return
        return x, y

    def run(self) -> Optional[callback]:
        result = self.get_event()
        if result is not None:
            return result

        self.click_time = max(0, self.click_time - 1)

        if any(pygame.mouse.get_pressed()):
            if pos := self.get_cell():
                self.selection.add(pos)
                self.last_selection = pos

        for pos in product(range(9), repeat=2):  # type: tuple[int, int]
            self.grid[pos].selected = pos in self.selection
            self.grid[pos].last_selected = pos == self.last_selection

        errors = v_check(self.grid, tuple(a in self.variants for a in ("??", "A?R", "??")))
        for variant in self.variants:
            errors |= checkers[variant](self.grid)
        for pos in product(range(9), repeat=2):  # type: tuple[int, int]
            self.grid[pos].error = pos in errors

        if all(self.grid[pos].number for pos in product(range(9), repeat=2)) and not errors:
            if self.clear_time < 0:
                self.clear_time = perf_counter() - self.begin_time
            self.screen.fill((48, 48, 48))

        time = self.clear_time if self.clear_time > 0 else perf_counter() - self.begin_time
        pos = (state.unit // 2, state.height - state.unit // 2)
        self.render(f"{time:05.1f}", pos, size=state.unit * 2 // 3, anchor="bottomleft")

        state.number_font = pygame.font.Font("resource/font/D2Coding.ttf", state.unit * 2 // 3)
        state.note_font = pygame.font.Font("resource/font/D2Coding.ttf", state.unit // 3)
        state.memo_font = pygame.font.Font("resource/font/D2Coding.ttf", state.unit // 4)
        state.side_font = pygame.font.Font("resource/font/D2Coding.ttf", state.unit // 2)

        self.cell_group.update()
        self.cell_group.draw(self.screen)

        self.render(state.level, (state.unit // 2, state.unit // 2), size=state.unit, anchor="topleft")

        for i in range(4):
            start_pos = (state.left + state.unit * 3 * i, state.top)
            end_pos = (state.left + state.unit * 3 * i, state.bottom)
            pygame.draw.line(self.screen, (255, 255, 255), start_pos, end_pos, width=3)
            start_pos = (state.left, state.top + state.unit * 3 * i)
            end_pos = (state.right, state.top + state.unit * 3 * i)
            pygame.draw.line(self.screen, (255, 255, 255), start_pos, end_pos, width=3)

        for i in range(9):
            text = " ".join(map(str, self.grid.top[i]))
            text_image = state.side_font.render(text, True, (255, 255, 255))
            text_image = pygame.transform.rotate(text_image, -90)
            pos = (state.left + state.unit // 2 + state.unit * i, state.top - state.unit // 3)
            text_rect = text_image.get_rect(midbottom=pos)
            self.screen.blit(text_image, text_rect)

            text = " ".join(map(str, self.grid.left[i]))
            text_image = state.side_font.render(text, True, (255, 255, 255))
            pos = (state.left - state.unit // 3, state.top + state.unit // 2 + state.unit * i)
            text_rect = text_image.get_rect(midright=pos)
            self.screen.blit(text_image, text_rect)

        for x, y in product(range(8), range(9)):
            text_image = state.side_font.render(self.grid.between[y][x], True, (255, 255, 255))
            pos = (state.left + state.unit * (x + 1), state.top + state.unit // 2 + state.unit * y)
            text_rect = text_image.get_rect(center=pos)
            self.screen.blit(text_image, text_rect)
