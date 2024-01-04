import os
import json
import cv2

from .isolate_def_agents import isolate_def_agents

def template_matching_in_minimap(full_folder_path, label, agents_of_interest, map):
    # Screenshot names will have the File Extensions (png)
    screenshot_names = [screenshot for screenshot in sorted(os.listdir(full_folder_path)) if screenshot.endswith(".png")]
    screenshot_paths = [(full_folder_path + "/" + screenshot) for screenshot in screenshot_names]
    # print(screenshot_paths)

    scalar_dict = {"Ascent": [1.778, 1.798], "Bind": [1.778, 1.798], "Breeze": [1.778, 1.798], "Fracture": [1.778, 1.798], "Haven": [1.860, 1.975], "Icebox": [1.778, 1.798], "Pearl": [1.778, 1.798], "Split": [1.778, 1.798], "Lotus": [1.778, 1.798], "Sunset": [1.778, 1.798]}
    atk_agents = {}

    if (label == "DEF Agents"):
        # print("Scanning for DEF Agents")
        for screenshot_path in screenshot_paths:
            def_agents = {}
            parts = screenshot_path.split("/")
            name_of_screenshot_with_ext = parts[-1]
            file_path_to_save_to = "/".join(parts[:-1]) + "/"
            # print("Name of Screenshot: ", name_of_screenshot_with_ext)
            img_minimap = isolate_def_agents(screenshot_path, map)
            
            for def_agent in agents_of_interest:
                agent_loc = find_agent_in_minimap(def_agent.name, img_minimap)
                scaled_x_coord = agent_loc[0] * scalar_dict[map][0]
                scaled_y_coord = agent_loc[1] * scalar_dict[map][1]
                def_agents[def_agent.name] = [[scaled_x_coord, scaled_y_coord]]

            file_name, extension = os.path.splitext(name_of_screenshot_with_ext)
            save_to_file(file_name, map, file_path_to_save_to, def_agents=def_agents)


def find_agent_in_minimap(agent, imgRGB):
    # Load in the Agent Icon Template
    file_path = os.path.abspath(__file__)
    cv_direc_path = os.path.dirname(file_path)
    src_directory_path = os.path.dirname(cv_direc_path)
    project_root = os.path.dirname(src_directory_path)
    base_template_path = os.path.join(project_root, f"assets/computer_vision/agent_icon_minimap_templates/{agent}.png")
    baseTemplate = cv2.imread(base_template_path, 0)

    # Determine the height and width of the base template
    h, w = baseTemplate.shape

    # Created a copy of the Colored Image but in Gray scale
    imgGray = cv2.cvtColor(imgRGB, cv2.COLOR_BGR2GRAY)

    # SQDIFF_NORMED is the Sum of Squared Differences, which means similar images have a smaller difference
    # - The values are btw 0 and 1, and the closer the min. value of result is to 0, the more closely the base template and image patch match
    # Matching for the Agent Icon Template in the Screenshot of the video
    result = cv2.matchTemplate(imgGray, baseTemplate, cv2.TM_SQDIFF_NORMED)

    maxDiff = 0.5 
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if min_val < maxDiff:
        # print(f"We found a(n) {agent} with our Base Template! Min value: ", min_val)
        top_left_loc = min_loc
        bottom_right_loc = (top_left_loc[0] + w, top_left_loc[1] + h)
        xCoord = int((top_left_loc[0] + bottom_right_loc[0])/2)
        yCoord = int((top_left_loc[1] + bottom_right_loc[1])/2)

        # Dotted where the agent is found on the minimap
        # imgRGB = cv2.circle(imgRGB, (xCoord,yCoord), radius=3, color=(0, 0, 255), thickness=-1)
        # cv2.imshow("Match", imgRGB)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return [xCoord, yCoord]
    
    else:
        # print(f"No match was found => Agent {agent} was not found ", min_val)
        return [30,30]


def save_to_file(file_name, map, file_path_to_save_to, atk_agents={}, def_agents={}, atk_utility={}, def_utility={}, date_created="", date_viewed="", notes=""):
    file_info = {}
    file_info["map"] = map
    file_info["file_path"] = file_path_to_save_to
    file_info["atk_agents"] = atk_agents
    file_info["def_agents"] = def_agents
    file_info["atk_utility"] = atk_utility
    file_info["def_utility"] = def_utility
    file_info["date_created"] = date_created
    file_info["date_viewed"] = date_viewed
    file_info["notes"] = notes

    with open(f"{file_path_to_save_to + file_name}.json", "w") as f:
        json.dump(file_info, f, sort_keys= True, indent= 4)
    # print(f"Saving File: {file_path_to_save_to + file_name}.json")



  