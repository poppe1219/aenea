#!/usr/bin/python

import os
import sys
import jsonrpclib.SimpleJSONRPCServer

import config

mouseGridModule = None
# Import OS-specific methods.
if os.name == "nt":
    from methods_win import (get_context, notify_host,  # @UnusedImport
        multiple_actions, list_rpc_commands)  # @UnusedImport
    import methods_win as methodsModule  # @UnusedImport
elif os.name == "posix":
    from methods_x11 import (get_context, notify_host,  # @Reimport
        multiple_actions, list_rpc_commands)  # @Reimport
    import methods_x11 as methodsModule  # @Reimport
    try:
        from mouse_grid import mouse_grid_dispatcher
        import mouse_grid
        mouseGridModule = mouse_grid
    except ImportError as e:
        mouse_grid_dispatcher = lambda params: None
        print("No mousegrid: %s" % e)
else:
    raise Exception("OS not supported.")


def setup_server(host, port):
    server = jsonrpclib.SimpleJSONRPCServer.SimpleJSONRPCServer((host, port))

    for command in list_rpc_commands():
        server.register_function(methodsModule.__dict__[command])
    if mouseGridModule:
        server.register_function(mouseGridModule.mouse_grid_dispatcher)
    server.register_function(multiple_actions)
    return server


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[-1] == "getcontext":
        ctx = get_context()
        try:
            import pprint
            pprint.pprint(ctx)
        except ImportError:
            print ctx
    else:
        if "-d" in sys.argv or "--daemon" in sys.argv:
            if os.fork() == 0:  # @UndefinedVariable
                os.setsid()  # @UndefinedVariable
                if os.fork() == 0:  # @UndefinedVariable
                    os.chdir("/")
                    os.umask(0)
                    # Safe upper bound on number of fds we could possibly
                    # have opened.
                    for fd in range(64):
                        try:
                            os.close(fd)
                        except OSError:
                            pass
                    os.open(os.devnull, os.O_RDWR)
                    os.dup2(0, 1)
                    os.dup2(0, 2)
                else:
                    os._exit(0)
            else:
                os._exit(0)
    port = 8888
    server = setup_server(config.HOST, port)
    notify_host("Starting on %s:%s" % (config.HOST, port))
    server.serve_forever()
