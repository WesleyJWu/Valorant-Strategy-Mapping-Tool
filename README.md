
# **Valorant Strategy Mapping Tool**

**[Valorant](https://playvalorant.com/en-us/)** is a tactical 5v5 first-person, character-based shooter game developed and published by Riot Games in 2020. As an avid player and fan of the professional competitive scene, I always wanted to participate and contribute to the rapidly growing Valorant Esports community. Lacking the skill to compete on a professional team, I instead pivoted to create a tool that can help players, coaches, and teams with:

- Developing new strategies to prepare for future matches and tournaments
- Analyzing their opponents' common strategies and patterns

I provided documentation below to offer a detailed explanation of my Mapping Tool’s capabilities and the three paths  — Creating a New File, Loading a File, and Analyzing a Video — to access the tool. Each path includes step-by-step instructions and presents a detailed overview of its respective features. Newly introduced features will be distinctly highlighted for ease of identification.

For a more in-depth understanding of the video analysis, I've included a dedicated section that delves into the **[computer vision](#computer-vision-details)** utilized in this project. Additionally, if you are new to Valorant, I recommend starting with the "**[Quick Overview of a Valorant Match](#quick-overview-of-a-valorant-match)**" section to gain some background knowledge before progressing into the documentation.

I hope you enjoy using my Mapping Tool!

---

## **Table of Contents**

- **[Quick Overview of a Valorant Match](#quick-overview-of-a-valorant-match)**
- **[Documentation](#documentation)**
  - **[Mapping Tool](#mapping-tool)**
  - **[Creating a New File](#creating-a-new-file)**
  - **[Loading a File](#loading-a-file)**
  - **[Analyzing a Video](#analyzing-a-video)**
    - **[What Does my Computer Vision Algorithm Detect?](#what-does-my-computer-vision-algorithm-detect)**
    - **[Instructions to Analyze a Video](#instructions-to-analyze-a-video)**
- **[Computer Vision Details](#computer-vision-details)**
  - **[Obstacles with Analyzing a Video](#obstacles-with-analyzing-a-video)**
  - **[Optimizations with Template Matching to Detect Agents:](#optimizations-with-template-matching-to-detect-agents)**
  - **[Attempting Feature Detection, Description, and Matching](#attempting-feature-detection-description-and-matching)**
 
---

## **Quick Overview of a Valorant Match**

A Valorant match features two teams, each consisting of five players. Before the match, one of ten available maps is selected either randomly or by mutual agreement between the two teams. Players then choose their agents (characters with unique abilities, such as flash-bangs or smokescreens). The game currently boasts 23 unique agents, with the rule that no agent can be duplicated within the same team.

Teams are initially designated as either Attackers or Defenders. The Attackers' goal is to plant a bomb-like-device called the Spike at one of the specified bomb sites and ensure it detonates, or alternatively, they can win the round by eliminating the Defending team. The Defenders aim to thwart this plan either by neutralizing all Attackers, running out the round's 100-second timer, or, if the Spike is planted, by defusing it before it explodes.

Matches in Valorant are segmented into rounds, each lasting approximately 100 seconds. Victory is achieved by the first team to win 13 of these rounds. The match is divided into two halves, with teams swapping roles (Attackers becoming Defenders and Defenders becoming Attackers) after the first 12 rounds. In cases where the score is tied 12-12, the match enters an overtime phase, requiring a team to secure a two-round lead to clinch victory.

---

## **Documentation**

From the Main Menu screen, Users can select three different paths to access the Mapping Tool:
- **[Creating a New File](#creating-a-new-file)**
- **[Loading a File](#loading-a-file)**
- **[Analyzing a Video](#analyzing-a-video)**

Each path contains step-by-step directions to successfully reach the Mapping Tool.

### **Mapping Tool**

Users are provided an intuitive, user-friendly interface to accurately place agents and their abilities onto any Valorant map, to formulate and refine new strategies as Attackers or Defenders. To reduce clutter and improve visibility, only the 5 most recently selected agents will have their abilities shown.

Attackers and Defenders are represented by red and green background colors, respectively, and Users can switch between selecting Attacking and Defending agents and abilities on the toolbar without changing the background color of agents and abilities already placed on the map.
 
Additional key features include:
- Taking notes with dynamic scrolling
- Saving the agents, abilities, their locations, and notes into a file
- Downloading and exporting the file as a pdf

### **Creating a New File**

Users can easily create a new file from the Main Menu or within the Mapping Tool. Users will need to name the file and select their desired map, before moving to the Directories Page to choose the appropriate folder (or create a new folder) to save the file. After saving to a folder, they will move to the Mapping Tool.

Other key features within the Directories Page when saving a new file include:
- Modifying the name and chosen map of the new file
- Left-clicking on any folder to reveal the files it contains
  - An option will appear to return to the parent folder
- Right-clicking on any file to view its details:
  - File name
  - Associated map
  - Creation date
  - Last viewed date
- Deleting an existing file


### **Loading a File**

Users can efficiently load an existing file from the Main Menu or within the Mapping Tool. Loading a file will move Users to the Directories Page where Users can open a file by left clicking on it. Once a file is opened, Users are taken to the Mapping Tool, where the map and note section are automatically prepopulated with agents, abilities, and notes to match any previously saved progress.

Other key features within the Directories Page when loading a file include:
- Left-clicking on any folder to reveal the files it contains
  - An option will appear to return to the parent folder
- Right-clicking on any file to view its details:
  - File name
  - Associated map
  - Creation date
  - Last viewed date
- Deleting an existing file


### **Analyzing a Video**

In a tactical game like Valorant, information is crucial for both the Attacking and Defending teams to make the correct macro and micro decisions in order to create the best opportunities to win rounds and, ultimately, the entire Valorant match. For example, within each round, players on both teams often use abilities to probe and collect information to determine which bomb site is weaker to attack and plant the Spike on or, on the opposite side, determine if players need to rotate to reinforce a bomb site and fill in gaps in the defense.

Not only is it important for high caliber teams to devise new attacking tactics and defensive setups, but it is also crucial to review and dissect their opponents strategies to recognize patterns and weaknesses. Similar to scouting reports in other professional sports, like football and basketball, these detailed analyses offer unique insights on what teams should expect. For example, recognizing their opponents’ commonly used defensive setups can help the team captain or in-game-leader choose the weaker bomb site to attack, massively raising the odds of winning that round.

#### ***What Does my Computer Vision Algorithm Detect?*** 

The video analysis was built on footage sourced from recordings of live Valorant tournaments and focuses on two regions of interest:

- The minimap in the upper left corner
- The round clock in the upper middle

Because the footage is provided for the spectators’ eyes, the minimap shows the positions of both the Attacking and Defending agents relative to the map in play.

My algorithm uses computer vision, specifically template matching, to:

1. Capture screenshots at the start of each round, which is when the round clock in the video resets to 1 minute and 39 seconds
2. Find the agents and their locations in each screenshot’s minimap, after the video has ended and all the screenshots are gathered

The agents' locations will then be resized to be in the same relative positive in the Mapping Tool’s map as the screenshot’s minimap, before being added to a new file. There will be a new file for each round in the video, and all the files will be placed in a new folder. 

More information about my computer vision algorithm can be found in "**[Computer Vision Details](#computer-vision-details)**".


#### ***Instructions to Analyze a Video***

Users can only analyze a video from the Main Menu screen. Prior to analysis, the Users need to select a video file in mp4 format from their computer, choose the appropriate map, and specify the Attacking and Defending agents to detect for.

After these initial selections, Users are then guided to the Directories Page, where they will need to choose the save location for the new folder and files. 

Video analysis commences once the Users select the “Save” button in the Directories Page. Once the analysis is complete and the folder and its associated files are generated, the Users may now open the new folder and select any of its files to view in the Mapping Tool. These files will prepopulate the Defending agents onto the map in the Mapping Tool and attach the round screenshot in the toolbar for side-by-side comparison.

---

## **Computer Vision Details**

A brief overview of my computer vision algorithm was provided earlier in "**[What Does my Computer Vision Algorithm Detect?](#what-does-my-computer-vision-algorithm-detect)**".

To elaborate further, my template matching algorithm used the Normalized Squared Difference method in the OpenCV python library, where the template image systematically slides over the source image similar to 2D convolution. For each position, it calculates the normalized squared difference between the template and the corresponding region in the source image. The resulting output is a grayscale image where each pixel's intensity reflects this squared difference. Contrary to other methods like Cross-Correlation and Correlation Coefficient, lower values (darker areas) in this resulting image indicate a higher similarity between the template and the source region. Thus, the best match is identified by locating the darkest point in the result image, signifying the area where the template and the source image align most closely in terms of structure and intensity.

In this section, I dive deeper into the obstacles with analyzing a video, optimizations with template matching, and trying feature detection, description, and matching to detect the agents.

### **Obstacles with Analyzing a Video**

The agents in the screenshot’s minimap are only around 25 x 30 pixels and are often overlapping each other, presenting significant challenges in finding an effective computer vision algorithm for accurate detection. After **[experimenting with several other computer vision techniques](#attempting-feature-detection-description-and-matching)**, template matching offered the most accurate results in detecting the agents.

Although template matching proved to be more accurate compared to other algorithms, it still encountered some issues. To effectively match the miniature agents in the screenshot’s minimap, template matching necessitates a comparably small template image. A small template, due to its limited number of pixels, provides less feature information, which hinders the algorithm's ability to locate an accurate match, for example, when agents overlap. Additionally, the reduced pixel count in a small template heightens its sensitivity to noise and minor variations, resulting in a few false positives and difficulties in finding the correct match, particularly when some agents look similar at such a small scale. Using a strict threshold level could also not consistently and accurately separate good and bad matches.

### **Optimizations with Template Matching to Detect Agents**

To improve the accuracy of detecting agents in the screenshot’s minimap, the computer vision algorithm incorporates several masks to filter out irrelevant elements before performing template matching.

By prompting Users to select the map in advance, the algorithm masks out extraneous background elements to leave behind the outlined area of the chosen map. In addition, the algorithm currently focuses on identifying Defending agents, which are uniquely marked by a green background and border. To isolate these agents effectively, four color masks are applied:

- A mask to separate out the gray areas, representing empty locations on the minimap
- A mask to exclude the yellow areas, indicating the bomb-sites
- A mask to remove red areas, corresponding to Attacking agents
- A mask to eliminate a lighter shade of green, specifying the vision range of Defending agents.

Each mask undergoes additional processing, including opening, closing, dilations, and erosions, to refine the masks and produce a final image that exclusively highlights the Defending agents. These optimizations significantly reduce the likelihood of false positive matches and improves the detection accuracy of the template matching.

### **Attempting Feature Detection, Description, and Matching**

In my attempts to identify the agents in the screenshot’s minimap, I initially explored various methods combining feature detection, description, and matching. 

- Using SIFT (Scale-Invariant Feature Transform):
  - I first tried applying SIFT (rotation invariant and scale invariant) for feature detection and description, and then paired it with a Brute Force Matcher or a FLANN (Fast Library for Approximate Nearest Neighbors) Based Matcher for feature matching.
- Using ORB (Oriented FAST and Rotated BRIEF):
  - I switched to ORB, which is faster than SIFT, for both detection and description, and combined it with a Brute Force Matcher or a FLANN Based Matcher for feature matching. 

I hoped that by experimenting with some of the most common and well-documented algorithms for feature detection, description, and matching, I could more seamlessly detect the agents in the screenshot’s minimap. However, none of these combinations of computer vision techniques were as consistant and accurate as template matching in these detections. The agents’ small size likely impeded the algorithms' abilities to detect and describe a sufficient number of features for effective matching. 




