import os
import time
# import pynotify  # Todo: fix this for windows.


_MOUSE_BUTTONS = {
    "left": 1,
    "middle": 2,
    "right": 3,
    "wheelup": 4,
    "wheeldown": 5
}

_MOUSE_CLICKS = {
    "click": "click",
    "down": "mousedown",
    "up": "mouseup"
}

_KEY_PRESSES = {
    "press": "",
    "up": "up",
    "down": "down"
}

_MOUSE_MOVE_COMMANDS = {
    "absolute": "mousemove",
    "relative": "mousemove_relative",
    "relative_active": "mousemove_active"
}

_SERVER_INFO = {
    "window_manager": "awesome",
    "operating_system": "linux",
    "display": "X11",
    "server": "aenea_reference",
    "server_version": 1
}

_XPROP_PROPERTIES = {
    "_NET_WM_DESKTOP(CARDINAL)": "desktop",
    "WM_WINDOW_ROLE(STRING)": "role",
    "_NET_WM_WINDOW_TYPE(ATOM)": "type",
    "_NET_WM_PID(CARDINAL)": "pid",
    "WM_LOCALE_NAME(STRING)": "locale",
    "WM_CLIENT_MACHINE(STRING)": "client_machine",
    "WM_NAME(STRING)": "name"
}

_MOD_TRANSLATION = {
    "alt": "Alt_L",
    "shift": "Shift_L",
    "control": "Control_L",
    "super": "Super_L",
    "hyper": "Hyper_L",
    "meta": "Meta_L",
    "win": "Super_L",
    "flag": "Super_L",
}

_KEY_TRANSLATION = {
    "ampersand": "ampersand",
    "apostrophe": "apostrophe",
    "apps": "Menu",
    "asterisk": "asterisk",
    "at": "at",
    "backslash": "backslash",
    "backspace": "BackSpace",
    "backtick": "grave",
    "bar": "bar",
    "caret": "asciicircum",
    "colon": "colon",
    "comma": "comma",
    "del": "Delete",
    "dollar": "dollar",
    "dot": "period",
    "dquote": "quotedbl",
    "enter": "Return",
    "equal": "equal",
    "exclamation": "exclam",
    "hash": "numbersign",
    "hyphen": "minus",
    "langle": "less",
    "lbrace": "braceleft",
    "lbracket": "bracketleft",
    "lparen": "parenleft",
    "minus": "minus",
    "npadd": "KP_Add",
    "npdec": "KP_Decimal",
    "npdiv": "KP_Divide",
    "npmul": "KP_Multiply",
    "percent": "percent",
    "pgdown": "Next",
    "pgup": "Prior",
    "plus": "plus",
    "question": "question",
    "rangle": "greater",
    "rbrace": "braceright",
    "rbracket": "bracketright",
    "rparen": "parenright",
    "semicolon": "semicolon",
    "shift": "Shift_L",
    "slash": "slash",
    "space": "space",
    "squote": "apostrophe",
    "tilde": "asciitilde",
    "underscore": "underscore",
    "win": "Super_L",
}


def update_key_translation(translation):
    # Todo: fix this for windows.
    pass


def run_command(command, executable="xdotool"):
    # Todo: fix this for windows.
    pass


def read_command(command, executable="xdotool"):
    # Todo: fix this for windows.
    pass


def write_command(message, executable="xdotool"):
    # Todo: fix this for windows.
    pass


def get_active_window(_xdotool=None):
    # Todo: fix this for windows.
    pass


def get_geometry(window_id=None, _xdotool=None):
    # Todo: fix this for windows.
    pass


def transform_relative_mouse_event(event):
    # Todo: fix this for windows.
    pass


def get_context(_xdotool=None):
    # Todo: fix this for windows.
    pass


def key_press(key, modifiers=(), direction="press", count=1, count_delay=None,
    _xdotool=None):
    # Todo: fix this for windows.
    pass


def notify_host(message):
    # Todo: fix this for windows.
    pass


def write_text(text, _xdotool=None):
    # Todo: fix this for windows.
    pass


def click_mouse(button, direction="click", count=1, count_delay=None,
    _xdotool=None):
    # Todo: fix this for windows.
    pass


def move_mouse(x, y, reference="absolute", proportional=False, phantom=None,
    _xdotool=None):
    # Todo: fix this for windows.
    pass


def pause(amount, _xdotool=None):
    # Todo: fix this for windows.
    pass


def server_info(_xdotool=None):
    # Todo: fix this for windows.
    pass


def flush_xdotool(actions):
    # Todo: fix this for windows.
    pass


def multiple_actions(actions):
    # Todo: fix this for windows.
    pass


def list_rpc_commands():
    _RPC_COMMANDS = {
        "get_context": get_context,
        "key_press": key_press,
        "write_text": write_text,
        "click_mouse": click_mouse,
        "move_mouse": move_mouse,
        "server_info": server_info,
        "pause": pause,
    }
    return _RPC_COMMANDS
