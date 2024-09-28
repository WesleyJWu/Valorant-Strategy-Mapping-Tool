import pygame
import os
import json
import datetime
import cv2
import platformdirs
import csv
import shutil

import src.utilities.constants as const
from src.utilities.button import Button
import src.utilities.textbox.pygametextboxinput as pyTxtBx

from src.game_states.base_state import BaseState
from src.computer_vision.capture_screenshots import capture_start_of_rounds
from src.computer_vision.template_matching import template_matching_in_minimap

""" Directories Game State """

class Directories(BaseState):
    def __init__(self, game, path="game_files/", file_name= "", map_selected= "", creating_new_file= True, analyze_VOD = False, video_name = "", full_video_path = "", selected_def_agents = [], selected_atk_agents = [], scrshot_buffer = [], scrshot_map_dims = []):

        # Initializing the Base Class
        super().__init__(game)

        file_path = os.path.abspath(__file__)
        game_states_direc_path = os.path.dirname(file_path)
        src_directory_path = os.path.dirname(game_states_direc_path)
        self.project_root = os.path.dirname(src_directory_path)
        self.current_path = os.path.join(self.project_root, path)
        self.file_name = file_name
        self.map_selected = map_selected
        self.creating_new_file = creating_new_file
        self.analyze_VOD = analyze_VOD
        self.video_name = video_name
        self.full_video_path = full_video_path
        self.selected_def_agents = selected_def_agents
        self.selected_atk_agents = selected_atk_agents
        self.scrshot_buffer = scrshot_buffer
        self.scrshot_map_dims = scrshot_map_dims

        self.directions = "Step 3) Choose location to save the file" 
        if (not self.creating_new_file):
            self.directions = "Step 1) Choose file to load"
        if (analyze_VOD):
            self.directions= "Step 4) Choose location to save the files"

        # Initialize the variables related to showing the selected file system node's info
        self.selected_current_path = self.current_path
        self.selected_fs_node_name = ""
        self.selected_fs_node_type = ""
        self.selected_fs_node_map = ""
        self.selected_fs_node_date_created = ""
        self.selected_fs_node_date_viewed = ""
        self.selected_fs_node_textbox = pyTxtBx.TextInputBox(1279, 338, font_family="arial", font_size=20, max_width=132, max_height=30, text_color="black", cursor_color="black")
        self.selected_fs_node_textbox.set_text("")

        self.process_click = True
        self.new_file_textbox = pyTxtBx.TextInputBox(1214, 31, font_family="arial", font_size=23, max_width=225, max_height=30, text_color="black", cursor_color="black")
        self.new_file_textbox.set_text(self.file_name)
        self.new_fold_textbox = pyTxtBx.TextInputBox(1267 + 5, 689 - 100 - 40 + 25, font_family="arial", font_size=20, max_width=185, max_height=30, text_color="black", cursor_color="black")
        self.new_fold_textbox_is_activated = False
        self.events = []

        # Prepare the Surfs and Rects
        self.prepare_surfs_and_rects()

        # Load in and show the first file's info in the current directory
        if (self.files):
            self.load_fs_node_details(self.files[0], "File")

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
                        # Only open and load files if we are not creating a New File
                        if ( (not self.creating_new_file) and file_button.is_button_clicked(event.pos) and self.process_click):
                            self.load_saved_file(file_button.text)
                            self.process_click = False

                    # Check to see if the User selected the Add Folder button
                    if self.add_folder_button.is_button_clicked(event.pos):
                        self.add_folder(self.new_fold_textbox.get_text())
                    
                    # Check to see if the User selected the Prev. Direc. button
                    elif (self.prev_folder_button.is_button_clicked(event.pos)) and (os.path.basename(self.current_path[:-1]) != "game_files"):
                        new_path = self.current_path.split("/")
                        new_path = new_path[:-2]
                        self.current_path = "/".join(new_path) + "/"
                        self.create_folder_file_buttons()

                    # Check to see if the User selected the Cancel button
                    elif (self.cancel_button.is_button_clicked(event.pos)):
                        # The Cancel button should only go back 2 Game States if the User is creating a New File and not analyzing a video or loading a file
                        if (self.creating_new_file and not self.analyze_VOD):
                            self.game.return_to_prev_state()
                            if self.game.prev_state_status():
                                self.game.return_to_prev_state()
                            else:
                                self.game.return_to_main_menu()
                        else:
                            if self.game.prev_state_status():
                                self.game.return_to_prev_state()
                            else:
                                self.game.return_to_main_menu()
                        
                    # Check to see if the User selected the Delete File button
                    elif (self.delete_button.is_button_clicked(event.pos)):
                        # Ensures there is a something to delete
                        if (self.selected_fs_node_name != ""):
                            self.delete_selected_fs_node()
                            # Reload the Folders and Files
                            self.create_folder_file_buttons()
                        # else:
                        #     print("Nothing to Delete!")
                    
                    # Check to see if the User selected the Analyze Folder button
                    elif (self.selected_fs_node_type == "Folder" and self.analyze_folder_button.is_button_clicked(event.pos)):
                        self.analyze_folder()

                    # Only show the Save File button if the User is creating a New File or Analyzing a Video
                    elif (self.creating_new_file):
                        # Check to see if the User selected the Save File button
                        if self.save_file_button.is_button_clicked(event.pos):
                            current_date = datetime.datetime.now()
                            formatted_date = current_date.strftime("%m/%d/%y")
                            if (self.analyze_VOD):
                                self.analyze_video()
                                pygame.event.clear()
                                self.switch_from_saving_to_loading()
                                self.create_folder_file_buttons()
                            else:
                                self.game.enter_new_state("Gameplay", title=self.file_name, map=self.map_selected, file_path_to_save_to= self.current_path, date_created=formatted_date)

                        # Only show the Change File Info button if we are creating a New File and not Analyzing a Video
                        if (not self.analyze_VOD):
                            # Check to see if the User selected the Change File Info button
                            if self.change_file_info_button.is_button_clicked(event.pos):
                                self.game.store_state(self)
                                self.game.return_to_prev_state()

                    self.new_fold_textbox_is_activated = self.new_fold_textbox.editTextBox(event.pos)
                
                elif event.button == 3:
                    # Check to see if the User right-clicked on any of the File or Folder buttons
                    for file_button in self.file_buttons:
                        if (file_button.is_button_clicked(event.pos)):
                            # print(f"Reading File {file_button.text}'s description")
                            self.load_fs_node_details(file_button.text, "File")

                    for folder_button in self.folder_buttons:
                        if (folder_button.is_button_clicked(event.pos)):
                            self.load_fs_node_details(folder_button.text, "Folder")
 
 
    def update(self):
        self.selected_fs_node_textbox.update(self.events, False)
        self.new_file_textbox.update(self.events, False)
        self.new_fold_textbox.update(self.events, self.new_fold_textbox_is_activated)

        # Check to see if mouse is hovering over any buttons
        for folder_button in self.folder_buttons:
            folder_button.is_mouse_over_button(pygame.mouse.get_pos())
        
        # If we are creating a New File, there is no need to change the color over the files
        if (not self.creating_new_file):
            for file_button in self.file_buttons:
                file_button.is_mouse_over_button(pygame.mouse.get_pos())

        self.add_folder_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.change_file_info_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.save_file_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.prev_folder_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.cancel_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.delete_button.is_mouse_over_button(pygame.mouse.get_pos())
        if self.selected_fs_node_type == "Folder":
            self.analyze_folder_button.is_mouse_over_button(pygame.mouse.get_pos())

    def prepare_surfs_and_rects(self):

        # Prepare the Sub-Folder Buttons
        self.create_folder_file_buttons()

        # Create the other Buttons
        self.prev_folder_button = Button("Prev. Direc.", const.TEXT_FONT_SUBHEADER, (970, 730), (165, 50))
        self.save_file_button = Button("Save", const.TEXT_FONT_SUBHEADER, (1228, 730), (130, 50))
        self.cancel_button = Button("Cancel", const.TEXT_FONT_SUBHEADER, (1391, 730), (130, 50))
        self.delete_button = Button("Delete", pygame.font.SysFont("arial", 18), (1390, 481), (100, 35))
        self.analyze_folder_button = Button("Analyze Folder", pygame.font.SysFont("arial", 18), (1300, 405), (140, 48))
        self.add_folder_button = Button("Add Folder", pygame.font.SysFont("arial", 20), (1285, 650), (120, 50))
        self.change_file_info_button = Button("Edit Name/Map", pygame.font.SysFont("arial", 20), (1285, 135), (160, 50))

        # Create and fill in the Background Surface with a TAN color
        self.backgroundColorForScreenSurf = pygame.Surface((const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT))
        self.backgroundColorForScreenSurf.fill((const.TAN))

       # Create the Surfs for the Folder and File icons
        folder_img_path = os.path.join(self.project_root, "assets/misceallanous/folder_icon.png")
        file_img_path = os.path.join(self.project_root, "assets/misceallanous/file_icon.png")
        self.folder_surf = pygame.image.load(folder_img_path).convert_alpha()
        self.folder_surf = pygame.transform.smoothscale(self.folder_surf, (100, 100))
        self.original_file_surf = pygame.image.load(file_img_path).convert_alpha()
        self.file_surf = pygame.transform.smoothscale(self.original_file_surf, (100, 100))
        self.large_file_surf = pygame.transform.smoothscale(self.original_file_surf, (125, 125))

    def draw_on_screen(self, screen):
        # Blit the Background Color to the Screen
        screen.blit(self.backgroundColorForScreenSurf, (0,0))

        # Draw the Rectangle and Border behind the Title
        if (self.creating_new_file and not self.analyze_VOD):
            pygame.draw.rect(screen, (255,222,173),[1138, 17, 320, 88])
            pygame.draw.rect(screen, (139,69,19), [1138, 17, 320, 88], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)

        # Draw the Header Directions
        self.draw_text(screen, self.directions, const.TEXT_FONT_SUBHEADER, (550, 50), "black", "center" )

        # Draw the Add Folder
        self.draw_text(screen, "New Folder:", pygame.font.SysFont("arial", 22), (1143, 585), "black", "midleft")
        
        # Draw in the White border and the vertical line to separate the desciption of a file and the horizontal line to separate the title
        pygame.draw.rect(screen, "seashell2", [0, 0, const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT], 5, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        pygame.draw.line(screen, "seashell2", (1130, 0), (1130, const.DISPLAY_HEIGHT), width=6)
        pygame.draw.line(screen, "seashell2", (0, 100), (1130, 100), width=6)

        # Draw the Sub-Folder Buttons and Blit the Folder Icons
        for folder_button in self.folder_buttons:
            folder_button.draw_on_screen(screen)
            screen.blit(self.folder_surf, self.folder_surf.get_rect(center = folder_button.get_button_rect().center))

        # Draw the File Buttons 
        for file_button in self.file_buttons:
            file_button.draw_on_screen(screen)
            screen.blit(self.file_surf, self.file_surf.get_rect(center = file_button.get_button_rect().center))

        # Draw Selected File or Folder Details
        pygame.draw.rect(screen, (210,105,30), [1150, 200, 300, 310])
        pygame.draw.rect(screen, (25,25,112), [1150, 200, 300, 310], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        if self.selected_fs_node_type == "File":
            screen.blit(self.large_file_surf, self.large_file_surf.get_rect(center = (1300, 270)))
        else:
            screen.blit(self.folder_surf, self.folder_surf.get_rect(center = (1300, 270)))
        if self.selected_fs_node_type == "File":
            self.draw_text(screen, f"{self.selected_fs_node_type}:", pygame.font.SysFont("arial", 20), (1234, 350), "black", "midleft", trailing= "selec_file_name")
            self.draw_text(screen, f"Map: {self.selected_fs_node_map}", pygame.font.SysFont("arial", 20), (1300, 380), "black", "center")
            self.draw_text(screen, f"Date Created: {self.selected_fs_node_date_created}", pygame.font.SysFont("arial", 20), (1300, 410), "black", "center")
            self.draw_text(screen, f"Last Viewed On: {self.selected_fs_node_date_viewed}", pygame.font.SysFont("arial", 20), (1300, 440), "black", "center")
        elif self.selected_fs_node_type == "Folder":
            self.draw_text(screen, f"{self.selected_fs_node_type}:", pygame.font.SysFont("arial", 20), (1210, 350), "black", "midleft", trailing= "selec_file_name")
        else:
            self.draw_text(screen, "Folder:", pygame.font.SysFont("arial", 20), (1210, 350), "black", "midleft", trailing= "selec_file_name")
        self.draw_text(screen, "(Right-Click on file/folder for more info)", pygame.font.SysFont("arial", 18), (1300, 520), "black", "center")

        # Draw the Other Buttons
        self.add_folder_button.draw_on_screen(screen)
        self.cancel_button.draw_on_screen(screen)
        self.delete_button.draw_on_screen(screen)        
        if (os.path.basename(self.current_path[:-1]) != "game_files"):
            self.prev_folder_button.draw_on_screen(screen)
        if self.selected_fs_node_type == "Folder":
            self.analyze_folder_button.draw_on_screen(screen)
        
        # Only draw the File Name (textbox) and Map Selected if the User is trying to create a New File and not Analyze a VOD
        if (self.creating_new_file):
            self.save_file_button.draw_on_screen(screen)
            if (not self.analyze_VOD):
                self.draw_text(screen, "File: ", pygame.font.SysFont("arial", 27), (1150, 42), "black", "midleft", trailing="curr_file_name" )
                self.draw_text(screen, "Map: " + self.map_selected, pygame.font.SysFont("arial", 27), (1150, 82), "black", "midleft" )
                self.change_file_info_button.draw_on_screen(screen)

                # Draw the New File Textbox
                pygame.draw.rect(screen, "white", [1210, 25, 230, 35])
                pygame.draw.rect(screen, "black", [1210, 25, 230, 35], 1)

                self.new_file_textbox.render(screen)

        # Draw the Selected FS Node Textbox
        pygame.draw.rect(screen, "white", [1275, 334, 141, 30])
        pygame.draw.rect(screen, "black", [1275, 334, 141, 30], 1)
        self.selected_fs_node_textbox.render(screen)

        # Draw the New Folder Textbox
        pygame.draw.rect(screen, "white", [1268, 685 - 100 - 40 + 25, 190, 35])
        pygame.draw.rect(screen, "black", [1268, 685 - 100 - 40 + 25, 190, 35], 1)
        self.new_fold_textbox.render(screen)

        # Draw the Folder and File Names in
        for folder_txt in self.folder_names_and_loc:
            self.draw_text(screen, folder_txt[0], pygame.font.SysFont("arial", 18), folder_txt[1], "black", trailing= "prev_folder_name")
        for file_txt in self.file_names_and_loc:
            self.draw_text(screen, file_txt[0][:-5], pygame.font.SysFont("arial", 18), file_txt[1], "black", trailing= "prev_file_name")

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

        # Load in the Files into Buttons
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
            self.create_folder_file_buttons()
        except FileExistsError:
            print("Folder already exists:", title)

    def update_file_info(self, title, map):
        self.file_name = title
        self.new_file_textbox.set_text(self.file_name)
        self.map_selected = map

    def load_fs_node_details(self, fs_node_name, fs_node_type):
        self.selected_fs_node_name = fs_node_name
        self.selected_fs_node_type = fs_node_type
        self.selected_current_path = self.current_path

        if fs_node_type == "File":
            self.selected_fs_node_textbox.set_text(self.selected_fs_node_name[:-5])            
            with open(self.selected_current_path + self.selected_fs_node_name, "r") as f:
                saved_data = json.load(f)
                self.selected_fs_node_map = saved_data["map"]
                self.selected_fs_node_date_created = saved_data["date_created"]
                self.selected_fs_node_date_viewed = saved_data["date_viewed"]

        else:
            self.selected_fs_node_map = ""
            self.selected_fs_node_date_created = ""
            self.selected_fs_node_date_viewed = ""
            self.selected_fs_node_textbox.set_text(self.selected_fs_node_name)


    def delete_selected_fs_node(self):
        full_fs_node_path = self.selected_current_path + self.selected_fs_node_name
        if self.selected_fs_node_type == "File":
            try:
                os.remove(full_fs_node_path)
                print("File deleted successfully:", full_fs_node_path)
            except:
                print("File was not deleted")

            pos_screenshot_path = full_fs_node_path[:-4] + "png"
            try:
                os.remove(pos_screenshot_path)
                print("File's screenshot was deleted")
            except:
                print("Screenshot was not deleted or didn't exist")

        else:
            try:
                shutil.rmtree(full_fs_node_path)
                print("Folder was deleted")
            except:
                print("Folder was not deleted")

        self.selected_current_path = ""
        self.selected_fs_node_name = ""
        self.selected_fs_node_type = ""
        self.selected_fs_node_map = ""
        self.selected_fs_node_date_created = ""
        self.selected_fs_node_date_viewed = ""
        self.selected_fs_node_textbox.set_text("")

    def analyze_video(self):
        current_date = datetime.datetime.now()
        formatted_date = current_date.strftime("%m/%d/%y")
        map_template_buffer = None
        map_template_dims = None
        map_templ_info_path = os.path.join(self.project_root, "src/utilities/map_templates_dimensions.json")
        with open(map_templ_info_path, "r") as f:
            map_template_info = json.load(f)
            map_template_buffer = map_template_info[self.map_selected]["X_Y_Buffer"]
            map_template_dims = map_template_info[self.map_selected]["Map_Size"]

        # Analyze the video and capture screenshots at the start of each round (when the clock says 1:39)
        capture_start_of_rounds(full_video_path=self.full_video_path, folder_name= self.video_name, current_path= self.current_path)
        # Search for the selected agent icons in each screenshot
        template_matching_in_minimap((self.current_path + self.video_name), self.selected_def_agents, self.selected_atk_agents, self.map_selected, self.scrshot_buffer, self.scrshot_map_dims, map_template_buffer, map_template_dims, date=formatted_date)

    def switch_from_saving_to_loading(self):
        self.creating_new_file = False
        self.analyze_VOD = False
        self.directions = "Step 5) Choose file to load"

    def find_callout_loc(self, row, col, img_RGB_map, color_map):
        hitbox_border = [[0,0], [-22, 0], [0, -22], [22, 0], [0, 22]]
        counter = 0
        callout = "Off-Map"
        while callout == "Off-Map" and counter <= 4:
            RGB_color = img_RGB_map[row + hitbox_border[counter][0]][col + hitbox_border[counter][1]]
            counter += 1
            RGB_str = f"({RGB_color[0]}, {RGB_color[1]}, {RGB_color[2]})"
            callout = color_map.get(RGB_str, "Off-Map")

        return callout

    def analyze_folder(self):

        selected_folder_path = self.current_path + f"{self.selected_fs_node_name}/"
        files_to_analyze = [file for file in sorted(os.listdir(selected_folder_path)) if (os.path.isfile((os.path.join(selected_folder_path, file))) and file.endswith(".json"))]

        def_agents = set()
        atk_agents = set()
        map_to_files = {}

        for file in files_to_analyze:
            with open(selected_folder_path + file, "r") as f:
                saved_data = json.load(f)
            def_agents = def_agents | set(saved_data["def_agents"].keys())
            atk_agents = atk_agents | set(saved_data["atk_agents"].keys())

            map = saved_data["map"]
            if map not in map_to_files:
                map_to_files[map] = []
            map_to_files[map].append(file)

        def_header = ["File", "Map"] + list(def_agents)
        atk_header = ["File", "Map"] + list(atk_agents)
        def_agents_coords = []
        def_agents_callouts = []
        atk_agents_coords = []
        atk_agents_callouts = []

        for map in map_to_files:
            # Load RGB Map
            map_callouts_path = os.path.join(self.project_root, f"assets/colored_maps/colored_{map}.png")
            img_BGR_map = cv2.imread(map_callouts_path, cv2.IMREAD_COLOR)
            img_RGB_map = cv2.cvtColor(img_BGR_map, cv2.COLOR_BGR2RGB)

            # Opening the Map Color Dict
            with open(f"assets/map_callouts/{map}_callouts.json", "r") as f:
                color_map = json.load(f)

            # Examing the Files with the same Map
            # Each json file will be a row and be a dictionary with the keys representing column headers
            for file in map_to_files[map]:
                def_agents_coord_row = {"File": file, "Map": map}
                def_agents_callouts_row = {"File": file, "Map": map}
                atk_agents_coord_row = {"File": file, "Map": map}
                atk_agents_callouts_row = {"File": file, "Map": map}

                with open(selected_folder_path + file, "r") as file:
                    saved_data = json.load(file)
                dict_def_agents = saved_data["def_agents"]
                dict_atk_agents = saved_data["atk_agents"]

                for agent in def_agents:
                    if agent in dict_def_agents:
                        agent_coords = round(dict_def_agents[agent][0][0]), round(dict_def_agents[agent][0][1])
                        def_agents_coord_row[agent] = str(agent_coords)
                        def_agents_callouts_row[agent] = self.find_callout_loc(agent_coords[1], agent_coords[0], img_RGB_map, color_map)

                    else:
                        def_agents_coord_row[agent] = "Not Present"
                        def_agents_callouts_row[agent] = "Not Present"

                for agent in atk_agents:
                    if agent in dict_atk_agents:
                        agent_coords = round(dict_atk_agents[agent][0][0]), round(dict_atk_agents[agent][0][1])
                        atk_agents_coord_row[agent] = str(agent_coords)
                        atk_agents_callouts_row[agent] = self.find_callout_loc(agent_coords[1], agent_coords[0], img_RGB_map, color_map)
                    else:
                        atk_agents_coord_row[agent] = "Not Present"
                        atk_agents_callouts_row[agent] = "Not Present"
            
                def_agents_coords.append(def_agents_coord_row)
                def_agents_callouts.append(def_agents_callouts_row)
                atk_agents_coords.append(atk_agents_coord_row)
                atk_agents_callouts.append(atk_agents_callouts_row)

        downloads_path = platformdirs.user_downloads_path()
        new_folder_path = downloads_path / self.selected_fs_node_name

        # If the path already exists, modify the directory name
        counter = 1
        while os.path.exists(new_folder_path):
            new_folder_path = downloads_path / f"{self.selected_fs_node_name} ({counter})"
            counter += 1
        
        new_folder_path.mkdir(exist_ok=True)

        # Download all the Map Templates to the Folder bc the coordinates are directly correlated to those dimensions and spacing
        for map in map_to_files:
            map_template_path = os.path.join(self.project_root, f"assets/maps/{map.capitalize()}.png")
            shutil.copy2(map_template_path, new_folder_path / f"{map.capitalize()}.png")    

        with open(new_folder_path / "DEF_coords.csv", "w", newline="") as DEF_coords_file:
            dict_writer = csv.DictWriter(DEF_coords_file, fieldnames=def_header)
            dict_writer.writeheader()
            dict_writer.writerows(def_agents_coords)
        with open(new_folder_path / "DEF_callouts.csv", "w", newline="") as DEF_callouts_file:
            dict_writer = csv.DictWriter(DEF_callouts_file, fieldnames=def_header)
            dict_writer.writeheader()
            dict_writer.writerows(def_agents_callouts)

        with open(new_folder_path / "ATK_coords.csv", "w", newline="") as ATK_coords_file:
            dict_writer = csv.DictWriter(ATK_coords_file, fieldnames=atk_header)
            dict_writer.writeheader()
            dict_writer.writerows(atk_agents_coords)
        with open(new_folder_path / "ATK_callouts.csv", "w", newline="") as ATK_callouts_file:
            dict_writer = csv.DictWriter(ATK_callouts_file, fieldnames=atk_header)
            dict_writer.writeheader()
            dict_writer.writerows(atk_agents_callouts)


