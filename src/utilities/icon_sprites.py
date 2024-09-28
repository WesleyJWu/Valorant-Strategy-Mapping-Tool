import pygame
import src.utilities.constants as const
import os

class Icon(pygame.sprite.Sprite):
    def __init__(self, name, type, start_loc, team, colorBackground = None, colorSubject = None, border = True, selectable = True, moveable = True):
        super().__init__()
        self.name = name
        self.type = type
        self.start_loc = start_loc # a tuple with the x and y coords
        self.team = team
        self.colorBackground = colorBackground
        self.colorSubject = colorSubject
        self.border = border
        self.selectable = selectable
        self.moveable = moveable
        self.selected_status = False

        file_path = os.path.abspath(__file__)
        utils_direc_path = os.path.dirname(file_path)
        src_directory_path = os.path.dirname(utils_direc_path)
        self.project_root = os.path.dirname(src_directory_path)

        self.image = self.loadAndScaleIMGWithBackgroundColor()
        starting_center_x, starting_center_y = self.start_loc

        self.rect = self.image.get_rect(center = (starting_center_x, starting_center_y))
        if (self.border == True):
            pygame.draw.rect(self.image, "black", [0, 0, self.image.get_width(), self.image.get_height()], 1)


    def loadAndScaleIMGWithBackgroundColor(self):
        pathway = "assets/"
        iconWidthAndHeight = 0
        if self.type == "agent":
            pathway = pathway + "agents/" + f"{self.name}.webp"
            iconWidthAndHeight = const.AGENT_HEIGHT_WIDTH
        elif self.type == "utility":
            pathway = pathway + "agent_utility/" + (self.name).split("_")[0] + "/" + f"{self.name}.webp"
            iconWidthAndHeight = const.UTILITY_HEIGHT_WIDTH

        # Load in the Icon IMG (create a Surface for the Icon IMG)
        img_path = os.path.join(self.project_root, pathway)
        iconIMG = pygame.image.load(img_path).convert_alpha()

        if (self.colorSubject != None):
            pixels = pygame.PixelArray(iconIMG)
            pixels.replace(pygame.Color(255, 255, 255), self.colorSubject)
            iconIMG = pixels.surface

        # Scale down the Icon IMG
        iconIMG = pygame.transform.smoothscale(iconIMG, (iconWidthAndHeight, iconWidthAndHeight))
        
        if self.colorBackground == None:
            return (iconIMG)

        # Create a copy of the iconIMG Surface
        iconBackground = iconIMG.copy()
        iconBackground.fill(self.colorBackground)
        iconBackground.blit(iconIMG, (0,0))
        return (iconBackground)

    def mouseSelect(self, position):
        if (self.selectable == False):
            return False
        return (self.rect.collidepoint(position))
    
    def possibleDeletion(self, trashcanRectangle):
        if self.moveable == False:
            return
        if self.rect.colliderect(trashcanRectangle):
            self.kill()
        if self.rect.centerx > const.MAP_WIDTH:
            self.kill()

    def updatePosition(self, relativePosition):
        if self.moveable == False:
            return
        self.rect.move_ip(relativePosition)

    def drawSelection(self, selected):
        if selected:
            if self.selected_status is True:
                return
            box = pygame.Surface((self.rect.width, self.rect.height))
            box.fill("black")
            box.set_alpha(125)
            self.image.blit(box, (0,0))
            self.selected_status = True
        else:
            self.selected_status = False
            self.image = self.loadAndScaleIMGWithBackgroundColor()
            if self.border == True:
                pygame.draw.rect(self.image, "black", [0, 0, self.image.get_width(), self.image.get_height()], 1)

    def changeTeams(self, newTeam, newColorBackground, newColorSubject):
        # Change the team name and background color
        self.team = newTeam
        if newColorBackground != None:
            self.colorBackground = newColorBackground
        if newColorSubject != None:
            self.colorSubject = newColorSubject
        # Reload the image
        self.image = self.loadAndScaleIMGWithBackgroundColor()
        # Draw the border around self.image
        pygame.draw.rect(self.image, "black", [0, 0, self.image.get_width(), self.image.get_height()], 1)
    
    def get_current_loc(self):
        return [self.rect.centerx, self.rect.centery]

    def get_hit_box_coords(self, direction):
        if direction == "center":
            return self.rect.center
        elif direction == "midleft":
            return self.rect.midleft
        elif direction == "midtop":
            return self.rect.midtop
        elif direction == "midright":
            return self.rect.midright
        elif direction == "midbottom":
            return self.rect.midbottom
        else:
            return 0,0


