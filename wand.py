import curses
import sys


def open_file(filename):
    try:
        with open(filename, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return [""]


def save_file(filename, content):
    with open(filename, "w") as file:
        file.write("\n".join(content))


def main(stdscr, filename):
    cursor_x = 0
    cursor_y = 0
    content = open_file(filename)

    while True:
        stdscr.clear()
        for index, line in enumerate(content):
            stdscr.addstr(index, 0, line)
        stdscr.move(cursor_y, cursor_x)
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
            cursor_y = max(0, cursor_y - 1)
            cursor_x = min(cursor_x, len(content[cursor_y]))
        elif key == curses.KEY_DOWN:
            cursor_y = min(len(content) - 1, cursor_y + 1)
            cursor_x = min(cursor_x, len(content[cursor_y]))
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
        elif key == 27:
            break
        else:
            content[cursor_y] = content[cursor_y][:cursor_x] + chr(key) + content[cursor_y][cursor_x:]
            cursor_x += 1

    save_file(filename, content)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        filename = "untitled"
    else:
        filename = sys.argv[1]
    curses.wrapper(main, filename)
