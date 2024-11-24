import os
import queue
import threading
from time import sleep
import tkinter as tk
from tkinter import scrolledtext, messagebox

class GUI:
    def __init__(self):
        pass

    def init_GUI(self, queue, should_ask_before_closing_window):
        self.queue = queue

        root = tk.Tk()
        root.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(root, should_ask_before_closing_window))
        gui = DualPanelGUI(root)

        # Example usage of add_text function
        gui.add_text("left", "This is cyan text in the left panel\n", "cyan")
        gui.add_text("right", "This is white text in the right panel\n", "white")
        gui.add_text("right", "This is red text in the right panel\n", "red")

        # Configure text colors for the right panel
        gui.right_panel.tag_config("white", foreground="white")
        gui.right_panel.tag_config("red", foreground="red")

        self.run_gui(root, gui)
        print("after thread start")

    def run_gui(self, root, gui):
        def update():
            try:
                # consume data from main thread
                data = self.queue.get(False)
                gui.add_text("left", data, "green")
            except queue.Empty:
                pass
            
            # Schedule the next update
            root.after(200, update)

        # Start the update cycle
        update()
        
        # Start the Tkinter main loop
        root.mainloop()



    def on_closing(self, root, should_ask):
        if should_ask:
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                root.destroy()
                os._exit(1)
        else:
            root.destroy()
            os._exit(1)

class DualPanelGUI:
    def __init__(self, master):
        self.master = master
        master.title("Dual Panel GUI")

        # Create left panel (CYAN text)
        self.left_panel = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=40, height=20)
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_panel.config(bg="black", fg="cyan")

        # Create right panel (WHITE and RED text)
        self.right_panel = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=40, height=20)
        self.right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_panel.config(bg="black")

        # Configure grid weights
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_rowconfigure(0, weight=1)

    def add_text(self, panel, text, color):
        if panel == "left":
            self.left_panel.config(state=tk.NORMAL)
            self.left_panel.insert(tk.END, text)
            self.left_panel.config(state=tk.DISABLED)
        elif panel == "right":
            self.right_panel.config(state=tk.NORMAL)
            self.right_panel.insert(tk.END, text, color)
            self.right_panel.config(state=tk.DISABLED)