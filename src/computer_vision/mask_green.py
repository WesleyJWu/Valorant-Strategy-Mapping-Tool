import numpy as np
import cv2

def include_green(img, hsv, maskToRemoveBackground):
    # Lower bound and upper bound for Light Green color (the color of the border of the Defending Agent Icons)
    lower_bound = np.array([63, 60, 0])	 
    upper_bound = np.array([89, 255, 255])

    # Replace Light Green with White
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Perform Closing and Dilation
    kernelForClosing = np.ones((7,7),np.uint8)
    kernelForDilation = np.ones((6,6),np.uint8)
    maskClosing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernelForClosing, iterations=3)
    # Final Mask has the Green pixels be White and everything else be Black
    maskClosingDilation = cv2.dilate(maskClosing, kernelForDilation, iterations=5)

    imgClosingDilation = cv2.bitwise_and(img, img, mask=maskClosingDilation)
    imgClosingDilationNoBackground = cv2.bitwise_and(imgClosingDilation, imgClosingDilation, mask=maskToRemoveBackground)
    return imgClosingDilationNoBackground


def remove_green_from_agent_view(img, hsv):
    # Lower bound and upper bound for Lime color
    lower_bound = np.array([65, 41, 0])
    upper_bound = np.array([92, 255, 212])

    # Replace the Lime with White
    maskColorTh = cv2.inRange(hsv, lower_bound, upper_bound)

    # Perform Opening
    kernelForOpening = np.ones((3, 3),np.uint8)
    maskColorThOpening = cv2.morphologyEx(maskColorTh, cv2.MORPH_OPEN, kernelForOpening, iterations=2)
    # Final Mask has the Lime colored pixels be Black and everything else is White
    maskColorThOpeningInverted = cv2.bitwise_not(maskColorThOpening)

    imgColorThOpeningInverted = cv2.bitwise_and(img, img, mask=maskColorThOpeningInverted)

    return imgColorThOpeningInverted