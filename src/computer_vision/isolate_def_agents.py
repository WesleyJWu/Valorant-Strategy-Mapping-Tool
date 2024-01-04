import numpy as np
import os
import cv2

from .mask_green import include_green, remove_green_from_agent_view
from .mask_gray import remove_gray_background
from .mask_yellow import remove_yellow
from .mask_red import remove_red

def isolate_def_agents(screenshot_path, map_name):
    # Uses 4 masks to include Green, remove Gray, remove Yellow, and remove Red
    # Read in the minimap image
    img = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)

    # Convert the image to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Read in the mask to remove the background
    file_path = os.path.abspath(__file__)
    cv_direc_path = os.path.dirname(file_path)
    src_directory_path = os.path.dirname(cv_direc_path)
    project_root = os.path.dirname(src_directory_path)
    map_mask_path = os.path.join(project_root, f"assets/computer_vision/map_masks/{map_name}MaskCrop.png")
    mapMask = cv2.imread(map_mask_path, cv2.IMREAD_COLOR)
    mapMask = cv2.cvtColor(mapMask, cv2.COLOR_BGR2GRAY)

    # Return imgGreen the image that should have mainly green
    imgGreen = include_green(img, hsv, mapMask)

    # Convert the imgGreen to HSV
    hsvGreen = cv2.cvtColor(imgGreen, cv2.COLOR_BGR2HSV)

    #  Return the image that has Green but no Gray
    imgGreenButNoGray = remove_gray_background(imgGreen, hsvGreen)

    #  Convert the imgGreenButNoGray to HSV
    hsvGreenButNoGray = cv2.cvtColor(imgGreenButNoGray, cv2.COLOR_BGR2HSV)

    # Return the image that has Green but no Gray and no Yellow
    imgGreenButNoGrayAndYellow = remove_yellow(imgGreenButNoGray, hsvGreenButNoGray)

    # Convert the imgGreenButNoGrayYellow to HSV
    hsvGreenButNoGrayAndYellow = cv2.cvtColor(imgGreenButNoGrayAndYellow, cv2.COLOR_BGR2HSV)

    # Return the image that has Green but no Gray, no Yellow, and no Red
    imgGreenButNoGrayYellowOrRed = remove_red(imgGreenButNoGrayAndYellow, hsvGreenButNoGrayAndYellow)

    # Grayscale the image
    grayImgGreenButNoGrayYellowOrRed = cv2.cvtColor(imgGreenButNoGrayYellowOrRed, cv2.COLOR_BGR2GRAY)
    
    # Threshold the grayscale image to create the binary mask
    _, maskWithColorThreshold = cv2.threshold(grayImgGreenButNoGrayYellowOrRed, 1, 255, cv2.THRESH_BINARY)

    # TouchUps - 1) Opening 2) Dilating
    kernelForOpening1 = np.ones((7,7),np.uint8)
    maskFinalOpening = cv2.morphologyEx(maskWithColorThreshold, cv2.MORPH_OPEN, kernelForOpening1)
    imgTouchUpOpening = cv2.bitwise_and(imgGreenButNoGrayYellowOrRed, imgGreenButNoGrayYellowOrRed, mask=maskFinalOpening)

    # After performing an Opening and Closing touchup, remove the Green View in front of the agent icons
    hsvTouchUpOpening = cv2.cvtColor(imgGreenButNoGrayAndYellow, cv2.COLOR_BGR2HSV)
    imgTouchUpOpeningAndNoLightGreen =  remove_green_from_agent_view(imgTouchUpOpening, hsvTouchUpOpening)

    return imgTouchUpOpeningAndNoLightGreen