import pygame

class Button():
    def __init__(self, text, font, center_loc, size, color = None, shading = False, hidden = False):
        self.text = text
        self.font = font
        self.loc = center_loc
        self.size = size
        self.color = color
        self.shading = shading
        self.hidden = hidden

        self.on = False
        self.prepare_surfs_rects_and_text()

    
    def prepare_surfs_rects_and_text(self):
        # Create the text Surf
        if self.color is None:
            self.color = (0,0,0)
        self.textSurf = self.font.render(self.text, True, self.color)
        # Create a Rect that is the same size as the text Surf and located in the middle
        self.text_rect = self.textSurf.get_rect(center= self.loc)

        # Create the button Surf and Rect, which is also located in the middle
        self.button_surf = pygame.Surface(self.size)
        self.button_rect = self.button_surf.get_rect(center= self.loc)

    def draw_on_screen(self, screen):
        if (not self.hidden):
            pygame.draw.rect(screen, (220,220,220), self.button_rect, width=0) 

        if self.on:
            pygame.draw.rect(screen, (176,196,222), self.button_rect, width=0) 
        elif self.shading:
            pygame.draw.rect(screen, (176,196,222), self.button_rect, width=0) 

        if (not self.hidden):
            pygame.draw.rect(screen, (0,0,0), self.button_rect, width=2)
            screen.blit(self.textSurf, self.text_rect)
    
    def is_button_clicked(self, mouse_loc):
        # If the mouse location collides with the Button Rectangle, then return True
        return (self.button_rect.collidepoint(mouse_loc))

    def is_mouse_over_button(self, mouse_loc):
        self.shading = self.button_rect.collidepoint(mouse_loc)

    def const_selected_button(self, yes_or_no):
        self.on = yes_or_no

    def get_label(self):
        return self.text

    def get_button_rect(self):
        return self.button_rect
    
  
