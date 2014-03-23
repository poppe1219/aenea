import os
import time

pynotify = None
try:
    import pynotify  # @UnresolvedImport (Linux only)
    if not pynotify.init("Aenea server"):
        pynotify = None
except ImportError:
    pass


LAST_SELECTED_APP = None
PREVIOUS_COMMAND = None


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
    "ctrl": "Control_L",
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
    for key in (["left", "right", "up", "down", "home", "end", "tab", "insert",
        "escape"] + ["f%i" % i for i in xrange(1, 13)]):
        translation[key] = key[0].upper() + key[1:]
    for index in xrange(10):
        translation["np%i" % index] = "KP_%i" % index
    for c in range(ord("a"), ord("z")) + range(ord("0"), ord("9")):
        translation[chr(c)] = chr(c)
        translation[chr(c).upper()] = chr(c).upper()
update_key_translation(_KEY_TRANSLATION)


def run_command(command, executable="xdotool"):
    command_string = "%s %s" % (executable, command)
    print("run_command:", command_string)
    os.system(command_string)


def read_command(command, executable="xdotool"):
    with os.popen("%s %s" % (executable, command), "r") as fd:
        rval = fd.read()
    return rval


def write_command(message, arguments="type --file -", executable="xdotool"):
    with os.popen("%s %s" % (executable, arguments), "w") as fd:
        fd.write(message)


def get_active_window(_xdotool=None):
    """Returns the window id and title of the active window."""
    flush_xdotool(_xdotool)
    window_id = read_command("getactivewindow")
    if window_id:
        window_id = int(window_id)
        window_title = read_command("getwindowname %i" % window_id).strip()
        return window_id, window_title
    else:
        return None, None


def get_geometry(window_id=None, _xdotool=None):
    flush_xdotool(_xdotool)
    if window_id is None:
        window_id, _ = get_active_window()
    geo = dict(
        [val.lower() for val in line.split("=")] for line in read_command(
            ("getwindowgeometry --shell %i" % window_id)).strip().split("\n"))
    geo = dict((key, int(value)) for (key, value) in geo.iteritems())
    return dict((key, geo[key]) for key in (
        "x", "y", "width", "height", "screen"))


def transform_relative_mouse_event(event):
    geo = get_geometry()
    dx, dy = map(int, map(float, event.split()))
    return [("mousemove", "%i %i" % (geo["x"] + dx, geo["y"] + dy))]


def get_context(_xdotool=None):
    """Return a dictionary of window properties for the currently active
    window. It is fine to include platform specific information, but at least
    include title and executable.

    """
    flush_xdotool(_xdotool)
    window_id, window_title = get_active_window()
    if window_id is None:
        return {}

    properties = {
        "id": window_id,
        "title": window_title,
    }
    for line in read_command("-id %s" % window_id, "xprop").split("\n"):
        split = line.split(" = ", 1)
        if len(split) == 2:
            rawkey, value = split
            if split[0] in _XPROP_PROPERTIES:
                property_value = value[1:-1] if "(STRING)" in rawkey else value
                properties[_XPROP_PROPERTIES[rawkey]] = property_value
            elif rawkey == "WM_CLASS(STRING)":
                window_class_name, window_class = value.split('", "')
                properties["cls_name"] = window_class_name[1:]
                properties["cls"] = window_class[:-1]

    properties["executable"] = None
    try:
        properties["executable"] = os.readlink(  # @UndefinedVariable
            "/proc/%s/exe" % properties["pid"])
    except OSError:
        ps = read_command("%s" % properties["pid"],
            executable="ps").split("\n")[1:]
        if ps:
            try:
                properties["executable"] = ps[0].split()[4]
            except Exception:
                pass

    return properties


