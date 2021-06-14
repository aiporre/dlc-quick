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
            self.screen.addstr(self.row, 2, self.text)
        # prints with colors
        else:
            self.screen.addstr(self.row, 2, self.text, curses.color_pair(self.status))
        self.screen.refresh()


def print_options(options):
    for o in options:
        o.print()


class Pad:
    def __init__(self, screen, shift_y, shift_x, rate_height, rate_width):
        self.screen = screen
        self.shift_y = shift_y
        self.shift_x = shift_x
        height, width = screen.getmaxyx()
        self.pad = curses.newpad(rate_height*height, rate_width*width)
        self.pad.scrollok(True)
        self.pad_pos = 0

    def refresh(self):
        height, width = self.screen.getmaxyx()
        self.pad.refresh(self.pad_pos + 2, 0, 0, 0, height - 1, width)

    def moveup(self):
        pass

    def movedown(self):
        pass

class OptionPad(Pad):
    def __init__(self, screen, options_text, shift_y, shift_x, rate_height, rate_width):
        super(OptionPad).__init__(screen, shift_y, shift_x, rate_height, rate_width)
        self.options_text = options_text
        self.options = [Option(self.pad, option, i) for i, option in enumerate(self.options_text)]
        print_options(self.options)


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

        screen.refresh()
        try:
            options = [Option(screen, option, i) for i, option in enumerate(self.options_text)]
            print_options(options)
            cursor_row = 0
            screen.addstr(cursor_row, 0, "➤➤")
            screen.refresh()

            while 1:
                c = screen.getch()
                if c == ord('D') or c == ord('d'):
                    screen.addstr(cursor_row, 0, "  ")
                    cursor_row = min(cursor_row + 1, len(options) - 1)
                    screen.addstr(cursor_row, 0, "➤➤")
                if c == ord('A') or c == ord('a'):
                    screen.addstr(cursor_row, 0, "  ")
                    cursor_row = max(cursor_row - 1, 0)
                    screen.addstr(cursor_row, 0, "➤➤")
                if c == 32:
                    options[cursor_row].toogle_selection()
                    print_options(options)
                screen.refresh()

        except Exception as e:
            print(e)
            # curses.napms(2000)
            screen.getch()


        finally:
            curses.endwin()

    def launch(self):
        curses.wrapper(self.__loop)


if __name__ == '__main__':
    example_options = [' option 1 ',
                    ' option 2 ',
                    ' option 3 ',
                    ' option 4 ',
                    ' option 5 ',
                    ' option 6 ']
    OptionInterface(example_options).launch()