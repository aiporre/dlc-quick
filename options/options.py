import curses
import curses.textpad


class CommandBox:
    COMMANDS_CODES = {
        'R/': 'Select range',
        'S/': 'Search options',
        'r/': 'Resets to orignal selection',
        'x/': 'Exit and saves options'}

    def __init__(self, screen, height, width):
        self.screen = screen
        self.height = height
        self.width = width

    def _validate_command_input(self, command: str):
        if not command[:2] in self.COMMANDS_CODES.keys():
            _cc = ''.join([f'\'{c}\' ' for c in self.COMMANDS_CODES.keys()])
            return 'Invalid command. Available Commands ' + _cc[:-2] + '.'

        if command.startswith('R/'):
            if command.count('/') != 2:
                return f'Invalid command \'Select range\'. Use two \'/\' separators. ERR: {command}'

        if command.startswith('S/'):
            if command.count('/') != 1 and command.count('/') != 2:
                return f'Invalid command \'Search options\'. Use one or two \'/\' separators. ERR: {command}'

        if command[:2] in ['r/', 'x/']:
            if len(command) != 2:
                return 'Invalid command. Only allowed input is Select range (R/) and Search options (S/)'

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
        action_name = ''
        if error is None:
            last_command_text = '++/ ' + command_text
            # parsing command into action fcn:
            if command_text.startswith('R/'):
                tokens = command_text.split('/')
                begin, end = tokens[1], tokens[2]
                action = lambda option_pad: option_pad.range_select(begin, end)
                action_name = 'range select'
            elif command_text.startswith('S/'):
                tokens = command_text.split('/')
                if len(tokens) == 2 and len(tokens[1]) == 0:
                    begin, end = None, None
                elif len(tokens) == 2 and len(tokens[1]) > 0:
                    begin, end = tokens[1], None
                else:
                    begin, end = tokens[1], tokens[2]
                action = lambda options_text: self.filter_options(options_text,begin, end)
                action_name = 'filter options'
            elif command_text.startswith('r/'):
                action = lambda option_pad: option_pad.reset_selections()
                action_name = 'reset selections'
            elif command_text.startswith('x/'):
                action = lambda option_pad: option_pad.save_selections()
                action_name = 'exit'
        else:
            last_command_text = "--/ Invalid command: " + error

        self.screen.addstr(self.height - 1, 0, last_command_text[:self.width])
        return action, action_name

    @staticmethod
    def filter_options(options_text, begin, end):
        # Finds filtered indices
        filtered_indices = []
        if begin is None:
            filtered_indices = list(range(len(options_text)))
        elif end is None:
            # meaning that is only looking for begin inside the text
            for i, text in options_text:
                if begin in text:
                    filtered_indices.append(i)
        else:
            # ranges search in between first "begin" in text and last "end" in text
            range_select = [None, None]
            for i, text in enumerate(options_text):
                if begin in text and range_select[0] is None:
                    range_select[0] = i
                if end in text and range_select[0] is not None:
                    range_select[1] = max(i, range_select[1]) if range_select[1] is not None else i
            if range_select[0] is not None and range_select[1] is not None:
                filtered_indices = list(range(range_select[0], range_select[1]+1))
            else:
                filtered_indices = list(range(len(options_text)))
        return filtered_indices


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
        self.options = [Option(self.pad, option, i, status=status) for i, (option,status) in enumerate(zip(self.options_text, options_status))]
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

    def range_select(self, begin_text, end_text):

        range_select = [None, None]
        for i, o in enumerate(self.options):
            if begin_text in o.text and range_select[0] is None:
                range_select[0] = i
            if end_text in o.text and range_select[0] is not None:
                range_select[1] = max(i, range_select[1]) if range_select[1] is not None else i

        if range_select[0] is not None and range_select[1] is not None:
            for o in self.options[range_select[0]:range_select[1]+1]:
                if not o.selected:
                    o.toogle_selection()
            print_options(self.options)
            self.refresh()


    def reset_selections(self):
        for o in self.options:
            if o.selected:
                o.toogle_selection()
        print_options(self.options)
        self.refresh()

    def save_selections(self):
        pass

    def clear(self):
        self.pad.clear()
        self.refresh()

class OptionInterface:
    def __init__(self, options_text, options_status):
        self.options_text = options_text
        self.options_status = options_status

    def __loop(self, screen):
        curses.curs_set(0)
        if curses.has_colors() and curses.can_change_color():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_GREEN)
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_WHITE)
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_GREEN)
        height, width = screen.getmaxyx()
        options_pad = OptionsPad(screen, self.options_text, self.options_status, shift_y=0, shift_x=0, sheight=height-1, swidth=width)
        command_box = CommandBox(screen, height, width)
        filtered = list(range(len(self.options_text)))
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
                    action, action_name = command_box.accept_command()
                    end_loop = False
                    if action_name == 'filter options':
                        filtered = action(self.options_text)
                        filtered_options = [self.options_text[i] for i in filtered]
                        filtered_status = [self.options_status[i] for i in filtered]
                        options_pad.clear()
                        options_pad = OptionsPad(screen, filtered_options, filtered_status, shift_y=0, shift_x=0, sheight=height-1, swidth=width)
                        options_pad.show()
                    elif action_name == 'exit':
                        end_loop = True
                    elif action_name in ['range select', 'reset selections']:
                        action(options_pad)
                        for i, f in enumerate(filtered):
                            self.options_status[f] = options_pad.options[i].status
                    if end_loop:
                        curses.napms(3000)
                        break
                elif c == 32:
                    options_pad.toogle_selection()
                    #TODO: Poor desing if we need to update data in two places.
                    for i, f in enumerate(filtered):
                        self.options_status[f] = options_pad.options[i].status
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
    opt_interface = OptionInterface(example_options, example_options_status)
    opt_interface.launch()

    for o, s in zip(opt_interface.options_text, opt_interface.options_status):
        print(f'OPTION ({o}) => {s}')
