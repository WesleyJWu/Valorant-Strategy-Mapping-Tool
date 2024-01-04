import pygame
import src.utilities.constants as const
from src.game_states.main_menu import Main_Menu
from src.game_states.new_file import New_Doc
from src.game_states.analyze_vod import Analyze_VOD
from src.game_states.directories import Directories
from src.game_states.gameplay import Gameplay


"""
Game State Manager:
- Manages which Game States are in the Stack
- Manages the Game Loop
- Switches between Games States

There are 5 Game States:
- Main Menu State
- New File State
- Directories State
- Analyze Video State
- Gameplay State

"""

class Game_State_Manager():
    def __init__(self):
        # Initializing pygame
        pygame.init()
        self.screen = pygame.display.set_mode((const.DISPLAY_WIDTH, const.DISPLAY_HEIGHT))
        pygame.display.set_caption("Valorant Strategy Mapping Tool")
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(200, 25)

        self.running = True
        self.state_stack = []
        self.stored_state = None
        starting_state = Main_Menu(self)
        self.state_stack.append(starting_state)

    def game_loop(self):
        while self.running:

            # Pass in the events to the Game State at the top of the Stack
            events = pygame.event.get()
            self.state_stack[-1].handle_events(events)
            self.state_stack[-1].update()
            self.state_stack[-1].draw_on_screen(self.screen)

            pygame.display.update()

            # Limit the FPS to 60
            self.time_delta = (self.clock.tick(60))/1000
    
    """ Helper Functions: """
    def return_to_main_menu(self):
        while len(self.state_stack) != 1:
            self.state_stack.pop()
        self.path = "game_files/"

    def current_state(self):
        return self.state_stack[-1]

    def enter_new_state(self, state, **kwargs):
        # Uses **kwargs to pass in the extra keyword arguments to each of the Game States
        new_state = None
        if (state == "New Doc"):
            new_state = New_Doc(self)
        elif (state == "Analyze VOD"):
            new_state = Analyze_VOD(self)
        elif (state == "Directories"):
            new_state = Directories(self, **kwargs)
        elif (state == "Gameplay"):
            new_state = Gameplay(self, **kwargs)

        self.state_stack.append(new_state)
        # print(len(self.state_stack))

    def return_to_prev_state(self):
        self.state_stack.pop()
        # print(len(self.state_stack))

    def update_state_info(self, **kwargs):
        if (self.stored_state):
            self.stored_state.update_file_info(**kwargs)

    def store_state(self, state):
        self.stored_state = state
    
    def get_stored_state(self):
        return self.stored_state

    def enter_stored_state(self):
        self.state_stack.append(self.stored_state)
        
    def reset_stored_state(self):
        self.stored_state = None
    
    def exit(self):
        self.running = False

if __name__ == "__main__":
    g = Game_State_Manager()
    g.game_loop()
