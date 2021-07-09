import curses
from curses.textpad import Textbox, rectangle
from ctypes import *
from timeit import timeit

def make_input_prompt(screen, prompt):
    rectangle(screen, 17, 1, 22, 78)
    screen.addstr(18, 18, prompt)
    rectangle(screen, 19, 6, 21, 73)
    window = curses.newwin(1, 65, 20, 7)  # h, w, y, x
    screen.refresh()  # Draw to the screen
    box = Textbox(window)  # Create a textbox
    box.edit()  # Enable editing
    return box.gather()


def cipher(message, key):
    return bytes([message[i] ^ key[i % len(key)] for i in range(0, len(message))])


def make_outer_rec(screen):
    # DIALOG WRAPPER
    rectangle(screen, 0, 0, 23, 79)  # win, y1, x1, y2, x2


def make_welcome_message(screen):
    # WELCOME MESSAGE
    welcome_message = "Welcome to the XOR-Cipher App!"
    screen.addstr(1, 26, welcome_message)


def make_menu(screen):
    # MENU
    rectangle(screen, 2, 20, 11, 60)
    menu_column = 22
    screen.addstr(3, menu_column, "[F] Read text from a local File")
    screen.addstr(4, menu_column, "[I] Read text from user Input prompt")
    screen.addstr(5, menu_column, "[R] Apply Rust cipher to this text")
    screen.addstr(6, menu_column, "[P] Apply Python cipher to this text ")
    screen.addstr(7, menu_column, "[V] Verify cipher results match")
    screen.addstr(8, menu_column, "[K] Change Key used for ciphers")
    screen.addstr(9, menu_column, "[B] Run Benchmarks on text (100000x)")
    screen.addstr(10, menu_column, "[Q] Quit the Application")


def make_haiku(screen, haiku_text, haiku_key):
    # HAIKU
    haiku_column = 4
    rectangle(screen, 12, 2, 15, 77)
    screen.addstr(13, haiku_column, haiku_text)
    screen.addstr(14, haiku_column, haiku_key)


def print_status_message(screen, message):
    # STATUS
    screen.addstr(24, 1, message)


def check_upper_and_lower(choice, char):
    return choice == ord(char) or (choice - 32) == ord(char) or (choice + 32) == ord(char)


def make_base_dialog(screen, status_message, haiku_text, haiku_key):
    make_outer_rec(screen)
    make_welcome_message(screen)
    make_menu(screen)
    make_haiku(screen, haiku_text, haiku_key)
    print_status_message(screen, status_message)


def build_haiku_text(string):
    return "TEXT [" + string + "]"


def build_haiku_key(string):
    return "KEY  [" + string + "]"


def load_cipher_lib(library_path):
    lib = cdll.LoadLibrary(library_path)
    lib.cipher.restype = None
    lib.cipher.argtypes = [c_char_p, c_char_p, c_char_p, c_uint8, c_int]
    return lib


def run_benchmarks(screen, lib, text, key):
    rectangle(screen, 17, 1, 22, 78)
    screen.addstr(18, 28, "Running benchmarks....")
    screen.refresh()
    python_time = timeit(lambda: cipher(text.encode(encoding='CP437'), key.encode(encoding='CP437')), number=100000)
    buf = create_string_buffer(len(text))
    rust_time = timeit(lambda: lib.cipher(text.encode(encoding='CP437'), key.encode(encoding='CP437'), buf, len(text) + 1, len(key) + 1), number=100000)
    print_results(screen, rust_time, python_time)


def print_results(screen, rust_time, python_time):
    screen.clear()
    rectangle(screen, 17, 1, 22, 78)
    screen.addstr(18, 28, "Results from Benchmark")
    screen.addstr(19, 28, "-" * 22)
    screen.addstr(20, 28, "Rust Cipher:   %06.3fs" % rust_time)
    screen.addstr(21, 28, "Python Cipher: %06.3fs" % python_time)


def cipher_verify(lib, text, key):
    buf = create_string_buffer(len(text))
    lib.cipher(text.encode(encoding='CP437'), key.encode(encoding='CP437'), buf, len(text) + 1, len(key) + 1)
    ciphered_text = cipher(text.encode(encoding='CP437'), key.encode(encoding='CP437'))
    if ciphered_text == buf.raw:
        return "Status: Cipher match verified!"
    else:
        return "Status: WARNING: ciphers do not match!"


