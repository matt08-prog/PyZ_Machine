import tkinter as tk
from tkinter import messagebox

root = tk.Tk()

def on_closing(root):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

root.mainloop()