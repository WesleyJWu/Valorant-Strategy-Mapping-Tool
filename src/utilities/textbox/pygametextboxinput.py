"""
Copyright 2021, Jack7511, All Rights Reserved.

Borrowed from https://github.com/Jack7511/pygame-textbox-input under the MIT License.

Some part of code is Borrowed from https://github.com/Nearoo/pygame-text-input under the MIT license.
"""

import os.path

from math import ceil
import pygame
import pygame.locals as pl

pygame.init()
pygame.font.init()
pygame.scrap.init()
pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

class TextInputBox:
    """
    This Class lets you write text at the blinking cursor.
    Wraps text to the next line if it exceeds the max_width.
    Enter, Delete, Home, End, Page Up and Page Down key works.
    Cursor can be moved using arrow keys or click on character to jump directly.
    Scrolling using mouse or scroll bar.
    Text Selection using mouse.
    Cut, Copy, Paste and Select all using shortcut.
    """
    def __init__(
            self,
            x = 0,
            y = 0,
            initial_string="",
            font_family="",
            font_size=35,
            align_text="left",
            max_width=650,
            max_height=450,
            antialias=True,
            text_color=(255, 255, 255),
            cursor_color=(255, 255, 255),
            selection_color=(51, 144, 255),
            scroll_bar_color = (100, 100, 100),
            max_string_length=float('inf'),
            password=False):
        """
        :param x: x coordinate
        :param y: y coordinate
        :param initial_string: Initial text to be displayed
        :param font_family: name or list of names for font (see pygame.font.match_font for precise format)
        :param font_size:  Size of font in pixels
        :param align_text: It aligns all lines by "left" or "center"
        :param max_width: Width of text box
        :param max_height: Height of text box
        :param antialias: Determines if antialias is applied to font (uses more processing power)
        :param text_color: Color of text (duh)
        :param cursor_color: Color of cursor
        :param selection_color: Color of selection of text
        :param scroll_bar_color: Color of scroll bar
        :param max_string_length: Allowed length of text
        """

        # Text related vars:
        self.x = x
        self.y = y
        self.antialias = antialias
        self.text_color = text_color
        self.font_size = font_size
        self.align_text = align_text
        self.max_width = max_width
        self.max_height = max_height
        self.selection_color = selection_color
        self.scroll_bar_color = scroll_bar_color
        self.max_string_length = max_string_length
        self.password = password
        self.input_string = initial_string  # Inputted text
        self.wrapped_lines = []
        self.require_wrap = False
        self.selected_text = [False, [0, 0, 0], [[0, 0], [0, 0], [0, 0]]]
        # 1st element represents if text is selected
        # 2nd element contains list of initial cursor_pos, cursor_x_pos, cursor_y_pos
        # 3rd element contains starting and ending pos of selected text in cursor_pos, cursor_x_pos, cursor_y_pos
        self.text_surface = [] # Stores rendered lines of wrapped_lines
        self.content = [0, 0] # Refer function visible_content
        
        if not os.path.isfile(font_family):
            font_family = pygame.font.match_font(font_family)

        self.font_object = pygame.font.Font(font_family, font_size)

        # Things cursor:
        self.cursor_surface = pygame.Surface((int(self.font_size / 20 + 1), self.font_object.size('a')[1]))
        self.cursor_surface.fill(cursor_color)
        self.cursor_position = len(initial_string)  # Inside text
        self.cursor_visible = True  # Switches every self.cursor_switch_ms ms
        self.cursor_switch_ms = 500  # /|\
        self.cursor_ms_counter = 0
        self.cursor_x_pos = 0 # Position of cursor at x index of wrapped_lines
        self.cursor_y_pos = 0 # Position of cursor at y index of wrapped_lines

        if self.max_width < self.font_size or self.max_height < self.font_size:
            raise ValueError("Width or Height too small")
        
        h = self.font_object.size('a')[1]
        self.text_rect = pygame.Rect(self.x, self.y, self.max_width, self.max_height)
        self.total_lines_possible = self.max_height // h
        self.scroll_bar = pygame.Rect(self.x + self.max_width, self.y, 7, 0)
        self.scroll_bar_selected = False

        self.clock = pygame.time.Clock()

    def update(self, events, active=True):
        for event in events:
            if event.type == pygame.KEYDOWN and not active:
                if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self._process_ctrlc()

            elif event.type == pygame.KEYDOWN and active:
                self.cursor_visible = True  # So the user sees where he writes
                self._process_keydown(event)

                string = self.input_string
                if self.password:
                    string = "*" * len(self.input_string)
                
                # Wraps the text and store lines in wrapped_lines
                # Then render it and store it in text_surface
                # So we dont have to render every frame unless any key is pressed
                if self.require_wrap:
                    
                    self.wrap_text(string)
                
            if event.type == pl.MOUSEBUTTONDOWN:
                if self.scroll_bar.collidepoint(event.pos):
                    # Scroll bar Selected
                    self.scroll_bar_selected = True
                    self.scroll_bar_selected_y = event.pos[1] - self.scroll_bar.y
                
                if self.text_rect.collidepoint(event.pos):
                    if event.button == 4:
                        # Scroll Up
                        self._process_scrollup()
                    
                    elif event.button == 5:
                        # Scroll Down
                        self._process_scrolldown()
                    
                    elif event.button == 1:
                        self.put_cursor_at_cursor_pos()
                        self.selected_text = [True, [self.cursor_position, self.cursor_x_pos, self.cursor_y_pos], [[self.cursor_position, self.cursor_position], [self.cursor_x_pos, self.cursor_y_pos], [self.cursor_x_pos, self.cursor_y_pos]]]

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                if self.text_rect.collidepoint(pygame.mouse.get_pos()) and not self.scroll_bar_selected:
                    self.put_cursor_at_cursor_pos()
                    
                    self._process_selecttext()
                
            if self.scroll_bar_selected:
                # Scrolls content on moving cursor
                if pygame.mouse.get_pressed()[0]:
                    y = pygame.mouse.get_pos()[1] - self.scroll_bar_selected_y
                    self.scroll_bar.y = y

                    if y < self.y:
                        self.scroll_bar.y = self.y
                    
                    elif self.scroll_bar.bottom > self.max_height + self.y:
                        self.scroll_bar.bottom = self.max_height + self.y
                    
                    if self.scroll_bar.h > 10:
                        self.content[0] = self.scroll_bar.y - self.y
                    
                    else:
                        y = (self.scroll_bar.y - self.y)
                        self.content[0] = y * self.n

                        for i in self.remaining_n:
                            self.content[0] += y // i
                    
                    self.content[1] = len(self.wrapped_lines[:self.content[0] + self.total_lines_possible]) - 1
                    self._rerender()
                    
                else:
                    self.scroll_bar_selected = False
        
        if active:
            # Update self.cursor_visible
            self.cursor_ms_counter += self.clock.get_time()
            if self.cursor_ms_counter >= self.cursor_switch_ms:
                self.cursor_ms_counter %= self.cursor_switch_ms
                self.cursor_visible = not self.cursor_visible
        else:
            self.cursor_visible = False
        
        self.clock.tick()
        return False
    
    def _process_keydown(self, event):
        attrname = f'_process_'
        mods = pygame.key.get_mods()
        
        if mods & pygame.KMOD_CTRL:
            attrname += 'ctrl'
        if mods & pygame.KMOD_SHIFT:
            attrname += 'shift'

        keyname = pygame.key.name(event.key)
        if keyname in ['left ctrl', 'left shift', 'right ctrl', 'right shift']:
            keyname = ''
        keyname = keyname.replace(' ', '')

        attrname += keyname

        if hasattr(self, attrname):
            getattr(self, attrname)()
        else:
            self._process_other(event)
    

    def _process_backspace(self):
        if not self.selected_text[0]:
            self.input_string = (
                self.input_string[:max(self.cursor_position - 1, 0)]
                + self.input_string[self.cursor_position:]
            )
            # Subtract one from cursor_pos, but do not go below zero:
            self.cursor_position = max(self.cursor_position - 1, 0)
        
        else:
            self.input_string = (
                self.input_string[:self.selected_text[2][0][0]]
                + self.input_string[self.selected_text[2][0][1]:]
            )
            self.cursor_position = self.selected_text[2][0][0]
            self.clear_selection()
        
        self.require_wrap = True
    
    def _process_delete(self):
        if not self.selected_text[0]:
            self.input_string = (
                self.input_string[:self.cursor_position]
                + self.input_string[self.cursor_position + 1:]
            )
        
        else:
            self.input_string = (
                self.input_string[:self.selected_text[2][0][0]]
                + self.input_string[self.selected_text[2][0][1]:]
            )
            self.cursor_position = self.selected_text[2][0][0]
            self.clear_selection()
        
        self.require_wrap = True
    
    def _process_return(self):
        if self.password:
            return True
        
        if not self.selected_text[0]:
            self.input_string = self.input_string[:self.cursor_position] + '\n' + self.input_string[self.cursor_position:]
            self.cursor_position += 1
        else:
            self.input_string = self.input_string[:self.selected_text[2][0][0]] + '\n' + self.input_string[self.selected_text[2][0][1]:]
            self.cursor_position = self.selected_text[2][0][0] + 1
            self.clear_selection()
        
        self.require_wrap = True
    
    def _process_tab(self):
        if len(self.input_string) + 4 <= self.max_string_length:
            if not self.selected_text[0]:
                self.input_string = (
                    self.input_string[:self.cursor_position]
                    + "    "
                    + self.input_string[self.cursor_position:]
                )
                self.cursor_position += 4
            else:
                self.input_string = (
                    self.input_string[:self.selected_text[2][0][0]]
                    + "    " 
                    + self.input_string[self.selected_text[2][0][1]:]
                )
                self.cursor_position = self.selected_text[2][0][0] + 4
                self.clear_selection()
        
        self.require_wrap = True
    
    def _process_right(self, shiftright=False):
        if not self.selected_text[0] or shiftright:
            # Add one to cursor_pos, but do not exceed len(input_string)
            if len(self.input_string):
                self.cursor_position = min(self.cursor_position + 1, len(self.input_string))
            else:
                self.cursor_position = 0
        else:
            self.cursor_position = self.selected_text[2][0][1]
            self.clear_selection()
        
        self.cursor_pos_to_x_y()
        self.visible_content()
        self._rerender()

        self.require_wrap = False
    
    def _process_left(self, shiftleft=False):
        if not self.selected_text[0] or shiftleft:
            # Subtract one from cursor_pos, but do not go below zero:
            self.cursor_position = max(self.cursor_position - 1, 0)
        else:
            self.cursor_position = self.selected_text[2][0][0]
            self.clear_selection()
        
        self.cursor_pos_to_x_y()
        self.visible_content()
        self._rerender()

        self.require_wrap = False
    
    def _process_home(self):
        # Go to start of line
        if len(self.input_string):
            self.cursor_position -= len(self.wrapped_lines[self.cursor_y_pos][:self.cursor_x_pos])
            self.cursor_x_pos = 0
        else:
            self.cursor_position = 0
        self.clear_selection()

        self.require_wrap = False
    
    def _process_end(self):
        # Go to end of line
        if len(self.input_string):
            self.cursor_position += len(self.wrapped_lines[self.cursor_y_pos][self.cursor_x_pos:])
            self.cursor_x_pos = len(self.wrapped_lines[self.cursor_y_pos])
        else:
            self.cursor_position = len(self.input_string)
        self.clear_selection()

        self.require_wrap = False
    
    def _process_pageup(self):
        self.cursor_position = 0
        self.cursor_x_pos = 0
        self.cursor_y_pos = 0

        self.clear_selection()
        self.visible_content()
        self._rerender()

        self.require_wrap = False
    
    def _process_pagedown(self):
        self.cursor_position = len(self.input_string)
        self.cursor_x_pos = len(self.wrapped_lines[-1]) if len(self.wrapped_lines) else 0
        self.cursor_y_pos = max(0, len(self.wrapped_lines) - 1)

        self.clear_selection()
        self.visible_content()
        self._rerender()

        self.require_wrap = False

    def _process_up(self):
        # Subtract one from cursor_y_pos, but do not go below zero
        if self.cursor_y_pos:
            self.cursor_y_pos -= 1
            self.cursor_position -= self.cursor_x_pos

            ## Checking if there is '\n' or space at the end of upper line
            if self.input_string[self.cursor_position - 1] == '\n' or self.input_string[self.cursor_position - 1] == ' ':
                self.cursor_position -= 1
            
            self.cursor_x_pos = len(self.wrapped_lines[self.cursor_y_pos][:self.cursor_x_pos])
            self.cursor_position -= len(self.wrapped_lines[self.cursor_y_pos][self.cursor_x_pos:])
        
        if len(self.wrapped_lines):
            self.visible_content()
            self._rerender()
        
        self.clear_selection()

        self.require_wrap = False
    
    def _process_down(self):
        # Add one to cursor_y_pos, but do not exceed len(wrapped_lines) - 1
        if self.cursor_y_pos < len(self.wrapped_lines) - 1:
            self.cursor_y_pos += 1
            self.cursor_position += len(self.wrapped_lines[self.cursor_y_pos - 1][self.cursor_x_pos:])

            ## Checking if there is '\n' or space at the end of current line
            if self.input_string[self.cursor_position] == '\n' or self.input_string[self.cursor_position] == ' ':
                self.cursor_position += 1
            
            self.cursor_x_pos = len(self.wrapped_lines[self.cursor_y_pos][:self.cursor_x_pos])
            self.cursor_position += self.cursor_x_pos
        
        if len(self.wrapped_lines):
            self.visible_content()
            self._rerender()
        
        self.clear_selection()

        self.require_wrap = False

    def _process_other(self, event):
        eventunicode = event.unicode.replace('\r', '')
        if not len(eventunicode):
            self.require_wrap = False
            return None

        if len(self.input_string) + len(eventunicode) <= self.max_string_length:
            if not self.selected_text[0]:
                # If no special key is pressed, add unicode of key to input_string
                self.input_string = (
                    self.input_string[:self.cursor_position]
                    + eventunicode
                    + self.input_string[self.cursor_position:]
                )
                self.cursor_position += len(eventunicode)  # Some are empty, e.g. K_UP
            else:
                self.input_string = (
                    self.input_string[:self.selected_text[2][0][0]]
                    + eventunicode
                    + self.input_string[self.selected_text[2][0][1]:]
                )
                self.cursor_position = self.selected_text[2][0][0] + len(eventunicode)
                self.clear_selection()
            
            self.require_wrap = True
    
    def _process_ctrla(self):
        # Select all text
        self.cursor_position = len(self.input_string)
        self.cursor_x_pos = len(self.wrapped_lines[-1]) if len(self.wrapped_lines) else 0
        self.cursor_y_pos = max(0, len(self.wrapped_lines) - 1)
        
        if len(self.wrapped_lines):
            self.selected_text = [True, [0, 0, 0], [[0, len(self.input_string)], [0, 0], [len(self.wrapped_lines[-1]), max(len(self.wrapped_lines) - 1, 0)]]]
        
        self.require_wrap = False
    
    def _process_ctrlc(self):
        # Copy the text to clipboard
        if self.selected_text[0]:
            pygame.scrap.put("text/plain;charset=utf-8", bytes(self.input_string[self.selected_text[2][0][0]:self.selected_text[2][0][1]], 'utf-8'))
        
        self.require_wrap = False
    
    def _process_ctrlx(self):
        # Cut the selected text and copy to clipboard
        if self.selected_text[0]:
            pygame.scrap.put("text/plain;charset=utf-8", bytes(self.input_string[self.selected_text[2][0][0]:self.selected_text[2][0][1]], 'utf-8'))
        
            self.input_string = (
                    self.input_string[:self.selected_text[2][0][0]]
                    + self.input_string[self.selected_text[2][0][1]:]
                )
            self.cursor_position = self.selected_text[2][0][0]
            self.clear_selection()
        
        self.require_wrap = True
    
    def _process_ctrlv(self):
        # Copy the text from clipboard
        pasted_text = pygame.scrap.get("text/plain;charset=utf-8").decode()
        pasted_text = pasted_text.replace('\r', '')

        if len(self.input_string) + len(pasted_text) <= self.max_string_length:
            if not self.selected_text[0]:
                self.input_string = (
                    self.input_string[:self.cursor_position]
                    + pasted_text
                    + self.input_string[self.cursor_position:]
                )
                self.cursor_position = self.cursor_position + len(pasted_text)
            else:
                self.input_string = (
                    self.input_string[:self.selected_text[2][0][0]]
                    + pasted_text
                    + self.input_string[self.selected_text[2][0][1]:]
                )
                self.cursor_position = self.selected_text[2][0][0] + len(pasted_text)
                self.clear_selection()

        self.require_wrap = True
    
    def _process_shiftbackspace(self):
        self._process_backspace()
    
    def _process_shiftdelete(self):
        self._process_delete()
    
    def _process_shiftreturn(self):
        self._process_return()
    
    def _process_shifttab(self):
        self._process_tab()

    def _process_shiftright(self):
        if self.selected_text[0]:
            selectedtext_pos = self.selected_text[1]
        else:
            selectedtext_pos = [self.cursor_position, self.cursor_x_pos, self.cursor_y_pos]
        
        self._process_right(True)
        self.selected_text[1] = selectedtext_pos
        self._process_selecttext()
    
    def _process_shiftleft(self):
        if self.selected_text[0]:
            selectedtext_pos = self.selected_text[1]
        else:
            selectedtext_pos = [self.cursor_position, self.cursor_x_pos, self.cursor_y_pos]
        
        self._process_left(True)
        self.selected_text[1] = selectedtext_pos
        self._process_selecttext()
    
    def _process_shifthome(self):
        if self.selected_text[0]:
            selectedtext_pos = self.selected_text[1]
        else:
            selectedtext_pos = [self.cursor_position, self.cursor_x_pos, self.cursor_y_pos]
        
        self._process_home()
        self.selected_text[1] = selectedtext_pos
        self._process_selecttext()
    
    def _process_shiftend(self):
        if self.selected_text[0]:
            selectedtext_pos = self.selected_text[1]
        else:
            selectedtext_pos = [self.cursor_position, self.cursor_x_pos, self.cursor_y_pos]
        
        self._process_end()
        self.selected_text[1] = selectedtext_pos
        self._process_selecttext()
    
    def _process_shiftpageup(self):
        if self.selected_text[0]:
            selectedtext_pos = self.selected_text[1]
        else:
            selectedtext_pos = [self.cursor_position, self.cursor_x_pos, self.cursor_y_pos]
        
        self._process_pageup()
        self.selected_text[1] = selectedtext_pos
        self._process_selecttext()
    
    def _process_shiftpagedown(self):
        if self.selected_text[0]:
            selectedtext_pos = self.selected_text[1]
        else:
            selectedtext_pos = [self.cursor_position, self.cursor_x_pos, self.cursor_y_pos]
        
        self._process_pagedown()
        self.selected_text[1] = selectedtext_pos
        self._process_selecttext()

    def _process_shiftup(self):
        if self.selected_text[0]:
            selectedtext_pos = self.selected_text[1]
        else:
            selectedtext_pos = [self.cursor_position, self.cursor_x_pos, self.cursor_y_pos]
        
        self._process_up()
        self.selected_text[1] = selectedtext_pos
        self._process_selecttext()
    
    def _process_shiftdown(self):
        if self.selected_text[0]:
            selectedtext_pos = self.selected_text[1]
        else:
            selectedtext_pos = [self.cursor_position, self.cursor_x_pos, self.cursor_y_pos]
        
        self._process_down()
        self.selected_text[1] = selectedtext_pos
        self._process_selecttext()
    
    def _process_ctrlbackspace(self):
        cursor_pos = self.cursor_position
        self._process_ctrlleft()

        self.input_string = self.input_string[:self.cursor_position] + self.input_string[cursor_pos:]
        
        self.require_wrap = True
    
    def _process_ctrldelete(self):
        cursor_pos = self.cursor_position
        self._process_ctrlright()

        self.input_string = self.input_string[:cursor_pos] + self.input_string[self.cursor_position:]
        self.cursor_position = cursor_pos

        self.require_wrap = True

    def _process_ctrlhome(self):
        self._process_pageup()
    
    def _process_ctrlend(self):
        self._process_pagedown()
    
    def _process_ctrlreturn(self):
        self._process_return()
    
    def _process_ctrltab(self):
        self._process_tab()

    def _process_ctrlright(self):
        space = False

        while len(self.input_string) > self.cursor_position:
            self.cursor_position += 1

            if len(self.input_string) == self.cursor_position or self.input_string[self.cursor_position] == '\n' or self.input_string[self.cursor_position - 1] == '\n':
                break

            if self.input_string[self.cursor_position] == ' ':
                space = True
            
            if space and self.input_string[self.cursor_position] != ' ':
                break
        
        self.cursor_pos_to_x_y()
        self.visible_content()
        self._rerender()

        self.clear_selection()

        self.require_wrap = False

    def _process_ctrlleft(self):
        space = False

        while self.cursor_position > 0:
            self.cursor_position -= 1

            if not self.cursor_position or self.input_string[self.cursor_position] == '\n' or self.input_string[self.cursor_position - 1] == '\n':
                break

            if self.input_string[self.cursor_position - 1] == ' ' and self.input_string[self.cursor_position] != ' ':
                space = True

            if space and self.input_string[self.cursor_position] != ' ':
                break

        self.cursor_pos_to_x_y()
        self.visible_content()
        self._rerender()

        self.clear_selection()

        self.require_wrap = False
        
    def _process_ctrlshiftbackspace(self):
        self.require_wrap = False
    
    def _process_ctrlshiftdelete(self):
        self.require_wrap = False
    
    def _process_ctrlshifthome(self):
        self._process_shiftpageup()
    
    def _process_ctrlshiftend(self):
        self._process_shiftpagedown()

    def _process_ctrlshiftreturn(self):
        self.require_wrap = False
    
    def _process_ctrlshifttab(self):
        self.require_wrap = False

    def _process_ctrlshiftright(self):
        if self.selected_text[0]:
            selectedtext_pos = self.selected_text[1]
        else:
            selectedtext_pos = [self.cursor_position, self.cursor_x_pos, self.cursor_y_pos]
        
        self._process_ctrlright()
        self.selected_text[1] = selectedtext_pos
        self._process_selecttext()
    
    def _process_ctrlshiftleft(self):
        if self.selected_text[0]:
            selectedtext_pos = self.selected_text[1]
        else:
            selectedtext_pos = [self.cursor_position, self.cursor_x_pos, self.cursor_y_pos]
        
        self._process_ctrlleft()
        self.selected_text[1] = selectedtext_pos
        self._process_selecttext()

    def _process_ctrlshiftup(self):
        self._process_shiftup()
    
    def _process_ctrlshiftdown(self):
        self._process_shiftdown()

    def _process_selecttext(self):
        self.selected_text[0] = True
        
        if self.selected_text[1][0] < self.cursor_position:
            self.selected_text[2][0][1] = self.cursor_position
            self.selected_text[2][0][0] = self.selected_text[1][0]
            self.selected_text[2][2][0] = self.cursor_x_pos
            self.selected_text[2][2][1] = self.cursor_y_pos
            self.selected_text[2][1][0] = self.selected_text[1][1]
            self.selected_text[2][1][1] = self.selected_text[1][2]
        
        elif self.selected_text[1][0] > self.cursor_position:
            self.selected_text[2][0][0] = self.cursor_position
            self.selected_text[2][0][1] = self.selected_text[1][0]
            self.selected_text[2][1][0] = self.cursor_x_pos
            self.selected_text[2][1][1] = self.cursor_y_pos
            self.selected_text[2][2][0] = self.selected_text[1][1]
            self.selected_text[2][2][1] = self.selected_text[1][2]
        
        else:
            self.selected_text[0] = False
            self.selected_text[2][0][0] = self.cursor_position
            self.selected_text[2][0][1] = self.cursor_position
            self.selected_text[2][1][0] = self.cursor_x_pos
            self.selected_text[2][1][1] = self.cursor_y_pos
            self.selected_text[2][2][0] = self.cursor_x_pos
            self.selected_text[2][2][1] = self.cursor_y_pos

    def _process_scrollup(self):
        self.content[0] = max(0, self.content[0] - 1)
        self.content[1] = len(self.wrapped_lines[:self.content[0] + self.total_lines_possible]) - 1
        self.adjust_scrollbar()

        self._rerender()
    
    def _process_scrolldown(self):
        if len(self.wrapped_lines) >= self.total_lines_possible and not self.content[1] == len(self.wrapped_lines) - 1:
            self.content[0] += 1
        
        self.content[1] = len(self.wrapped_lines[:self.content[0] + self.total_lines_possible]) - 1
        self.adjust_scrollbar()

        self._rerender()

    def put_cursor_at_cursor_pos(self):
        # Put Cursor at the cursor pos
        self.cursor_position = 0
        self.cursor_x_pos = 0
        self.cursor_y_pos = self.content[0]
        
        for i in range(self.cursor_y_pos):
            self.cursor_position += len(self.wrapped_lines[i])
            if self.input_string[self.cursor_position] == '\n' or self.input_string[self.cursor_position] == ' ':
                self.cursor_position += 1
        
        pos = pygame.mouse.get_pos()
        x = pos[0] - self.x
        y = pos[1] - self.y
        line = min(len(self.wrapped_lines) - 1, y // self.font_object.size('a')[1], self.total_lines_possible - 1)
        characters_size = 0
        
        for i in range(line):
            self.cursor_y_pos += 1
            self.cursor_position += len(self.wrapped_lines[self.content[0] + i])
            if self.input_string[self.cursor_position] == '\n' or self.input_string[self.cursor_position] == ' ':
                self.cursor_position += 1
        
        if len(self.wrapped_lines):
            for i in self.wrapped_lines[self.cursor_y_pos]:
                character_width = self.font_object.size(i)[0]
                characters_size += character_width

                if characters_size < x:
                    self.cursor_x_pos += 1
                    self.cursor_position += 1
                else:
                    if characters_size - character_width // 2 < x:
                        self.cursor_x_pos += 1
                        self.cursor_position += 1
                    break
    
    def clear_selection(self):
        self.selected_text = [False, [0, 0, 0], [[0, 0], [0, 0], [0, 0]]]
    
    def adjust_scrollbar(self):
        # Changes the position of scroll bar
        if len(self.wrapped_lines) > self.total_lines_possible:
            if self.scroll_bar.h > 10:
                self.scroll_bar.y = self.y + self.content[0]
                self.scroll_bar.h = self.max_height - (len(self.wrapped_lines) - self.total_lines_possible)
            else:
                y = self.content[0] // self.n

                while True:
                    temp = y * self.n
                    for i in self.remaining_n:
                        temp += y // i
                    if temp <= self.content[0]:
                        break
                    y -= 1
                
                self.scroll_bar.y = self.y + y
        else:
            self.scroll_bar.h = 0

    def wrap_text(self, string):
        if not len(string):
            self.wrapped_lines = []
            self.text_surface = []
            self.cursor_x_pos, self.cursor_y_pos = 0, 0
            self.content = [0, 0]
            return None
        
        ## Wrapped lines store each line as string
        self.wrapped_lines = []
        
        ## Splits the string by words and line
        text = [line.split(' ') for line in string.splitlines()]
        
        for line in text:
            ## Store as many words as possible to fit in allowed width
            while len(line):
                line_of_word = []
                while len(line):
                    ## If word even fit in allowed width
                    ## Otherwise wrap that word
                    fw, fh = self.font_object.size(line[0])
                    if fw > self.max_width:
                        wrapped_word = self.wrap_word(line.pop(0))

                        for i in range(len(wrapped_word) - 1):
                            self.wrapped_lines.append(wrapped_word[i])
                        
                        if not len(line):
                            line = [wrapped_word[-1]]
                        else:
                            line.insert(0, wrapped_word[-1])
                        
                        line_of_word = []
                        continue

                    line_of_word.append(line.pop(0))
                    fw, fh = self.font_object.size(' '.join(line_of_word + line[:1]))
                    
                    ## If width exceeds then store remaining words in new line
                    if fw > self.max_width:
                        break
                
                ## Join all words that fit in width into one line
                final_line = ' '.join(line_of_word)
                self.wrapped_lines.append(final_line)
        
        if self.input_string[-1] == '\n':
            self.wrapped_lines.append('')
        
        self.cursor_pos_to_x_y()
        self.visible_content()
        self._rerender()

        
    def wrap_word(self, word):
        wrapped_word = []

        while len(word):
            ## Store as many characters as possible to fit in allowed width
            line_of_char = []
            while len(word):
                
                line_of_char.append(word[:1])
                word = word[1:]
                fw, fh = self.font_object.size(''.join(line_of_char + [word[:1]]))

                ## If width exceeds then store remaining characters in new line
                if fw > self.max_width:
                    break
            
            ## Join all characters that fit in width into one line
            final_line = ''.join(line_of_char)
            wrapped_word.append(final_line)
        
        return wrapped_word
    
    def cursor_pos_to_x_y(self):
        cursor_x_temp = 0
        cursor_y_temp = 0

        ## Calculate the cursor x and y position
        for line in self.wrapped_lines:
            if (cursor_x_temp + len(line) + 1) <= self.cursor_position:

                if self.input_string[cursor_x_temp + len(line)] == '\n' or self.input_string[cursor_x_temp + len(line)] == ' ':
                    cursor_x_temp += len(line) + 1
                else:
                    cursor_x_temp += len(line)
                
                cursor_y_temp += 1
                continue
            
            self.cursor_x_pos = self.cursor_position - cursor_x_temp
            self.cursor_y_pos = cursor_y_temp
            break
        
        if len(self.wrapped_lines) > self.cursor_y_pos + 1:
            if self.cursor_x_pos == len(self.wrapped_lines[self.cursor_y_pos]):
                if self.input_string[self.cursor_position] != '\n' and self.input_string[self.cursor_position] != ' ':
                    self.cursor_x_pos = 0
                    self.cursor_y_pos += 1


    def visible_content(self):
        ## It will calculate which lines to render
        ## Based on cursor y pos
        ## Content list contains
        ## Starting index and Ending index of wrapped lines to render
        
        h = self.font_object.size('a')[1]
        total_h = h * len(self.wrapped_lines)
        
        if total_h > self.max_height:
            if self.cursor_y_pos < self.content[0]:
                self.content[0] = self.cursor_y_pos
                self.content[1] = min(self.content[0] + self.total_lines_possible - 1, len(self.wrapped_lines) - 1)
            
            elif self.cursor_y_pos > self.content[1]:
                self.content[1] = self.cursor_y_pos
                self.content[0] = max(0, self.content[1] - self.total_lines_possible + 1)
            
            if self.content[1] >= len(self.wrapped_lines):
                self.content[1] = len(self.wrapped_lines) - 1
                self.content[0] = max(0, self.content[1] - self.total_lines_possible + 1)
            
        else:
            self.content[0] = 0
            self.content[1] = len(self.wrapped_lines[:self.total_lines_possible]) - 1
        
        if len(self.wrapped_lines) > self.total_lines_possible:
            height = self.max_height - (len(self.wrapped_lines) - self.total_lines_possible)
            
            if height > 10:
                self.scroll_bar.y = self.y + self.content[0]
                self.scroll_bar.h = height
            else:
                self.scroll_bar.h = 10

                length = len(self.wrapped_lines) - self.total_lines_possible
                loops = self.max_height - self.scroll_bar.h

                self.n = length // loops

                n1 = length - self.n*loops
                left = n1
                self.remaining_n = []

                while left:
                    n1 = ceil(loops/n1)
                    self.remaining_n.append(n1)
                    left -= loops//n1
                    n1 = left
                
                y = self.content[0] // self.n

                while True:
                    temp = y * self.n
                    for i in self.remaining_n:
                        temp += y // i
                    if temp <= self.content[0]:
                        break
                    y -= 1
                
                self.scroll_bar.y = self.y + y
                
        else:
            self.scroll_bar.h = 0
    

    def _rerender(self):
        self.text_surface = []

        ## Render lines and store it
        if len(self.wrapped_lines):
            for i in range(self.content[0], self.content[1] + 1):
                self.text_surface.append(self.font_object.render(self.wrapped_lines[i], self.antialias, self.text_color))
        
    def render(self, screen):
        if not len(self.input_string):
            cursor_x_pos, cursor_y_pos = (self.x, self.y) if self.align_text == "left" else (self.x + self.max_width/2, self.y)
            
            if self.cursor_visible:
                screen.blit(self.cursor_surface, (cursor_x_pos, cursor_y_pos))
            return None
        
        y_offset = 0
        cursor_y_temp = self.content[0]
        i = self.content[0]

        ## Now Render each line individually
        for line in self.text_surface:
            fw, fh = line.get_size()

            if self.align_text == "left":
                x = self.x + 0
            else:
                x = self.x + self.max_width/2 - fw/2
            
            y = self.y + y_offset
            
            if cursor_y_temp == self.cursor_y_pos:
                cursor_x_pos = self.font_object.size(self.wrapped_lines[i][:self.cursor_x_pos])[0] + x
                cursor_y_pos = y_offset + self.y
            
            if self.selected_text[0]:
                if self.selected_text[2][1][1] < i and self.selected_text[2][2][1] > i:
                    pygame.draw.rect(screen, self.selection_color, (self.x, y, fw, fh))
                
                elif self.selected_text[2][1][1] == i:
                    if self.selected_text[2][1][1] == self.selected_text[2][2][1]:
                        w = self.font_object.size(self.wrapped_lines[i][self.selected_text[2][1][0]:self.selected_text[2][2][0]])[0]
                        x1 = self.x + self.font_object.size(self.wrapped_lines[i][:self.selected_text[2][1][0]])[0]
                    else:
                        w = self.font_object.size(self.wrapped_lines[i][self.selected_text[2][1][0]:])[0]
                        x1 = self.x + fw - w
                    pygame.draw.rect(screen, self.selection_color, (x1, y, w, fh))
                
                elif self.selected_text[2][2][1] == i:
                    w = self.font_object.size(self.wrapped_lines[i][:self.selected_text[2][2][0]])[0]
                    pygame.draw.rect(screen, self.selection_color, (self.x, y, w, fh))

            screen.blit(line, (x, y))
            
            y_offset += fh
            cursor_y_temp += 1
            i += 1
        
        if self.cursor_y_pos >= self.content[0] and self.cursor_y_pos <= self.content[1] and self.cursor_visible:
            screen.blit(self.cursor_surface, (cursor_x_pos, cursor_y_pos))
        
        pygame.draw.rect(screen, self.scroll_bar_color, self.scroll_bar)
        
    def get_surface(self):
        return self.text_surface
    
    def get_text(self):
        return self.input_string

    def get_cursor_position(self):
        return self.cursor_x_pos, self.cursor_y_pos, self.cursor_position
    
    def set_text(self, string):
        self.input_string = string
        self.cursor_position = 0
        self.selected_text = [False, [0, 0, 0], [[0, 0], [0, 0], [0, 0]]]
        
        string = self.input_string
        if self.password:
            string = "*" * len(self.input_string)
        
        self.wrap_text(string)
        
        self.content[0] = 0
        self.content[1] = len(self.wrapped_lines[:self.total_lines_possible]) - 1

        self._rerender()

    def set_dimension(self, x, y, max_width, max_height):
        if self.max_width < self.font_size or self.max_height < self.font_size:
            raise ValueError("Width or Height too small")
        
        self.x = x
        self.y = y
        self.max_width = max_width
        self.max_height = max_height

        h = self.font_object.size('a')[1]
        self.text_rect = pygame.Rect(self.x, self.y, self.max_width, self.max_height)
        self.total_lines_possible = self.max_height // h
        self.scroll_bar = pygame.Rect(self.x + self.max_width, self.y, 7, 0)
        self.scroll_bar_selected = False

        string = self.input_string
        if self.password:
            string = "*" * len(self.input_string)
        
        self.wrap_text(string)
        
        self.content[0] = 0
        self.content[1] = len(self.wrapped_lines[:self.total_lines_possible]) - 1

        self._rerender()
    
    def set_position(self, x, y):
        self.x = x
        self.y = y
    
    def set_selection_color(self, color):
        self.selection_color = color

    def set_text_color(self, color):
        self.text_color = color

    def set_cursor_color(self, color):
        self.cursor_surface.fill(color)

    def clear_text(self):
        self.input_string = ""
        self.cursor_position = 0
        self.cursor_x_pos = 0
        self.cursor_y_pos = 0
        self.wrapped_lines = []
        self.selected_text = [False, [0, 0, 0], [[0, 0], [0, 0], [0, 0]]]
        self.content = [0, 0]
        self.text_surface = []
    
    def editTextBox(self, mousePos):
        if (self.text_rect.collidepoint(mousePos)):
            return True
        return False

if __name__ == "__main__":
    pygame.init()

    WIN = pygame.display.set_mode((700, 500))
    clock = pygame.time.Clock()

    # Create TextInput-object
    textinput = TextInputBox(25, 15, font_family='Calibri', font_size=25, max_width=100, max_height=100)

        # """
        # :param x: x coordinate
        # :param y: y coordinate
        # :param initial_string: Initial text to be displayed
        # :param font_family: name or list of names for font (see pygame.font.match_font for precise format)
        # :param font_size:  Size of font in pixels
        # :param align_text: It aligns all lines by "left" or "center"
        # :param max_width: Width of text box
        # :param max_height: Height of text box
        # :param antialias: Determines if antialias is applied to font (uses more processing power)
        # :param text_color: Color of text (duh)
        # :param cursor_color: Color of cursor
        # :param selection_color: Color of selection of text
        # :param scroll_bar_color: Color of scroll bar
        # :param max_string_length: Allowed length of text
        # """

    font = pygame.font.Font(pygame.font.match_font('Calibri'), 15)

    pygame.key.set_repeat(200, 25)

    backgroundRect = pygame.Rect(20, 10, 110, 110)

    editingTextBox = False
    
    while True:
        WIN.fill((30, 30, 30))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                editingTextBox = textinput.editTextBox(event.pos)

            if event.type == pygame.QUIT:
                exit()
        
        pygame.draw.rect(WIN, "blue", backgroundRect)

        ## Feed it with events
        textinput.update(events, editingTextBox)
        
        ## Render the font
        textinput.render(WIN)

        ## Just to look cool
        pygame.draw.rect(WIN, (0, 118, 197), (0, 480, 700, 20))

        cursor_pos = font.render(f"Ln {textinput.cursor_y_pos + 1}, Col {textinput.cursor_x_pos + 1}", True, (255, 255, 255))
        WIN.blit(cursor_pos, (700 - cursor_pos.get_width() - 15, 482))
        
        pygame.display.update()
        clock.tick(60)