def run_gui(screen):
    curses.noecho()
    curses.cbreak()
    status_message = "Status: Application started successfully."
    text = "This is a haiku; it is not too long I think; but you may disagree"
    key = "But there's one sound that no one knows... What does the Fox say?"
    haiku_text = build_haiku_text(text)
    haiku_key = build_haiku_key(key)
    ciphered_text = ""
    skip_clear = False
    ctrl_translation = str.maketrans(bytes(range(0, 32)).decode("CP437"), "�☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼")
    lib = load_cipher_lib("./libxorcipher.so")

    while True:
        if not skip_clear:
            screen.clear()
        make_base_dialog(screen, status_message, haiku_text, haiku_key)
        screen.refresh()
        skip_clear = False
        choice = screen.getch()

        if check_upper_and_lower(choice, 'F'):
            user_input = make_input_prompt(screen, "Enter file to load below, then press [ENTER]").strip()[0:65]
            if not user_input:
                status_message = "Status: File load cancelled."
            else:
                try:
                    with open(user_input, 'r', encoding='CP437') as f:
                        read_data = f.read()[0:65]
                    text = read_data
                    haiku_text = build_haiku_text(text)
                    status_message = "Status: File contents loaded successfully."
                except IOError:
                    status_message = "Status: ERROR: COULD NOT LOAD FILE: " + user_input
        elif check_upper_and_lower(choice, 'Q'):
            curses.endwin()
            print('Thanks for using the XOR-Cipher App; See you next time!')
            break
        elif check_upper_and_lower(choice, 'I'):
            user_input = make_input_prompt(screen, "Enter new text below, then press [ENTER]").strip()
            if not user_input:
                status_message = "Status: Cancelled user input of text (empty string)."
            else:
                text = user_input
                haiku_text = build_haiku_text(text)
                status_message = "Status: New text loaded into memory from user input."
        elif check_upper_and_lower(choice, 'K'):
            user_input = make_input_prompt(screen, "Enter new key and then press [ENTER]").strip()
            if not user_input:
                status_message = "Status: Cancelled user input of key (empty string)."
            else:
                key = user_input
                haiku_key = build_haiku_key(key)
                status_message = "Status: New key loaded into memory from user input."
        elif check_upper_and_lower(choice, 'R'):
            buf = create_string_buffer(len(text))
            if not ciphered_text:
                lib.cipher(text.encode(encoding='CP437'), key.encode(encoding='CP437'), buf, len(text) + 1,
                           len(key) + 1)
                display_text = buf.raw.decode("CP437").translate(ctrl_translation)
                haiku_text = build_haiku_text(display_text)
                ciphered_text = buf.raw
            else:
                lib.cipher(ciphered_text, key.encode(encoding='CP437'), buf, len(text) + 1,
                           len(key) + 1)
                display_text = buf.raw.decode("CP437").translate(ctrl_translation)
                haiku_text = build_haiku_text(display_text)
                ciphered_text = ""
            status_message = "Status: Applied Rust cipher."
        elif check_upper_and_lower(choice, 'P'):
            if not ciphered_text:
                ciphered_text = cipher(text.encode(encoding='CP437'), key.encode(encoding='CP437'))
                display_text = ciphered_text.decode("CP437").translate(ctrl_translation)
                haiku_text = build_haiku_text(display_text)
            else:
                ciphered_text = cipher(ciphered_text, key.encode(encoding='CP437'))
                display_text = ciphered_text.decode("CP437").translate(ctrl_translation)
                haiku_text = build_haiku_text(display_text)
                ciphered_text = ""
            status_message = "Status: Applied Python cipher."
        elif check_upper_and_lower(choice, 'B'):
            run_benchmarks(screen, lib, text, key)
            status_message = "Status: Benchmark results displayed."
            skip_clear = True
        elif check_upper_and_lower(choice, 'V'):
            status_message = cipher_verify(lib, text, key)
        else:
            status_message = "Status: ERROR: Invalid menu selection!"
            skip_clear = True


def main():
    curses.wrapper(run_gui)


if __name__ == '__main__':
    exit(main())
