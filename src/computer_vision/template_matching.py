import os
import json
import cv2

from .isolate_def_agents import isolate_def_agents
from .isolate_atk_agents import isolate_atk_agents


def template_matching_in_minimap(full_folder_path, selected_def_agents, selected_atk_agents, map, scrshot_buffer, scrshot_map_dims, map_template_buffer, map_template_dims, date = ""):
    # Screenshot Names will have the File Extensions (png)
    screenshot_names = [screenshot for screenshot in sorted(os.listdir(full_folder_path)) if screenshot.endswith(".png")]
    screenshot_paths = [(full_folder_path + "/" + screenshot) for screenshot in screenshot_names]

    for screenshot_path in screenshot_paths:
        parts = screenshot_path.split("/")
        name_of_screenshot_with_ext = parts[-1]
        file_path_to_save_to = "/".join(parts[:-1]) + "/"
        # print("Name of Screenshot: ", name_of_screenshot_with_ext)

        def_agents = {}
        def_img_minimap = isolate_def_agents(screenshot_path, map, scrshot_buffer, scrshot_map_dims)
        for def_agent in selected_def_agents:
            agent_loc = find_agent_in_minimap(def_agent.name, def_img_minimap)
            def_agents[def_agent.name] = get_relative_coords(agent_loc, scrshot_buffer, scrshot_map_dims, map_template_buffer, map_template_dims)

        atk_agents = {}
        atk_img_minimap = isolate_atk_agents(screenshot_path, map, scrshot_buffer, scrshot_map_dims)
        for atk_agent in selected_atk_agents:
            agent_loc = find_agent_in_minimap(atk_agent.name, atk_img_minimap)
            atk_agents[atk_agent.name] = get_relative_coords(agent_loc, scrshot_buffer, scrshot_map_dims, map_template_buffer, map_template_dims)

        file_name, extension = os.path.splitext(name_of_screenshot_with_ext)
        save_to_file(file_name, map, file_path_to_save_to, atk_agents=atk_agents, def_agents=def_agents, date_created=date)


def get_relative_coords(agent_loc, scrshot_buffer, scrshot_map_dims, map_template_buffer, map_template_dims):
    norm_x, norm_y = calc_normalization(agent_loc[0], agent_loc[1], scrshot_buffer[0], scrshot_buffer[1], scrshot_map_dims[0], scrshot_map_dims[1])
    corresponding_x = (norm_x * map_template_dims[0]) + map_template_buffer[0]
    corresponding_y = (norm_y * map_template_dims[1]) + map_template_buffer[1]
    return [[corresponding_x, corresponding_y]]

def calc_normalization(x_loc, y_loc, x_buffer, y_buffer, map_width, map_height):
    norm_x = (x_loc - x_buffer)/map_width
    norm_y = (y_loc - y_buffer)/map_height
    return norm_x, norm_y

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

        top_left_loc = min_loc
        bottom_right_loc = (top_left_loc[0] + w, top_left_loc[1] + h)
        xCoord = int((top_left_loc[0] + bottom_right_loc[0])/2)
        yCoord = int((top_left_loc[1] + bottom_right_loc[1])/2)


        # # Dotted where the agent is found on the minimap
        # print(f"We found a(n) {agent} with our Base Template! Min value: ", min_val)        
        # imgRGB = cv2.circle(imgRGB, (xCoord,yCoord), radius=3, color=(0, 0, 255), thickness=-1)
        # cv2.imshow("Match", imgRGB)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()


        return [xCoord, yCoord]
    
    else:
        print(f"No match was found => Agent {agent} was not found ", min_val)
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
