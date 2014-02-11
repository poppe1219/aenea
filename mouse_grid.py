import subprocess
import re
# import json

import grid_base
import config

GRID_WINDOWS = {}
MONITORS = {}
MONITOR_SELECTED = None
MOUSE_MARK_POSITION = None


def _get_monitors():
    args = ["xrandr", "-q", "-d", ":0"]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    return _parse_xrandr_output(proc.stdout.read())


def _parse_xrandr_output(output):
    found = {}
    ys = {}
    for line in output.split("\n"):
        hitList = re.findall(r"[0-9]+x[0-9]+\+\-?[0-9]+\+\-?[0-9]+", line)
        if hitList:
            hit = hitList[0]
            split1 = hit.split("x")
            split2 = split1[1].split("+")
            monitor = {
                "width": split1[0],
                "height": split2[0],
                "x": split2[1],
                "y": split2[2]
            }
            found[hit] = monitor
            if not monitor["y"] in ys.keys():
                ys[monitor["y"]] = {}
            ys[monitor["y"]][monitor["x"]] = hit
    monitors = {}
    index = 1
    for posY in sorted(ys.keys()):
        xs = ys[posY]
        for posX in sorted(xs.keys()):
            tempKey = xs[posX]
            monitors[str(index)] = found[tempKey]
            index += 1
    return monitors


def _create_grid_windows(monitors):
    for key, monitor in MONITORS.items():
        grid = grid_base.GridConfig(
            positionX=int(monitor["x"]),
            positionY=int(monitor["y"]),
            width=int(monitor["width"]),
            height=int(monitor["height"]),
            monitorNum=key)
        gui = grid_base.TransparentWin(grid)
        gui.draw_grid()
        gui.update()
        gui.deiconify()
        gui.lift()
        gui.focus_force()
        GRID_WINDOWS[key] = gui
    if len(GRID_WINDOWS) == 1:
        GRID_WINDOWS["1"].set_single_monitor()


def mouse_grid_dispatcher(params=None):
    methodName = params["do"]
    method = globals()[methodName]
    method(params)


def mouse_grid(attributes):
    """Creates new or reuses grid windows. Can also delegate positioning."""
    global MONITORS
    global GRID_WINDOWS
    for key, window in GRID_WINDOWS.items():
        window.refresh()


def hide_grids(attributes):
    """Hides the grids, optionally excluding one grid.

    Grids are not closed but instead hidden, so they can be reused later.
    If excludePosition matches the position of a grid, it is not hidden.

    """
    global GRID_WINDOWS
    global MONITOR_SELECTED
    print("hide_grids: %s" % attributes)
    excludePosition = attributes.get("excludePosition", None)
    count = 0
    for index, win in GRID_WINDOWS.items():
        if excludePosition and str(excludePosition) == index:
            continue
        if win.winfo_viewable():
            win.withdraw()
        count += 1
    if count == len(GRID_WINDOWS):
        MONITOR_SELECTED = None


def mouse_pos(attributes):
    """Selects monitor (if not already selected), then repositions the grid.

    Takes multiple positions in sequence. If a monitor is not already selected,
    the first position variable is used to select monitor.
    The position variables are treated in sequence to select sections that the
    grid is moved into.

    """
    print("mouse_pos: %s" % attributes)


def go(attributes):
    """Places the mouse at the grid coordinates. Hides the grid."""
    print("go: %s" % attributes)


def left_click(attributes):
    """Places the mouse the grid coordinates and clicks the left mouse
    button.

    """
    print("left_click: %s" % attributes)


def right_click(attributes):
    """Places the mouse the grid coordinates and clicks the the right mouse
    button.

    """
    print("right_click: %s" % attributes)


def double_click(attributes):
    """Places the mouse the grid coordinates and double clicks the left mouse
    button.

    """
    print("double_click: %s" % attributes)


def control_click(attributes):
    """Places the mouse the grid coordinates and holds down the CTRL-key while
    clicking the left mouse button.

    """
    print("control_click: %s" % attributes)


def shift_click(attributes):
    """Places the mouse the grid coordinates and holds down the SHIFT-key while
    clicking the left mouse button.

    """
    print("shift_click: %s" % attributes)


def mouse_mark(attributes):
    """Remembers the grid coordinates, to be used as a start position for
    mouse drag.

    """
    print("mouse_mark: %s" % attributes)


def mouse_drag(attributes):
    """Holds down the left mouse button while moving the mouse mouse from a
    previous position to the current position.

    """
    print("mouse_drag: %s" % attributes)


#  Initialize the information about monitors and the grid windows.
if not MONITORS:
    MONITORS = _get_monitors()
elif not MONITORS:
    MONITORS = config.MONITORS
if not GRID_WINDOWS:
    _create_grid_windows(MONITORS)
    hide_grids({})


if __name__ == "__main__":
    test1 = """Screen 0: minimum 8 x 8, current 2560 x 1024, maximum 8192 x 8192  # @IgnorePep8
    DVI-I-0 disconnected (normal left inverted right x axis y axis)
    VGA-0 connected 1280x1024+1280+0 (normal left inverted right x axis y axis) 376mm x 301mm  # @IgnorePep8
       1280x1024      75.0*+   60.0
       1024x768       75.0     60.0
       800x600        75.0     72.2     60.3
       640x480        75.0     72.8     59.9
    DVI-I-1 connected primary 1280x1024+0+0 (normal left inverted right x axis y axis) 376mm x 301mm  # @IgnorePep8
       1280x1024      60.0*+   75.0
       1280x960       60.0
       1152x864       75.0
       1024x768       75.0     70.1     60.0
       800x600        75.0     72.2     60.3     56.2
       640x480        75.0     72.8     59.9
       640x400        70.1
    HDMI-0 disconnected (normal left inverted right x axis y axis)
    """

    test2 = """
    foo 1280x1024+-1280+0 bar
    foo 1280x1024+0+0 bar
    """

    test3 = """
    foo 1280x1024+1280+1024 bar
    foo 1280x1024+1280+0 bar
    foo 1280x1024+0+1024 bar
    foo 1280x1024+0+0 bar
    """

    monitors = _parse_xrandr_output(test1)
    print(monitors)
    monitors = _parse_xrandr_output(test2)
    print(monitors)
    monitors = _parse_xrandr_output(test3)
    print(monitors)
