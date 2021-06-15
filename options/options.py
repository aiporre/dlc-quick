import curses
import curses.textpad
import random


class CommandBox:
    COMMANDS_CODES = {
        'R/': 'Select range',
        'S/': 'Search options',
        'r/': 'Resets to orignal selection',
        'x/': 'Exit and saves options',
        'q/': 'Exit without saving'}

    def __init__(self, screen, height, width):
        self.screen = screen
        self.height = height
        self.width = width

    def _validate_command_input(self, command: str):
        if not command[:2] in self.COMMANDS_CODES.keys():
            _cc = ''.join([f'\'{c}\' ' for c in self.COMMANDS_CODES.keys()])
            return 'Invalid command. Available Commands ' + _cc[:-2] + '.'

    def _maketextbox(self, h, w, y, x, value="", textColorpair=0):
        window = curses.newwin(h, w, y, x)
        txtbox = curses.textpad.Textbox(window)
        window.addstr(0, 0, value)
        window.attron(textColorpair)
        window.refresh()
        return txtbox

    def accept_command(self):
        command_textbox = self._maketextbox(1, self.width, self.height - 1, 0, ":")
        text = command_textbox.edit()
        command_text = text.strip()[1:]
        error = self._validate_command_input(command_text)
        action = None
        exit = False
        if error is None:
            last_command_text = '++/ ' + command_text
            # parsing command into action fcn:
            if command_text.startswith('R/'):
                tokens = command_text.split('/')
                begin, end = tokens[1], tokens[2]
                action = lambda option_pad: option_pad.range_select(begin, end)
            elif command_text.startswith('S/'):
                tokens = command_text.split('/')
                begin, end = tokens[1], tokens[2]
                action = lambda option_pad: option_pad.filter_options(begin, end)
            elif command_text.startswith('r/'):
                action = lambda option_pad: option_pad.reset_selections(begin, end)
            elif command_text.startswith('x/'):
                action = lambda option_pad: option_pad.save_selections()
                exit = True
        else:
            last_command_text = "--/ Invalid command: " + error

        self.screen.addstr(self.height - 1, 0, last_command_text[:self.width])
        return action, exit


class Option:
    '''
    Class Option

    it has 4 status indicated by the integer between 0 and 3:
        0 = not processed
        1 = processed
        2 = will be processed
        3 = will be re-processed
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
    def __init__(self, screen, options_text, options_status, shift_y, shift_x, sheight, swidth):
        super().__init__(screen, pheight=len(options_text), shift_y=shift_y, shift_x=shift_x, sheight=sheight, swidth=swidth)
        self.options_text = options_text
        self.options_status = options_status
        self.options = [Option(self.pad, option, i, status=status) for i, (option,status) in enumerate(zip(self.options_text, self.options_status))]
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
    def __init__(self, options_text, options_status):
        self.options_text = options_text
        self.options_status = options_status

    def __loop(self, screen):
        curses.curs_set(0)
        if curses.has_colors() and curses.can_change_color():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_GREEN)
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_WHITE)
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_GREEN)
        height, width = screen.getmaxyx()
        options_pad = OptionsPad(screen, self.options_text, self.options_status, shift_y=0, shift_x=0, sheight=height-1, swidth=width)
        command_box = CommandBox(screen, height, width)
        screen.refresh()

        try:
            options_pad.show()
            while 1:
                c = screen.getch()
                if c == ord('D') or c == ord('d'):
                    options_pad.move_down()
                elif c == ord('A') or c == ord('a'):
                    options_pad.move_up()
                elif c == ord(':'):
                    action, exit = command_box.accept_command()
                    action(options_pad)
                    if exit:
                        curses.napms(3000)
                        break
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
    example_options_status = [0]*len(example_options)
    example_options_status[1] = 2

    OptionInterface(example_options, example_options_status).launch()