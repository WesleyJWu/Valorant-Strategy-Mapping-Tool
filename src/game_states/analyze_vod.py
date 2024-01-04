import pygame

import src.utilities.constants as const
from src.utilities.button import Button

from src.game_states.base_state import BaseState
import pygame_gui
from pygame_gui.windows.ui_file_dialog import UIFileDialog
from pygame_gui.elements.ui_button import UIButton
from src.utilities.icon_sprites import Icon

""" Analyze Video State """

class Analyze_VOD(BaseState):
    def __init__(self, game):

        # Initializing the Base Class
        super().__init__(game)

        self.prepare_surfs_and_rects()
        self.prepare_buttons()
        self.prepare_agent_icons()

        self.file_name = None
        self.prev_selected_map_button = None
        self.selected_map_button = None
        self.missing_map_info = False
        self.selected_atk_agents =[]
        self.selected_def_agents =[]
        self.full_video_path = ""

        self.pygame_gui_manager = pygame_gui.UIManager((const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT))
        self.file_selection_button = UIButton(relative_rect=pygame.Rect(675, 111, 130, 50), manager=self.pygame_gui_manager, text='Select Video')
     
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
                    
                    # Check to see if the User selected any of the Atk Agents
                    for atk_agent in self.atk_agents:
                        if atk_agent.mouseSelect(event.pos):
                            # Selecting an Atk Agent will either place a White border around it or remove its White border
                            if atk_agent not in self.selected_atk_agents:
                                atk_agent.drawSelection(True)
                                self.selected_atk_agents.append(atk_agent)
                            else:
                                atk_agent.drawSelection(False)
                                self.selected_atk_agents.remove(atk_agent)
                    
                    # Check to see if the User selected any of the Def Agents
                    for def_agent in self.def_agents:
                        if def_agent.mouseSelect(event.pos):
                            # Selecting a Def Agent will either place a White border around it or remove its White border
                            if def_agent not in self.selected_def_agents:
                                def_agent.drawSelection(True)
                                self.selected_def_agents.append(def_agent)
                            else:
                                def_agent.drawSelection(False)
                                self.selected_def_agents.remove(def_agent)
                                
                    # Check to see if the User selected the Save Button
                    if (self.save_button.is_button_clicked(event.pos)):
                        if ((self.full_video_path == "") or (self.selected_map_button == None) or (len(self.selected_atk_agents) != 5) or (len(self.selected_def_agents) != 5)):
                            self.missing_map_info = True
                        else:
                            self.missing_map_info = False
                            # Create and Enter the Directories Game State
                            self.game.enter_new_state("Directories", map_selected= self.selected_map_button.text, creating_new_file= True, analyze_VOD= True, video_name= self.video_name, full_video_path = self.full_video_path, agents_of_interest= self.selected_def_agents)
                        
                    # Check to see if the User selected the Cancel Button
                    elif (self.cancel_button.is_button_clicked(event.pos)):
                        self.game.return_to_prev_state()

            if event.type == pygame.USEREVENT:
                # Check if the User selected the File Dialog
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.file_selection_button:
                        self.file_selection = UIFileDialog(rect=pygame.Rect(0, 0, 500, 500), manager=self.pygame_gui_manager, allow_picking_directories=True)
                    if event.ui_element == self.file_selection.ok_button:
                        self.full_video_path = str(self.file_selection.current_file_path)
                    
            
            self.pygame_gui_manager.process_events(event)

        self.pygame_gui_manager.update(self.game.time_delta)
            
                    
    def update(self):
        # If the User selected another Map, then the previous selected Map Button is "turned off"
        if (self.prev_selected_map_button is not None and self.prev_selected_map_button != self.selected_map_button):
            self.prev_selected_map_button.const_selected_button(False)
        self.prev_selected_map_button = self.selected_map_button
        # "Turn On" the currently selected Map
        if self.selected_map_button:
            self.selected_map_button.const_selected_button(True)

        # Check to see if the User's mouse is hovering over any of the buttons
        self.save_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.cancel_button.is_mouse_over_button(pygame.mouse.get_pos())
        for map_button in self.map_buttons:
            map_button.is_mouse_over_button(pygame.mouse.get_pos())
        
    def prepare_surfs_and_rects(self):
        self.hidden_background =  pygame.Surface((const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT))
        self.hidden_background.fill(const.TAN)
        self.backgroundColorForScreenSurf = pygame.Surface((const.NEW_FILE_STATE_WIDTH, const.NEW_FILE_STATE_HEIGHT + 250))
        self.backgroundColorForScreenSurf.fill((244,164,96))
        self.backgroundRect = self.backgroundColorForScreenSurf.get_rect(center=(const.DISPLAY_WIDTH/2, const.DISPLAY_HEIGHT/2))
    
    def draw_on_screen(self, screen):
        # Draw in the background colors and the border rects
        screen.blit(self.hidden_background, (0,0))
        pygame.draw.rect(screen, "seashell2", [0, 0, const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT], 5, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0) #mistyrose4
        screen.blit(self.backgroundColorForScreenSurf, self.backgroundRect)
        pygame.draw.rect(screen, (0,0,0), self.backgroundRect, width=3)
        pygame.draw.rect(screen, "slategray4",[450, 443, 570, 250])

        # Draw in the text
        pygame.draw.rect(screen, (255,222,173),[560, 37, 350, 65])
        pygame.draw.rect(screen, (139,69,19), [560, 37, 350, 65], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        self.draw_text(screen, "Analyze Video", const.TEXT_FONT_HEADER, (350 + const.NEW_FILE_STATE_WIDTH/2, 68), "black")
        self.draw_text(screen, "Step 1) Select Video", const.TEXT_FONT_SUBHEADER, (const.NEW_FILE_STATE_WIDTH/2, 270 - 132), "black", "midleft")
        self.draw_text(screen, "Step 2) Select Map", const.TEXT_FONT_SUBHEADER, (const.NEW_FILE_STATE_WIDTH/2, 270 - 50), "black", "midleft")
        self.draw_text(screen, "Step 3) Choose the Agents to Scan for (5 Atk & 5 Def)", const.TEXT_FONT_SUBHEADER, (const.NEW_FILE_STATE_WIDTH/2, 270 - 50 + 170 + 30), "black", "midleft")

        for button in self.map_buttons:
            button.draw_on_screen(screen)
        
        self.atk_agents.draw(screen)
        self.def_agents.draw(screen)

        self.save_button.draw_on_screen(screen)
        self.cancel_button.draw_on_screen(screen)

        if (self.full_video_path != ""):
            path_elements = self.full_video_path.split("/")
            self.video_name = path_elements[-1]
            # Self.video_name is the Video's Name without its file extension
            self.video_name = ".".join(self.video_name.split(".")[:-1])
            self.draw_text(screen, self.video_name, const.TEXT_FONT_SUBHEADER, (const.NEW_FILE_STATE_WIDTH/2 + 435, 270 - 132), "black", "midleft")

        if (self.missing_map_info):
            self.draw_text(screen, "(Please Complete All Steps Before Saving)", const.TEXT_FONT_MAP_BUTTON, (const.NEW_FILE_STATE_WIDTH/2 - 32, 730), "black", "midleft")

        # Draw the File Dialog in
        self.pygame_gui_manager.draw_ui(screen)

    """ Helper Functions """

    def prepare_buttons(self):
        # Create the Save and Cancel Buttons
        self.save_button = Button("Save", const.TEXT_FONT_SUBHEADER, (900, 730), (105,40))
        self.cancel_button = Button("Cancel", const.TEXT_FONT_SUBHEADER, (1040, 730), (105,40))

        # Create the Map Buttons
        map_names = ["Ascent", "Bind", "Breeze", "Fracture", "Haven", "Icebox", "Pearl", "Split", "Lotus", "Sunset"]
        base_x = 350 + const.NEW_FILE_STATE_WIDTH/2
        y_positions = [280, 330]
        self.map_buttons = []
        for i, map_name in enumerate(map_names):
            # Determine the row number and the index within the row
            row = i // 5
            position_in_row = i % 5
            
            # Calculate the x position based on the index in the row
            x_position = base_x + (position_in_row - 2) * 113

            # Create and add the button
            position = (x_position, y_positions[row])
            button = Button(map_name, const.TEXT_FONT_MAP_BUTTON, position, (105,40))
            self.map_buttons.append(button)
            
    def prepare_agent_icons(self):
        # Create the Agent Sprite Group for the Atk and Def Agents
        self.atk_agents = pygame.sprite.Group()
        self.def_agents = pygame.sprite.Group()
        for index in range(len(const.AGENT_LIST)):
            loc1 = self.starting_location("ATK", index)
            self.atk_agents.add(Icon(const.AGENT_LIST[index], "agent", loc1, "ATK", colorBackground=const.PALE_VIOLET_RED, moveable=False))
            loc2 = self.starting_location("DEF", index)
            self.def_agents.add(Icon(const.AGENT_LIST[index], "agent", loc2, "DEF", colorBackground=const.PALE_GREEN_3, moveable=False))

    def starting_location(self, team, index):
        centerX = 0
        centerY = 0
        agent_y_row_coords = []
        if (team == "ATK"):
            agent_y_row_coords = [485, 533]
        else:
            agent_y_row_coords = [600, 648]
        position_in_row = index % 11
        row = index//11
        centerX = 500 + ((const.AGENT_HEIGHT_WIDTH + 2) * position_in_row)
        centerY = agent_y_row_coords[row]

        return centerX, centerY



