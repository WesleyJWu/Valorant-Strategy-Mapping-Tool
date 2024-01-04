import numpy as np
import cv2

def remove_yellow(img, hsv):
    # Lower bound and upper bound for Yellow color
    lower_bound = np.array([22, 22, 0])	 
    upper_bound = np.array([50, 80, 190])

    # Replace Yellow with White
    maskColorThreshold = cv2.inRange(hsv, lower_bound, upper_bound)

    # Perform Opening and Closing
    kernelForOpening = np.ones((5,5),np.uint8) 
    kernelForClosing = np.ones((5,5),np.uint8)
    maskColorThOpening = cv2.morphologyEx(maskColorThreshold, cv2.MORPH_OPEN, kernelForOpening)
    maskColorThOpeningClosing = cv2.morphologyEx(maskColorThOpening, cv2.MORPH_CLOSE, kernelForClosing, iterations=3)
    # Final Mask has Yellow colored pixels as Black and every other color as White
    maskColorThOpeningClosingInverted = cv2.bitwise_not(maskColorThOpeningClosing)
    
    imgColorThOpeningClosingInverted = cv2.bitwise_and(img, img, mask=maskColorThOpeningClosingInverted)

    return imgColorThOpeningClosingInverted