def key_press(key, modifiers=(), direction="press", count=1, count_delay=0,
    _xdotool=None):
    """Press a key possibly modified by modifiers. direction may be "press",
    "down", or "up". modifiers may contain "alt", "shift", "control", "super".
    this X11 server also supports "hyper", "meta", and "flag"
    (same as super). count is number of times to press it. count_delay delay
    in ms between presses.

    """
    if (count_delay is None or count < 2):
        delay = ""
    else:
        delay = "--delay %i " % count_delay
    modifiers = [_MOD_TRANSLATION.get(mod, mod) for mod in modifiers]
    key_to_press = _KEY_TRANSLATION.get(key, key)
    keys = (["keydown " + key for key in modifiers] +
          (["key%s %s" % (_KEY_PRESSES[direction], key_to_press)] * count) +
          ["keyup " + key for key in reversed(modifiers)])
    if _xdotool is not None:
        _xdotool.extend(keys)
    else:
        run_command(delay + " ".join(keys))
    _command_has_run("key_press")


def notify_host(message):
    if pynotify:
        n = pynotify.Notification("Aenea server", message)
        n.set_urgency(pynotify.URGENCY_LOW)
        if not n.show():
            print("Failed to send notification")


def write_text(text, _xdotool=None):
    """send text formatted exactly as written to active window."""
    # Workaround for https://github.com/jordansissel/xdotool/pull/29
    if text:
        flush_xdotool(_xdotool)
        write_command(text, arguments="type --file - --delay 0")
        _command_has_run("write_text")


def click_mouse(button, direction="click", count=1, count_delay=None,
    modifiers=(), _xdotool=None):
    """Click the mouse button specified. button maybe one of "right", "left",
    "middle", "wheeldown", "wheelup". This X11 server will also accept a
    number.

    """
    if (count_delay is None or count < 2):
        delay = ""
    else:
        delay = "--delay %i" % count_delay
    repeat = "" if count == 1 else "--repeat %i" % count
    try:
        button = _MOUSE_BUTTONS[button]
    except KeyError:
        button = int(button)

    command = ("%s %s %s %s" %
             (_MOUSE_CLICKS[direction], delay, repeat, button))
    if modifiers:
        modifierList = [_MOD_TRANSLATION.get(mod, mod) for mod in modifiers]
        command = _wrap_modifiers(modifierList, command)

    if _xdotool is not None:
        _xdotool.append(command)
    else:
        run_command(command)
    _command_has_run("click_mouse")


def _wrap_modifiers(modifierList, command):
    newCommand = ""
    newCommand += "keydown " + " ".join(modifierList)
    newCommand += " " + command + " "
    newCommand += "keyup " + " ".join(modifierList)
    return newCommand


def move_mouse(x, y, reference="absolute", proportional=False, phantom=None,
    dragButton=None, _xdotool=None):
    """Move the mouse to the specified coordinates. reference may be one of
    "absolute", "relative", or "relative_active". if phantom is not None,
    it is a button as click_mouse. If possible, click that location without
    moving the mouse. If not, the server will move the mouse there and click.

    """
    geo = get_geometry()
    if proportional:
        x = geo["width"] * x
        y = geo["height"] * y
    command = _MOUSE_MOVE_COMMANDS[reference]
    if command == "mousemove_active":
        command = "mousemove --window %i" % get_active_window()[0]
    commands = ["%s --sync %f %f" % (command, x, y)]
    if phantom is not None:
        commands.append("click %s" % _MOUSE_BUTTONS[phantom])
        commands.append("mousemove restore")
    commandString = " ".join(commands)
    if dragButton:
        try:
            button = _MOUSE_BUTTONS[dragButton]
        except KeyError:
            button = int(dragButton)
        commandString = _wrap_mouse_button_drag(button, commandString)
    if _xdotool is not None:
        _xdotool.extend(commands)
    else:
        run_command(commandString)


def _wrap_mouse_button_drag(button, command):
    newCommand = ""
    newCommand += "sleep 0.2 && "
    newCommand += "xdotool mousedown %d && " % button
    newCommand += "xdotool sleep 0.5 && "
    newCommand += "xdotool " + command + " && "
    newCommand += "xdotool sleep 0.2 && "
    newCommand += "xdotool mouseup %d" % button
    return newCommand


def pause(amount, _xdotool=None):
    """Pause amount in ms."""
    if _xdotool is not None:
        _xdotool.append("sleep %f" % (amount / 1000.))
    else:
        time.sleep(amount / 1000.)


