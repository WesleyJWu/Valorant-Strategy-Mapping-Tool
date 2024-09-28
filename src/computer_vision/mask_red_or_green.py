import numpy as np
import cv2


def include_color(img, hsv, lower_bound, upper_bound):

    # Replace Bounded colors with White
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Perform Closing and Dilation
    kernelForClosing = np.ones((7,7),np.uint8)
    kernelForDilation = np.ones((6,6),np.uint8)
    maskClosing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernelForClosing, iterations=3)
    maskClosingDilation = cv2.dilate(maskClosing, kernelForDilation, iterations=5)

    imgClosingDilation = cv2.bitwise_and(img, img, mask=maskClosingDilation)
    return imgClosingDilation

def remove_color(img, hsv, lower_bound, upper_bound):
    # Replace Bounded color with White
    maskColorTh = cv2.inRange(hsv, lower_bound, upper_bound)

    # Perform Opening, Closing, and Dilating
    kernelForOpening = np.ones((3,3),np.uint8)
    kernelForClosing = np.ones((35,35),np.uint8)
    kernelForDilating = np.ones((3,3),np.uint8)
    maskColorThOpening = cv2.morphologyEx(maskColorTh, cv2.MORPH_OPEN, kernelForOpening)
    maskColorThOpeningClosing = cv2.morphologyEx(maskColorThOpening, cv2.MORPH_CLOSE, kernelForClosing, iterations=2)
    maskColorThOpeningClosingDilating = cv2.dilate(maskColorThOpeningClosing, kernelForDilating, iterations=2)

    maskColorThOpeningClosingDilatingInverted = cv2.bitwise_not(maskColorThOpeningClosingDilating)
    imgColorThOpeningClosingDilatingInverted = cv2.bitwise_and(img, img, mask=maskColorThOpeningClosingDilatingInverted)
    
    return imgColorThOpeningClosingDilatingInverted


def remove_view_color(img, hsv, lower_bound, upper_bound):
    # Replace the Bounded Color with White
    maskColorTh = cv2.inRange(hsv, lower_bound, upper_bound)

    # Perform Opening
    kernelForOpening = np.ones((3, 3),np.uint8)
    maskColorThOpening = cv2.morphologyEx(maskColorTh, cv2.MORPH_OPEN, kernelForOpening, iterations=2)

    # Final Mask has the Bounded colored pixels be Black and everything else is White
    maskColorThOpeningInverted = cv2.bitwise_not(maskColorThOpening)
    imgColorThOpeningInverted = cv2.bitwise_and(img, img, mask=maskColorThOpeningInverted)

    return imgColorThOpeningInverted
