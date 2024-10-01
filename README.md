# **Valorant Strategy Mapping Tool**

**Update Notes - [Version 2.0](#version-20)**

(Unfortunately, there will be minimal updates to this project in the foreseeable future as I will be busy starting graduate school at UC San Diego this Fall.)

---

**[Valorant](https://playvalorant.com/en-us/)** is a tactical 5v5 first-person, character-based shooter game developed and published by Riot Games in 2020. As an avid player and fan of the professional competitive scene, I always wanted to participate and contribute to the rapidly growing Valorant Esports community. Lacking the skill to compete on a professional team, I instead pivoted to create a tool that can specifically help professional players, coaches, and teams with:

- Crafting new tactics and gameplans to deepen their playbook and stay ahead of the meta
- Developing countermeasures and pre-set responses/protocols (aka anti-stratting) against their opponents by analyzing their strategies and patterns - notably, their Attacking and Defending setups at the start of each round

The Mapping Tool is where players and coaches can formulate new strategies and set plays and can be accessed using any of the three paths - Creating a New File, Loading a File, and Analyzing a Video. The documentation below offers a detailed explanation of my Mapping Tool’s capabilities, includes step-by-step instructions for each path, and dives deeper into the unique features throughout my project. 

My project assists teams with anti-stratting their opponents by detecting the Attacking and Defending agents selected by the User and collecting their locations at the start of each round in a match footage uploaded by the User. After video analysis completes, they can verify the detection accuracy and download CSV files describing the agents' locations (coordinates and map-specific callouts) for each round in the entire match. With this data, players and coaches can perform statistical analysis to identify patterns in their opponents' Attacking or Defending setups to prepare and gain an advantage over their opponents. More explanation about the importance of data analytics in Valorant and my tool's benefits can be found in "**[How my Project Pairs with Data Analytics](#how-my-project-pairs-with-data-analytics)**".

If you are new to Valorant, I recommend starting with the "**[Quick Overview of a Valorant Match](#quick-overview-of-a-valorant-match)**" section to gain some background knowledge before progressing into the documentation.

For a more in-depth understanding of the video analysis or the data collection, I've included dedicated sections that dives into the difficulties and trade-offs for the **[computer vision](#computer-vision-details)** and **[data collection](#collecting-data---coordinates-and-map-callouts)** utilized in this project.

I hope you enjoy using my Mapping Tool!

> [!TIP]
> 
> Any new features/changes for Version 2.0 are identified with green text or green and purple blocks

---

## **Version 2.0**

In this update, I focused on:

- Enhancing the accuracy of detecting and determining relative positioning of the Attacking and Defending agents during video analysis
- Collecting and organizing data related to each agent’s and agent ability’s location (coordinates and callouts) for each analyzed round/game file
- Improving User experience across all the game states
- Updating assets to the most recent Valorant Patch (Patch 9.05)


After watching more Valorant tournaments and specifically paying extra attention to the minimaps, I realized that the tournaments within the same region and across other regions often used different sized minimaps. This varied enough that I found my original version’s video analysis lacking in one of its goals: finding the relative position of the scanned agents. In addition, because of the spacing between the minimap’s border and the screenshot’s edges also differed depending on the minimap’s size, a simple scalar could not accurately calculate the relative positions.

> [!TIP]
> 
> Deeper explanations for the new features and changes are marked in the Documentation and Computer Vision Details section below with green text or green and purple blocks

### **New Features**
- During video analysis, Attacking agents can now be selected and detected, and their locations will be recorded.
- Between the game state for choosing which video, map, and agents to analyze and the game state for choosing where to save the analyzed rounds, an additional game state (Map Boundaries) has been added. This new game state allows Users to adjust the size of a bounding box around the border of the minimap of the video’s first round’s screenshot to improve template matching and relative location determination.
- Map-specific callouts (short, qualitative labels describing specific areas on a map) have been added. Every file, whether created by analyzing a video or by the Users themselves, can track these callouts for each agent and agent’s ability.
- Entire folders in the Directories Page can be analyzed, which will download a new folder containing 4 CSV files and the map template PNG(s). The Attackers and the Defenders will each have two CSV files describing the agents’ positions through coordinates relative to the map template PNG and map-specific callouts.
- Downloading files as PDFs will include map-specific callouts for the agents and the abilities found within them.


### **Improvements**
- Documentation
  - Changed the introduction of my project to be more succinct and clarified the benefits my project has to offer the Valorant Esports scene
  - Replaced some pictures with GIFs
- Video Analysis
  - Previous map masks included a buffer space between the screenshots’ edges and the minimaps’ borders. New map masks have been created and added with the screenshots' edges flushed with the minimaps’ borders so that when scaled, they will properly fit the analyzed rounds’ screenshots’ minimaps.
  - For the best accuracy, separate Attacking and Defending map masks have been created and added

- UI
  - The white border created from selecting an agent or agent ability is replaced by a translucent, gray cover.
  - To adjust for the growing agent pool, the agent table in the Mapping Tool is now dynamic with top and bottom arrows to move between different rows of agents.
  - The hover and selection color for buttons is changed from light blue to dark gray.
  - To prevent text from running off the screen and allow Users to still read file, folder, and video names, read-only text boxes that can scroll are implemented in the Mapping Tool, Directories page, and when choosing the video to analyze.

### **Updated Assets related to Valorant Patches (up to Patch 9.05)**

- Outdated map templates are replaced with their most current ones, and any missing maps (including Abyss) have been added
- New agents and their abilities (including Vyse) have been added

---

## **Table of Contents**

- **[Version 2.0 Notes](#version-20)**
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
- **[Collecting Data - Coordinates and Map Callouts](#collecting-data---coordinates-and-map-callouts)**
  - **[Creating the Map Callouts](#creating-the-map-callouts)**
  - **[Balancing Specificity and Clarity](#balancing-specificity-and-clarity)**
  - **[How my Project Pairs with Data Analytics](#how-my-project-pairs-with-data-analytics)**
 
---

## **Quick Overview of a Valorant Match**

A Valorant match features two teams, each consisting of five players. Before the match, one map is selected either randomly or by mutual agreement between the two teams. Players then choose their agents (characters with unique abilities, such as flash-bangs or smokescreens). The game currently boasts 25 unique agents (Patch 9.05), with the rule that no agent can be chosen twice within the same team.

Teams are initially designated as either Attackers or Defenders. The Attackers' goal is to plant a bomb-like-device called the Spike at one of the specified bomb sites and ensure it detonates, or alternatively, they can win the round by eliminating the Defending team. The Defenders aim to thwart this plan either by neutralizing all Attackers, running out the round's 100-second timer, or, if the Spike is planted, by defusing it before it explodes.

Matches in Valorant are segmented into rounds, each lasting approximately 100 seconds. Victory is achieved by the first team to win 13 of these rounds. The match is divided into two halves, with teams swapping roles (Attackers becoming Defenders and Defenders becoming Attackers) after the first 12 rounds. In cases where the score is tied 12-12, the match enters an overtime phase, requiring a team to secure a two-round lead to clinch victory.

---

## **Documentation**

From the Main Menu screen, Users can select three different paths to access the Mapping Tool:
- **[Creating a New File](#creating-a-new-file)**
- **[Loading a File](#loading-a-file)**
- **[Analyzing a Video](#analyzing-a-video)**

Each path contains step-by-step directions to successfully reach the Mapping Tool.

<p align="middle">
  <img width="600" alt="main_menu_screen" src="https://github.com/WesleyJWu/Valorant-Strategy-Mapping-Tool/assets/112910934/2de366d7-0ac0-4885-9d06-1db26ed64579">
</p>

### **Mapping Tool**

Users are provided an intuitive, user-friendly interface to accurately place agents and their abilities onto any Valorant map to help them formulate and refine new strategies as Attackers or Defenders. To reduce clutter and improve visibility, the agent table will only contain two rows of agents ordered by alphabetical order and only the 5 most recently selected agents' abilities will be shown.

> [!TIP]
> To see and select the other agents, Users can use the arrows above or below the agent table to view the previous or next agent row.

Attackers and Defenders are represented by red and green background colors, respectively, and Users can switch teams when selecting the agents and abilities on the toolbar. This will not change the preexisting agents' and abilities' teams.
 
Additional key features include:

- Taking notes with dynamic scrolling
- Saving the agents, abilities, their coordinates, and notes into a file
- Downloading and exporting the file as a PDF, which includes:
  - A screenshot of the agents and abilities on the map in the Mapping Tool
  - The analyzed round's screenshot (if applicable)
  - User's notes
  - List of Attacking and Defending agents ${\textsf{\color{lightGreen}with map callouts}}$
  - List of Attacking and Defending abilities ${\textsf{\color{lightGreen}with map callouts}}$

<p align="middle">
  <img width="700" alt="Mapping_Tool_GIF" src="https://github.com/user-attachments/assets/3d5bbd1c-3f52-4087-b8c0-18734e33a2e3">
  <img width="500" alt="Mid-Round_PDF_JPG" src="https://github.com/user-attachments/assets/c4c9d40d-551a-431c-893f-f38ec64df8c5">
</p>

### **Creating a New File**

Users can easily create a new file from the Main Menu or within the Mapping Tool. Users will need to name the file and select their desired map, before moving to the Directories Page to choose the appropriate folder (or create a new folder) to save the file. After saving to a folder, they will move to the Mapping Tool.

Other key features within the Directories Page when saving a new file include:
- Modifying the name and chosen map of the new file
- Left-clicking on any folder to enter it and reveal the files it contains
  - An option will appear to return to the parent folder
- Right-clicking on a file to show:
  - File name
  - Associated map
  - Creation date
  - Last viewed date
- ${\textsf{\color{lightGreen}Right-clicking on a folder to show:}}$
  - ${\textsf{\color{lightGreen}Folder name}}$
  - ${\textsf{\color{lightGreen}Option to "Analyze Folder"}}$

> [!TIP]
> 
> Analyzing a folder will download:
>  - Map template PNG(s)
>  - 4 CSV files describing agents' locations with file names as row headers and agent names found in the files as column headers:
>    - 2 CSV files detailing Attacking agents' positions, either with coordinates relative to the map template PNG or with map callouts
>    - 2 CSV files detailing Defending agents' positions, either with coordinates relative to the map template PNG or with map callouts

- Option to delete the right-clicked file or folder

<p align="middle">
  <img width="700" alt="New_File_GIF" src="https://github.com/user-attachments/assets/b70bd67c-b2d2-4e56-b5ca-76d580c83d95">
</p>

### **Loading a File**

Users can load an existing file from the Main Menu or within the Mapping Tool. Loading a file will move Users to the Directories Page where Users can open a file by left clicking on it. Once a file is opened, Users are taken to the Mapping Tool, where the map and notes section are automatically prepopulated with agents, abilities, and notes to match any previously saved progress.

Other key features within the Directories Page when loading a file include:
- Left-clicking on any folder to enter it and reveal the files it contains
  - An option will appear to return to the parent folder
- Right-clicking on a file to show:
  - File name
  - Associated map
  - Creation date
  - Last viewed date
- ${\textsf{\color{lightGreen}Right-clicking on a folder to show:}}$
  - ${\textsf{\color{lightGreen}Folder name}}$
  - ${\textsf{\color{lightGreen}Option to "Analyze Folder"}}$

> [!TIP]
> 
> Analyzing a folder will download:
>  - Map template PNG(s)
>  - 4 CSV files describing agents' locations with file names as row headers and agent names found in the files as column headers:
>    - 2 CSV files detailing Attacking agents' positions, either with coordinates relative to the map template PNG or with map callouts
>    - 2 CSV files detailing Defending agents' positions, either with coordinates relative to the map template PNG or with map callouts

- Option to delete the right-clicked file or folder

<p align="middle">
  <img width="700" alt="Load_File_GIF" src="https://github.com/user-attachments/assets/12d26c5b-12fb-4236-8f61-35de97aa8b89">
</p>

### **Analyzing a Video**

In a tactical game like Valorant, information is crucial for both the Attacking and Defending teams to understand where their opponents are located and predict their opponents' next move. For example, within each round, players on both teams often use abilities to probe and collect information to determine which bomb site is weaker to attack and plant the Spike on or, on the opposite side, determine if players need to rotate to reinforce a bomb site and fill in gaps in the defense. These macro and micro decisions ultimately win rounds and entire matches for teams.

Not only is it important for high caliber teams to devise new attacking tactics and defensive setups, but it is just as crucial to review and dissect their opponents' strategies to recognize patterns and weaknesses. Similar to scouting reports in other professional sports, like football and basketball, these detailed analyses offer unique insights on what teams should expect. For example, recognizing their opponents’ commonly used defensive setups can help the team captain or in-game-leader choose the weaker bomb site to attack, massively raising the odds of winning that round.

All teams already review and take notes on their opponents' previous matches. My projects' video analysis helps find their opponents' starting setups faster, improving efficiency and allowing teams to spend more time devising new strategies or watch more past matches played by their opponents.

#### ***What Does my Computer Vision Algorithm Detect?*** 

The video analysis was built on footage sourced from recordings of live Valorant tournaments and focuses on two regions of interest:

- The minimap in the upper left corner
- The round clock in the upper middle

Because the footage is provided for the spectators’ eyes, the minimap shows the positions of both the Attacking and Defending agents relative to the map in play.

My algorithm uses computer vision, specifically template matching, to:

1. Capture screenshots at the start of each round, which is when the round clock in the video resets to 1 minute and 39 seconds
2. Find the agents and their locations in each screenshot’s minimap, after the video has ended and all the screenshots are gathered

The agents' locations will then be converted to their relative positions in the Mapping Tool’s map, before being added to a new file. There will be a new file for each round in the video, and all the files will be placed in a new folder. 

More information about my computer vision algorithm can be found in "**[Computer Vision Details](#computer-vision-details)**".

<p align="middle">
  <img width="600" src="https://github.com/WesleyJWu/Valorant-Strategy-Mapping-Tool/assets/112910934/baad5982-26e3-4355-a410-981c0e8af042" alt="starting_round_screenshot">
  <img width="300" src="https://github.com/WesleyJWu/Valorant-Strategy-Mapping-Tool/assets/112910934/b7759f80-dd68-45f0-a2cb-6f945ad354a4" alt="minimap_screenshot">
</p>

> [!IMPORTANT]
> <h3> Calculate Relative Positioning </h3>
>
> Prior to video analysis, Users are asked to adjust a Bounding Box around the edges of the minimap to gather:
> 
> - The dimensions of the screenshot’s minimap
> - The spacing between the minimap’s edges and the screenshot’s edges (the buffer zone)
> 
> The dimensions and buffer zones of all the map templates used by the Mapping Tool have already been calculated and hard-coded into this project.
> 
> During video analysis, after my program detects the agent and determines their coordinates in the screenshot, it will:
> 
> 1. Subtract the coordinates by the screenshot’s buffer zone
>     - The result is the location of the agent if the origin (0,0) and the axes started at the top-left of the minimap’s bounding box.
> 2. Divide the result by the screenshot’s minimap’s dimensions to calculate the normalization.
> 3. Multiply the normalization by the map template’s dimensions, which as a reminder do not include the buffer zone.
> 4. Add the map template’s buffer zone to the result to retrieve the relative coordinates for the Mapping Tool's map.
> 5. Record the relative position into the file.


#### ***Instructions to Analyze a Video***

Users can only analyze a video from the Main Menu screen. Prior to analysis, the Users need to select a video file in MP4 format from their computer, choose the appropriate map, and choose the Attacking and Defending agents to detect for.

> [!IMPORTANT]
>
> After these initial selections, Users are shown the screenshot taken from the video's first round that contains the round's minimap. To improve template matching and relative location calculations, they should adjust the Bounding Box's size so that the Bounding Box is barely touching the left-most, top-most, right-most, and bottom-most edges of the minimap.

After clicking Next, Users are then guided to the Directories Page, where they will need to choose the save location for the new folder and files. 

<p align="middle">
  <img width="700" alt="Analyze_VOD_Map_Boundaries_GIF" src="https://github.com/user-attachments/assets/3047487b-09f0-464b-8290-6261b40b6902">
</p>

The rest of the video analysis starts once the Users select the “Save” button in the Directories Page. Once the analysis is complete and the folder and its associated files are generated, the Users may now open the new folder and select any of its files to view and verify detection and position accuracy in the Mapping Tool. These files will prepopulate the Attacking and Defending agents onto the map in the Mapping Tool and attach the round screenshot in the toolbar for side-by-side comparison. Then the Users can enter the Directories Page and select the option to "Analyze Folder" to download the map template PNG(s) and 4 CSV files describing the detected Attacking and Defending agents' locations with coordinates and map callouts.

<p align="middle">
  <img width="700" alt="Loading_Analyzed_Round_GIF" src="https://github.com/user-attachments/assets/640523dd-1d60-4749-b358-34193acc12d9">
</p>

<p align="middle">
  <img width="700" alt="Analyze_Folder" src="https://github.com/user-attachments/assets/6b5d88df-1583-43a4-b298-d5eb30735a2c">
</p>

<p align="middle">
  <img width="700" alt="download_folder" src="https://github.com/user-attachments/assets/f94bc807-02d5-4f28-bcea-a2187ce0dfc3">
</p>

<h3 align="center">
  <a href="https://github.com/user-attachments/files/17200793/DEF_callouts.csv">Ex: DEF_callouts.csv</a>
</h3>

---

## **Computer Vision Details**

A brief overview of my computer vision algorithm was provided earlier in "**[What Does my Computer Vision Algorithm Detect?](#what-does-my-computer-vision-algorithm-detect)**".

To elaborate further, my template matching algorithm used the Normalized Squared Difference method in the OpenCV python library, where the template image systematically slides over the source image similar to 2D convolution. For each position, it calculates the normalized squared difference between the template and the corresponding region in the source image. The resulting output is a grayscale image where each pixel's intensity reflects this squared difference. Contrary to other methods like Cross-Correlation and Correlation Coefficient, lower values (darker areas) in this resulting image indicate a higher similarity between the template and the source region. Thus, the darkest point in the resulting image highlights the area where the template and the source image align most closely in terms of structure and intensity.

In this section, I dive deeper into the obstacles with analyzing a video, optimizations with template matching, and trying feature detection, description, and matching to detect the agents.

### **Obstacles with Analyzing a Video**

The agents in the screenshot’s minimap are only around 25 x 30 pixels and are often overlapping each other, presenting significant challenges in finding an effective computer vision algorithm for accurate detection. After **[experimenting with several other computer vision techniques](#attempting-feature-detection-description-and-matching)**, template matching offered the most accurate results in detecting the agents.

Although template matching proved to be more accurate compared to other algorithms, it still encountered some issues. To effectively match the miniature agents in the screenshot’s minimap, template matching necessitates a comparably small template image. A small template, due to its limited number of pixels, provides less feature information, which hinders the algorithm's ability to locate an accurate match, for example, when agents overlap. Additionally, the reduced pixel count in a small template heightens its sensitivity to noise and minor variations, resulting in a few false positives and difficulties in finding the correct match, particularly when some agents look similar at such a small scale. Using a strict threshold level could also not consistently and accurately separate good and bad matches.

### **Optimizations with Template Matching to Detect Agents**

To improve the accuracy of detecting agents in the screenshot’s minimap, the computer vision algorithm incorporates several masks to filter out irrelevant elements before performing template matching.

By prompting Users to select the map in advance, the algorithm can use a team map-specific mask to remove extraneous background elements and isolate the half of the map where the team can be found prior to the start of each round. To better isolate both the Attacking and Defending agents effectively, up to five color masks are also applied:

> [!IMPORTANT]
> 
> **Team Map-Specific Masks**
> 
> - Before each round starts, spawn barriers are placed to prevent teams from reaching the middle of the map and are only removed at the start of the round. Thus, the program knows which half of the map the analyzed team will be located.
> - Due to their varying sizes, the minimaps are also rarely at the center of their screenshots.
> - All the team map-specific masks have their buffer zones removed.
> - During video analysis, these masks are scaled to be the same dimensions as the screenshot’s minimap.
> - A numpy array with the color black is created with the same size as the screenshot, and the scaled mask is placed in the same location as the minimap. Thus, when masking is performed between the screenshot and the combined numpy array and map mask, the map mask matches the size and location of the minimap.

5 Additional Color Masks:
- A mask to include red or green areas, depending on the team being scanned for
- A mask to separate out the gray areas, representing empty locations on the minimap
- A mask to exclude the yellow areas, indicating the empty parts of the bomb-sites
- A mask to remove red or green areas, corresponding to the opposing team
- A mask to eliminate a lighter shade of red or green, specifying the analyzed team's vision range, their abilities found in the screenshot, and the spawn barriers

Each mask undergoes additional processing, including opening, closing, dilations, and erosions, to refine the masks and produce a final image that exclusively highlights the Attacking or Defending agents. These optimizations significantly reduce the likelihood of false positive matches and improves the detection accuracy of the template matching.

### **Attempting Feature Detection, Description, and Matching**

In my attempts to identify the agents in the screenshot’s minimap, I initially explored various methods combining feature detection, description, and matching. 

- Using SIFT (Scale-Invariant Feature Transform):
  - I first tried applying SIFT (rotation invariant and scale invariant) for feature detection and description, and then paired it with a Brute Force Matcher or a FLANN (Fast Library for Approximate Nearest Neighbors) Based Matcher for feature matching.
- Using ORB (Oriented FAST and Rotated BRIEF):
  - I switched to ORB, which is faster than SIFT, for both detection and description, and combined it with a Brute Force Matcher or a FLANN Based Matcher for feature matching. 

I hoped that by experimenting with some of the most common and well-documented algorithms for feature detection, description, and matching, I could more seamlessly detect the agents in the screenshot’s minimap. However, none of these combinations of computer vision techniques were as consistent and accurate as template matching for this project. The agents’ small size likely impeded the algorithms' abilities to detect and describe enough features for effective matching.



---

> [!IMPORTANT]
>
> ## **Collecting Data - Coordinates and Map Callouts**
>
> ### **Creating the Map Callouts**
>
> I created copies of all 11 map templates (Patch 9.05) and used anywhere from around 30 - 50 unique RGB colors to color in different areas of the maps to describe certain locations. The entire map had to be colored and given callouts. Then, I created a color dictionary for each map to relate the unique RGB colors to the distinctive callouts describing those locations and saved them into JSON files.
>
> To retrieve the callout for an agent's location, the program will first use the agent's center coordinates relative to the map template to find the RGB value at the same location in the colored map copy. Then, it will load the JSON file for that map and fetch the callout directly tied to that color. If that RGB value is not found, then the program will check the agents' midleft, midtop, midright, and midbottom coordinates in that order. If none of those are found, then the callout for the agent's position will be “Off-Map”.
>
> ### **Balancing Specificity and Clarity**
>
> When any player, casual or professional, plays a Valorant game, they will see callouts on their minimap that describe large, common areas like A Site or B Lobby. Some of these large areas have been split into smaller portions by the community, with each piece receiving a callout like "A Generator" or "A Dice". The more callouts that are specific and cover smaller areas, the more intuitive it is to understand where an agent or their utility is located. For example, on the map Ascent, saying the Attackers planted the Spike at "A Dice" (a tiny portion of "A Site") provides significantly more information than saying they planted the Spike on "A Site".
>
> However, the trouble I faced when trying to create my callout dictionaries that could precisely describe different bits of entire maps was a lack of community-accepted callouts. I found multiple disagreements between reddit posts, Youtubers, and friend groups on how they named certain segments of the map. That being said, I understand many of the benefits in not providing a detailed list of all the position names for every map because it encourages discussion, collaboration, and creativity among the community and fanbase. Finding a lack of consensus repeatedly for different components of the map, I decided to accept less specificity in exchange for clarity for my map callouts. I didn't want to create new callouts that aren't accepted by the general player-base or confuse any Users. In addition, because map callouts are retrieved for all the agents and abilities when downloading the PDF in the Mapping Tool, I needed to have my color dictionary cover the entire map. To address these different concerns, I used callouts that spread over larger areas to create the callout dictionaries and colored maps, especially for many of the newly released maps.
>
> I also understand that with fewer callouts that cover larger areas, the data analytics cannot uncover as many patterns and differences for Attacking and Defending setups. Therefore, I truly believe if a professional player or team wants to use this project and resource to its greatest potential, they will need to add or change parts of my colored maps and colored dictionaries to align with their preferences and their callout protocols. If anyone needs assistance with this, I would be happy to help. 
>
> ### **How my Project Pairs with Data Analytics**
>
> All professional Valorant teams already review their opponents' previous matches and in some form or another, take in data and analyze it. Whether that's determining the frequency of the Defending team stacking one site with four players during low economic rounds or counting the number of times two compatible agents play together on the same site, teams look for patterns in their opponents' tactics to create counter strategies and anti-strat.
>
> Especially in tournaments, a team only has a limited amount of time to prepare against their opponents. Instead of watching a past match and typing into Excel where their opponents start at the beginning of each round, a player or coach can upload the video into my project, and while my project scans through all the rounds, they can design new protocols to deepen their playbook or even watch a different match played by their opponents. My project can streamline the process of anti-stratting, for example, their opponents' Defending setups. With my project, players and coaches can be more efficient with their time, and once the video analysis completes, they can quickly verify if the program correctly detected and located the selected agents by looking at the game files in the Mapping Tool.
>
> After video analysis, they can even analyze the match folder and download CSV files describing the agents' locations through coordinates and map callouts per round. With this raw data, they can search for patterns in a player's playstyle or discover trends in which site the Defending team likes to retake. In addition, they could create heat maps for the Defending agents across all the rounds to see the gaps in their setups or calculate the probability of them stacking and pushing A Lobby. With video analysis, my project offers data that players and coaches can scrutinize and use however they see fit to help them win their next match and hopefully lift a trophy. 






