def server_info(_xdotool=None):
    flush_xdotool(_xdotool)
    return _SERVER_INFO


def flush_xdotool(actions):
    if actions:
        run_command(" ".join(actions))
        del actions[:]


def switch_to_window(windowName):
    global LAST_SELECTED_APP
    windowName = windowName.lower()
    print("Trying to switch to:", windowName)
    apps = {}
    cmd = (r"search --name '\S' | "
        r"xargs -i xwininfo -id {} -stats -wm | "
        r"tr '\n' '#' | "
        r"sed -e 's/#xwininfo: Window id: \([x0-9a-f]*\) /\n\1 TITLE:/g' "
        r"-e 's/##  Absolute upper-left X:[-a-zA-Z0-9#:() ]*Map State: "
        r"\([a-zA-Z]*\)/ STATE:\1/g' "
        r"""-e 's/#  Override Redirect State:[-a-zA-Z0-9#:()+" ]*"""
        r"""Window type:#[ ]*\([a-zA-Z]*\)#[-a-zA-Z0-9#:()+" ]*"""
        r"Frame extents:[-+0-9, ]*##/ TYPE:\1/g' -e 's/#  "
        r"""Override Redirect State:[-a-zA-Z0-9#:()+" ]* """
        r"Process id:[-a-zA-Z0-9() ]*##//g' -e 's/#  "
        r"""Override Redirect State:[-a-zA-Z0-9#:()+" ]*"""
        r"""No window manager hints defined[-a-zA-Z0-9#:()+" ]*"""
        r"Frame extents:[-+0-9, ]*##//g' | "
        r"grep 'STATE:IsViewable TYPE:Normal'"
    )
    try:
        result = read_command(cmd)
        for line in result.split("\n"):
            if line:
                wid, rest1 = line.split(' TITLE:"')
                title, rest2 = rest1.split('" STATE:')  # @UnusedVariable
                apps[wid] = title.lower()
        matches = []
        _match_title(windowName, apps, matches)
        windowName = windowName.replace(" ", "")
        _match_title(windowName, apps, matches)
        matches.sort()
        import json
        print "apps: ", json.dumps(apps, indent=4)
        print "matches:", matches
        appId = None
        if len(matches) > 1 and LAST_SELECTED_APP != None:
            if not LAST_SELECTED_APP in matches:
                appId = matches[0]
            else:
                index = matches.index(LAST_SELECTED_APP)
                index += 1
                if index > (len(matches) - 1):
                    index = 0
                appId = matches[index]
        else:
            appId = matches[0]
        if appId:
            run_command("windowactivate --sync %s" % appId)
            LAST_SELECTED_APP = appId
            print("LAST_SELECTED_APP:", LAST_SELECTED_APP)
    except Exception as e:
        print(e)
    _command_has_run("switch_to_window")


def _match_title(title, apps, matches):
    for key, value in apps.items():
        if title in value:  # See if the decide title exist in existing title.
            wid = key
            if not wid in matches:
                matches.append(key)


def list_rpc_commands():
    return {
        "get_context": get_context,
        "key_press": key_press,
        "write_text": write_text,
        "click_mouse": click_mouse,
        "move_mouse": move_mouse,
        "server_info": server_info,
        "pause": pause,
        "notify_host": notify_host,
        "switch_to_window": switch_to_window,
    }


def multiple_actions(actions):
    """execute multiple rpc commands, aborting on any error.
    will not return anything ever. actions is an array of objects, possessing
    "method", "params", and "optional" keys. See also JSON-RPC multicall.
    Guaranteed to execute in specified order.

    """
    xdotool = []
    for (method, parameters, optional) in actions:
        commands = list_rpc_commands()
        if method in commands:
            commands[method](*parameters, _xdotool=xdotool, **optional)
        else:
            break
    flush_xdotool(xdotool)
    _command_has_run("multiple_actions")


def _command_has_run(cmd):
    global PREVIOUS_COMMAND
    PREVIOUS_COMMAND = cmd
    if cmd != "switch_to_window":
        LAST_SELECTED_APP = None  # Reset value for all other commands.
