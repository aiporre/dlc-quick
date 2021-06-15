import curses
import random



class Option:
    '''
    Class Option

    it has 4 status indicated by the integer between 0 and 3:
        1 = not processed
        2 = processed
        3 = will be processed
        4 = will be re-processed
    '''

    def __init__(self, screen, text, row, status=0):
        self.screen = screen
        self.text = text + '\n'
        self.row = row
        self.status = status

    @property
    def selected(self):
        if self.status == 2 or self.status == 0:
            return False
        elif self.status == 1 or self.status == 3:
            return True

    def toogle_selection(self):
        if self.status == 0:
            self.status = 1
        elif self.status == 2:
            self.status = 3
        elif self.status == 1:
            self.status = 0
        elif self.status == 3:
            self.status = 2
        else:
            raise ValueError(f'Invalid state {self.status} for option {self.text} ')

    def print(self):
        # prints without colors
        # TODO: 2 is hardcoded to the lenght of the cursor
        if not curses.has_colors():
            self.screen.addstr(self.row, 2, self.text + ' ysize = ' + str(self.screen.getyx()[0]))
        # prints with colors
        else:
            self.screen.addstr(self.row, 2, ' ' + self.text.strip(), curses.color_pair(self.status))


def print_options(options):
    for o in options:
        o.print()


class Pad:
    def __init__(self, screen, pheight, shift_y, shift_x, sheight, swidth):
        self.screen = screen
        self.shift_y = shift_y
        self.shift_x = shift_x
        self.pheight, self.pwidth = (pheight, swidth)
        self.sheight, self.swidth = (sheight, swidth)
        self.pheight = pheight
        self.pad = curses.newpad(pheight, swidth)
        self.screen.refresh()
        self.pad.scrollok(True)
        self.pad_pos = 0

    def refresh(self):
        self.pad.refresh(self.pad_pos, 0, 0, 0, self.sheight - 1, self.swidth)

    def move_up(self):
        self.pad_pos = max(self.pad_pos-1, 0)

    def move_down(self):
        self.pad_pos = min(self.pad_pos + 1, self.pheight - 1)


class OptionsPad(Pad):
    def __init__(self, screen, options_text, shift_y, shift_x, sheight, swidth):
        super().__init__(screen, pheight=len(options_text), shift_y=shift_y, shift_x=shift_x, sheight=sheight, swidth=swidth)
        self.options_text = options_text
        self.options = [Option(self.pad, option, i) for i, option in enumerate(self.options_text)]
        self.cursor_text = "➤➤"
        self.cursor_position = 0

    def show(self):
        print_options(self.options)
        self.pad.addstr(self.cursor_position, 0, self.cursor_text)
        self.refresh()

    def toogle_selection(self):
        self.options[self.cursor_position].toogle_selection()
        print_options(self.options)
        self.refresh()

    def move_down(self):
        self.pad.addstr(self.cursor_position, 0, ''.join(len(self.cursor_text)*[' ']))
        self.cursor_position = min(self.cursor_position + 1, self.pheight - 1)
        self.pad.addstr(self.cursor_position, 0, self.cursor_text)
        if self.cursor_position - self.pad_pos > self.sheight-1:
            super().move_down()
        self.refresh()

    def move_up(self):
        self.pad.addstr(self.cursor_position, 0, ''.join(len(self.cursor_text)*[' ']))
        self.cursor_position = max(self.cursor_position-1, 0)
        self.pad.addstr(self.cursor_position, 0, self.cursor_text)
        if self.cursor_position < self.pad_pos:
            super().move_up()
        self.refresh()

class OptionInterface:
    def __init__(self, options_text: str):
        self.options_text = options_text

    def __loop(self, screen):
        curses.curs_set(0)
        if curses.has_colors() and curses.can_change_color():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_GREEN)
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_WHITE)
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_GREEN)
        height, width = screen.getmaxyx()
        options_pad = OptionsPad(screen, self.options_text, shift_y=0, shift_x=0, sheight=height, swidth=width)
        screen.refresh()

        try:
            options_pad.show()
            while 1:
                c = screen.getch()
                if c == ord('D') or c == ord('d'):
                    options_pad.move_down()
                elif c == ord('A') or c == ord('a'):
                    options_pad.move_up()
                elif c == 32:
                    options_pad.toogle_selection()
                screen.refresh()

        except Exception as e:
            print(e)
            # curses.napms(2000)
            screen.getch()
            raise e

        finally:
            curses.endwin()

    def launch(self):
        curses.wrapper(self.__loop)


if __name__ == '__main__':
    example_options = [f' OPTION {i}' for i in range(10)]


    OptionInterface(example_options).launch()