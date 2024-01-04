import pygame
import src.utilities.constants as const
from src.utilities.button import Button
from src.game_states.base_state import BaseState

""" Main Menu Game State """

class Main_Menu(BaseState):
    def __init__(self, game):

        # Initialiazing the Base Class
        super().__init__(game)

        self.prepare_surfs_and_rects()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check if the User selected the New File button
                    if self.start_button.is_button_clicked(event.pos):
                        self.game.enter_new_state("New Doc")
                    # Check if the User selected the Load File button
                    elif self.load_button.is_button_clicked(event.pos):
                        self.game.enter_new_state("Directories", creating_new_file=False )
                    # Check if the User selected the Analyze Video button
                    elif self.analyze_vod_button.is_button_clicked(event.pos):
                        self.game.enter_new_state("Analyze VOD")
                    # Check if the User selected the Quit button
                    elif self.quit_button.is_button_clicked(event.pos):
                        self.game.running = False
        
    def update(self):
        # Checks if the mouse is hovering over the buttons
        self.start_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.load_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.analyze_vod_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.quit_button.is_mouse_over_button(pygame.mouse.get_pos())
        

    def prepare_surfs_and_rects(self):
        # Create the Surf for the background color
        self.backgroundColorForScreenSurf = pygame.Surface((const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT))
        self.backgroundColorForScreenSurf.fill(const.TAN)  
        # Create the 4 Buttons on the Main Menu (New File, Load File, Analyze Video, and Quit)
        self.start_button = Button("New File", const.TEXT_FONT_HEADER, (735.0, 400.0), (350, 80))
        self.load_button = Button("Load File", const.TEXT_FONT_HEADER, (735.0, 488.0), (350, 80))
        self.analyze_vod_button = Button("Analyze Video", const.TEXT_FONT_HEADER, (735.0, 576.0), (350, 80))
        self.quit_button = Button("Quit", const.TEXT_FONT_HEADER, (735.0, 664.0), (350, 80))  

    def draw_on_screen(self, screen):
        # Blit the background color to the Screen
        screen.blit(self.backgroundColorForScreenSurf, (0,0))
        pygame.draw.rect(screen, "seashell2", [0, 0, const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT], 5, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)

        # Draw the Title Rect in
        pygame.draw.rect(screen, (255,222,173),[370, 100, 725, 240])
        pygame.draw.rect(screen, (139,69,19), [370, 100, 725, 240], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)

        # Draw the Title In
        self.draw_text(screen, "Valorant Strategy", pygame.font.SysFont("arial", 85), (735, 170), "black", "center")
        self.draw_text(screen, "Mapping Tool", pygame.font.SysFont("arial", 85), (735, 270), "black", "center")

        # Draw the Buttons on the Screen
        self.start_button.draw_on_screen(screen)
        self.load_button.draw_on_screen(screen)
        self.analyze_vod_button.draw_on_screen(screen)
        self.quit_button.draw_on_screen(screen)





