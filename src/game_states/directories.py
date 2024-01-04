import pygame
import os
import json
import datetime
import src.utilities.constants as const
from src.utilities.button import Button
from src.utilities.textbox import pygametextboxinput as pyTxtBx
from src.game_states.base_state import BaseState
from src.computer_vision.capture_screenshots import capture_start_of_rounds
from src.computer_vision.template_matching import template_matching_in_minimap


""" Directories Game State """

class Directories(BaseState):
    def __init__(self, game, path="game_files/", file_name= "", map_selected= "", creating_new_file= True, analyze_VOD = False, video_name = "", full_video_path = "", agents_of_interest = []):

        # Initializing the Base Class
        super().__init__(game)

        file_path = os.path.abspath(__file__)
        game_states_direc_path = os.path.dirname(file_path)
        src_directory_path = os.path.dirname(game_states_direc_path)
        project_root = os.path.dirname(src_directory_path)
        self.current_path = os.path.join(project_root, path)
        # print(f"Current Folder Path: {path} - - - File Name: {file_name} - - - Map: {map_selected}")
        self.file_name = file_name
        self.map_selected = map_selected
        self.creating_new_file = creating_new_file
        self.analyze_VOD = analyze_VOD
        self.video_name = video_name
        self.full_video_path = full_video_path
        self.agents_of_interest = agents_of_interest

        self.directions = "Step 3) Choose Where to Save the New File" 
        if (not self.creating_new_file):
            self.directions = "Step 1) Choose File to Load"
        if (analyze_VOD):
            self.directions= "Step 4) Choose Where to Save Files"

        # Initialize the variables related to showing the selected file's info
        self.selected_current_path = self.current_path
        self.selected_file_name = ""
        self.selected_file_map = ""
        self.selected_file_date_created = ""
        self.selected_file_date_viewed = ""

        self.process_click = True
        self.textbox = pyTxtBx.TextInputBox(1267 + 5, 689 - 100 - 40 + 25, font_family="arial", font_size=20, max_width=185, max_height=30, text_color="black", cursor_color="black")
        self.textbox_is_activated = False
        self.events = []

        # Prepare the Surfs and Rects
        self.prepare_surfs_and_rects()

        # Load in and show the first file's info in the current directory
        if (self.files):
            self.load_file_details(self.files[0])

    def handle_events(self, events):
        self.events = events
        for event in events:
            if event.type == pygame.QUIT:
                self.game.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.process_click = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check to see if the User selected any of the Folders
                    for folder_button in self.folder_buttons:
                        if (folder_button.is_button_clicked(event.pos) and self.process_click):
                            self.current_path = self.current_path + folder_button.text + "/"
                            # print(f"Clicked \"{folder_button.text}\" folder")
                            # print(f"Current Path:", self.current_path)
                            self.create_folder_file_buttons()
                            self.process_click = False

                    # Check to see if the User selected any of the Files
                    for file_button in self.file_buttons:
                        # Only open and load files if we are not creating a New Doc
                        if ((not self.creating_new_file) and file_button.is_button_clicked(event.pos) and self.process_click):
                            # print("Opening File:", file_button.text)
                            self.load_saved_file(file_button.text)
                            self.process_click = False

                    # Check to see if the User selected the Add Folder button
                    if self.add_folder_button.is_button_clicked(event.pos):
                        self.add_folder(self.textbox.get_text())
                    
                    # Check to see if the User selected the Prev. Direc. button
                    elif (self.prev_folder_button.is_button_clicked(event.pos)) and (os.path.basename(self.current_path[:-1]) != "game_files"):
                        new_path = self.current_path.split("/")
                        new_path = new_path[:-2]
                        self.current_path = "/".join(new_path) + "/"
                        self.create_folder_file_buttons()

                    # Check to see if the User selected the Cancel button
                    elif (self.cancel_button.is_button_clicked(event.pos)):
                        # The Cancel button should only go back 2 Game States if the User is creating a New Doc 
                        # and not analyzing a video or loading a file
                        if (self.creating_new_file and not self.analyze_VOD):
                            self.game.return_to_prev_state()
                            self.game.return_to_prev_state()
                        else:
                            self.game.return_to_prev_state()
                        
                    # Check to see if the User selected the Delete File button
                    elif (self.delete_button.is_button_clicked(event.pos)):
                        # Ensures there is a file to delete
                        if (self.selected_file_name != ""):
                            self.delete_selected_file()
                            # Reload the Folders and Files
                            self.create_folder_file_buttons()
                        # else:
                        #     # print("Nothing to Delete!")

                    # Only show the Save File button if the User is creating a New File or Analyzing a Video
                    elif (self.creating_new_file):
                        # Check to see if the User selected the Save File button
                        if self.save_file_button.is_button_clicked(event.pos):
                            current_date = datetime.datetime.now()
                            formatted_date = current_date.strftime("%m/%d/%y")
                            if (self.analyze_VOD):
                                # print("Capturing Screenshots!")
                                self.analyze_video()
                                pygame.event.clear()
                                self.switch_from_saving_to_loading()
                                self.create_folder_file_buttons()
                            else:
                                self.game.enter_new_state("Gameplay", title=self.file_name, map=self.map_selected, file_path_to_save_to= self.current_path, date_created=formatted_date)

                        # Only show the change file info button if we are creating a New File and not Analyzing a Video
                        if (not self.analyze_VOD):
                            # Check to see if the User selected the Change File Info button
                            if self.change_file_info_button.is_button_clicked(event.pos):
                                # Storing the current State in the State Manager
                                self.game.store_state(self)
                                # Return to Prev. Game State
                                self.game.return_to_prev_state()

                    self.textbox_is_activated = self.textbox.editTextBox(event.pos)
                
                elif event.button == 3:
                    # Check to see if the User Right-Clicked on any of the File buttons
                    for file_button in self.file_buttons:
                        if (file_button.is_button_clicked(event.pos)):
                            # print(f"Reading File {file_button.text}'s description")
                            self.load_file_details(file_button.text)
 
    def update(self):
        # Update textbox
        self.textbox.update(self.events, self.textbox_is_activated)

        # Check to see if mouse is hovering over any buttons
        for folder_button in self.folder_buttons:
            folder_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.add_folder_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.change_file_info_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.save_file_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.prev_folder_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.cancel_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.delete_button.is_mouse_over_button(pygame.mouse.get_pos())

        # If we are creating a New File, there is no need to change the color over the files
        if (not self.creating_new_file):
            for file_button in self.file_buttons:
                file_button.is_mouse_over_button(pygame.mouse.get_pos())

    def prepare_surfs_and_rects(self):
        # Prepare the Sub-Folder Buttons
        self.create_folder_file_buttons()

        # Create the Other Buttons
        self.prev_folder_button = Button("Prev. Direc.", const.TEXT_FONT_SUBHEADER, (970, 730), (165, 50))
        self.save_file_button = Button("Save", const.TEXT_FONT_SUBHEADER, (1228, 730), (130, 50))
        self.cancel_button = Button("Cancel", const.TEXT_FONT_SUBHEADER, (1391, 730), (130, 50))
        self.delete_button = Button("Delete File", pygame.font.SysFont("arial", 18), (1390, 481), (100, 35))
        self.add_folder_button = Button("Add Folder", pygame.font.SysFont("arial", 20), (1285, 650), (120, 50))
        self.change_file_info_button = Button("Edit Name/Map", pygame.font.SysFont("arial", 20), (1285, 135), (160, 50))

        # Create and fill in the Background Surface with a TAN color
        self.backgroundColorForScreenSurf = pygame.Surface((const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT))
        self.backgroundColorForScreenSurf.fill((const.TAN))

        # Create the Surfs for the Folder and File icons
        file_path = os.path.abspath(__file__)
        game_states_direc_path = os.path.dirname(file_path)
        src_directory_path = os.path.dirname(game_states_direc_path)
        project_root = os.path.dirname(src_directory_path)
        folder_img_path = os.path.join(project_root, "assets/misceallanous/folder_icon.png")
        file_img_path = os.path.join(project_root, "assets/misceallanous/file_icon.png")
        self.folder_surf = pygame.image.load(folder_img_path).convert_alpha()
        self.folder_surf = pygame.transform.smoothscale(self.folder_surf, (100, 100))
        self.original_file_surf = pygame.image.load(file_img_path).convert_alpha()
        self.file_surf = pygame.transform.smoothscale(self.original_file_surf, (100, 100))
        self.large_file_surf = pygame.transform.smoothscale(self.original_file_surf, (125, 125))

    def draw_on_screen(self, screen):
        # Blit the Background Color to the Screen
        screen.blit(self.backgroundColorForScreenSurf, (0,0))
        # Draw in the White border and the vertical line to separate the desciption of a file and the horizontal line to separate the title
        pygame.draw.rect(screen, "seashell2", [0, 0, const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT], 5, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0) #mistyrose4
        pygame.draw.line(screen, "seashell2", (1130, 0), (1130, const.DISPLAY_HEIGHT), width=6)
        pygame.draw.line(screen, "seashell2", (0, 100), (1130, 100), width=6)

        # Draw the Rectangle and Border behind the Title
        if (self.creating_new_file and not self.analyze_VOD):
            pygame.draw.rect(screen, (255,222,173),[1138, 17, 320, 88])
            pygame.draw.rect(screen, (139,69,19), [1138, 17, 320, 88], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)

        # Draw the Header Directions
        self.draw_text(screen, self.directions, const.TEXT_FONT_SUBHEADER, (550, 50), "black", "center" )

        # Draw the Add Folder
        self.draw_text(screen, "New Folder:", pygame.font.SysFont("arial", 22), (1143, 585), "black", "midleft")
        
        # Draw the Sub-Folder buttons and Blit the Folder Icons
        for folder_button in self.folder_buttons:
            folder_button.draw_on_screen(screen)
            screen.blit(self.folder_surf, self.folder_surf.get_rect(center = folder_button.get_button_rect().center))

        # Draw the File Buttons 
        for file_button in self.file_buttons:
            file_button.draw_on_screen(screen)
            screen.blit(self.file_surf, self.file_surf.get_rect(center = file_button.get_button_rect().center))

        # Draw Selected File Details
        pygame.draw.rect(screen, (128,128,128), [1150, 200, 300, 310])
        pygame.draw.rect(screen, (25,25,112), [1150, 200, 300, 310], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        screen.blit(self.large_file_surf, self.large_file_surf.get_rect(center = (1300, 270)))
        self.draw_text(screen, f"File Name: {self.selected_file_name[:-5]}", pygame.font.SysFont("arial", 20), (1300, 350), "black", "center")
        self.draw_text(screen, f"Map: {self.selected_file_map}", pygame.font.SysFont("arial", 20), (1300, 380), "black", "center")
        self.draw_text(screen, f"Date Created: {self.selected_file_date_created}", pygame.font.SysFont("arial", 20), (1300, 410), "black", "center")
        self.draw_text(screen, f"Last Viewed On: {self.selected_file_date_viewed}", pygame.font.SysFont("arial", 20), (1300, 440), "black", "center")
        self.draw_text(screen, "(Right Click for File's Info)", pygame.font.SysFont("arial", 18), (1300, 520), "black", "center")

        # Draw the Other Buttons
        self.add_folder_button.draw_on_screen(screen)
        self.cancel_button.draw_on_screen(screen)
        self.delete_button.draw_on_screen(screen)        
        if (os.path.basename(self.current_path[:-1]) != "game_files"):
            self.prev_folder_button.draw_on_screen(screen)
        
        # Only draw the File Name and Map Selected if the User is trying to create a New File and not Analyze a Video
        if (self.creating_new_file):
            self.save_file_button.draw_on_screen(screen)
            if (not self.analyze_VOD):
                self.draw_text(screen, "File Name: " + self.file_name, pygame.font.SysFont("arial", 27), (1150, 42), "black", "midleft" )
                self.draw_text(screen, "Map: " + self.map_selected, pygame.font.SysFont("arial", 27), (1150, 82), "black", "midleft" )
                self.change_file_info_button.draw_on_screen(screen)

        # Draw the Textbox
        pygame.draw.rect(screen, "white", [1263 + 5, 685 - 100 - 40 + 25, 190, 35])
        pygame.draw.rect(screen, "black", [1263 + 5, 685 - 100 - 40 + 25, 190, 35], 1)
        self.textbox.render(screen)

        # Draw the Folder and File Names in
        folder_file_font = pygame.font.SysFont("arial", 18)
        for folder_txt in self.folder_names_and_loc:
            self.draw_text(screen, folder_txt[0], folder_file_font, folder_txt[1], "black")
        for file_txt in self.file_names_and_loc:
            self.draw_text(screen, file_txt[0][:-5], folder_file_font, file_txt[1], "black")

    """ Helper functions """

    def create_folder_file_buttons(self):
        # Check if the directory path exists
        if not os.path.exists(self.current_path):
            # If not, create the directory
            os.makedirs(self.current_path)

        # Create a list of all the folders/directories in the curret directory path
        self.folders = [folder for folder in sorted(os.listdir(self.current_path)) if os.path.isdir((os.path.join(self.current_path, folder)))]
        # print("Existing sub-folders:", self.folders)
        
        # Loads in the Sub-Folders/Sub-Directories into buttons
        self.folder_buttons = []
        self.folder_names_and_loc = []
        self.icon_row_y_coords = [175, 350, 525, 700, 875]
        self.text_row_y_coords = [243, 418, 593, 768, 943]
        for index, folder_name in enumerate(self.folders):
            row_index = index // 8 
            column_index = index % 8
            self.folder_buttons.append(Button(folder_name, const.TEXT_FONT_MAP_BUTTON, (80 + 138*column_index, self.icon_row_y_coords[row_index]), (115, 115), hidden= True))
            self.folder_names_and_loc.append([folder_name, (80 + 138*column_index, self.text_row_y_coords[row_index])])

        # Create a list of all the files in the curret directory path
        self.files = [file for file in sorted(os.listdir(self.current_path)) if (os.path.isfile((os.path.join(self.current_path, file))) and file.endswith(".json"))]
        # print("Existing files:", self.files)

        # Loads in the Files into Buttons
        self.file_buttons = []
        self.file_names_and_loc = []
        buffer = len(self.folder_buttons)
        for index, file_name in enumerate(self.files):
            row_index = (index + buffer) // 8
            column_index = (index + buffer) % 8
            self.file_buttons.append(Button(file_name, const.TEXT_FONT_MAP_BUTTON, (80 + 138*column_index, self.icon_row_y_coords[row_index]), (115, 115), hidden= True))
            self.file_names_and_loc.append([file_name, (80 + 138*column_index, self.text_row_y_coords[row_index])])

    def load_saved_file(self, file_name):
        # Load in a Saved File
        with open(f"{self.current_path + file_name}", "r") as f:
            saved_data = json.load(f)
            self.game.enter_new_state("Gameplay", title=file_name[:-5], map=saved_data["map"], file_path_to_save_to= self.current_path, saved_data= saved_data)

    def add_folder(self, title):
        new_folder_path = self.current_path + title
        # Try to create a New Folder/Directory
        try:
            os.makedirs(new_folder_path)
            # print("Created New Folder:", new_folder_path)
            self.create_folder_file_buttons()

        except FileExistsError:
            print("Folder already exists:", title)

    def update_file_info(self, title, map):
        self.file_name = title
        self.map_selected = map
        # print("New title or map:", self.file_name, self.map_selected)

    def load_file_details(self, file_name):
        # The file_name parameter has its file extension (.json)
        self.selected_file_name = file_name
        self.selected_current_path = self.current_path
        with open(self.selected_current_path + self.selected_file_name, "r") as f:
            saved_data = json.load(f)
            self.selected_file_map = saved_data["map"]
            self.selected_file_date_created = saved_data["date_created"]
            self.selected_file_date_viewed = saved_data["date_viewed"]

    def delete_selected_file(self):
        full_file_path = self.selected_current_path + self.selected_file_name
        if os.path.exists(full_file_path):
            os.remove(full_file_path)
            # print("File deleted successfully:", full_file_path)
        # else:
        #     print("The file does not exist")
        self.selected_current_path = ""
        self.selected_file_name = ""
        self.selected_file_map = ""
        self.selected_file_date_created = ""
        self.selected_file_date_viewed = ""

    def analyze_video(self):
        # Analyze the video and capture screenshots at the start of each round (when the clock says 1:39)
        capture_start_of_rounds(full_video_path=self.full_video_path, folder_name= self.video_name, current_path= self.current_path)
        # Search for the selected agent icons in each screenshot
        template_matching_in_minimap((self.current_path + self.video_name), "DEF Agents", self.agents_of_interest, self.map_selected)
        
    def switch_from_saving_to_loading(self):
        self.creating_new_file = False
        self.analyze_VOD = False
        self.directions = "Step 5) Choose File to Load"