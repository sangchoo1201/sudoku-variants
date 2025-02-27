import pygame

PosType = (pygame.math.Vector2 | tuple[int, int])
ColorType = (pygame.color.Color | tuple[int, int, int] | tuple[int, int, int, int])


class TextRender:
    def __init__(self, screen: pygame.Surface, size: int,
                 color: ColorType = pygame.color.Color(255, 255, 255),
                 font: str = "D2Coding.ttf"):
        self.screen = screen
        self.size = size
        self.color = color
        self.font = font

    def __call__(self, text: str, pos: PosType, alpha: int = None,
                 size: int = None, color: ColorType = None,
                 font: str = None, anchor: str = "center"):
        text_image = self.get_image(text, alpha, size, color, font)
        self.blit(text_image, pos, anchor)

    def get_image(self, text: str, alpha: int = None, size: int = None,
                  color: ColorType = None, font: str = None) -> pygame.Surface:
        if size is None:
            size = self.size
        if color is None:
            color = self.color
        if font is None:
            font = self.font

        color = pygame.color.Color(color)

        text_font = pygame.font.Font(f"resource/font/{font}", size)
        text_image = text_font.render(text, True, color).convert_alpha()
        if alpha is not None:
            text_image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        return text_image

    def blit(self, text_image: pygame.Surface, pos: PosType, anchor: str = "center"):
        pos = pygame.math.Vector2(pos)
        text_rect = text_image.get_rect(**{anchor: pos})
        self.screen.blit(text_image, text_rect)

    def get_rect(self, text: str, pos: PosType, size: int = None,
                 font: str = None, anchor: str = "center") -> pygame.rect.Rect:
        image = self.get_image(text, size=size, font=font)
        return image.get_rect(**{anchor: pos})
