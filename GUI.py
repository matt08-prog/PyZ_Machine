import os
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

class GUI:
    def __init__(self):
        pass

    def init_GUI(self, queue):
        self.queu = queue

        root = tk.Tk()
        root.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(root))
        gui = DualPanelGUI(root)

        # Example usage of add_text function
        gui.add_text("left", "This is cyan text in the left panel\n", "cyan")
        gui.add_text("right", "This is white text in the right panel\n", "white")
        gui.add_text("right", "This is red text in the right panel\n", "red")

        # Configure text colors for the right panel
        gui.right_panel.tag_config("white", foreground="white")
        gui.right_panel.tag_config("red", foreground="red")

        self.run_gui(root)
        print("after thread start")


    def run_gui(self, root):
        while 1:
            # root.mainloop()
            root.update()
            # exit(-1)
            
            # print("after mainloop start")

    def on_closing(self, root):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
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