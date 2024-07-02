import curses
import sys
import os


def validate_filepath(filepath):
    if not os.path.isfile(filepath):
        filepath = os.path.abspath(filepath)
    return filepath


def open_file(filename):
    try:
        with open(filename, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError as e:
        print(f"Error: Failed to open file. ({e})")
        return [""]
    except IOError as e:
        print(f"Error: Failed to open file. ({e})")


def save_file(filename, content):
    try:
        if content and not content[-1].endswith("\n"):
            content.append("")
        with open(filename, "w") as file:
            file.write("\n".join(content))
    except IOError as e:
        print(f"Error: Failed to save file. ({e})")


def save_as_file(stdscr, content):
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Save As: ")
        curses.echo()
        filename = stdscr.getstr().decode("utf-8")
        curses.noecho()
        if filename.strip():
            save_file(filename, content)
            break


def command_palette(stdscr, filename, content):
    options = ["Save", "Save As", "Exit", "Save & Exit", "Cancel"]
    option_index = 0
    curses.curs_set(0)
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        palette_width = max(len(option) for option in options) + 6
        palette_height = len(options) + 4
        min_palette_width = 50
        if palette_width < min_palette_width:
            palette_width = min_palette_width
        start_x = (width - palette_width) // 2
        start_y = (height - palette_height) // 2
        window = curses.newwin(palette_height, palette_width, start_y, start_x)
        window.box()
        window.addstr(1, 2, "[Command Palette]")
        for index, option in enumerate(options):
            if index == option_index:
                window.attron(curses.A_BOLD)
                window.addstr(index + 2, 2, f"> {option}")
                window.attroff(curses.A_BOLD)
            else:
                window.addstr(index + 2, 2, f"  {option}")
        stdscr.refresh()
        window.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP:
            option_index = (option_index - 1) % len(options)
        elif key == curses.KEY_DOWN:
            option_index = (option_index + 1) % len(options)
        elif key in (curses.KEY_ENTER, 10, 13):
            selected_option = options[option_index]
            if selected_option == "Save":
                save_file(filename, content)
                break
            elif selected_option == "Save As":
                curses.curs_set(1)
                save_as_file(stdscr, content)
                curses.curs_set(0)
                break
            elif selected_option == "Exit":
                return True
            elif selected_option == "Save & Exit":
                save_file(filename, content)
                return True
            elif selected_option == "Cancel":
                break
            return False
    curses.curs_set(1)


def main(stdscr, filename):
    cursor_x = 0
    cursor_y = 0
    filename = validate_filepath(filename)
    content = open_file(filename)

    curses.start_color()
    curses.init_pair(1, 8, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)

    while True:
        stdscr.clear()
        max_lines_display = curses.LINES - 1
        for index, line in enumerate(content):
            line_number = index + 1
            if index < max_lines_display:
                stdscr.addstr(index, 0, f"{line_number}: ", curses.color_pair(1))
                stdscr.addstr(f"{line}", curses.color_pair(2))
        stdscr.move(cursor_y, len(str(len(content))) + 2 + cursor_x)
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_LEFT:
            if cursor_x > 0:
                cursor_x -= 1
            elif cursor_y > 0:
                cursor_y -= 1
                cursor_x = len(content[cursor_y])
        elif key == curses.KEY_RIGHT:
            if cursor_x < len(content[cursor_y]):
                cursor_x += 1
            elif cursor_y < len(content) - 1:
                cursor_y += 1
                cursor_x = 0
        elif key == curses.KEY_UP:
            if cursor_y > 0:
                cursor_y = max(0, cursor_y - 1)
                cursor_x = min(cursor_x, len(content[cursor_y]))
            else:
                cursor_x = 0
        elif key == curses.KEY_DOWN:
            if cursor_y < len(content) - 1:
                cursor_y = min(len(content) - 1, cursor_y + 1)
                cursor_x = min(cursor_x, len(content[cursor_y]))
            else:
                cursor_x = len(content[cursor_y])
        elif key == 9:
            content[cursor_y] = content[cursor_y][:cursor_x] + "    " + content[cursor_y][cursor_x:]
            cursor_x += 4
        elif key in (curses.KEY_BACKSPACE, 127):
            if cursor_x > 0:
                content[cursor_y] = content[cursor_y][: cursor_x - 1] + content[cursor_y][cursor_x:]
                cursor_x -= 1
            elif cursor_y > 0:
                cursor_x = len(content[cursor_y - 1])
                content[cursor_y - 1] += content.pop(cursor_y)
                cursor_y -= 1
        elif key in (curses.KEY_ENTER, 10, 13):
            content.insert(cursor_y + 1, content[cursor_y][cursor_x:])
            content[cursor_y] = content[cursor_y][:cursor_x]
            cursor_x = 0
            cursor_y += 1
        elif key in (16, 27):
            if command_palette(stdscr, filename, content):
                break
        else:
            if content:
                content[cursor_y] = content[cursor_y][:cursor_x] + chr(key) + content[cursor_y][cursor_x:]
                cursor_x += 1
            else:
                content.append(chr(key))
                cursor_x += 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        filename = "untitled"
    else:
        filename = sys.argv[1]
    curses.wrapper(main, filename)
