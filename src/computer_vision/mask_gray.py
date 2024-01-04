import numpy as np
import cv2

def remove_gray_background(img, hsv):
    # Lower bound and upper bound for Gray color
    lower_bound = np.array([0, 0, 100])	 
    upper_bound = np.array([165, 37, 174])

    # Replace Gray with White
    maskFirst = cv2.inRange(hsv, lower_bound, upper_bound)

    # Perform Opening, Closing, and Erosion
    kernelForOpening = np.ones((3,3),np.uint8)
    kernelForClosing = np.ones((5,5),np.uint8)
    kernelForErosion = np.ones((3,3),np.uint8)
    maskWithOpening = cv2.morphologyEx(maskFirst, cv2.MORPH_OPEN, kernelForOpening, iterations=2)
    maskWithOpeningClosing = cv2.morphologyEx(maskWithOpening, cv2.MORPH_CLOSE, kernelForClosing, iterations=2)
    maskWithOpeningClosingErosion = cv2.erode(maskWithOpeningClosing, kernelForErosion)
    # Final Mask has Gray colored pixels as Black and every other color as White
    maskOpeningClosingErosionInverted = cv2.bitwise_not(maskWithOpeningClosingErosion)

    imgWithOpeningClosingErosionInverted = cv2.bitwise_and(img, img, mask=maskOpeningClosingErosionInverted)

    return imgWithOpeningClosingErosionInverted