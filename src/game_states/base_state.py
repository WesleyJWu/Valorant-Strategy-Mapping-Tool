from abc import ABC, abstractmethod

""" Base State used by all Game States """

class BaseState(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def handle_events(self, events):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def prepare_surfs_and_rects(self):
        pass

    @abstractmethod
    def draw_on_screen(self, screen):
        pass


    """ Helper Functions: """

    def draw_text(self, screen, text, font, loc, text_color, loc_position = "center"):
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center= loc)
        if loc_position == "midleft":
            text_rect = text_surf.get_rect(midleft= loc)
        screen.blit(text_surf, text_rect)

