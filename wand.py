import curses


def main(stdscr):
    while True:
        stdscr.clear()
        stdscr.addstr("Hello, World!")
        stdscr.refresh()


if __name__ == "__main__":
    curses.wrapper(main)
