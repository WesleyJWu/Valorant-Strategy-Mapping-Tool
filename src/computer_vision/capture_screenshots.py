import cv2
import os

def capture_start_of_rounds(full_video_path, folder_name, current_path ):
    # Without any overtimes, there are max 24 rounds in a Valorant Game
    # This function captures a screenshot in the video when the round clock is at 1:39
    round_counter = 0
    prev_round_start_frame_pos_plus_buffer = 0

    # Try to create New Folder/Directory to store screenshots and .json files 
    new_folder_path = current_path + folder_name
    try:
        os.makedirs(new_folder_path)
        # print("Created New Folder:", new_folder_path)
    except FileExistsError:
        print("Folder already exists in this Directory:", folder_name)

    capture = cv2.VideoCapture(full_video_path)
    if (capture.isOpened()== False):
        print("Error opening video stream or file")
    fps = capture.get(cv2.CAP_PROP_FPS)
    # Create a buffer when screenshots are taken
    pre_round_buffer = int(fps*(30))

    # Read each frame until the video is completed
    while(capture.isOpened()): 
        # Capture each frame of the video  
        ret, frame = capture.read()
        # Check to make sure the video hasn't ended yet
        if ret == True:
            # Loaded in the Color Image
            img_RGB = frame

            # Loaded in the base template
            file_path = os.path.abspath(__file__)
            cv_direc_path = os.path.dirname(file_path)
            src_directory_path = os.path.dirname(cv_direc_path)
            project_root = os.path.dirname(src_directory_path)
            base_template_path = os.path.join(project_root, "assets/computer_vision/baseTemplateForRoundStart.png")
            base_template_round_start = cv2.imread(base_template_path, 0)
            
            # Created a copy of the Colored Image but in "black and white"
            img_gray = cv2.cvtColor(img_RGB, cv2.COLOR_BGR2GRAY)
            
            # Focused on the round timer in the gray image
            img_round_timer_gray_ROI = img_gray[0:75, 920:1000]

            # SQDIFF_NORMED is the Sum of Squared Differences, which means similar images have a smaller difference
            # - The values are btw 0 and 1, and the closer the min. value of result is to 0, the more closely the base template and image patch match
            # Comparing the smaller, gray image of the round timer to the base template
            result = cv2.matchTemplate(img_round_timer_gray_ROI, base_template_round_start, cv2.TM_SQDIFF_NORMED)
        
            max_diff = 0.1
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            # The start of a new round is when the Sum of Squared Differences is small and when the prevous round was at least 30 seconds (or that converted to frames) before the next round
            if min_val < max_diff and capture.get(cv2.CAP_PROP_POS_FRAMES) > (prev_round_start_frame_pos_plus_buffer):
                # print("We found a match with our Base Template! Min value: ", min_val)

                # Tracks the previous frame position of a match and adds the 30 second pre-round buffer converted to frames to prevent multiple back-to-back screenshots
                prev_round_start_frame_pos_plus_buffer = capture.get(cv2.CAP_PROP_POS_FRAMES) + pre_round_buffer
                round_counter += 1

                # Copies the round number to the bottom left of the Mini-Map screenshot
                round_number = img_RGB[0:75, 920:1000]
                minimap = img_RGB[25:430, 0:430]
                minimap[330:405, 0:80] = round_number
               
                cv2.imwrite(new_folder_path + f"/{folder_name}_Rnd_{round_counter}.png", minimap)
                # print("Screenshot was capture for Round: ", round_counter)

                frame = img_RGB

            # Display each frame
            cv2.imshow("Frame", frame)

            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     # waitkey(1) means wait 1 millisecond
            #     #   - if nothing happens in 1 millisecond, then move on
            #     #   - if you press a key within that 1 millisecond, then check to see if
            #     #   you pressed 'q'
            #     #       - if it is q, then break out of the while loop
            #     break
        
        else:
            # Video is complete
            break

    capture.release()
    cv2.destroyAllWindows()
