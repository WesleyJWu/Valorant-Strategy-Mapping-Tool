import numpy as np
import cv2
import os

from .mask_red_or_green import include_color, remove_color, remove_view_color
from .mask_gray import remove_gray_background

def isolate_atk_agents(screenshot_path, map_name, scrshot_buffer, scrshot_map_dims):
    # Uses Map Mask and 4 Color Masks: include Red, remove Gray, remove Green, and remove Light Red 
    # Read in the minimap image
    img = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)

    # Convert the image to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Read in the mask to remove the background
    file_path = os.path.abspath(__file__)
    cv_direc_path = os.path.dirname(file_path)
    src_directory_path = os.path.dirname(cv_direc_path)
    project_root = os.path.dirname(src_directory_path)
    map_mask_path = os.path.join(project_root, f"assets/computer_vision/map_masks/atk_masks/{map_name}_atk.png")
    mapMask = cv2.imread(map_mask_path, cv2.IMREAD_COLOR)
    mapMask = cv2.cvtColor(mapMask, cv2.COLOR_BGR2GRAY)

    map_mask_height, map_mask_width = mapMask.shape
    minimap_width = scrshot_map_dims[0]
    diff = minimap_width - map_mask_width
    ratio = round((diff + 5 + map_mask_width)/map_mask_width, 3)
    mapMask = cv2.resize(mapMask,None,fx=ratio,fy=ratio)
    map_mask_height, map_mask_width = mapMask.shape

    top_left_x = scrshot_buffer[0]
    top_left_y = scrshot_buffer[1]

    # Creating Black Background with the same size as the img
    black_background = np.zeros_like(img)
    black_background = cv2.cvtColor(black_background, cv2.COLOR_BGR2GRAY)

    # Adding the Map Mask to the Black Background at the top left position
    black_background[top_left_y:top_left_y + map_mask_height, top_left_x:top_left_x + map_mask_width] = mapMask

    # Lower bound and Upper bound for Red color (the color of the border of the Attacking Agent Icons)
    lower_bound = np.array([170, 127, 96])	 
    upper_bound = np.array([179, 255, 255])

    # Return imgRed the image that should have mainly Red
    imgRed = include_color(img, hsv, lower_bound, upper_bound )

    # Remove background
    imgRed = cv2.bitwise_and(imgRed, imgRed, mask=black_background)

    # Convert the imgRed to HSV
    hsvRed = cv2.cvtColor(imgRed, cv2.COLOR_BGR2HSV)

    # Return the image that has Red but no Gray
    imgRedButNoGray = remove_gray_background(imgRed, hsvRed)

    # Convert the imgRedButNoGray to HSV
    hsvRedButNoGray = cv2.cvtColor(imgRedButNoGray, cv2.COLOR_BGR2HSV)

    # Lower bound and Upper bound for Green color
    lower_bound = np.array([63, 60, 0])	 
    upper_bound = np.array([89, 255, 255])

    # Return the image that has Red but no Gray, and no Green
    imgRedButNoGrayOrGreen = remove_color(imgRedButNoGray, hsvRedButNoGray, lower_bound, upper_bound)

    # Grayscale the image
    grayImgRedButNoGrayOrGreen = cv2.cvtColor(imgRedButNoGrayOrGreen, cv2.COLOR_BGR2GRAY)
    
    # Threshold the grayscale image to create the binary mask
    _, maskWithColorThreshold = cv2.threshold(grayImgRedButNoGrayOrGreen, 1, 255, cv2.THRESH_BINARY)

    # Perform Opening
    kernelForOpening1 = np.ones((7,7),np.uint8)
    maskFinalOpening = cv2.morphologyEx(maskWithColorThreshold, cv2.MORPH_OPEN, kernelForOpening1)
    imgTouchUpOpening = cv2.bitwise_and(imgRedButNoGrayOrGreen, imgRedButNoGrayOrGreen, mask=maskFinalOpening)
    hsvTouchUpOpening = cv2.cvtColor(imgRedButNoGrayOrGreen, cv2.COLOR_BGR2HSV)

    # Lower bound and Upper bound for Light Red color (Attacking Agents' sight of view color)
    lower_bound = np.array([128, 45, 0])
    upper_bound = np.array([179, 255, 255])

    # Returns the image that has the touch ups and remove some of the Light Red Color from Agent View or Spawn Borders
    imgTouchUpOpeningAndNoViewColor =  remove_view_color(imgTouchUpOpening, hsvTouchUpOpening, lower_bound, upper_bound)

    return imgTouchUpOpeningAndNoViewColor

