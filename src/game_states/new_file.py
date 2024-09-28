import pygame
import src.utilities.constants as const
from src.utilities.button import Button
import src.utilities.textbox.pygametextboxinput as pyTxtBx
from src.game_states.base_state import BaseState


""" New File Game State """

class New_Doc(BaseState):
    def __init__(self, game):

        # Initializing the Base Class
        super().__init__(game)

        self.prepare_surfs_and_rects()
        self.prepare_buttons()

        self.file_name = None
        self.prev_selected_map_button = None
        self.selected_map_button = None
        self.missing_map_info = False

        # Create the TextBox
        self.textbox = pyTxtBx.TextInputBox(526, 305, font_family="arial", font_size=22, max_width=443, max_height=30, text_color="black", cursor_color="black")
        self.textbox_is_activated = False
        self.events = []
        
    def handle_events(self, events):
        self.events = events
        for event in events:
            if event.type == pygame.QUIT:
                self.game.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check to see if the User selected a Map
                    for map_button in self.map_buttons:
                        if (map_button.is_button_clicked(event.pos)):
                            self.selected_map_button = map_button

                    # Check to see if the User selected the Next Button
                    if (self.next_button.is_button_clicked(event.pos)):
                        if ((self.textbox.get_text() == "") or (self.selected_map_button == None)):
                            self.missing_map_info = True
                        else:
                            self.missing_map_info = False
                            # Check to see if there is a stored Next State
                            if (self.game.get_stored_state()):
                                # Updated the stored state's info
                                self.game.update_state_info(title=self.textbox.get_text(), map=self.selected_map_button.text)
                                self.game.enter_stored_state()
                                self.game.reset_stored_state()
                            # If not, just create a new Directories State
                            else:
                                # Entering the New Directories State
                                self.game.enter_new_state("Directories", file_name= self.textbox.get_text(), map_selected= self.selected_map_button.text, creating_new_file= True)
                            
                    # Check to see if the User selected the Cancel Button
                    if (self.cancel_button.is_button_clicked(event.pos)):
                        # Check to see if there is a stored Next State
                        if (self.game.get_stored_state()):
                                self.game.enter_stored_state()
                                self.game.reset_stored_state()
                        # If not, just return to the prev. state
                        else:
                            self.game.return_to_prev_state()

                    self.textbox_is_activated = self.textbox.editTextBox(event.pos)
                    
    def update(self):
        if self.prev_selected_map_button is not None and self.prev_selected_map_button != self.selected_map_button:
            self.prev_selected_map_button.const_selected_button(False)
        self.prev_selected_map_button = self.selected_map_button
        if self.selected_map_button:
            self.selected_map_button.const_selected_button(True)

        self.next_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.cancel_button.is_mouse_over_button(pygame.mouse.get_pos())
        for map_button in self.map_buttons:
            map_button.is_mouse_over_button(pygame.mouse.get_pos())

        # Update the textbox
        self.textbox.update(self.events, self.textbox_is_activated)
        
    def prepare_surfs_and_rects(self):
        # Prepare the background Surf and Rect
        self.backgroundColorForScreenSurf = pygame.Surface((const.NEW_FILE_STATE_WIDTH, const.NEW_FILE_STATE_HEIGHT))
        self.backgroundColorForScreenSurf.fill((244,164,96))
        self.backgroundRect = self.backgroundColorForScreenSurf.get_rect(center=(const.DISPLAY_WIDTH/2, const.DISPLAY_HEIGHT/2))
    
    def draw_on_screen(self, screen):
        pygame.draw.rect(screen, "seashell2", [0, 0, const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT], 5, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        screen.blit(self.backgroundColorForScreenSurf, self.backgroundRect)
        pygame.draw.rect(screen, (0,0,0), self.backgroundRect, width=3)

        pygame.draw.rect(screen, (255,222,173),[610, 165, 250, 65])
        pygame.draw.rect(screen, (139,69,19), [610, 165, 250, 65], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        self.draw_text(screen, "New File", const.TEXT_FONT_HEADER, (735.0, 200), "black")
        self.draw_text(screen, "Step 1) Name the File", const.TEXT_FONT_SUBHEADER, (735.0, 270), "black")
        self.draw_text(screen, "Name:", pygame.font.SysFont("arial", 18), (486, 315), "black")
        self.draw_text(screen, "Step 2) Select Map", const.TEXT_FONT_SUBHEADER, (735.0, 370), "black")

        # Draw the textbox and text in
        pygame.draw.rect(screen, "white", [519, 300, 455, 35])
        pygame.draw.rect(screen, "black", [519, 300, 455, 35], 1)
        self.textbox.render(screen)

        # Draw the buttons
        for button in self.map_buttons:
            button.draw_on_screen(screen)
        self.next_button.draw_on_screen(screen)
        self.cancel_button.draw_on_screen(screen)

        if (self.missing_map_info):
            self.draw_text(screen, "(Please type a file name and select a map before clicking Next)", const.TEXT_FONT_MAP_BUTTON, (350 + const.NEW_FILE_STATE_WIDTH/2, 550), "black")


    """ Helper Functions """

    def prepare_buttons(self):
        # Create Next and Cancel Buttons
        self.next_button = Button("Next", const.TEXT_FONT_SUBHEADER, (900, 600),(130, 50))
        self.cancel_button = Button("Cancel", const.TEXT_FONT_SUBHEADER, (1040, 600), (130, 50))
        
        map_names = ["Abyss", "Ascent", "Bind", "Breeze", "Fracture", "Haven", "Icebox", "Lotus", "Pearl", "Split", "Sunset"]
        base_x = 350 + const.NEW_FILE_STATE_WIDTH/2
        offset = 25 + 20
        y_positions = [460 - offset, 510 - offset, 560 - offset]
        self.map_buttons = []

        for i, map_name in enumerate(map_names):
            # Determines the row and index within the row
            row = i // 5
            position_in_row = i % 5
            
            # Calculate x position based on index
            x_position = base_x + (position_in_row - 2) * 113

            # Create and add the button
            position = (x_position, y_positions[row])
            button = Button(map_name, const.TEXT_FONT_MAP_BUTTON, position, (105,40))
            self.map_buttons.append(button)
            


