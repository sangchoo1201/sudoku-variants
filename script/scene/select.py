import pygame

from script.scene import *
from script.text import TextRender
from script.state import state
from script.file import get_level_list

KEYMAP = {pygame.K_UP: -1, pygame.K_DOWN: 1}


class Select(Scene):
    def __init__(self, screen: pygame.Surface):
        from script.scene.play import Play

        super().__init__(screen)
        self.render = TextRender(screen, size=state.unit // 2, color=(24, 24, 30))
        self.play_scene = Play
        self.level_list = get_level_list()

    def get_event(self) -> Optional[callback]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return End
            if event.type == pygame.MOUSEWHEEL:
                state.level_selection -= event.y
                state.level_selection %= len(self.level_list)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    state.level = self.level_list[state.level_selection]
                    return self.play_scene
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return End
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                state.level = self.level_list[state.level_selection]
                return self.play_scene
            if event.key in KEYMAP:
                state.level_selection += KEYMAP[event.key]
                state.level_selection %= len(self.level_list)

    def run(self) -> Optional[callback]:
        result = self.get_event()
        if result is not None:
            return result

        if state.level_selection < state.level_offset:
            state.level_offset = state.level_selection
        elif state.level_selection >= state.level_offset + 10:
            state.level_offset = state.level_selection - 9

        for i, level in enumerate(self.level_list[state.level_offset: state.level_offset + 10]):
            color = (255, 255, 0) if i + state.level_offset == state.level_selection else (255, 255, 255)
            self.render(level, (state.width // 2, state.top + state.unit * i), size=state.unit // 2, color=color)
