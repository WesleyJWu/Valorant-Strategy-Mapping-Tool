import pygame
import os
import json

import src.utilities.constants as const
from src.utilities.button import Button
from src.game_states.base_state import BaseState

class Map_Boundaries(BaseState):
    def __init__(self, game, map_name, r1_scrshot_path, video_name, full_video_path, def_agents, atk_agents):

        # Initializing the Base Class
        super().__init__(game)

        self.map_name = map_name
        self.r1_scrshot_path = r1_scrshot_path
        self.video_name = video_name
        self.full_video_path = full_video_path
        self.def_agents = def_agents
        self.atk_agents = atk_agents
        self.selected_arrow_rect = None

        # Prepare Surfs and Rects
        self.prepare_surfs_and_rects()

        # Prepare Buttons
        self.prepare_buttons()
    
    def handle_events(self, events):
        self.events = events
        for event in events:
            if event.type == pygame.QUIT:
                self.game.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:   
                    # Check to see if the arrow-boundaries were selected
                    for rect in self.arrow_rects:
                        if rect.collidepoint(event.pos):
                            self.selected_arrow_rect = rect

                    # Check to see if the Cancel Button was selected
                    if (self.cancel_button.is_button_clicked(event.pos)):
                        try:
                            print("R1 Screenshot Path: ", self.r1_scrshot_path)
                            os.remove(self.r1_scrshot_path)
                            print("R1 Screenshot Deleted")
                        except:
                            print("R1 Screenshot NOT deleted")

                        if (self.game.get_stored_state()):
                                self.game.enter_stored_state()
                                self.game.reset_stored_state()
                        else:
                            self.scrshot_buffer = [self.left_arrow_rect.right - self.screenshot_rect.left, self.top_arrow_rect.bottom - self.screenshot_rect.top]
                            self.scrshot_map_dims = [self.right_arrow_rect.left - self.left_arrow_rect.right, self.bot_arrow_rect.top -  self.top_arrow_rect.bottom]
                            self.game.return_to_prev_state()
                    
                    # Check to see if the Finish Button was selected
                    if (self.finish_button.is_button_clicked(event.pos)):
                        self.scrshot_buffer = [self.left_arrow_rect.right - self.screenshot_rect.left, self.top_arrow_rect.bottom - self.screenshot_rect.top]
                        self.scrshot_map_dims = [self.right_arrow_rect.left - self.left_arrow_rect.right, self.bot_arrow_rect.top -  self.top_arrow_rect.bottom]
                        self.game.enter_new_state("Directories", map_selected= self.map_name, creating_new_file= True, analyze_VOD= True, video_name= self.video_name, full_video_path = self.full_video_path, selected_def_agents = self.def_agents, selected_atk_agents = self.atk_agents, scrshot_buffer=self.scrshot_buffer, scrshot_map_dims=self.scrshot_map_dims)
                        try:
                            print("R1 Screenshot Path: ", self.r1_scrshot_path)
                            os.remove(self.r1_scrshot_path)
                            print("R1 Screenshot Deleted")
                        except:
                            print("R1 Screenshot NOT deleted")

            elif event.type == pygame.MOUSEMOTION:
                if self.selected_arrow_rect:
                    self.move_arrow(event.rel)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.selected_arrow_rect != None:
                    self.selected_arrow_rect = None
              
    def update(self):
        self.finish_button.is_mouse_over_button(pygame.mouse.get_pos())
        self.cancel_button.is_mouse_over_button(pygame.mouse.get_pos())
        
    def prepare_surfs_and_rects(self):
        self.hidden_background =  pygame.Surface((const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT))
        self.hidden_background.fill(const.TAN)
        self.backgroundColorForScreenSurf = pygame.Surface((const.NEW_FILE_STATE_WIDTH, const.NEW_FILE_STATE_HEIGHT + 250))
        self.backgroundColorForScreenSurf.fill((244,164,96))
        self.backgroundRect = self.backgroundColorForScreenSurf.get_rect(center=(const.DISPLAY_WIDTH/2, const.DISPLAY_HEIGHT/2))

        # Loading in the Screenshot of the first round in the video
        file_path = os.path.abspath(__file__)
        game_states_direc_path = os.path.dirname(file_path)
        src_directory_path = os.path.dirname(game_states_direc_path)
        project_root = os.path.dirname(src_directory_path)
        self.screenshot = pygame.image.load(self.r1_scrshot_path).convert_alpha()
        self.screenshot_rect = self.screenshot.get_rect(center = (735, 430))

        arrow_icon_path = os.path.join(project_root, "assets/misceallanous/arrow_icon.png")
        self.left_arrow_icon = pygame.image.load(arrow_icon_path)
        self.left_arrow_rect = self.left_arrow_icon.get_rect(center=(self.screenshot_rect.midleft[0] + 20, self.screenshot_rect.midleft[1]))
        self.right_arrow_icon = pygame.transform.rotate(self.left_arrow_icon, 180)
        self.right_arrow_rect = self.right_arrow_icon.get_rect(center=(self.screenshot_rect.midright[0] - 20, self.screenshot_rect.midright[1]))
        self.top_arrow_icon = pygame.transform.rotate(self.left_arrow_icon, -90)
        self.top_arrow_rect = self.top_arrow_icon.get_rect(center=(self.screenshot_rect.midtop[0], self.screenshot_rect.midtop[1] + 20))
        self.bot_arrow_icon = pygame.transform.rotate(self.left_arrow_icon, 90)
        self.bot_arrow_rect = self.bot_arrow_icon.get_rect(center=(self.screenshot_rect.midbottom[0], self.screenshot_rect.midbottom[1] - 20))

        self.arrow_rects = [self.left_arrow_rect, self.right_arrow_rect, self.top_arrow_rect, self.bot_arrow_rect]
    
    def draw_on_screen(self, screen):
        screen.blit(self.hidden_background, (0,0))
        pygame.draw.rect(screen, "seashell2", [0, 0, const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT], 5, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        screen.blit(self.backgroundColorForScreenSurf, self.backgroundRect)
        pygame.draw.rect(screen, (0,0,0), self.backgroundRect, width=3)

        pygame.draw.rect(screen, (255,222,173),[485, 37, 500, 65])
        pygame.draw.rect(screen, (139,69,19), [485, 37, 500, 65], 2, border_top_left_radius= 0, border_top_right_radius=0, border_bottom_left_radius=0, border_bottom_right_radius=0)
        self.draw_text(screen, "Set Map Boundaries", const.TEXT_FONT_HEADER, (350 + const.NEW_FILE_STATE_WIDTH/2, 68), "black")
        self.draw_text(screen, "Move the bars to isolate the edges of the minimap", const.TEXT_FONT_SUBHEADER, (const.NEW_FILE_STATE_WIDTH/2 + 30, 270 - 132), "black", "midleft")

        screen.blit(self.screenshot, self.screenshot_rect)
        pygame.draw.rect(screen, "black", ((self.screenshot_rect.topleft), (self.screenshot_rect.width, self.screenshot_rect.height)), 3)

        # Drawing the Translucent Grey Boxes
        left_box = pygame.Surface((self.left_arrow_rect.right - self.screenshot_rect.left, self.screenshot_rect.height))
        right_box = pygame.Surface((self.screenshot_rect.right - self.right_arrow_rect.left, self.screenshot_rect.height))
        top_box = pygame.Surface((self.right_arrow_rect.left - self.left_arrow_rect.right, self.top_arrow_rect.bottom - self.screenshot_rect.top))
        bot_box = pygame.Surface((self.right_arrow_rect.left - self.left_arrow_rect.right, self.screenshot_rect.bottom - self.bot_arrow_rect.top))
        grey_boxes = [left_box, right_box, top_box, bot_box]
        for box in grey_boxes:
            box.fill("black")
            box.set_alpha(125)
        screen.blit(left_box, self.screenshot_rect.topleft)
        screen.blit(right_box, (self.right_arrow_rect.left, self.screenshot_rect.top))
        screen.blit(top_box, (self.left_arrow_rect.right, self.screenshot_rect.top))
        screen.blit(bot_box, (self.left_arrow_rect.right, self.bot_arrow_rect.top))

        # Drawing the moving-boundaries as a rectangle
        pygame.draw.rect(screen, "red", (self.left_arrow_rect.right, self.top_arrow_rect.bottom, self.right_arrow_rect.left - self.left_arrow_rect.right, self.bot_arrow_rect.top -  self.top_arrow_rect.bottom), width = 3)

        # Drawing the arrow icons
        screen.blit(self.left_arrow_icon, self.left_arrow_rect)
        screen.blit(self.right_arrow_icon, self.right_arrow_rect)
        screen.blit(self.top_arrow_icon, self.top_arrow_rect)
        screen.blit(self.bot_arrow_icon, self.bot_arrow_rect)

        self.finish_button.draw_on_screen(screen)
        self.cancel_button.draw_on_screen(screen)

    """ Helper Functions """

    def prepare_buttons(self):
        self.finish_button = Button("Next", const.TEXT_FONT_SUBHEADER,(860, 730), (120,50))
        self.cancel_button = Button("Cancel", const.TEXT_FONT_SUBHEADER,(1015, 730), (150,50))

    def move_arrow(self, rel_mov):
        # Moving Left or Right Arrows
        if self.selected_arrow_rect is self.left_arrow_rect or self.selected_arrow_rect is self.right_arrow_rect:
            self.selected_arrow_rect.move_ip((rel_mov[0],0))
            if self.selected_arrow_rect is self.left_arrow_rect and self.selected_arrow_rect.midright[0] > self.right_arrow_rect.midleft[0]:
                self.selected_arrow_rect.midright = self.right_arrow_rect.midleft
            if self.selected_arrow_rect is self.right_arrow_rect and self.selected_arrow_rect.midleft[0] < self.left_arrow_rect.midright[0]:
                self.selected_arrow_rect.midleft = self.left_arrow_rect.midright
        # Moving Top or Bottom Arrows
        else:
            self.selected_arrow_rect.move_ip((0, rel_mov[1]))
            if self.selected_arrow_rect is self.top_arrow_rect and self.selected_arrow_rect.midbottom[1] > self.bot_arrow_rect.midtop[1]:
                self.selected_arrow_rect.midbottom = self.bot_arrow_rect.midtop
            if self.selected_arrow_rect is self.bot_arrow_rect and self.selected_arrow_rect.midtop[1] < self.top_arrow_rect.midbottom[1]:
                self.selected_arrow_rect.midtop = self.top_arrow_rect.midbottom        
        
        # Prevent arrows from going beyond the screenshot
        arrow_offset = self.left_arrow_rect.width
        if self.selected_arrow_rect.left < self.screenshot_rect.left - arrow_offset:
            self.selected_arrow_rect.left = self.screenshot_rect.left - arrow_offset
        elif self.selected_arrow_rect.right > self.screenshot_rect.right + arrow_offset:
            self.selected_arrow_rect.right = self.screenshot_rect.right + arrow_offset
        elif self.selected_arrow_rect.top < self.screenshot_rect.top - arrow_offset:
            self.selected_arrow_rect.top = self.screenshot_rect.top  - arrow_offset
        elif self.selected_arrow_rect.bottom > self.screenshot_rect.bottom + arrow_offset:
            self.selected_arrow_rect.bottom = self.screenshot_rect.bottom + arrow_offset
        
        # Keep the arrows centered
        if self.selected_arrow_rect is self.left_arrow_rect or self.selected_arrow_rect is self.right_arrow_rect:
            halfway_x = (self.left_arrow_rect.centerx + self.right_arrow_rect.centerx)/2
            self.top_arrow_rect.centerx = halfway_x
            self.bot_arrow_rect.centerx = halfway_x
        else:
            halfway_y = (self.top_arrow_rect.centery + self.bot_arrow_rect.centery)/2
            self.left_arrow_rect.centery = halfway_y
            self.right_arrow_rect.centery = halfway_y

    def transform_coords(self):
        full_folder_path = os.path.dirname(self.r1_scrshot_path)
        json_names = [file for file in os.listdir(full_folder_path) if file.endswith(".json")]
        json_paths = [(full_folder_path + "/" + json) for json in json_names]

        scrshot_buffer = [self.left_arrow_rect.right - self.screenshot_rect.left, self.top_arrow_rect.bottom - self.screenshot_rect.top]
        scrshot_map_dims = [self.right_arrow_rect.left - self.left_arrow_rect.right, self.bot_arrow_rect.top -  self.top_arrow_rect.bottom]

        map_template_buffer = None
        map_template_dims = None
        with open("src/utilities/map_templates_dimensions.json", "r") as f:
            map_template_info = json.load(f)
            map_template_buffer = map_template_info[self.map_name]["X_Y_Buffer"]
            map_template_dims = map_template_info[self.map_name]["Map_Size"]

        # print(self.map_name)
        # print(map_template_buffer)
        # print(map_template_dims)
        
        for path in json_paths:
            with open(path, "r") as f:
                saved_data = json.load(f)
            def_dict = saved_data["def_agents"]

            for def_agent in def_dict:
                agent_loc = def_dict[def_agent][0]
                def_dict[def_agent] = self.get_relative_coords(agent_loc, scrshot_buffer, scrshot_map_dims, map_template_buffer, map_template_dims)

            with open(path, "w") as f:
                json.dump(saved_data, f, sort_keys=True, indent=4)

    def get_relative_coords(self, agent_loc, scrshot_buffer, scrshot_map_dims, map_template_buffer, map_template_dims):
        norm_x, norm_y = self.calc_normalization(agent_loc[0], agent_loc[1], scrshot_buffer[0], scrshot_buffer[1], scrshot_map_dims[0], scrshot_map_dims[1])
        corresponding_x = (norm_x * map_template_dims[0]) + map_template_buffer[0]
        corresponding_y = (norm_y * map_template_dims[1]) + map_template_buffer[1]
        return [[corresponding_x, corresponding_y]]

    def calc_normalization(self, x_loc, y_loc, x_buffer, y_buffer, map_width, map_height):
        norm_x = (x_loc - x_buffer)/map_width
        norm_y = (y_loc - y_buffer)/map_height
        return norm_x, norm_y