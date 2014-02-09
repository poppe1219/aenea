

def mouse_grid_dispatcher(params=None):
    print("%s" % params)
    methodName = params["do"]
    method = globals()[methodName]
    method(params)


def mouse_grid(attributes):
    """Creates new or reuses grid windows. Can also delegate positioning."""
    print("mouse_grid: %s" % attributes)


def hide_grids(attributes):
    """Hides the grids, optionally excluding one grid.

    Grids are not closed but instead hidden, so they can be reused later.
    If excludePosition matches the position of a grid, it is not hidden.

    """
    print("hide_grids: %s" % attributes)


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
