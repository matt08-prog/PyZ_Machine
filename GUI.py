import os
import queue
import threading
from time import sleep
import tkinter as tk
from tkinter import scrolledtext, messagebox, Entry

possible_colors = ["white", "blue", "green", "red", "cyan", "yellow", "purple", "pink", "green2", "turquoise1", "MediumPurple1", "DodgerBlue", "DodgerBlue3"]
special_colors = {
    "scroll": {"font": ("Arial", 32), "foreground": "red"},
    "bold": {"font": ("Arial", 12), "foreground": "white"},
    "underline": {"font": ("Arial", 10), "foreground": "white", "underline": True}
}
class GUI:
    def __init__(self):
        pass

    def init_GUI(self, queue, should_ask_before_closing_window):
        self.queue = queue

        root = tk.Tk()
        root.state("zoomed")
        root.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(root, should_ask_before_closing_window))
        gui = DualPanelGUI(root)

        # Example usage of add_text function
        # gui.add_text("left", "This is cyan text in the left panel\n", "cyan")
        # gui.add_text("right", "This is white text in the right panel\n", "white")
        # gui.add_text("right", "This is red text in the right panel\n", "red")

        for color in possible_colors:
            # Configure text colors for the right panel
            gui.left_panel.tag_config(color, foreground=color)
            # Configure text colors for the right panel
            gui.right_panel.tag_config(color, foreground=color)
        for color_name, props in special_colors.items():
            # gui.right_panel.tag_config("scroll", foreground="red", font=("Arial", 32))
            should_underline = "underline" in props.keys()
            gui.right_panel.tag_config(color_name, foreground=props["foreground"], font=props["font"], underline=should_underline)
            gui.left_panel.tag_config(color_name, foreground=props["foreground"], font=props["font"], underline=should_underline)


        self.run_gui(root, gui)

    def run_gui(self, root, gui):
        def update():
            try:
                # consume data from main thread
                while not self.queue.empty():
                    data_object = self.queue.get(False)
                    # print(f"recieved text_data_object: {data_object}")

                    if data_object["text_color"] not in possible_colors and data_object["text_color"] not in special_colors.keys():
                        print(f"{data_object["text_color"]} is not one of the current colors the GUI is ready to accept")
                        os._exit(1)

                    gui.add_text(
                        data_object["text_location"], 
                        data_object["text"],
                        data_object["text_color"],
                        data_object["should_scroll"]
                        )
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

        # Create top right search bar
        self.search_frame = tk.Frame(master)
        self.search_frame.grid(row=0, column=1, sticky="ne", padx=10, pady=5)
        
        self.search_entry = Entry(self.search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT)
        
        self.search_button = tk.Button(self.search_frame, text="Search", command=self.search)
        self.search_button.pack(side=tk.LEFT)

        # Create left panel (CYAN text)
        self.left_panel = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=40, height=20)
        self.left_panel.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.left_panel.config(bg="black")

        # Create right panel (WHITE and RED text)
        self.right_panel = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=40, height=20)
        self.right_panel.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.right_panel.config(bg="black")

        # Configure grid weights
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_rowconfigure(1, weight=1)

    def search(self):
        search_term = self.search_entry.get()
        start_index = "1.0"
        
        # Find the position of the search term
        pos = self.right_panel.search(search_term, start_index, stopindex=tk.END, nocase=1)
        
        if pos:
            # Calculate the line number of the found text
            line_number = int(pos.split('.')[0])
            
            # Calculate the total number of lines in the text widget
            total_lines = int(self.right_panel.index(tk.END).split('.')[0])
            
            # Calculate the fraction to scroll to
            fraction = (line_number - 1) / total_lines
            
            # Scroll to the calculated fraction
            self.right_panel.yview_moveto(fraction)
            
            # Highlight the found text
            end_pos = f"{pos}+{len(search_term)}c"
            self.right_panel.tag_add("search", pos, end_pos)
            self.right_panel.tag_config("search", background="grey")
            
            messagebox.showinfo("Search", f"Found '{search_term}' at position {pos}")
        else:
            messagebox.showinfo("Search", f"'{search_term}' not found")

    def add_text(self, panel, text, color, should_scroll=False):
        if panel == "left":
            self.left_panel.config(state=tk.NORMAL)
            self.left_panel.insert(tk.END, text, color)
            self.left_panel.config(state=tk.DISABLED)
        elif panel == "right":
            self.right_panel.config(state=tk.NORMAL)
            self.right_panel.insert(tk.END, text, color)
            self.right_panel.config(state=tk.DISABLED)
        if should_scroll:
            self.right_panel.update_idletasks()  # Update the widget
            self.right_panel.yview_moveto(1.0)  # Scroll to the bottom

            self.left_panel.update_idletasks()  # Update the widget
            self.left_panel.yview_moveto(1.0)  # Scroll to the bottom