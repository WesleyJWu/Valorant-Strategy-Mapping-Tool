from fpdf import FPDF
import os
import platformdirs

def create_and_download_PDF(file_name, map_name, edited_map_screenshot_path, list_of_agents_on_map, list_of_utility_on_map, notes = "", screenshot_from_video_path = None):
    PAGE_WIDTH = 210
    STARTING_Y_FOR_IMAGE = 32
    WIDTH_UIMAP = PAGE_WIDTH/2 - 10
    text_color = {"ATK": (255,0,0), "DEF": (0,128,0)}
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=20)
    pdf.ln(5)

    # Adding the Title
    pdf.cell(0, 7, f"{file_name} - Map: {map_name}", 0, align="C")
    pdf.ln(2)
    pdf.set_font_size(15)
    pdf.set_text_color(0,0,0)
    pdf.cell(PAGE_WIDTH/2 - 8, 7, f"", 0, 1, align="C")
    pdf.cell(0, 5, "", 0, 1)
    pdf.cell(PAGE_WIDTH/2 - 8, 7, "",)

    # Adding the Agent Tracker Table
    pdf.cell(PAGE_WIDTH/2 - 10, 7, "Agent Tracker:", 0, 1, align="L")
    startingX = WIDTH_UIMAP + 10 + 11
    startingY = pdf.get_y() + 1
    pdf.set_xy(startingX, startingY)
    for index, agentOnMap in enumerate(list_of_agents_on_map, 1):
        if index!= 1:
            pdf.set_font("Times", size=10)
            r, g, b = text_color[agentOnMap[0]]
            pdf.set_text_color(r, g, b)
            pdf.cell((PAGE_WIDTH/2 - 13)/4, 5, "   " + agentOnMap[0], "L, B")
            pdf.cell((PAGE_WIDTH/2 - 13)/4, 5, "    " + agentOnMap[1], "B")
            pdf.cell((PAGE_WIDTH/2 - 13)/4 + 12, 5, "    " + agentOnMap[2], "R, B")
            pdf.set_xy(startingX, startingY + 5 * index)
        else:
            pdf.set_font("Times", "B", size=11)
            pdf.set_text_color(0,0,0)
            pdf.cell((PAGE_WIDTH/2 - 13)/4, 5, agentOnMap[0], "B, L, T")
            pdf.cell((PAGE_WIDTH/2 - 13)/4, 5, agentOnMap[1], "T, B")
            pdf.cell((PAGE_WIDTH/2 - 13)/4 + 12, 5, agentOnMap[2], "T, R, B")
            pdf.set_xy(startingX, startingY + 5 * index)
            pdf.set_font("Times", size=10)

    # Adding the Utility Tracker Table
    pdf.set_text_color(0,0,0)
    pdf.ln(5)
    pdf.set_font_size(15)
    pdf.cell(PAGE_WIDTH/2 - 8)
    pdf.cell(PAGE_WIDTH/2 - 10, 7, "Ability/Utility Tracker:", 0, 1, align="L")
    startingX = WIDTH_UIMAP + 10 + 11
    startingY = pdf.get_y() + 1
    pdf.set_xy(startingX, startingY)
    for index, utilityOnMap in enumerate(list_of_utility_on_map, 1):
        if index!= 1:
            pdf.set_font("Times", size=10)
            r, g, b = text_color[utilityOnMap[0]]
            pdf.set_text_color(r, g, b)
            pdf.cell((PAGE_WIDTH/2 - 16)/4, 5, "   " + utilityOnMap[0], "L, B")
            pdf.cell((PAGE_WIDTH/2)/3, 5, "    " + utilityOnMap[1], "B")
            pdf.cell((PAGE_WIDTH/2 - 13)/4 + 12, 5, "    " + utilityOnMap[2], " R, B")
            pdf.set_xy(startingX, startingY + 5 * index)
        else:
            pdf.set_font("Times", "B", size=11)
            pdf.set_text_color(0,0,0)
            pdf.cell((PAGE_WIDTH/2 - 16)/4, 5, utilityOnMap[0], "B, L, T")
            pdf.cell((PAGE_WIDTH/2)/3, 5, utilityOnMap[1], "T, B")
            pdf.cell((PAGE_WIDTH/2 - 13)/4 + 12, 5, utilityOnMap[2], "T, R, B")
            pdf.set_xy(startingX, startingY + 5 * index)
            pdf.set_font("Times", size=10)

    #  Adding the Notes
    pdf.set_text_color(0,0,0)
    pdf.ln(4)
    pdf.set_font_size(15)
    pdf.cell(PAGE_WIDTH/2 - 7)
    pdf.cell(PAGE_WIDTH/2 - 10, 7, "Notes:", 0, 2, align="L")
    pdf.ln(1)
    pdf.set_font_size(10)
    pdf.set_x(WIDTH_UIMAP + 21)
    pdf.set_draw_color(0,0,255)
    pdf.multi_cell(PAGE_WIDTH/2 - 23, 5, notes, 1, "L")

    # Adding the Edited Map Screenshot
    pdf.image(edited_map_screenshot_path, 10, STARTING_Y_FOR_IMAGE, WIDTH_UIMAP)

    if screenshot_from_video_path != None:
        # Adding the screenshot taken from the video
        pdf.image(screenshot_from_video_path, 10, STARTING_Y_FOR_IMAGE + WIDTH_UIMAP + 5, WIDTH_UIMAP, WIDTH_UIMAP)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.4)
        pdf.rect(10, STARTING_Y_FOR_IMAGE + WIDTH_UIMAP + 5, WIDTH_UIMAP, WIDTH_UIMAP, "D")
    
    # Download the PDF to the Downloads Folder
    downloads_folder_path = platformdirs.user_downloads_path()
    pdf_file_path = os.path.join(downloads_folder_path, f"{file_name}.pdf")
    # If the path already exists, modify the PDF name
    counter = 1
    while os.path.exists(pdf_file_path):
        pdf_file_path = os.path.join(downloads_folder_path, f"{file_name} ({counter}).pdf")
        counter += 1
    pdf.output(pdf_file_path, "F")

    # Delete the edited_map_screenshot
    os.remove(edited_map_screenshot_path)
