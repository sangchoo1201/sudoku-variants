import pygame

from script.scene import Scene, End
from script.scene.select import Select
from script.state import state

import asyncio

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
clock = pygame.time.Clock()

async def main():
    scene: Scene = Select(screen)

    while True:
        screen.fill((0, 0, 0))

        result = scene.run()
        if result is not None:
            if result is End:
                pygame.quit()
                break
            scene = result(screen)
        else:
            pygame.display.update()

        clock.tick(state.fps)
        await asyncio.sleep(0)


asyncio.run(main())
