import re
import subprocess
import traceback
# import json

import grid_base
import config
from methods_x11 import move_mouse, click_mouse


class GridStates:
    NothingSelected = 0
    MonitorsSelected = 1


GRID_DATA = {
    "grid_windows": {},
    "monitors": {},
    "mark_position": {},
    "monitor_selected": None,
    "grid_state": GridStates.NothingSelected,
}


def _get_monitors():
    try:
        args = ["xrandr", "-q", "-d", ":0"]
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        return _parse_xrandr_output(proc.stdout.read())
    except:
        return None


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


def _create_grid_windows():
    gridData = _get_grid_data()
    for key, monitor in gridData["monitors"].items():
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
        gridData["grid_windows"][key] = gui
    if len(gridData["grid_windows"]) == 1:
        gridData["grid_windows"]["1"].set_single_monitor()


def mouse_grid_dispatcher(params=None):
    methodName = params["do"]
    method = globals()[methodName]
    print("mouse_grid_dispatcher: %s, arguments: %s" % (methodName, params))
    try:
        method(params.get("attributes"))
    except Exception:
        traceback.print_exc()


def mouse_grid(attributes):
    """Creates new or reuses grid windows. Can also delegate positioning."""
    gridData = _get_grid_data()
    pos1 = attributes.get(u"pos1")
    if pos1:
        if len(gridData["monitors"]) > 1:
            print("More than one monitor")
            newAttr = {}
            gridData["monitor_selected"] = pos1
            for i in range(1, 9):
                value = attributes.get("pos%d" % (i + 1))
                if value:
                    newAttr["pos%d" % i] = value
            newAttr["action"] = attributes.get("action")
            mouse_pos(newAttr)
        elif attributes.get("pos1"):
            gridData["monitor_selected"] = 1  # Only one monitor.
            mouse_pos(attributes)
    else:
        print("No position arguments given.")
        gridData["monitor_selected"] = None
        for window in gridData["grid_windows"].values():
            window.refresh()


def hide_grids(attributes):
    """Hides the grids, optionally excluding one grid.

    Grids are not closed but instead hidden, so they can be reused later.
    If excludePosition matches the position of a grid, it is not hidden.

    """
    gridData = _get_grid_data()
    print("hide_grids: %s" % attributes)
    for win in gridData["grid_windows"].values():
        gridConfig = win.get_grid()
        gridConfig.reset()
        if win.winfo_viewable():
            win.withdraw()
    if len(gridData["monitors"]) > 1:
        gridData["monitor_selected"] = None


def go(attributes):
    """Places the mouse at the grid coordinates. Hides the grid."""
    print("go: %s" % attributes)
    win = _get_active_grid_window()
    gridConfig = win.get_grid()
    (x, y) = gridConfig.get_absolute_centerpoint()
    move_mouse(x, y)
    hide_grids({})


def left_click(attributes):
    """Places the mouse the grid coordinates and clicks the left mouse
    button.

    """
    print("left_click: %s" % attributes)
    hide_grids({})


def right_click(attributes):
    """Places the mouse the grid coordinates and clicks the the right mouse
    button.

    """
    print("right_click: %s" % attributes)
    hide_grids({})


def double_click(attributes):
    """Places the mouse the grid coordinates and double clicks the left mouse
    button.

    """
    print("double_click: %s" % attributes)
    hide_grids({})


def control_click(attributes):
    """Places the mouse the grid coordinates and holds down the CTRL-key while
    clicking the left mouse button.

    """
    print("control_click: %s" % attributes)
    hide_grids({})


def shift_click(attributes):
    """Places the mouse the grid coordinates and holds down the SHIFT-key while
    clicking the left mouse button.

    """
    print("shift_click: %s" % attributes)
    hide_grids({})


def mouse_mark(attributes):
    """Remembers the grid coordinates, to be used as a start position for
    mouse drag.

    """
    print("mouse_mark: %s" % attributes)
    hide_grids({})


def mouse_drag(attributes):
    """Holds down the left mouse button while moving the mouse mouse from a
    previous position to the current position.

    """
    print("mouse_drag: %s" % attributes)
    hide_grids({})


actions = {
    "[left] click": left_click,
    "right click": right_click,
    "double click": double_click,
    "control click": control_click,
    "shift click": shift_click,
    "mark": mouse_mark,
    "drag": mouse_drag,
    "go": go,
}


def mouse_pos(attributes):
    """Selects monitor (if not already selected), then repositions the grid.

    Takes multiple positions in sequence. If a monitor is not already selected,
    the first position variable is used to select monitor.
    The position variables are treated in sequence to select sections that the
    grid is moved into.

    """
    gridData = _get_grid_data()
    print("--- mouse_pos ---")
    print("attributes: %s" % attributes)
    firstAttr = 1
    if not gridData["monitor_selected"]:
        position = attributes["pos1"]
        if position > len(gridData["monitors"]):
            return
        gridData["monitor_selected"] = position
        firstAttr = 2
        for index, window in gridData["grid_windows"].items():
            if not index == gridData["monitor_selected"]:
                window.clear()
    print("monitor_selected: %d" % gridData["monitor_selected"])
    print("firstAttr: %d" % firstAttr)
    win = _get_active_grid_window()
    if win:
        for index in range(firstAttr, 10):
            position = attributes.get("pos%d" % index)
            if position:
                _reposition_grid(win, position)
        action = attributes.get("action")
        if action:
            actions[action]
            gridData["monitor_selected"] = None
        else:
            win.refresh()


def _get_grid_data():
    global GRID_DATA
    return GRID_DATA


def _get_active_grid_window():
    gridData = _get_grid_data()
    selectedMonitor = gridData["monitor_selected"]
    if selectedMonitor != None:
        return gridData["grid_windows"][str(selectedMonitor)]
    else:
        return None


def _reposition_grid(win, section):
    """Repositions the grid window to a specified section in the grid.

    If the grid is smaller than 25 pixels across, the grid is not repositioned
    into a section, but instead moved one section width in the direction of
    the selected section.

    """
    print("--- _reposition_grid ---")
    print("win: %s" % win)
    print("section: %d" % section)
    grid = win.get_grid()
    if grid.width > 25:
        grid.recalculate_to_section(section)
        grid.calculate_axis()
    else:
        grid.move_to_section(section)


#  Initialize the information about monitors and the grid windows.
if not GRID_DATA["monitors"]:
    GRID_DATA["monitors"] = _get_monitors()
if not GRID_DATA["monitors"]:
    GRID_DATA["monitors"] = config.MONITORS
if not GRID_DATA["grid_windows"]:
    _create_grid_windows()
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
