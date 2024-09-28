import numpy as np
import cv2
import os

from .mask_red_or_green import include_color, remove_color, remove_view_color
from .mask_gray import remove_gray_background
from .mask_yellow import remove_yellow

def isolate_def_agents(screenshot_path, map_name, scrshot_buffer, scrshot_map_dims):
    # Uses Map Mask and 5 Color Masks: include Green, remove Gray, remove Yellow, remove Red, and remove Lime 
    # Read in the minimap image
    img = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)

    # Convert the image to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Read in the mask to remove the background
    file_path = os.path.abspath(__file__)
    cv_direc_path = os.path.dirname(file_path)
    src_directory_path = os.path.dirname(cv_direc_path)
    project_root = os.path.dirname(src_directory_path)
    map_mask_path = os.path.join(project_root, f"assets/computer_vision/map_masks/def_masks/{map_name}_def.png")
    mapMask = cv2.imread(map_mask_path, cv2.IMREAD_COLOR)
    mapMask = cv2.cvtColor(mapMask, cv2.COLOR_BGR2GRAY)

    map_mask_height, map_mask_width = mapMask.shape
    minimap_width = scrshot_map_dims[0]
    diff = minimap_width - map_mask_width
    ratio = round((diff + 8 + map_mask_width)/map_mask_width, 3)
    mapMask = cv2.resize(mapMask,None,fx=ratio,fy=ratio)
    map_mask_height, map_mask_width = mapMask.shape
    
    top_left_x = scrshot_buffer[0] - 4
    top_left_y = scrshot_buffer[1]

    # Creating Black Background with the same size as the img
    black_background = np.zeros_like(img)
    black_background = cv2.cvtColor(black_background, cv2.COLOR_BGR2GRAY)

    # Adding Map Mask to the Black Background at the top left position
    black_background[top_left_y:top_left_y + map_mask_height, top_left_x:top_left_x + map_mask_width] = mapMask

    # Lower bound and upper bound for the Light Green color (the color of the border of the Defending Agent Icons)
    lower_bound = np.array([63, 60, 0])	 
    upper_bound = np.array([89, 255, 255])

    # Return imgGreen the image that should have mainly green
    imgGreen = include_color(img, hsv, lower_bound, upper_bound)

    # Remove the background
    imgGreen = cv2.bitwise_and(imgGreen, imgGreen, mask=black_background)

    # Convert the imgGreen to HSV
    hsvGreen = cv2.cvtColor(imgGreen, cv2.COLOR_BGR2HSV)

    # Return the image that has Green but no Gray
    imgGreenButNoGray = remove_gray_background(imgGreen, hsvGreen)

    # Convert the imgGreenButNoGray to HSV
    hsvGreenButNoGray = cv2.cvtColor(imgGreenButNoGray, cv2.COLOR_BGR2HSV)

    # Return the image that has Green but no Gray and no Yellow
    imgGreenButNoGrayAndYellow = remove_yellow(imgGreenButNoGray, hsvGreenButNoGray)

    #  Convert the imgGreenButNoGrayYellow to HSV
    hsvGreenButNoGrayAndYellow = cv2.cvtColor(imgGreenButNoGrayAndYellow, cv2.COLOR_BGR2HSV)

    # Lower bound and Upper bound for Red color
    lower_bound = np.array([170, 127, 96])	 
    upper_bound = np.array([179, 255, 255])

    # Return the image that has Green but no Gray, no Yellow, and no Red
    imgGreenButNoGrayYellowOrRed = remove_color(imgGreenButNoGrayAndYellow, hsvGreenButNoGrayAndYellow, lower_bound, upper_bound)

    # Grayscale the image
    grayImgGreenButNoGrayYellowOrRed = cv2.cvtColor(imgGreenButNoGrayYellowOrRed, cv2.COLOR_BGR2GRAY)
    
    # Threshold the grayscale image to create the binary mask
    _, maskWithColorThreshold = cv2.threshold(grayImgGreenButNoGrayYellowOrRed, 1, 255, cv2.THRESH_BINARY)

    # Perform Opening
    kernelForOpening1 = np.ones((7,7),np.uint8)
    maskFinalOpening = cv2.morphologyEx(maskWithColorThreshold, cv2.MORPH_OPEN, kernelForOpening1)
    imgTouchUpOpening = cv2.bitwise_and(imgGreenButNoGrayYellowOrRed, imgGreenButNoGrayYellowOrRed, mask=maskFinalOpening)
    hsvTouchUpOpening = cv2.cvtColor(imgGreenButNoGrayAndYellow, cv2.COLOR_BGR2HSV)

    # Lower bound and Upper bound for Lime color (Defending Agents' sight of view color)
    lower_bound = np.array([65, 41, 0])
    upper_bound = np.array([92, 255, 212])

    # Returns the image that has the touch ups and remove some of the Light Green from Agent View or Spawn Borders
    imgTouchUpOpeningAndNoLightGreen = remove_view_color(imgTouchUpOpening, hsvTouchUpOpening, lower_bound, upper_bound)

    return imgTouchUpOpeningAndNoLightGreen