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


import Tkinter as tk
import tkFont
# import datetime
# import sys
import threading
import ttk


class ServerWindow(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.wm_title("Aenea server")
        self.geometry('400x600+400+0')
#         self.overrideredirect(True)
        self.wait_visibility(self)
        note = ttk.Notebook(self)
        self.tab1 = tk.Frame(note)
        self.tab2 = tk.Frame(note)
        w = tk.LabelFrame(self.tab1, text=u"Controls")
        w.pack(side=tk.TOP, fill=tk.BOTH)
        self.button1 = tk.Button(
                w,
                text=u"Start server",
                command=self.start_capture
            )
        self.button1.pack(side=tk.LEFT)
        self.button2 = tk.Button(
                w,
                text=u"Stop server",
                command=self.stop_capture,
                state=tk.DISABLED
            )
        self.button2.pack(side=tk.LEFT)
        self.button3 = tk.Button(
                w,
                text=u"Clear box",
                command=self.clear_text
            )
        self.button3.pack(side=tk.LEFT)
        self.display_entered_text = tk.IntVar()
        self.checkbox1 = tk.Checkbutton(
                w,
                text="Display entered text",
                variable=self.display_entered_text
            )
        self.checkbox1.pack(side=tk.LEFT)
        self.button4 = tk.Button(
                w,
                text=u"Close",
                command=self.exit
            )
        self.button4.pack(side=tk.RIGHT)

        dFont = tkFont.Font(family="Tahoma", size=8)

        l = tk.Label(self.tab1, text=u"Capture:")
        l.pack(side=tk.TOP)

        self.tab1.text1 = tk.Text(self.tab1, width=16, height=5, font=dFont)
        yscrollbar = tk.Scrollbar(
                self.tab1.text1,
                orient=tk.VERTICAL,
                command=self.tab1.text1.yview
            )
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tab1.text1["yscrollcommand"] = yscrollbar.set
        self.tab1.text1.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.tab1.pack(side=tk.TOP, fill=tk.X)
        self.tab1.text1.bind("<FocusIn>", lambda event: self.focus())

        l = tk.Label(self.tab1, text=u"Log:")
        l.pack(side=tk.TOP)

        self.tab1.text2 = tk.Text(self.tab1, width=16, height=5, font=dFont)
        yscrollbar = tk.Scrollbar(
                self.tab1.text2,
                orient=tk.VERTICAL,
                command=self.tab1.text2.yview
            )
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tab1.text2["yscrollcommand"] = yscrollbar.set
        self.tab1.text2.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.tab1.pack(side=tk.TOP,  fill=tk.X)
        self.tab1.text2.bind("<FocusIn>", lambda event: self.focus())

        l = tk.Label(self.tab2, text=u"Todo...")
        l.pack(side=tk.LEFT)

        note.add(self.tab1, text="Capturing")
        note.add(self.tab2, text="Configuration")
        note.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

        try:
            self.client = communications.Proxy(ip, int(port))
            self.client_proxy = communications.BatchProxy()
        except Exception as e:
            self.log(str(e))

        threading.Thread(target=self.worker_thread).start()


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
