import pygame
import os
import json
import datetime
import src.utilities.constants as const
from src.utilities.textbox import pygametextboxinput as pyTxtBx

from src.game_states.base_state import BaseState
from src.utilities.icon_sprites import Icon
from src.utilities.button import Button
from src.utilities.generate_PDF import create_and_download_PDF

""" Gameplay Game State """

class Gameplay(BaseState):
    def __init__(self, game, title, map, file_path_to_save_to, date_created = "", saved_data = None):
        # Initializing the Base Class
        super().__init__(game)
        
        self.file_title = title
        self.map = map
        self.file_path_to_save_to = file_path_to_save_to
        self.date_created = date_created
        self.saved_data = saved_data

        self.screenshot = False
        self.possible_screenshot_path=""
        self.events = []
        self.iconSelected = None
        self.last_clicked_agent_icon = None
        self.most_recent_clicked_agent_icon = None
        self.recently_selected_agent_names = []
        self.prev_team = "DEF"
        self.new_team = "DEF"
        self.team_dict = {"ATK": const.PALE_VIOLET_RED, "DEF": const.PALE_GREEN_3}

        # Create Textbox w/ Input
        self.text_box = pyTxtBx.TextInputBox(837, 574, font_family='arial', font_size=20, max_width= 342 - 12 + 270, max_height= 100 + 95, text_color="black", cursor_color="black")
        self.editingTextBox = False

        self.prepare_surfs_and_rects()
        self.load_sprite_groups()
        # Load in the Saved Data, if it exists
        if (self.saved_data):
            self.load_saved_game()

    def handle_events(self, events):
        self.events = events
        for event in events:

            if event.type == pygame.QUIT:
                self.save_to_file()
                self.game.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check if the User selected the Atk team button
                    if (self.atk_button.is_button_clicked(event.pos)):
                        self.new_team = self.atk_button.text
                        self.atk_button.const_selected_button(True)
                        self.def_button.const_selected_button(False)

                    # Check if the User selected the Def team button
                    elif (self.def_button.is_button_clicked(event.pos)):
                        self.new_team = self.def_button.text
                        self.def_button.const_selected_button(True)
                        self.atk_button.const_selected_button(False)

                    # Check if the User selected the Main Menu button
                    elif (self.main_menu_button.is_button_clicked(event.pos)):
                        self.save_to_file()
                        self.game.return_to_main_menu()

                    # Check if the User selected the New File button
                    elif (self.new_file_button.is_button_clicked(event.pos)):
                        self.save_to_file()
                        # Create and Enter a New File Game State
                        self.game.enter_new_state("New Doc")

                    # Check if the User selected the Load File button
                    elif (self.load_file_button.is_button_clicked(event.pos)):
                        self.save_to_file()
                        # Create and Enter a Directories Game State
                        self.game.enter_new_state("Directories", creating_new_file=False)

                    # Check if the User selected the Save icon
                    elif (self.save_button.is_button_clicked(event.pos)):
                        self.save_to_file()

                    # Check if the User selected the Download icon
                    elif (self.download_button.is_button_clicked(event.pos)):
                        self.save_to_file()
                        self.download_pdf()

                    # Check if the User selected on the Agent Icons in the Table
                    for agent in self.agentGroupTable:
                        if agent.mouseSelect(event.pos):
                            self.most_recent_clicked_agent_icon = agent
                            # Create a copy of the Agent Icon
                            self.iconSelected = Icon(agent.name, agent.type, agent.start_loc, agent.team, agent.colorBackground)
                            self.agentsOnMap.add(self.iconSelected)

                    # Check if the User selected on the Agent Icons on the Map
                    for activeAgent in self.agentsOnMap:
                        if activeAgent.mouseSelect(event.pos):
                            self.iconSelected = activeAgent

                    # Check if the User selected on the Utility Icons on the Toolbar
                    for utility in self.utilityGroupRows:
                        if utility.mouseSelect(event.pos):
                            # Creates a copy of the Utility Icon
                            self.iconSelected = Icon(utility.name, utility.type, utility.start_loc, team=utility.team, colorBackground= utility.colorBackground, colorSubject= utility.colorSubject)
                            # The icon in utilityGroupRows can be either an Agent or a Utility; it needs to be placed in its correct Sprite Group
                            if (self.iconSelected.type == "utility"):
                                self.utilityOnMap.add(self.iconSelected)
                            else:
                                self.agentsOnMap.add(self.iconSelected)

                    # Check if the User selected on the Utility Icons on the Map
                    for activeUtility in self.utilityOnMap:
                        if activeUtility.mouseSelect(event.pos):
                            self.iconSelected = activeUtility

                    # Check if the user clicked on the Notes textbox
                    self.editingTextBox = self.text_box.editTextBox(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                if self.iconSelected != None:
                    # Update the location of the Selected Icon as the mouse moves
                    self.iconSelected.updatePosition(event.rel)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if (event.button == 1 and self.iconSelected != None):
                    # Check if the Selected Icon was placed in the Trash Can or back into the Toolbar
                    self.iconSelected.possibleDeletion(self.trashcanRect)
                    self.iconSelected.drawSelection(False)
                    self.iconSelected = None

    def update(self):
        # Check if the mouse is hovering over any buttons
        self.atk_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.def_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.main_menu_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.new_file_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.load_file_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.save_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.download_button.is_mouse_over_button(pygame.mouse.get_pos())

        # Update the TextBox if self.editingTextBox is True
        self.text_box.update(self.events, self.editingTextBox)
        
        # Check if the User changed Teams
        if (self.prev_team != self.new_team):
            # print(f"Changing Team from {self.prev_team} to self.new_team")
            for agent in self.agentGroupTable:
                agent.changeTeams(self.new_team, self.team_dict[self.new_team], None)
            for utility in self.utilityGroupRows:
                utility.changeTeams(self.new_team, self.team_dict[self.new_team], None)
            self.prev_team = self.new_team
            if (self.last_clicked_agent_icon != None):
                self.last_clicked_agent_icon.drawSelection(True)

        # Draw a border around the icon the mouse is selecting
        if self.iconSelected != None:
            self.iconSelected.drawSelection(True)
        
        if self.most_recent_clicked_agent_icon != self.last_clicked_agent_icon:
            # Remove the border around the previously selected Agent Icon and draw a border around the currently selected agent icon
            if self.last_clicked_agent_icon != None:
                self.last_clicked_agent_icon.drawSelection(False)
            self.last_clicked_agent_icon = self.most_recent_clicked_agent_icon
            self.last_clicked_agent_icon.drawSelection(True)

            # Add the 5 most recently clicked Agent Icons into the Utility Rows without duplicates
            if (self.last_clicked_agent_icon.name not in self.recently_selected_agent_names):
                # Check if the length of the list is larger than 5, if so, pop from the end
                if (len(self.recently_selected_agent_names) >= 5):
                    self.recently_selected_agent_names.pop()

                self.recently_selected_agent_names.insert(0, self.last_clicked_agent_icon.name)
                self.utilityGroupRows.empty()
                for agent_index, agent_name in enumerate(self.recently_selected_agent_names, start=1):
                    agent_loc = self.starting_location(f"Utility Row {agent_index}", 0)
                    utility_agent_icon = Icon(agent_name, "agent", agent_loc, self.new_team, colorBackground= self.team_dict[self.new_team])
                    self.utilityGroupRows.add(utility_agent_icon)
                    list_agent_utility = const.AGENT_TO_UTILITY_DICT[agent_name]
                    for utility_index in range(len(list_agent_utility)):
                        utility_loc = self.starting_location(f"Utility Row {agent_index}", utility_index+1)
                        self.utilityGroupRows.add(Icon(list_agent_utility[utility_index], "utility", utility_loc, self.new_team, colorBackground= self.team_dict[self.new_team]))

    def prepare_surfs_and_rects(self):
        # Create Buttons
        self.create_buttons()

        file_path = os.path.abspath(__file__)
        game_states_direc_path = os.path.dirname(file_path)
        src_directory_path = os.path.dirname(game_states_direc_path)
        project_root = os.path.dirname(src_directory_path)
        trashcan_img_path = os.path.join(project_root, "assets/misceallanous/trashcan.png")
        map_template_img_path = os.path.join(project_root, f"assets/maps/{self.map}.png")
        save_img_path = os.path.join(project_root, "assets/misceallanous/save_icon.png")
        download_img_path = os.path.join(project_root, "assets/misceallanous/download_icon.png")

        # Create a background color Surface for the Map
        self.backgroundColorForMapSurf = pygame.Surface((const.MAP_WIDTH, const.MAP_HEIGHT))
        self.backgroundColorForMapSurf.fill("slategray4")

        # Create a background color Surface for the Toolbar
        self.backgroundColorForToolbarSurf = pygame.Surface((const.TOOLBAR_WIDTH, const.TOOLBAR_HEIGHT))
        self.backgroundColorForToolbarSurf.fill("darkgray")
        pygame.draw.line(self.backgroundColorForToolbarSurf, "seashell2", (0, 0), (0, const.MAP_HEIGHT), width=2)

        # Load in the trashcan image
        self.trashcanSurf = pygame.image.load(trashcan_img_path).convert_alpha()
        self.trashcanRect = self.trashcanSurf.get_rect(center = (const.MAP_WIDTH - 50, const.MAP_HEIGHT - 50))

        # Load in the Map image and scale it down
        self.mapTemplateSurf = pygame.image.load(map_template_img_path).convert_alpha()
        self.mapTemplateSurf = pygame.transform.smoothscale(self.mapTemplateSurf, (const.MAP_WIDTH, const.MAP_HEIGHT))

        # Load in the Save and Download Icons
        self.save_surf = pygame.image.load(save_img_path).convert_alpha()
        self.save_surf = pygame.transform.smoothscale(self.save_surf, (48,48))
        self.download_surf = pygame.image.load(download_img_path).convert_alpha()
        self.download_surf = pygame.transform.smoothscale(self.download_surf, (45,45))

    def draw_on_screen(self, screen):
        screen.blit(self.backgroundColorForMapSurf, (0,0))
        screen.blit(self.backgroundColorForToolbarSurf, (const.MAP_WIDTH, 0))
        screen.blit(self.mapTemplateSurf, (0,0))
        screen.blit(self.trashcanSurf, self.trashcanRect)
        pygame.draw.rect(screen, "seashell2", [0, 0, const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT], 2, 10, border_top_left_radius= 0, border_top_right_radius=0)


        # Draw Title and Map Header
        pygame.draw.rect(screen, (255,222,173),[23, 18, 320, 76])
        pygame.draw.rect(screen, (139,69,19), [23, 18, 320, 76], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        self.draw_text(screen, f"File Name: {self.file_title}", pygame.font.SysFont("arial", 25), (30,38), "black", "midleft")
        self.draw_text(screen, f"Map: {self.map}", pygame.font.SysFont("arial", 25), (30, 72), "black", "midleft")

        # Draw the Agents Header
        pygame.draw.rect(screen, (255,222,173),[810, 10, 88, 32])
        pygame.draw.rect(screen, (139,69,19), [810, 10, 88, 32], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        self.draw_text(screen, "Agents", pygame.font.SysFont("arial", 23), (817, 25), "black", "midleft" )

        # Draw the Agent Utility Header
        pygame.draw.rect(screen, (255,222,173),[810, 163, 138, 32])
        pygame.draw.rect(screen, (139,69,19), [810, 163, 138, 32], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        self.draw_text(screen, "Agent Utility", pygame.font.SysFont("arial", 23), (const.MAP_WIDTH + 17, const.AGENT_SECOND_ROW + 60), "black", "midleft")

        # Draw the Notes Header
        pygame.draw.rect(screen, (255,222,173),[810, 519, 100, 42])
        pygame.draw.rect(screen, (139,69,19), [810, 519, 100, 42], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        self.draw_text(screen, "Notes", pygame.font.SysFont("arial", 30), (820, 539), "black", "midleft" )

        # Draw the notes in the textbox
        pygame.draw.rect(screen, "lightblue", [830, 569, 612, 200])
        pygame.draw.rect(screen, "blue", [830, 569, 612, 200], 1)
        self.text_box.render(screen)

        # Draw the Agent Table and Utility Toolbar
        self.agentGroupTable.draw(screen)
        self.utilityGroupRows.draw(screen)

        # Draw the Agent Icons and the Utility Icons on the Map
        self.agentsOnMap.draw(screen)
        self.utilityOnMap.draw(screen)

        # Draw the Buttons in
        self.atk_button.draw_on_screen(screen)
        self.def_button.draw_on_screen(screen)
        self.main_menu_button.draw_on_screen(screen)
        self.new_file_button.draw_on_screen(screen)
        self.load_file_button.draw_on_screen(screen)
        # Draw the Save and Download Buttons and Surfs
        self.save_button.draw_on_screen(screen)
        screen.blit(self.save_surf, self.save_surf.get_rect(center = self.save_button.get_button_rect().center))
        self.download_button.draw_on_screen(screen)
        screen.blit(self.download_surf, self.download_surf.get_rect(center = self.download_button.get_button_rect().center))

        self.screen_copy = screen

        # Draw in the corresponding screenshot from the video, if there exists one
        if (self.screenshot):
            pygame.draw.rect(self.screenshotSurf, (70,130,180), [0, 0, 300, 300], 2)
            screen.blit(self.screenshotSurf, self.screenshotRect)


    """ Helper Fxns """

    def load_sprite_groups(self):
        # Create the Agent Sprite Group for the Agent Table and add the Agent Icons to it
        self.agentGroupTable = pygame.sprite.Group()
        for index in range(len(const.AGENT_LIST)):
            loc = self.starting_location("Agent Table", index)
            self.agentGroupTable.add(Icon(const.AGENT_LIST[index], "agent", loc, self.prev_team, colorBackground=self.team_dict[self.prev_team]))
        
        # Create the Utility Sprite Group for the Toolbar
        self.utilityGroupRows = pygame.sprite.Group()

        # Create the Sprite Groups for the Agent Icons and Utility Icons on the Map 
        self.agentsOnMap = pygame.sprite.Group()
        self.utilityOnMap = pygame.sprite.Group()

    def starting_location(self, label, index):
        centerX = 0
        centerY = 0
        displacement = 0
        y_gap = 60

        if (label == "Agent Table"):
            if (index < (len(const.AGENT_LIST)//2)):
                centerX = 32 + const.MAP_WIDTH + ((const.AGENT_HEIGHT_WIDTH + 2) * index)
                centerY = const.AGENT_FIRST_ROW
            else:
                centerX = 32 + const.MAP_WIDTH + ((const.AGENT_HEIGHT_WIDTH + 2) * (index - len(const.AGENT_LIST)//2))
                centerY = const.AGENT_SECOND_ROW

        elif (label == "Utility Row 1"):
            if (index != 0):
                displacement = 17
            centerX = 32 + const.MAP_WIDTH + displacement + ((const.UTILITY_HEIGHT_WIDTH + 7) * (index))
            centerY = const.AGENT_SECOND_ROW + 113

        elif (label == "Utility Row 2"):
            if (index != 0):
                displacement = 17
            centerX = 32 + const.MAP_WIDTH + displacement + ((const.UTILITY_HEIGHT_WIDTH + 7) * (index))
            centerY = y_gap + const.AGENT_SECOND_ROW + 113

        elif (label == "Utility Row 3"):
            if (index != 0):
                displacement = 17
            centerX = 32 + const.MAP_WIDTH + displacement + ((const.UTILITY_HEIGHT_WIDTH + 7) * (index))
            centerY = 2*y_gap + const.AGENT_SECOND_ROW + 113

        elif (label == "Utility Row 4"):
            if (index != 0):
                displacement = 17
            centerX = 32 + const.MAP_WIDTH + displacement + ((const.UTILITY_HEIGHT_WIDTH + 7) * (index))
            centerY = 3*y_gap + const.AGENT_SECOND_ROW + 113

        elif (label == "Utility Row 5"):
            if (index != 0):
                displacement = 17
            centerX = 32 + const.MAP_WIDTH + displacement + ((const.UTILITY_HEIGHT_WIDTH + 7) * (index))
            centerY = 4*y_gap + const.AGENT_SECOND_ROW + 113

        return centerX, centerY
    
    def create_buttons(self):
        # Create the Atk and Def Buttons
        self.atk_button = Button("ATK", pygame.font.SysFont("arial", 18), (947, 25), (63, 28), "red")
        self.def_button = Button("DEF", pygame.font.SysFont("arial", 18), (1008, 25), (63, 28), (0,128,0))
        self.def_button.const_selected_button(True)

        # Create the Main Menu, New File, and Load File Buttons
        self.main_menu_button = Button("Main Menu", pygame.font.SysFont("arial", 18), (1397, 31), (115, 35))
        self.new_file_button = Button("New Doc", pygame.font.SysFont("arial", 18), (1397, 73), (115, 35))
        self.load_file_button = Button("Load Doc", pygame.font.SysFont("arial", 18), (1397, 115), (115, 35))

        # Create the Save Button and the Download Button
        self.save_button = Button("Save", pygame.font.SysFont("arial", 18), (1369, 169), (55,55), hidden=True)
        self.download_button = Button("Download", pygame.font.SysFont("arial", 18), (1419, 169), (55,55), hidden=True)

    def save_to_file(self):
        # Split the agentsOnMap into 2 distinct Dicts. (Atk Agents and Def Agents)
        self.atk_agents = {}
        self.def_agents = {}
        # Split the utilityOnMap into 2 distinct Dicts. (Atk Utility and Def Utility)
        self.atk_utility = {}
        self.def_utility = {}
        # Store the Notes
        self.notes = ""

        # Cycle through all the Agents on the map
        for agent in self.agentsOnMap:
            # If an Atk Agent, then add to the atk_agents Dict. with key = agent.name and value = [agent.get_current_loc()]
            if (agent.team == "ATK"):
                # If this is a new Agent in the Dict., then create a value for it (put the location into a list)
                if (agent.name not in self.atk_agents):
                    self.atk_agents[agent.name] = [agent.get_current_loc()]
                # Otherwise, append the location to the current key-value pair
                else:
                    self.atk_agents[agent.name].append(agent.get_current_loc())

            if (agent.team == "DEF"):
                if (agent.name not in self.def_agents):
                    self.def_agents[agent.name] = [agent.get_current_loc()]
                else:
                    self.def_agents[agent.name].append(agent.get_current_loc())

        # Cycle through all the Utility on the map
        for utility in self.utilityOnMap:
            if (utility.team == "ATK"):
                if (utility.name not in self.atk_utility):
                    self.atk_utility[utility.name] = [utility.get_current_loc()]
                else:
                    self.atk_utility[utility.name].append(utility.get_current_loc())
            if (utility.team == "DEF"):
                if (utility.name not in self.def_utility):
                    self.def_utility[utility.name] = [utility.get_current_loc()]
                else:
                    self.def_utility[utility.name].append(utility.get_current_loc())
            
        # Save the Notes
        self.notes = self.text_box.get_text()

        # Update the Most Recently Viewed Date
        current_date = datetime.datetime.now()
        formatted_date = current_date.strftime("%m/%d/%y")

        # Create a Dict[string_label_for_sub_dicts] --> sub_Dict[string_agent/utility_name] --> [[string_agent/utility_loc], [string_agent/utility_loc], ...]
        # For Map, File Path, Date Created, Viewed Date, and Notes, it's just Dict[key] = value
        file_info = {}
        file_info["map"] = self.map
        file_info["file_path"] = self.file_path_to_save_to
        file_info["atk_agents"] = self.atk_agents
        file_info["def_agents"] = self.def_agents
        file_info["atk_utility"] = self.atk_utility
        file_info["def_utility"] = self.def_utility
        file_info["date_created"] = self.date_created
        file_info["date_viewed"] = formatted_date
        file_info["notes"] = self.notes

        with open(f"{self.file_path_to_save_to + self.file_title}.json", "w") as f:
            json.dump(file_info, f, sort_keys= True, indent= 4)
        # print(f"Saving File: {self.file_path_to_save_to + self.file_title}.json")


    def load_saved_game(self):
        # Load in the Atk Agents
        for atk_agent_name in self.saved_data["atk_agents"]:
            for index in range(len(self.saved_data["atk_agents"][atk_agent_name])):
                atk_agent_icon = Icon(atk_agent_name, "agent", self.saved_data["atk_agents"][atk_agent_name][index], "ATK", const.PALE_VIOLET_RED)
                self.agentsOnMap.add(atk_agent_icon)

        # Load in the Def Agents
        for def_agent_name in self.saved_data["def_agents"]:
            for index in range(len(self.saved_data["def_agents"][def_agent_name])):
                def_agent_icon = Icon(def_agent_name, "agent", self.saved_data["def_agents"][def_agent_name][index], "DEF", const.PALE_GREEN_3)
                self.agentsOnMap.add(def_agent_icon)

        # Load in the Atk Utility
        for atk_utility_name in self.saved_data["atk_utility"]:
            for index in range(len(self.saved_data["atk_utility"][atk_utility_name])):
                atk_utility_icon = Icon(atk_utility_name, "utility", self.saved_data["atk_utility"][atk_utility_name][index], "ATK", const.PALE_VIOLET_RED)
                self.utilityOnMap.add(atk_utility_icon)

        # Load in the Def Utility
        for def_utility_name in self.saved_data["def_utility"]:
            for index in range(len(self.saved_data["def_utility"][def_utility_name])):
                def_utility_icon = Icon(def_utility_name, "utility", self.saved_data["def_utility"][def_utility_name][index], "DEF", const.PALE_GREEN_3)
                self.utilityOnMap.add(def_utility_icon)

        # Load in Date Created and Most Recent Date Viewed:
        self.date_created = self.saved_data["date_created"]
        self.date_viewed = self.saved_data["date_viewed"]

        # Load in the Notes
        notes = self.saved_data["notes"]
        self.text_box.set_text(notes)

        # Load in the Screenshot image, if it exists
        self.possible_screenshot_path = f"{self.file_path_to_save_to + self.file_title}.png"
        if (os.path.exists(self.possible_screenshot_path)):
            self.screenshot = True
            self.screenshotSurf = pygame.image.load(self.possible_screenshot_path)
            self.screenshotSurf = pygame.transform.smoothscale(self.screenshotSurf, (300, 300) )
            self.screenshotRect = self.screenshotSurf.get_rect( center = (1270, 360))

    def download_pdf(self):
        # Take a screenshot of the image
        edited_map_screenshot = pygame.Surface((const.MAP_WIDTH+2, const.MAP_HEIGHT))
        edited_map_screenshot.blit(self.screen_copy, (0,0))
        pygame.draw.rect(edited_map_screenshot, "black", [0, 0, const.MAP_WIDTH+2, const.MAP_HEIGHT], 3, 10)
        edited_map_screenshot_path = f"{self.file_path_to_save_to}{self.file_title}.jpg"
        pygame.image.save(edited_map_screenshot, edited_map_screenshot_path)

        # Create the Agents list and Utility list and order them with Atk ones first and then Def ones
        list_of_agents_on_map = []
        list_of_utility_on_map = []
        for agent in self.agentsOnMap:
            if (agent.team == "ATK"):
                list_of_agents_on_map.insert(0,[agent.team, agent.name])
            else:
                list_of_agents_on_map.append([agent.team, agent.name])
        for utility in self.utilityOnMap:
            if (utility.team == "ATK"):
                list_of_utility_on_map.insert(0,[utility.team, utility.name])
            else:
                list_of_utility_on_map.append([utility.team, utility.name])
        list_of_agents_on_map.insert(0,["Team:", "Agent:"])
        list_of_utility_on_map.insert(0,["Team:", "Utility:"])

        # Gather notes
        notes = self.text_box.get_text()

        # Check if there is a screenshot attached to this File
        if (self.screenshot == False):
            self.possible_screenshot_path = None

        # Download PDF
        create_and_download_PDF(self.file_title, self.map, edited_map_screenshot_path, list_of_agents_on_map, list_of_utility_on_map, notes, self.possible_screenshot_path)

