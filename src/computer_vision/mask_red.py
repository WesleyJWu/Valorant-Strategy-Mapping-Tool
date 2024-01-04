import numpy as np
import cv2

def remove_red(img, hsv):
    # Lower bound and upper bound for Red color
    lower_bound = np.array([170, 127, 96])	 
    upper_bound = np.array([179, 255, 255])

    # Replace Red with White
    maskColorTh = cv2.inRange(hsv, lower_bound, upper_bound)

    # Perform Opening, Closing, and Dilating
    kernelForOpening = np.ones((3,3),np.uint8)
    kernelForClosing = np.ones((35,35),np.uint8)
    kernelForDilating = np.ones((3,3),np.uint8)
    maskColorThOpening = cv2.morphologyEx(maskColorTh, cv2.MORPH_OPEN, kernelForOpening)
    maskColorThOpeningClosing = cv2.morphologyEx(maskColorThOpening, cv2.MORPH_CLOSE, kernelForClosing, iterations=2)
    maskColorThOpeningClosingDilating = cv2.dilate(maskColorThOpeningClosing, kernelForDilating, iterations=2)
    # Final Mask has Red colored pixels as Black and every other color as White
    maskColorThOpeningClosingDilatingInverted = cv2.bitwise_not(maskColorThOpeningClosingDilating)

    imgColorThOpeningClosingDilatingInverted = cv2.bitwise_and(img, img, mask=maskColorThOpeningClosingDilatingInverted)
    
    return imgColorThOpeningClosingDilatingInverted