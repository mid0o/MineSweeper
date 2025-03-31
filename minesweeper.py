""" 
Minesweeper game
Developed by Muhammad Saeed (https://github.com/mid0o)
"""
from tkinter import *
from tkinter import messagebox, ttk
from random import randint
from datetime import datetime
import json
import os
import sys
from PIL import Image, ImageTk
import winsound
import threading

# Get correct path to resources
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Minesweeper:
    """ Our game class """

    def __init__(self, tk):
        """ Initialize the game """
        # Define color scheme
        self.colors = {
            "bg": "#121212",
            "fg": "#FFFFFF", 
            "button_bg": "#1F1F1F",
            "button_fg": "#FFFFFF",
            "accent": "#BB86FC",
            "error": "#CF6679",
            "success": "#03DAC5"
        }
        
        # Sound effects (more pleasant sounds)
        self.sounds = {
            "click": 800,   # Regular click sound
            "flag": 900,    # Flag sound
            "win": 1500,    # Win sound
            "lose": 400,    # Lose sound
            "hint": 1200    # New sound for hints
        }
        
        # Enable sound by default
        self.sound_on = True
        
        # Store high scores
        self.high_scores = self.load_high_scores()

        # Create the main window
        self.tk = tk
        self.tk.title("Minesweeper - By Muhammad Saeed")
        self.tk.configure(bg=self.colors["bg"])
        self.tk.resizable(False, False)
        
        # Initialize difficulty settings
        self.difficulties = {
            "easy": {"size": 9, "mines": 10},
            "medium": {"size": 16, "mines": 40},
            "hard": {"size": 20, "mines": 80}  # Reduced from 24x24 to 20x20
        }
        
        # Default difficulty
        self.current_difficulty = "easy"
        self.size = self.difficulties[self.current_difficulty]["size"]
        self.selected_mines = self.difficulties[self.current_difficulty]["mines"]
        
        # Check if we should use modern images
        self.use_modern_tiles = True  # True to use modern tiles, False for original
        
        # Initialize image paths
        self.tile_paths = {}
        self.number_paths = []
        
        # Try to create modern tiles directory if it doesn't exist
        try:
            modern_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images/modern")
            if not os.path.exists(modern_dir):
                os.makedirs(modern_dir, exist_ok=True)
                
            # Store standard paths for classic images
            self.classic_paths = {
                "tile": resource_path("images/unclicked_tile.png"),
                "mine": resource_path("images/unclicked_mine_tile.png"),
                "flag": resource_path("images/flag_tile.png"),
                "clicked_mine": resource_path("images/clicked_mine_tile.png"),
                "wrong_flag": resource_path("images/wrong_flag_tile.png"),
                "hint": resource_path("images/flag_tile.png")  # Reuse flag for hint in classic
            }
            self.classic_number_paths = [resource_path(f"images/num{i}_tile.png") for i in range(9)]
            
            # Create modern tiles if they don't exist
            if not os.path.exists(os.path.join(modern_dir, "unclicked_tile.png")):
                self.tile_paths, self.number_paths = create_modern_tiles()
            else:
                # Just set paths to existing modern tiles
                self.tile_paths = {
                    "tile": os.path.join(modern_dir, "unclicked_tile.png"),
                    "mine": os.path.join(modern_dir, "unclicked_mine_tile.png"),
                    "flag": os.path.join(modern_dir, "flag_tile.png"),
                    "clicked_mine": os.path.join(modern_dir, "clicked_mine_tile.png"),
                    "wrong_flag": os.path.join(modern_dir, "wrong_flag_tile.png"),
                    "hint": os.path.join(modern_dir, "hint_tile.png")
                }
                self.number_paths = [os.path.join(modern_dir, f"num{i}_tile.png") for i in range(9)]
                
        except Exception as e:
            print(f"Could not create modern tiles: {e}")
            self.use_modern_tiles = False
            
            # Fallback to classic paths
            self.tile_paths = self.classic_paths
            self.number_paths = self.classic_number_paths
        
        # Show the main menu first
        self.show_main_menu()
        
    def show_main_menu(self):
        """ Show the main menu screen """
        # Clear any existing frames
        for widget in self.tk.winfo_children():
            widget.destroy()
            
        # Create main menu frame
        self.main_menu_frame = Frame(self.tk, bg=self.colors["bg"], padx=20, pady=20)
        self.main_menu_frame.pack(expand=True, fill="both")
        
        # Title
        title_label = Label(self.main_menu_frame, text="MINESWEEPER", 
                          font=("Arial", 24, "bold"), bg=self.colors["bg"], 
                          fg=self.colors["accent"], pady=20)
        title_label.pack()
        
        # Author credit
        author_label = Label(self.main_menu_frame, text="By Muhammad Saeed", 
                           font=("Arial", 12), bg=self.colors["bg"], 
                           fg=self.colors["fg"])
        author_label.pack(pady=(0, 30))
        
        # Style for buttons
        button_style = {"font": ("Arial", 12), "width": 20, "height": 2, 
                        "bg": self.colors["button_bg"], "fg": self.colors["fg"],
                        "activebackground": self.colors["accent"]}
        
        # Difficulty selection
        difficulty_frame = Frame(self.main_menu_frame, bg=self.colors["bg"], pady=10)
        difficulty_frame.pack()
        
        difficulty_label = Label(difficulty_frame, text="Select Difficulty:", 
                               font=("Arial", 12), bg=self.colors["bg"], 
                               fg=self.colors["fg"])
        difficulty_label.pack(pady=(0, 10))
        
        self.difficulty_var = StringVar(value=self.current_difficulty)
        
        # Difficulty radio buttons in a row
        for diff in ["easy", "medium", "hard"]:
            diff_btn = Radiobutton(difficulty_frame, text=diff.capitalize(), 
                                  variable=self.difficulty_var, value=diff,
                                  command=self.set_difficulty,
                                  font=("Arial", 11), bg=self.colors["bg"], 
                                  fg=self.colors["fg"], 
                                  selectcolor=self.colors["button_bg"],
                                  activebackground=self.colors["bg"])
            diff_btn.pack(side=LEFT, padx=10)
        
        # Game buttons
        play_button = Button(self.main_menu_frame, text="Play Game", 
                            command=self.start_game, **button_style)
        play_button.pack(pady=10)
        
        scores_button = Button(self.main_menu_frame, text="High Scores", 
                              command=self.show_high_scores, **button_style)
        scores_button.pack(pady=10)
        
        quit_button = Button(self.main_menu_frame, text="Quit", 
                            command=self.tk.destroy, **button_style)
        quit_button.pack(pady=10)
    
    def set_difficulty(self):
        """ Set the game difficulty """
        self.current_difficulty = self.difficulty_var.get()
        self.size = self.difficulties[self.current_difficulty]["size"]
        self.selected_mines = self.difficulties[self.current_difficulty]["mines"]
    
    def load_high_scores(self):
        """ Load high scores from file """
        if os.path.exists("high_scores.json"):
            try:
                with open("high_scores.json", "r") as file:
                    return json.load(file)
            except:
                pass
        return {"easy": [], "medium": [], "hard": []}
    
    def save_high_score(self, time):
        """ Save a new high score """
        # Add the score to the list
        self.high_scores[self.current_difficulty].append({"time": time, "date": datetime.now().strftime("%Y-%m-%d")})
        
        # Sort the list and keep top 5
        self.high_scores[self.current_difficulty] = sorted(
            self.high_scores[self.current_difficulty], 
            key=lambda x: x["time"]
        )[:5]
        
        # Save to file
        with open("high_scores.json", "w") as file:
            json.dump(self.high_scores, file)
            
    def show_high_scores(self):
        """ Show the high scores screen """
        # Clear any existing frames
        for widget in self.tk.winfo_children():
            widget.destroy()
            
        # Create high scores frame
        high_scores_frame = Frame(self.tk, bg=self.colors["bg"], padx=20, pady=20)
        high_scores_frame.pack(expand=True, fill="both")
        
        # Title
        title_label = Label(high_scores_frame, text="HIGH SCORES", 
                          font=("Arial", 24, "bold"), bg=self.colors["bg"], 
                          fg=self.colors["accent"], pady=20)
        title_label.pack()
        
        # Create notebook for different difficulties
        notebook = ttk.Notebook(high_scores_frame)
        notebook.pack(pady=20, fill="both", expand=True)
        
        # Style for the notebook
        style = ttk.Style()
        style.configure("TNotebook", background=self.colors["bg"])
        style.configure("TNotebook.Tab", background=self.colors["button_bg"], 
                        foreground=self.colors["fg"], padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", self.colors["accent"])],
                 foreground=[("selected", self.colors["bg"])])
        
        # Add a tab for each difficulty
        for diff in ["easy", "medium", "hard"]:
            tab = Frame(notebook, bg=self.colors["bg"])
            notebook.add(tab, text=diff.capitalize())
            
            # Create a list of high scores
            if self.high_scores[diff]:
                # Table headers
                Label(tab, text="Rank", font=("Arial", 12, "bold"), 
                     bg=self.colors["bg"], fg=self.colors["accent"], width=5).grid(row=0, column=0, padx=5, pady=5)
                Label(tab, text="Time", font=("Arial", 12, "bold"), 
                     bg=self.colors["bg"], fg=self.colors["accent"], width=10).grid(row=0, column=1, padx=5, pady=5) 
                Label(tab, text="Date", font=("Arial", 12, "bold"), 
                     bg=self.colors["bg"], fg=self.colors["accent"], width=15).grid(row=0, column=2, padx=5, pady=5)
                
                # Add scores
                for i, score in enumerate(self.high_scores[diff]):
                    Label(tab, text=f"{i+1}", font=("Arial", 12), 
                         bg=self.colors["bg"], fg=self.colors["fg"]).grid(row=i+1, column=0, padx=5, pady=5)
                    Label(tab, text=f"{score['time']} sec", font=("Arial", 12), 
                         bg=self.colors["bg"], fg=self.colors["fg"]).grid(row=i+1, column=1, padx=5, pady=5)
                    Label(tab, text=f"{score['date']}", font=("Arial", 12), 
                         bg=self.colors["bg"], fg=self.colors["fg"]).grid(row=i+1, column=2, padx=5, pady=5)
            else:
                Label(tab, text="No scores yet!", font=("Arial", 12), 
                     bg=self.colors["bg"], fg=self.colors["fg"], pady=20).pack()
        
        # Back button
        back_button = Button(high_scores_frame, text="Back to Menu", 
                           command=self.show_main_menu, font=("Arial", 12),
                           bg=self.colors["button_bg"], fg=self.colors["fg"],
                           activebackground=self.colors["accent"])
        back_button.pack(pady=20)
    
    def start_game(self):
        """ Start the actual game """
        # Clear any existing frames
        for widget in self.tk.winfo_children():
            widget.destroy()
            
        # Main container
        main_container = Frame(self.tk, bg=self.colors["bg"])
        main_container.pack(fill=BOTH, expand=True)
        
        # Create header frame for time and mine count
        header_frame = Frame(main_container, bg=self.colors["bg"])
        header_frame.pack(fill=X, padx=10, pady=(10, 0))
        
        # Time label with modern look
        time_frame = Frame(header_frame, bg=self.colors["button_bg"], padx=10, pady=5, relief="raised", borderwidth=1)
        time_frame.pack(side=LEFT, fill=X, expand=True)
        clock_icon = Label(time_frame, text="⏱️", bg=self.colors["button_bg"], fg=self.colors["fg"])
        clock_icon.pack(side=LEFT, padx=(0, 5))
        self.time_label = Label(time_frame, text="Time: 0", bg=self.colors["button_bg"], fg=self.colors["fg"], font=("Arial", 10, "bold"))
        self.time_label.pack(side=LEFT)
        
        # Progress bar for time (visual indicator of time passed)
        self.time_progress = Canvas(time_frame, width=100, height=10, bg=self.colors["bg"], highlightthickness=0)
        self.time_progress.pack(side=RIGHT, padx=(10, 0))
        
        # Mines left counter with modern look
        mine_frame = Frame(header_frame, bg=self.colors["button_bg"], padx=10, pady=5, relief="raised", borderwidth=1)
        mine_frame.pack(side=RIGHT)
        mine_icon = Label(mine_frame, text="💣", bg=self.colors["button_bg"], fg=self.colors["fg"])
        mine_icon.pack(side=LEFT, padx=(0, 5))
        self.mine_label = Label(mine_frame, text=f"Mines: {self.selected_mines}", bg=self.colors["button_bg"], fg=self.colors["fg"], font=("Arial", 10, "bold"))
        self.mine_label.pack(side=LEFT)

        # Create game area (scrollable for hard difficulty)
        game_container = Frame(main_container)
        game_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        if self.current_difficulty == "hard":
            # Create a canvas with scrollbars
            canvas = Canvas(game_container, bg=self.colors["bg"])
            
            # Add vertical scrollbar
            v_scrollbar = Scrollbar(game_container, orient=VERTICAL, command=canvas.yview)
            v_scrollbar.pack(side=RIGHT, fill=Y)
            canvas.configure(yscrollcommand=v_scrollbar.set)
            
            # Add horizontal scrollbar
            h_scrollbar = Scrollbar(game_container, orient=HORIZONTAL, command=canvas.xview)
            h_scrollbar.pack(side=BOTTOM, fill=X)
            canvas.configure(xscrollcommand=h_scrollbar.set)
            
            # Pack the canvas
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            
            # Create a frame inside the canvas for the game grid
            self.frame = Frame(canvas, bg=self.colors["bg"])
            
            # Add the frame to the canvas
            canvas.create_window((0, 0), window=self.frame, anchor="nw")
            
            # Configure the scroll region when the frame size changes
            self.frame.bind("<Configure>", lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            ))
        else:
            # For easy and medium difficulty, use a simple frame
            self.frame = Frame(game_container, bg=self.colors["bg"])
            self.frame.pack(fill=BOTH, expand=True)

        # Create a label with the game over message (outside the scrollable area)
        self.message_label = Label(main_container, text="", font=("Arial", 14, "bold"), bg=self.colors["bg"], fg=self.colors["accent"])
        self.message_label.pack(pady=10)

        # Create control buttons area (outside the scrollable area)
        control_container = Frame(main_container, bg=self.colors["bg"], pady=10)
        control_container.pack(side=BOTTOM, fill=X)

        # Create cool game controls in two rows
        # Main control frame
        control_panel = Frame(control_container, bg=self.colors["bg"])
        control_panel.pack()
        
        # First row - Game actions
        game_actions = Frame(control_panel, bg=self.colors["bg"], pady=5)
        game_actions.pack(fill="x")
        
        # Button style
        button_style = {"font": ("Arial", 10, "bold"), "bg": self.colors["button_bg"], 
                     "fg": self.colors["fg"], "activebackground": self.colors["accent"],
                     "relief": "raised", "borderwidth": 1, "padx": 5, "pady": 5}
        
        # Create tooltip function for buttons
        def create_tooltip(widget, text):
            def enter(event):
                widget.tooltip = Toplevel(widget)
                widget.tooltip.withdraw()
                widget.tooltip.overrideredirect(True)
                
                x = widget.winfo_rootx() + widget.winfo_width() // 2
                y = widget.winfo_rooty() + widget.winfo_height() + 5
                
                widget.tooltip.geometry(f"+{x}+{y}")
                
                tip_frame = Frame(widget.tooltip, bg=self.colors["bg"], padx=5, pady=3, relief="solid", borderwidth=1)
                tip_frame.pack()
                
                tip_label = Label(tip_frame, text=text, bg=self.colors["bg"], 
                                fg=self.colors["fg"], font=("Arial", 9), justify=LEFT)
                tip_label.pack()
                
                widget.tooltip.deiconify()
                
            def leave(event):
                if hasattr(widget, "tooltip"):
                    widget.tooltip.destroy()
                    
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)
        
        # Modern game control buttons with icons and tooltips
        restart_btn = Button(game_actions, text=" 🔄 New Game", command=self.restart, width=10, **button_style)
        restart_btn.pack(side=LEFT, padx=5)
        create_tooltip(restart_btn, "Start a completely new game\nwith new mine positions")
        
        reload_btn = Button(game_actions, text=" 🔁 Try Again", command=self.reload, width=10, **button_style)
        reload_btn.pack(side=LEFT, padx=5)
        create_tooltip(reload_btn, "Reset this game with the\nsame mine positions")
        
        menu_btn = Button(game_actions, text=" 🏠 Menu", command=self.show_main_menu, width=10, **button_style)
        menu_btn.pack(side=LEFT, padx=5)
        create_tooltip(menu_btn, "Return to main menu")
        
        # Hint button
        self.hints_remaining = 3  # Number of hints available
        self.hint_btn = Button(game_actions, text=f" 💡 Hint ({self.hints_remaining})", 
                             command=self.give_hint, width=12, **button_style)
        self.hint_btn.pack(side=LEFT, padx=5)
        create_tooltip(self.hint_btn, "Get a hint (limited to 3)")
        
        # Create hover effects for buttons
        for btn in [restart_btn, reload_btn, menu_btn, self.hint_btn]:
            btn.bind("<Enter>", lambda e, b=btn: self.button_hover_in(b))
            btn.bind("<Leave>", lambda e, b=btn: self.button_hover_out(b))
        
        # Second row - Additional features
        features_frame = Frame(control_panel, bg=self.colors["bg"], pady=5)
        features_frame.pack(fill="x")
        
        # Toggle dark/light mode button
        self.dark_mode = True
        self.theme_btn = Button(features_frame, text=" 🌓 Theme", 
                               command=self.toggle_theme, width=12, **button_style)
        self.theme_btn.pack(side=LEFT, padx=5)
        create_tooltip(self.theme_btn, "Switch between dark and light mode")
        
        # Help button
        help_btn = Button(features_frame, text=" ❓ Help", 
                         command=self.show_help, width=10, **button_style)
        help_btn.pack(side=LEFT, padx=5)
        create_tooltip(help_btn, "Show game instructions")
        
        # Sound toggle button
        self.sound_btn = Button(features_frame, text=" 🔊 Sound", 
                              command=self.toggle_sound, width=10, **button_style)
        self.sound_btn.pack(side=LEFT, padx=5)
        create_tooltip(self.sound_btn, "Toggle game sounds on/off")
        
        # Stats button
        stats_btn = Button(features_frame, text=" 📊 Stats", 
                         command=self.show_game_stats, width=10, **button_style)
        stats_btn.pack(side=LEFT, padx=5)
        create_tooltip(stats_btn, "View current game statistics")
        
        # Add hover effect to new buttons too
        for btn in [self.theme_btn, help_btn, self.sound_btn, stats_btn]:
            btn.bind("<Enter>", lambda e, b=btn: self.button_hover_in(b))
            btn.bind("<Leave>", lambda e, b=btn: self.button_hover_out(b))

        # Setup images
        self.images = {
            "tile": PhotoImage(file=resource_path("images/unclicked_tile.png")),
            "mine": PhotoImage(file=resource_path("images/unclicked_mine_tile.png")),
            "flag": PhotoImage(file=resource_path("images/flag_tile.png")),
            "clicked_mine": PhotoImage(file=resource_path("images/clicked_mine_tile.png")),
            "wrong_flag": PhotoImage(file=resource_path("images/wrong_flag_tile.png")),
            "hint": PhotoImage(file=resource_path("images/flag_tile.png")),  # Reuse flag image for hint
            "numbers": []
        }
        for i in range(0, 9):
            self.images["numbers"].append(
                PhotoImage(file=resource_path("images/num{}_tile.png".format(str(i))))
            )

        self.start()
        
    def load_game_images(self):
        """ Load appropriate game images based on current style setting """
        try:
            if self.use_modern_tiles:
                # Use modern tiles from dynamically created images
                self.images = {
                    "tile": PhotoImage(file=self.tile_paths["tile"]),
                    "mine": PhotoImage(file=self.tile_paths["mine"]),
                    "flag": PhotoImage(file=self.tile_paths["flag"]),
                    "clicked_mine": PhotoImage(file=self.tile_paths["clicked_mine"]),
                    "wrong_flag": PhotoImage(file=self.tile_paths["wrong_flag"]),
                    "hint": PhotoImage(file=self.tile_paths["hint"]),
                    "numbers": []
                }
                for i in range(9):
                    self.images["numbers"].append(
                        PhotoImage(file=self.number_paths[i])
                    )
            else:
                # Use classic (original) tiles
                self.images = {
                    "tile": PhotoImage(file=self.classic_paths["tile"]),
                    "mine": PhotoImage(file=self.classic_paths["mine"]),
                    "flag": PhotoImage(file=self.classic_paths["flag"]),
                    "clicked_mine": PhotoImage(file=self.classic_paths["clicked_mine"]),
                    "wrong_flag": PhotoImage(file=self.classic_paths["wrong_flag"]),
                    "hint": PhotoImage(file=self.classic_paths["hint"]),
                    "numbers": []
                }
                for i in range(9):
                    self.images["numbers"].append(
                        PhotoImage(file=self.classic_number_paths[i])
                    )
        except Exception as e:
            # Fallback to classic images if anything fails
            print(f"Error loading images: {e}")
            self.use_modern_tiles = False
            
            # Last resort fallback using resource_path directly
            self.images = {
                "tile": PhotoImage(file=resource_path("images/unclicked_tile.png")),
                "mine": PhotoImage(file=resource_path("images/unclicked_mine_tile.png")),
                "flag": PhotoImage(file=resource_path("images/flag_tile.png")),
                "clicked_mine": PhotoImage(file=resource_path("images/clicked_mine_tile.png")),
                "wrong_flag": PhotoImage(file=resource_path("images/wrong_flag_tile.png")),
                "hint": PhotoImage(file=resource_path("images/flag_tile.png")),  # Reuse flag image for hint
                "numbers": []
            }
            for i in range(9):
                self.images["numbers"].append(
                    PhotoImage(file=resource_path(f"images/num{i}_tile.png"))
                )

    def toggle_tile_style(self):
        """ Toggle between modern and classic tile styles """
        self.use_modern_tiles = not self.use_modern_tiles
        style_text = "Modern" if self.use_modern_tiles else "Classic"
        
        # Update the message to inform the user
        self.message_label.config(text=f"Switched to {style_text} Tile Style")
        self.tk.after(1500, lambda: self.message_label.config(text=""))
        
        # Restart the game to apply the new style
        self.restart()

    def button_hover_in(self, button):
        """ Add hover effect to button """
        button.config(bg=self.colors["accent"], fg=self.colors["bg"])
    
    def button_hover_out(self, button):
        """ Remove hover effect from button """
        button.config(bg=self.colors["button_bg"], fg=self.colors["fg"])
    
    def toggle_theme(self):
        """ Toggle between dark and light mode """
        if self.dark_mode:
            # Switch to light mode
            self.colors.update({
                "bg": "#F5F5F5",
                "fg": "#212121",
                "button_bg": "#E0E0E0",
                "button_fg": "#212121",
                "accent": "#6200EE",
                "error": "#B00020",
                "success": "#03DAC5"
            })
            self.dark_mode = False
            self.theme_btn.config(text=" 🌓 Theme")
        else:
            # Switch to dark mode
            self.colors.update({
                "bg": "#121212",
                "fg": "#FFFFFF",
                "button_bg": "#1F1F1F",
                "button_fg": "#FFFFFF", 
                "accent": "#BB86FC",
                "error": "#CF6679",
                "success": "#03DAC5"
            })
            self.dark_mode = True
            self.theme_btn.config(text=" 🌓 Theme")
        
        # Update all colors
        self.tk.configure(bg=self.colors["bg"])
        self.frame.configure(bg=self.colors["bg"])
        self.message_label.configure(bg=self.colors["bg"], fg=self.colors["accent"])
        
        # Update all controls
        for widget in self.tk.winfo_children():
            if isinstance(widget, Frame):
                widget.configure(bg=self.colors["bg"])
                for child in widget.winfo_children():
                    if isinstance(child, (Button, Label, Frame)):
                        try:
                            child.configure(bg=self.colors["bg"], fg=self.colors["fg"])
                            if isinstance(child, Button):
                                child.configure(activebackground=self.colors["accent"])
                        except:
                            pass
    
    def toggle_sound(self):
        """ Toggle game sounds on/off """
        self.sound_on = not self.sound_on
        if self.sound_on:
            self.sound_btn.config(text=" 🔊 Sound")
            self.message_label.config(text="Sound enabled")
        else:
            self.sound_btn.config(text=" 🔇 Sound")
            self.message_label.config(text="Sound disabled")
        self.tk.after(1500, lambda: self.message_label.config(text=""))
    
    def show_help(self):
        """ Display game help """
        help_window = Toplevel(self.tk)
        help_window.title("Game Help")
        help_window.configure(bg=self.colors["bg"])
        help_window.resizable(False, False)
        help_window.transient(self.tk)
        help_window.grab_set()
        
        # Center the window
        w = 400
        h = 350
        ws = self.tk.winfo_screenwidth()
        hs = self.tk.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        help_window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        # Title
        Label(help_window, text="How to Play", font=("Arial", 18, "bold"), 
             bg=self.colors["bg"], fg=self.colors["accent"], pady=10).pack()
        
        # Help content
        help_frame = Frame(help_window, bg=self.colors["bg"], padx=20, pady=10)
        help_frame.pack(fill="both", expand=True)
        
        help_text = [
            "- The goal: uncover all the squares without hitting a mine",
            "- Left click: uncover a square",
            "- Right click: flag a square",
            "- Numbers: indicate the number of mines around the square",
            "",
            "Buttons:",
            "- 🔄 New Game: start a new game",
            "- 🔁 Try Again: start the same game again",
            "- 🏠 Menu: return to the main menu",
            "- 🌓 Theme: toggle between dark and light mode",
            "- 🔊 Sound: toggle game sounds on/off",
            "",
            "Developed by: Muhammad Saeed"
        ]
        
        for i, line in enumerate(help_text):
            Label(help_frame, text=line, font=("Arial", 11), bg=self.colors["bg"], 
                 fg=self.colors["fg"], anchor="w", justify=LEFT).pack(fill="x", pady=2)
        
        # Close button
        Button(help_window, text="Close", command=help_window.destroy, 
              font=("Arial", 12), bg=self.colors["button_bg"], fg=self.colors["fg"],
              activebackground=self.colors["accent"], padx=10, pady=5).pack(pady=15)

    def start(self):
        """ Start the game """
        # Setting our variables
        self.is_armed = False
        self.clicks = 0
        self.flags = 0
        self.stop = False
        self.reloaded = False
        self.repeat_timer = "after#0"
        
        # Track the last time a sound was played to limit multiple sounds
        self.last_sound_time = 0
        self.sound_cooldown = 0.1  # seconds between sounds

        # Setup time
        self.time = 0
        self.time_label.config(text="Time: 0")

        # Setup mine counter
        self.mine_label.config(text=f"Mines: {self.selected_mines - self.flags}")
                               
        # Welcome message with scrolling instructions for hard difficulty
        if self.current_difficulty == "hard":
            self.message_label.config(text="Hard mode - Use scrollbars to navigate the larger grid")
            self.tk.after(4000, lambda: self.message_label.config(text=""))
        else:
            self.message_label.config(text=f"Welcome to Minesweeper ({self.current_difficulty.capitalize()})")
            self.tk.after(3000, lambda: self.message_label.config(text=""))

        # Create the grid
        self.grid = {}
        
        # Adjust tile size based on difficulty to ensure buttons are visible
        if self.current_difficulty == "hard":
            # Use smaller tiles for hard difficulty
            for img_name, img in self.images.items():
                if img_name == "numbers":
                    # Handle the numbers list separately
                    for i in range(len(self.images["numbers"])):
                        # Create a smaller version of each number image
                        img = self.images["numbers"][i]
                        self.images["numbers"][i] = self.resize_image(img, 0.7)
                else:
                    # Resize other images
                    self.images[img_name] = self.resize_image(img, 0.7)
        
        # Add padding between tiles based on difficulty
        padding = 1 if self.current_difficulty == "easy" else 0
        
        # Create a centered container for the grid
        grid_container = Frame(self.frame, bg=self.colors["bg"], padx=20, pady=20)
        grid_container.pack(expand=True, fill=BOTH)
        
        # Use the grid layout manager to position tiles
        for i in range(self.size):
            grid_container.grid_columnconfigure(i, weight=1, uniform="col")
            grid_container.grid_rowconfigure(i, weight=1, uniform="row")
        
        # Create the grid of tiles
        for x in range(0, self.size):
            for y in range(0, self.size):
                if y == 0:
                    self.grid[x] = {}
                
                tile = {
                    "button": Button(grid_container,
                                     image=self.images["tile"],
                                     borderwidth=0,
                                     highlightthickness=0),
                    "is_mine": False,
                    "surrounding_mines": 0,
                    "is_flagged": False,
                    "is_clicked": False,
                    "first": False,
                    "x": x,
                    "y": y
                }
                tile["button"].bind("<Button-1>",
                                    lambda Button, x=x, y=y:
                                    self.left_click(x, y))
                tile["button"].bind("<Button-3>",
                                    lambda Button, x=x, y=y:
                                    self.right_click(x, y))
                
                # Place tiles in a grid with equal spacing
                tile["button"].grid(row=x, column=y, padx=padding, pady=padding, sticky="nsew")
                
                self.tk.bind("r", lambda Res: self.restart())
                self.grid[x][y] = tile
        
        # After creating all tiles, update the parent frame
        self.frame.update_idletasks()
        
        # For hard mode, update the canvas to show the centered content
        if self.current_difficulty == "hard":
            # Get the canvas from the frame's master
            canvas = self.frame.master
            
            # Update the canvas to reflect changes
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

    def resize_image(self, img, scale_factor):
        """ Resize an image by a scale factor """
        if not hasattr(img, 'width') or not hasattr(img, 'height'):
            return img
            
        # Get the original width and height
        width = img.width()
        height = img.height()
        
        # Calculate new dimensions
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Create a temporary image with the new dimensions
        temp_img = PhotoImage(width=new_width, height=new_height)
        
        # Scale the original image into the temporary image
        img.zoom(new_width, new_height)
        img.subsample(width, height)
        
        return img

    def restart(self):
        """ Restart the game """
        self.stop = True
        self.tk.after_cancel(self.repeat_timer)
        self.message_label.config(text="")
        try:
            self.game_over_window.destroy()
        except Exception:
            pass
        self.start_game()

    def create_mine(self):
        """ Create mines """
        for x in self.grid:
            for y in self.grid[x]:
                # Check the place where the lpayer first click to avoid mines
                if self.grid[x][y]["first"] is True:
                    continue

                # If the mine already exists, continue
                if self.grid[x][y]["is_mine"] is True:
                    continue

                # Distributes the mines with max efficiency
                if randint(0, (self.size ** 2 + 1) //
                           (self.selected_mines) + 1) == 0:
                    self.grid[x][y]["is_mine"] = True
                    # self.grid[x][y]["button"].config(
                    # image=self.images["mine"])
                    self.mines += 1

                # If the amount of mines is met, return
                if self.mines == self.selected_mines:
                    return

    def check_mines(self):
        """ Check surrounding mines """
        for x in self.grid:
            for y in self.grid[x]:

                # If it was mine continue
                if self.grid[x][y]["is_mine"] is True:
                    continue

                # Check surrounding mines
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        # if out of boundries top and side
                        if x + i < 0 or y + j < 0:
                            continue

                        # if out of boundries bot and side
                        if x + i > self.size - 1 or y + j > self.size - 1:
                            continue

                        if self.grid[x + i][y + j]["is_mine"] is True:
                            self.grid[x][y]["surrounding_mines"] += 1
                # self.grid[x][y]["button"].config(
                    # image=self.images["numbers"]
                    # [self.grid[x][y]["surrounding_mines"]])

    def play_sound(self, sound_type):
        """ Play a sound effect """
        if not self.sound_on:
            return
            
        # Check if we're in a multi-tile clearing operation
        current_time = datetime.now().timestamp()
        time_since_last = current_time - self.last_sound_time
        
        # If sound is triggered by clearing multiple cells and cooldown hasn't expired, skip
        if sound_type == "click" and time_since_last < self.sound_cooldown:
            return
            
        # Update the last sound time
        self.last_sound_time = current_time
            
        # Play sound in a separate thread to avoid freezing the UI
        def play():
            frequency = self.sounds[sound_type]
            duration = 150  # milliseconds
            
            # Reduce click sound volume for multiple clears by reducing duration
            if sound_type == "click" and time_since_last < 0.5:
                duration = 50  # Shorter duration for rapid clicks
            
            if sound_type == "win":
                # Play victory melody
                for freq in [frequency, frequency+200, frequency+400]:
                    winsound.Beep(freq, 150)
            elif sound_type == "lose":
                # Play failure sound
                winsound.Beep(frequency, 500)
            else:
                # Play normal sound
                winsound.Beep(frequency, duration)
                
        threading.Thread(target=play).start()

    def left_click(self, x, y):
        """ Left click """
        if self.stop:
            return
        if self.is_armed is False:
            # Create mines in the grid
            self.mines = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    # if out of boundries top and side
                    if x + i < 0 or y + j < 0:
                        continue

                    # if out of boundries bot and side
                    if x + i > self.size - 1 or y + j > self.size - 1:
                        continue

                    self.grid[x + i][y + j]["first"] = True
            while True:
                # forever loop until the number is met
                self.create_mine()
                if self.mines == self.selected_mines:
                    break
            self.is_armed = True
            self.timer()

            # Check surrounding mines
            self.check_mines()

        if self.reloaded is True:
            self.reloaded = False
            self.timer()
        if self.grid[x][y]["is_flagged"] is True:
            return

        if self.grid[x][y]["is_clicked"] is True:
            return

        elif self.grid[x][y]["is_mine"] is True:
            self.grid[x][y]["button"].config(
                image=self.images["clicked_mine"])
            self.grid[x][y]["is_clicked"] = True
            self.play_sound("lose")
            self.game_over(False)

        elif self.grid[x][y]["surrounding_mines"] == 0:
            self.grid[x][y]["button"].config(
                image=self.images["numbers"][0])
            self.grid[x][y]["is_clicked"] = True
            self.play_sound("click")
            self.clicks += 1
            if self.clicks == (self.size ** 2 - self.mines):
                self.play_sound("win")
                self.game_over(True)
            else:
                self.clear_surr(x, y)

        else:
            self.grid[x][y]["button"].config(
                image=self.images["numbers"]
                [self.grid[x][y]["surrounding_mines"]])
            self.grid[x][y]["is_clicked"] = True
            self.play_sound("click")
            self.clicks += 1
            if self.clicks == (self.size ** 2 - self.mines):
                self.play_sound("win")
                self.game_over(True)

    def clear_surr(self, x, y):
        """ Clear surrounding tiles """
        # Create a list of surrounding tiles to check
        tiles_to_check = []
        
        for i in range(-1, 2):
            for j in range(-1, 2):
                # If out of boundaries top and side
                if x + i < 0 or y + j < 0:
                    continue

                # If out of boundaries bottom and side
                if x + i > self.size - 1 or y + j > self.size - 1:
                    continue
                
                # Add to list to check
                tiles_to_check.append((x + i, y + j))
        
        # Use a timer to stagger the opening of surrounding tiles
        # This makes the clearing animation smoother and reduces sound overload
        def open_tile_staggered(index):
            if index < len(tiles_to_check):
                tx, ty = tiles_to_check[index]
                self.left_click(tx, ty)
                # Schedule next tile opening with a small delay
                self.tk.after(5, lambda: open_tile_staggered(index + 1))
        
        # Start the staggered opening
        open_tile_staggered(0)

    def right_click(self, x, y):
        """ Right click """
        if self.stop:
            return

        if self.grid[x][y]["is_clicked"] is True:
            return

        if self.grid[x][y]["is_flagged"] is False:
            # Change to flagged
            self.grid[x][y]["button"].config(image=self.images["flag"])
            self.grid[x][y]["is_flagged"] = True
            self.flags += 1
            self.play_sound("flag")
        else:
            # Change to unflagged
            self.grid[x][y]["button"].config(image=self.images["tile"])
            self.grid[x][y]["is_flagged"] = False
            self.flags -= 1
            self.play_sound("flag")

        # Update mines left
        self.mine_label.config(text=f"Mines: {self.selected_mines - self.flags}")

    def game_over(self, result):
        """ Game over screen """
        self.stop = True
        self.tk.after_cancel(self.repeat_timer)
        
        # Handle high score if player wins
        if result:
            # Check if this is a high score
            is_high_score = False
            if len(self.high_scores[self.current_difficulty]) < 5:
                is_high_score = True
            elif self.time < max([score["time"] for score in self.high_scores[self.current_difficulty]], default=999999):
                is_high_score = True
                
            # Save high score
            if is_high_score:
                self.save_high_score(self.time)
                winner_text = f"You Win! New High Score: {self.time}s"
                message_color = self.colors["success"]
            else:
                winner_text = f"You Win! Time: {self.time}s"
                message_color = self.colors["accent"]
        else:
            winner_text = "Game Over!"
            message_color = self.colors["error"]
            
        # Update message label
        self.message_label.config(text=winner_text, fg=message_color)
        
        # Show all mines
        for x in self.grid:
            for y in self.grid[x]:
                if not self.grid[x][y]["is_clicked"]:
                    if self.grid[x][y]["is_mine"] and not self.grid[x][y]["is_flagged"]:
                        self.grid[x][y]["button"].config(
                            image=self.images["mine"])
                    elif not self.grid[x][y]["is_mine"] and self.grid[x][y]["is_flagged"]:
                        self.grid[x][y]["button"].config(
                            image=self.images["wrong_flag"])

        # Show game over popup
        self.game_over_window = Toplevel(self.tk)
        self.game_over_window.title("Game Over")
        self.game_over_window.configure(bg=self.colors["bg"])
        self.game_over_window.resizable(False, False)
        self.game_over_window.transient(self.tk)
        self.game_over_window.grab_set()
        
        # Center the window
        w = 300
        h = 200
        ws = self.tk.winfo_screenwidth()
        hs = self.tk.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.game_over_window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        # Game over message
        if result:
            Label(self.game_over_window, text="You Win!", font=("Arial", 20, "bold"), 
                 bg=self.colors["bg"], fg=self.colors["success"], pady=10).pack()
        else:
            Label(self.game_over_window, text="Game Over!", font=("Arial", 20, "bold"), 
                 bg=self.colors["bg"], fg=self.colors["error"], pady=10).pack()
        
        # Game stats
        stats_frame = Frame(self.game_over_window, bg=self.colors["bg"], pady=10)
        stats_frame.pack(fill="x")
        
        Label(stats_frame, text=f"Difficulty: {self.current_difficulty.capitalize()}", 
             font=("Arial", 12), bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        Label(stats_frame, text=f"Time: {self.time} seconds", 
             font=("Arial", 12), bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        
        # Buttons frame
        button_frame = Frame(self.game_over_window, bg=self.colors["bg"], pady=20)
        button_frame.pack()
        
        # Button style
        button_style = {"font": ("Arial", 10), "width": 12, "bg": self.colors["button_bg"], 
                      "fg": self.colors["fg"], "activebackground": self.colors["accent"]}
        
        # Buttons
        Button(button_frame, text="Play Again", command=lambda: [self.game_over_window.destroy(), self.restart()], 
              **button_style).pack(side=LEFT, padx=5)
        Button(button_frame, text="Main Menu", command=lambda: [self.game_over_window.destroy(), self.show_main_menu()], 
              **button_style).pack(side=LEFT, padx=5)

    def reload(self):
        """ Reload the same game """
        self.reloaded = True
        self.time_label.config(text="Time: 0")
        self.stop = True
        self.tk.after_cancel(self.repeat_timer)
        self.message_label.config(text="")
        
        # Reset flags counter
        self.flags = 0
        self.mine_label.config(text=f"Mines: {self.selected_mines}")
        
        # Reset the grid but maintain mines
        for x in self.grid:
            for y in self.grid[x]:
                # Put the unclicked tile back
                self.grid[x][y]["button"].config(image=self.images["tile"])
                self.grid[x][y]["is_clicked"] = False
                self.grid[x][y]["is_flagged"] = False
        
        # Reset time
        self.time = 0
        self.stop = False

    def timer(self):
        """ Update the timer """
        if self.stop:
            return
        self.time += 1
        self.time_label.config(text=f"Time: {self.time}")
        
        # Update progress bar - max time we show is 5 minutes (300 seconds)
        max_time = 300
        progress_width = min(100, (self.time / max_time) * 100)
        
        # Change color based on time elapsed
        if self.time < 60:  # First minute - green
            color = self.colors["success"]
        elif self.time < 180:  # 1-3 minutes - accent color
            color = self.colors["accent"]
        else:  # Over 3 minutes - getting urgent
            color = self.colors["error"]
            
        # Clear and redraw progress bar
        self.time_progress.delete("all")
        self.time_progress.create_rectangle(0, 0, progress_width, 10, fill=color, outline="")
        
        self.repeat_timer = self.tk.after(1000, self.timer)
    
    def give_hint(self):
        """ Provide a hint to the player """
        if self.hints_remaining <= 0:
            self.message_label.config(text="No hints left!", fg=self.colors["error"])
            self.play_sound("lose")
            self.tk.after(1500, lambda: self.message_label.config(text=""))
            return
            
        # Find a safe tile to reveal
        safe_tiles = []
        for x in self.grid:
            for y in self.grid[x]:
                # Look for unclicked, unflagged, non-mine tiles
                if (not self.grid[x][y]["is_clicked"] and 
                    not self.grid[x][y]["is_flagged"] and 
                    not self.grid[x][y]["is_mine"]):
                    safe_tiles.append((x, y))
        
        # Find an unflagged mine
        unflagged_mines = []
        for x in self.grid:
            for y in self.grid[x]:
                if (self.grid[x][y]["is_mine"] and 
                    not self.grid[x][y]["is_flagged"] and
                    not self.grid[x][y]["is_clicked"]):
                    unflagged_mines.append((x, y))
        
        if safe_tiles and self.is_armed:
            # Play the hint sound
            self.play_sound("hint")
            
            # Randomly choose whether to reveal a safe tile or hint at a mine
            if unflagged_mines and randint(0, 2) == 0:
                # Hint at a mine location
                x, y = unflagged_mines[randint(0, len(unflagged_mines)-1)]
                
                # Temporarily change the button appearance
                original_image = self.grid[x][y]["button"].cget("image")
                self.grid[x][y]["button"].config(image=self.images["hint"])
                
                # Show hint message
                self.message_label.config(text="Hint: There is a mine in the revealed square!", fg=self.colors["accent"])
                
                # Reset after 1.5 seconds
                self.tk.after(1500, lambda: [
                    self.grid[x][y]["button"].config(image=original_image),
                    self.message_label.config(text="")
                ])
            else:
                # Reveal a safe tile
                x, y = safe_tiles[randint(0, len(safe_tiles)-1)]
                
                # Highlight the safe tile
                original_image = self.grid[x][y]["button"].cget("image")
                self.grid[x][y]["button"].config(bg=self.colors["success"])
                
                # Show hint message
                self.message_label.config(text="Hint: The revealed square is safe!", fg=self.colors["success"])
                
                # Reset after 1.5 seconds
                self.tk.after(1500, lambda: [
                    self.grid[x][y]["button"].config(bg=self.colors["bg"]),
                    self.message_label.config(text="")
                ])
        else:
            self.message_label.config(text="Start the game first!", fg=self.colors["accent"])
            self.tk.after(1500, lambda: self.message_label.config(text=""))
            return
            
        # Decrement hint count and update button
        self.hints_remaining -= 1
        self.hint_btn.config(text=f" 💡 Hint ({self.hints_remaining})")
        
        # Disable hint button if no hints left
        if self.hints_remaining <= 0:
            self.hint_btn.config(state=DISABLED)
            
    def show_game_stats(self):
        """ Show game statistics """
        stats_window = Toplevel(self.tk)
        stats_window.title("Game Statistics")
        stats_window.configure(bg=self.colors["bg"])
        stats_window.resizable(False, False)
        stats_window.transient(self.tk)
        stats_window.grab_set()
        
        # Center the window
        w = 400
        h = 300
        ws = self.tk.winfo_screenwidth()
        hs = self.tk.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        stats_window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        # Title
        Label(stats_window, text="Game Statistics", font=("Arial", 18, "bold"), 
             bg=self.colors["bg"], fg=self.colors["accent"], pady=10).pack()
        
        # Current game stats
        stats_frame = Frame(stats_window, bg=self.colors["bg"], padx=20, pady=10)
        stats_frame.pack(fill="both", expand=True)
        
        # Calculate progress
        total_cells = self.size * self.size
        non_mine_cells = total_cells - self.selected_mines
        progress_pct = int((self.clicks / non_mine_cells) * 100) if non_mine_cells > 0 else 0
        
        # Display stats
        stats = [
            {"label": "Difficulty", "value": self.current_difficulty.capitalize()},
            {"label": "Time Elapsed", "value": f"{self.time} seconds"},
            {"label": "Uncovered Squares", "value": f"{self.clicks} out of {non_mine_cells}"},
            {"label": "Completion Percentage", "value": f"{progress_pct}%"},
            {"label": "Remaining Mines", "value": f"{self.selected_mines - self.flags}"},
            {"label": "Hints Used", "value": f"{3 - self.hints_remaining} out of 3"}
        ]
        
        # Add progress bar
        progress_frame = Frame(stats_frame, bg=self.colors["bg"], pady=10)
        progress_frame.pack(fill="x")
        
        Label(progress_frame, text="Progress:", font=("Arial", 12, "bold"), 
             bg=self.colors["bg"], fg=self.colors["fg"]).pack(anchor="w")
        
        progress_bg = Frame(progress_frame, bg=self.colors["button_bg"], height=20, width=350)
        progress_bg.pack(fill="x", pady=5)
        
        progress_bar = Frame(progress_bg, bg=self.colors["accent"], height=20, width=progress_pct*3.5)
        progress_bar.place(x=0, y=0)
        
        progress_text = Label(progress_bar, text=f"{progress_pct}%", font=("Arial", 10, "bold"), 
                            bg=self.colors["accent"], fg=self.colors["bg"])
        progress_text.place(relx=0.5, rely=0.5, anchor="center")
        
        # Stats table
        for i, stat in enumerate(stats):
            if i != 2:  # Skip "Uncovered Squares" as we show it in progress bar
                Frame(stats_frame, height=1, bg=self.colors["button_bg"]).pack(fill="x", pady=5)
                stat_frame = Frame(stats_frame, bg=self.colors["bg"])
                stat_frame.pack(fill="x")
                
                Label(stat_frame, text=stat["label"], font=("Arial", 12), width=15, anchor="w",
                     bg=self.colors["bg"], fg=self.colors["fg"]).pack(side=LEFT)
                
                Label(stat_frame, text=stat["value"], font=("Arial", 12, "bold"), 
                     bg=self.colors["bg"], fg=self.colors["accent"]).pack(side=LEFT)
        
        # Close button
        Button(stats_window, text="Close", command=stats_window.destroy, 
              font=("Arial", 12), bg=self.colors["button_bg"], fg=self.colors["fg"],
              activebackground=self.colors["accent"], padx=10, pady=5).pack(pady=15)


if __name__ == "__main__":
    # Create main window
    window = Tk()
    window.title("Minesweeper by Muhammad Saeed")
    
    # Configure window properties
    window.configure(bg="#121212")
    icon = PhotoImage(file=resource_path("images/unclicked_mine_tile.png"))
    window.iconphoto(True, icon)
    
    # Center the window
    w = 600
    h = 600
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
    # Create game instance
    game = Minesweeper(window)
    
    # Run main loop
    window.mainloop()
