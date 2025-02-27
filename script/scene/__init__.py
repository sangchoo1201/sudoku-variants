from typing import Optional, Type

import pygame

callback = Type["Scene"]


class Scene:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def get_event(self) -> Optional[callback]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return End

    def run(self) -> Optional[callback]:
        return self.get_event()


class End(Scene):
    pass
