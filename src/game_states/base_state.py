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

    def draw_text(self, screen, text, font, loc, text_color, loc_position = "center", trailing = None):
        if trailing != None:
            text = self.shorten_text(text, trailing)
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center= loc)
        if loc_position == "midleft":
            text_rect = text_surf.get_rect(midleft= loc)
        screen.blit(text_surf, text_rect)

    def shorten_text(self, text, type):
        if type == "curr_file_name":
            if len(text) > 23:
                text = text[:20] + "..."
        elif type == "prev_folder_name" or type == "prev_file_name":
            if len(text) > 13:
                text = text[:7] + "..." + text[-3:]
        elif type == "selec_file_name":
            if len(text) > 24:
                text = text[:18] + "..." + text[-3:]
        elif type == "active_file_name":
            if len(text) > 25:
                text = text[:18] + "..." + text[-4:]
        elif type == "selec_video_name":
            if len(text) > 17:
                text = text[:7] + "..." + text[-7:]
        return text

    def safe_to_load(self):
        return True