import pygame
import os
import cv2
import platformdirs

import src.utilities.constants as const
from src.utilities.button import Button
import src.utilities.textbox.pygametextboxinput as pyTxtBx

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
        self.video_textbox = pyTxtBx.TextInputBox(824, 126, font_family="arial", font_size=20, max_width=225, max_height=30, text_color="black", cursor_color="black")
        self.video_textbox.set_text("")
        self.events = []
        self.prev_selected_map_button = None
        self.selected_map_button = None
        self.missing_map_info = False
        self.selected_def_agents = []
        self.selected_atk_agents = []
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
                    
                    # Check to see if the User selected any of the Def Agents
                    for def_agent in self.def_agents:
                        if def_agent.mouseSelect(event.pos):
                            if def_agent not in self.selected_def_agents:
                                def_agent.drawSelection(True)
                                self.selected_def_agents.append(def_agent)
                            else:
                                def_agent.drawSelection(False)
                                self.selected_def_agents.remove(def_agent)
                    
                    # Check to see if the User selected any of the Atk Agents
                    for atk_agent in self.atk_agents:
                        if atk_agent.mouseSelect(event.pos):
                            if atk_agent not in self.selected_atk_agents:
                                atk_agent.drawSelection(True)
                                self.selected_atk_agents.append(atk_agent)
                            else:
                                atk_agent.drawSelection(False)
                                self.selected_atk_agents.remove(atk_agent)
                                
                    # Check to see if the User selected the Save Button
                    if (self.next_button.is_button_clicked(event.pos)):
                        if ((self.full_video_path == "") or (self.selected_map_button == None) or (len(self.selected_def_agents) > 5) or (len(self.selected_atk_agents) > 5)):
                            self.missing_map_info = True
                        else:
                            self.missing_map_info = False
                            self.capture_r1_scrsht()
                            # Create and Enter the Map Boundaries Game State
                            self.game.enter_new_state("Map Boundaries", map_name = self.selected_map_button.text, r1_scrshot_path = self.scrshot_path, video_name= self.video_name, full_video_path = self.full_video_path, def_agents= self.selected_def_agents, atk_agents = self.selected_atk_agents)

                    # Check to see if the User selected the Cancel Button
                    if (self.cancel_button.is_button_clicked(event.pos)):
                        if (self.game.get_stored_state()):
                                self.game.enter_stored_state()
                                self.game.reset_stored_state()
                        else:
                            self.game.return_to_prev_state()

            if event.type == pygame.USEREVENT:
                # Check to see if the User selected the File Dialog
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.file_selection_button:
                        downloads_folder = platformdirs.user_downloads_dir()
                        self.file_selection = UIFileDialog(rect=pygame.Rect(0, 0, 500, 500), manager=self.pygame_gui_manager, initial_file_path=downloads_folder, allow_picking_directories=True)

                    if event.ui_element == self.file_selection.ok_button:
                        self.full_video_path = str(self.file_selection.current_file_path)
                        path_elements = self.full_video_path.split("/")
                        self.video_textbox.set_text(path_elements[-1])
            
            self.pygame_gui_manager.process_events(event)
        self.pygame_gui_manager.update(self.game.time_delta)
        
    def update(self):
        self.video_textbox.update(self.events, False)
        if self.prev_selected_map_button is not None and self.prev_selected_map_button != self.selected_map_button:
            self.prev_selected_map_button.const_selected_button(False)
        self.prev_selected_map_button = self.selected_map_button
        if self.selected_map_button:
            self.selected_map_button.const_selected_button(True)

        self.next_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.cancel_button.is_mouse_over_button(pygame.mouse.get_pos())
        for map_button in self.map_buttons:
            map_button.is_mouse_over_button(pygame.mouse.get_pos())
        
    def prepare_surfs_and_rects(self):
        self.hidden_background =  pygame.Surface((const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT))
        self.hidden_background.fill(const.TAN)
        self.backgroundColorForScreenSurf = pygame.Surface((770, 750))
        self.backgroundColorForScreenSurf.fill((244,164,96))
        self.backgroundRect = self.backgroundColorForScreenSurf.get_rect(center=(const.DISPLAY_WIDTH/2, const.DISPLAY_HEIGHT/2))
    
    def draw_on_screen(self, screen):
        screen.blit(self.hidden_background, (0,0))
        pygame.draw.rect(screen, "seashell2", [0, 0, const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT], 5, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        screen.blit(self.backgroundColorForScreenSurf, self.backgroundRect)
        pygame.draw.rect(screen, (0,0,0), self.backgroundRect, width=3)
        pygame.draw.rect(screen, (210,105,30),[400, 415, 330, 283])
        pygame.draw.rect(screen, (210,105,30),[750, 415, 330, 283])

        pygame.draw.rect(screen, (255,222,173),[560, 37, 350, 65])
        pygame.draw.rect(screen, (139,69,19), [560, 37, 350, 65], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        self.draw_text(screen, "Analyze Video", const.TEXT_FONT_HEADER, (735, 68), "black")
        self.draw_text(screen, "Step 1) Select video", const.TEXT_FONT_SUBHEADER, (385, 270 - 132), "black", "midleft")
        self.draw_text(screen, "Step 2) Select map", const.TEXT_FONT_SUBHEADER, (385, 270 - 80), "black", "midleft")
        self.draw_text(screen, "Step 3) Select up to 5 DEF and 5 ATK agents to track", const.TEXT_FONT_SUBHEADER, (385, 390), "black", "midleft")

        for button in self.map_buttons:
            button.draw_on_screen(screen)
        
        self.def_agents.draw(screen)
        self.atk_agents.draw(screen)

        self.next_button.draw_on_screen(screen)
        self.cancel_button.draw_on_screen(screen)

        if (self.full_video_path != ""):
            path_elements = self.full_video_path.split("/")
            self.video_name = path_elements[-1]

            # Draw in the Video Name Textbox
            pygame.draw.rect(screen, "white", [const.NEW_FILE_STATE_WIDTH/2 + 435, 270 - 132 - 19, 230, 35])
            pygame.draw.rect(screen, "black", [const.NEW_FILE_STATE_WIDTH/2 + 435, 270 - 132 - 19, 230, 35], 1)
            self.video_textbox.render(screen)

        if (self.missing_map_info):
            self.draw_text(screen, "(Please follow all the steps)", const.TEXT_FONT_MAP_BUTTON, (435, 730), "black", "midleft")

        # Draw the File Dialog in
        self.pygame_gui_manager.draw_ui(screen)

    """ Helper Functions """


    def prepare_buttons(self):
        # Create Next and Cancel Buttons
        self.next_button = Button("Next", const.TEXT_FONT_SUBHEADER, (900, 730), (130, 50))
        self.cancel_button = Button("Cancel", const.TEXT_FONT_SUBHEADER, (1040, 730), (130, 50))
        
        map_names = ["Abyss", "Ascent", "Bind", "Breeze", "Fracture", "Haven", "Icebox", "Pearl", "Split", "Lotus", "Sunset"]
        base_x = 735
        y_positions = [240, 290, 340]
        self.map_buttons = []

        for i, map_name in enumerate(map_names):
            # Determines the row number and index within the row
            row = i // 5
            position_in_row = i % 5
            

            # Calculate x position based on index
            x_position = base_x + (position_in_row - 2) * 113

            # Create and add the button
            position = (x_position, y_positions[row])
            button = Button(map_name, const.TEXT_FONT_MAP_BUTTON, position, (105,40))
            self.map_buttons.append(button)
            
    def prepare_agent_icons(self):
        # Create the Agent Sprite Groups for the Atk and Def Agents
        self.def_agents = pygame.sprite.Group()
        self.atk_agents = pygame.sprite.Group()
        for index in range(len(const.AGENT_LIST)):
            loc = self.starting_location("DEF", index)
            self.def_agents.add(Icon(const.AGENT_LIST[index], "agent", loc, "DEF", colorBackground=const.PALE_GREEN_3, moveable=False))
            loc = self.starting_location("ATK", index)
            self.atk_agents.add(Icon(const.AGENT_LIST[index], "agent", loc, "ATK", colorBackground=const.PALE_VIOLET_RED, moveable=False))

    def starting_location(self, team, index):
        centerX = 0
        centerY = 0
        offset = 75
        agent_y_row_coords = [535 - offset, 583 - offset, 631 - offset, 679 - offset, 727 - offset, 775 - offset]

        position_in_row = index % 6
        row = index//6

        if team == "DEF":
            centerX = 445 + ((const.AGENT_HEIGHT_WIDTH + 2) * position_in_row)
            centerY = agent_y_row_coords[row]
        if team == "ATK":
            centerX = 320 + 475 + ((const.AGENT_HEIGHT_WIDTH + 2) * position_in_row)
            centerY = agent_y_row_coords[row]

        return centerX, centerY

    def capture_r1_scrsht(self):
        file_path = os.path.abspath(__file__)
        cv_direc_path = os.path.dirname(file_path)
        src_directory_path = os.path.dirname(cv_direc_path)
        project_root = os.path.dirname(src_directory_path)
        game_files_path = os.path.join(project_root, "game_files")
        # print("Game Files Path ------- ", game_files_path)

        scrshot_fnd = False

        # Create a VideoCapture Object
        capture = cv2.VideoCapture(self.full_video_path)

        # Check if camera opened successfully
        if (capture.isOpened()== False):
            print("Error opening video stream or file")

        # Read each frame until we capture the first screenshot
        while(capture.isOpened()): 

            # Check to see if we have found a screenshot yet 
            if scrshot_fnd is True:
                break

            # Capture each frame of the video  
            ret, frame = capture.read()
            # Check to make sure the video hasn't ended yet
            if ret == True:
                # Loaded in the Color Image
                img_RGB = frame
                # Loaded in the base template
                base_template_path = os.path.join(project_root, "assets/computer_vision/baseTemplateForRoundStart.png")
                base_template_round_start = cv2.imread(base_template_path, 0)
                
                img_gray = cv2.cvtColor(img_RGB, cv2.COLOR_BGR2GRAY)
                
                # Focused on the round timer in the gray image
                img_round_timer_gray_ROI = img_gray[0:75, 920:1000]

                # SQDIFF_NORMED is the Sum of Squared Differences, which means similar images have a smaller difference
                # - The values are btw 0 and 1, and the closer the min. value of result is to 0, the more closely the base template and image patch match
                # Matching for the 1:39 Round Timer in the video's screenshot
                result = cv2.matchTemplate(img_round_timer_gray_ROI, base_template_round_start, cv2.TM_SQDIFF_NORMED)
            
                max_diff = 0.1
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                if min_val < max_diff:
                    scrshot_fnd = True
                    # Copies the round number to the bottom left of the Mini-Map screenshot
                    round_number = img_RGB[0:75, 920:1000]
                    minimap = img_RGB[25:480, 0:480]
                    minimap[380:455, 0:80] = round_number
                    self.scrshot_path = game_files_path + f"/{self.video_name}_Rnd_1.png"
                    cv2.imwrite(self.scrshot_path, minimap)
                    frame = img_RGB
            
            else:
                break

        capture.release()
        cv2.destroyAllWindows()


