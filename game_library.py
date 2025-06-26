import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog, ttk # Import ttk for themed widgets
import json
import os
import subprocess
from datetime import datetime
import sys

# --- File Path for Data Storage ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, 'game_library.json')

# --- Data Management Functions ---
def load_games():
    """Loads game data from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Could not decode game_library.json. File might be corrupted. Starting with an empty library.")
        return []
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred loading games: {e}")
        return []

def save_games(games):
    """Saves game data to the JSON file."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(games, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save games: {e}")

# --- Main Application Class ---
class GameLibraryApp:
    # Define a cohesive color palette for a sleek look as class attributes
    COLOR_BG_APP = '#2b2b2b'        # Dark background for the overall app
    COLOR_BG_PANEL = '#3c3c3c'      # Slightly lighter dark for content panels
    COLOR_HEADER_BG = '#1e1e1e'     # Even darker for header
    COLOR_ACCENT_PRIMARY = '#6A5ACD' # Indigo for primary actions
    COLOR_ACCENT_PRIMARY_HOVER = '#836FFF' # Lighter indigo for hover
    COLOR_TEXT_LIGHT = '#ffffff'    # White text for dark backgrounds
    COLOR_TEXT_MEDIUM = '#cccccc'   # Light gray text
    COLOR_TEXT_DARK = '#eeeeee'     # Off-white text

    def __init__(self, root):
        self.root = root
        self.root.title("Game Vault - Desktop Library")
        self.root.geometry("1000x750") # Slightly larger initial window
        self.root.minsize(800, 600) # Minimum window size for responsiveness

        # --- Tkinter.ttk Styling ---
        self.style = ttk.Style()
        # Using 'clam' theme as a base for its flatter appearance
        self.style.theme_use('clam')

        # Configure global styles for ttk widgets
        self.style.configure('TFrame', background=self.COLOR_BG_APP)
        self.style.configure('TLabel', background=self.COLOR_BG_APP, foreground=self.COLOR_TEXT_LIGHT, font=('Helvetica Neue', 11))
        self.style.configure('TButton', font=('Helvetica Neue', 10, 'bold'), borderwidth=0, focusthickness=2, focuscolor=self.COLOR_ACCENT_PRIMARY)
        self.style.map('TButton',
                       background=[('active', self.COLOR_ACCENT_PRIMARY_HOVER), ('!disabled', self.COLOR_ACCENT_PRIMARY)],
                       foreground=[('active', 'black'), ('!disabled', self.COLOR_TEXT_LIGHT)]) # Text becomes black on hover for contrast

        # Specific styles for distinct elements and consistency
        self.style.configure('Header.TLabel', font=('Helvetica Neue', 26, 'bold'), foreground=self.COLOR_TEXT_LIGHT, background=self.COLOR_HEADER_BG)
        self.style.configure('HeaderContainer.TFrame', background=self.COLOR_HEADER_BG, relief='flat')

        self.style.configure('ContentFrame.TFrame', background=self.COLOR_BG_PANEL, borderwidth=1, relief='flat', bordercolor=self.COLOR_BG_PANEL)
        self.style.configure('SectionTitle.TLabel', font=('Helvetica Neue', 18, 'bold'), background=self.COLOR_BG_PANEL, foreground=self.COLOR_TEXT_LIGHT)
        self.style.configure('DetailsTitle.TLabel', font=('Helvetica Neue', 20, 'bold'), background=self.COLOR_BG_PANEL, foreground=self.COLOR_TEXT_LIGHT)
        self.style.configure('GameName.TLabel', font=('Helvetica Neue', 15, 'bold'), background=self.COLOR_BG_PANEL, foreground=self.COLOR_TEXT_LIGHT)
        self.style.configure('Platform.TLabel', font=('Helvetica Neue', 12), background=self.COLOR_BG_PANEL, foreground=self.COLOR_TEXT_MEDIUM)
        self.style.configure('LaunchPath.TLabel', font=('Helvetica Neue', 12), background=self.COLOR_BG_PANEL, foreground=self.COLOR_TEXT_MEDIUM)
        self.style.configure('Description.TLabel', font=('Helvetica Neue', 12), background=self.COLOR_BG_PANEL, foreground=self.COLOR_TEXT_MEDIUM)
        self.style.configure('SmallItalic.TLabel', font=('Helvetica Neue', 9, 'italic'), background=self.COLOR_BG_PANEL, foreground='#aaaaaa') # Darker grey for hints

        self.style.configure('TEntry', fieldbackground='#4f4f4f', foreground=self.COLOR_TEXT_LIGHT, borderwidth=0, relief='flat', font=('Helvetica Neue', 10), padding=(5, 5))
        self.style.map('TEntry', fieldbackground=[('focus', '#5a5a5a')]) # Darken on focus
        self.style.configure('TCombobox', fieldbackground='#4f4f4f', foreground=self.COLOR_TEXT_LIGHT, background='#4f4f4f', borderwidth=0, relief='flat', font=('Helvetica Neue', 10), padding=(5, 5))
        self.style.map('TCombobox', fieldbackground=[('readonly', '#4f4f4f')]) # Ensure read-only combobox maintains dark background
        # ScrolledText needs manual background as it's not a ttk widget
        self.style.configure('ScrolledText.Text', background='#4f4f4f', foreground=self.COLOR_TEXT_LIGHT, borderwidth=0, relief='flat')


        self.games = load_games()
        self.selected_game_index = -1

        self.create_widgets()
        self.populate_game_list()

    def create_widgets(self):
        # --- Root Window Configuration ---
        self.root.config(background=self.style.lookup('TFrame', 'background')) # Root background to match app background

        # --- Header Frame ---
        header_frame = ttk.Frame(self.root, style='HeaderContainer.TFrame', padding=(20, 15))
        header_frame.pack(fill=tk.X, pady=(0, 1)) # Small gap between header and main content

        header_label = ttk.Label(header_frame, text="🎮 Game Vault", style='Header.TLabel')
        header_label.pack(side=tk.LEFT, padx=10)

        import_button = ttk.Button(header_frame, text="Import Games (Steam/Epic)", command=self.show_import_games_info)
        self.style.map('Import.TButton',
                  background=[('active', '#e68a00'), ('!disabled', '#FFA500')], # Orange palette for accent
                  foreground=[('active', 'white'), ('!disabled', 'white')])
        import_button.config(style='Import.TButton')
        import_button.pack(side=tk.RIGHT, padx=10)

        # --- Main Content Frame ---
        self.main_frame = ttk.Frame(self.root, style='TFrame', padding=(1, 1)) # Minimal padding to align with header gap
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.main_frame.grid_columnconfigure(0, weight=1, minsize=280)
        self.main_frame.grid_columnconfigure(1, weight=2, minsize=500)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # --- Game List Frame ---
        list_frame = ttk.Frame(self.main_frame, style='ContentFrame.TFrame', padding=20)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0,1), pady=0) # No left/bottom padding, 1px right padding for separator
        list_frame.grid_rowconfigure(1, weight=1)

        list_label = ttk.Label(list_frame, text="Your Game Library", style='SectionTitle.TLabel')
        list_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # Listbox with Scrollbar (tk.Listbox, so manual bg set)
        listbox_frame = ttk.Frame(list_frame, style='ContentFrame.TFrame') # Frame to hold listbox and scrollbar
        listbox_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=0, pady=0)
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)

        self.game_listbox = tk.Listbox(listbox_frame, font=('Helvetica Neue', 10), selectmode=tk.SINGLE,
                                       bd=0, relief="flat", bg="#4f4f4f", fg=self.COLOR_TEXT_LIGHT, # Dark background for listbox
                                       selectbackground="#836FFF", selectforeground="black", # Brighter selection
                                       highlightthickness=0, borderwidth=0)
        self.game_listbox.grid(row=0, column=0, sticky="nsew")
        self.game_listbox.bind("<<ListboxSelect>>", self.on_game_select)

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.game_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.game_listbox.config(yscrollcommand=scrollbar.set)

        # Buttons for list management
        button_frame = ttk.Frame(list_frame, style='ContentFrame.TFrame')
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        self.add_button = ttk.Button(button_frame, text="Add New Game", command=self.show_add_game_form)
        self.style.map('Add.TButton', background=[('active', '#22aa22'), ('!disabled', '#32CD32')]) # Green palette
        self.add_button.config(style='Add.TButton')
        self.add_button.grid(row=0, column=0, padx=5, pady=8, sticky="ew")

        self.edit_button = ttk.Button(button_frame, text="Edit Selected", command=self.show_edit_game_form)
        self.style.map('Edit.TButton', background=[('active', '#eecc00'), ('!disabled', '#FFD700')]) # Gold palette
        self.edit_button.config(style='Edit.TButton')
        self.edit_button.grid(row=0, column=1, padx=5, pady=8, sticky="ew")

        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_game)
        self.style.map('Delete.TButton', background=[('active', '#dd4433'), ('!disabled', '#FF4500')]) # Red palette
        self.delete_button.config(style='Delete.TButton')
        self.delete_button.grid(row=1, column=0, columnspan=2, padx=5, pady=8, sticky="ew")

        # --- Details/Form Frame ---
        self.details_frame = ttk.Frame(self.main_frame, style='ContentFrame.TFrame', padding=25)
        self.details_frame.grid(row=0, column=1, sticky="nsew", padx=(1,0), pady=0) # 1px left padding for separator
        self.details_frame.grid_rowconfigure(8, weight=1)
        self.details_frame.grid_columnconfigure(0, weight=1)

        self.show_welcome_message()

    def show_welcome_message(self):
        """Displays a welcome message or instructions in the details frame."""
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        # Labels within details frame use its background via ContentFrame.TFrame style
        welcome_label = ttk.Label(self.details_frame, text="Welcome to your Game Vault!",
                                 style='DetailsTitle.TLabel', wraplength=400)
        welcome_label.pack(pady=(40, 20))

        instructions_label = ttk.Label(self.details_frame,
                                      text="Select a game from the left or click 'Add New Game' to get started.",
                                      font=("Helvetica Neue", 12), background=self.style.lookup('ContentFrame.TFrame', 'background'), foreground=self.style.lookup('TLabel', 'foreground'), wraplength=400)
        instructions_label.pack(pady=10)

    def show_import_games_info(self):
        """Displays information about the 'Import Games' feature."""
        info_message = (
            "Automatic game recognition from platforms like Steam and Epic Games, "
            "especially with login integration, is a very complex feature.\n\n"
            "It typically requires:\n"
            "- Direct interaction with platform-specific APIs (often requiring developer keys and OAuth).\n"
            "- Parsing complex local game manifest files (which can change).\n"
            "- Handling platform-specific launch arguments.\n\n"
            "This level of integration goes beyond the scope of a simple Python Tkinter application. "
            "Dedicated launchers like Playnite or GOG Galaxy are built with more robust frameworks "
            "and extensive platform-specific integrations to achieve this.\n\n"
            "For this application, you can manually add games and their launch paths."
        )
        messagebox.showinfo("Import Games Info", info_message)

    def populate_game_list(self):
        """Populates the listbox with game names, sorted alphabetically."""
        self.game_listbox.delete(0, tk.END)
        self.games.sort(key=lambda x: x.get('name', '').lower()) # Sort by name
        for i, game in enumerate(self.games):
            self.game_listbox.insert(tk.END, game.get('name', 'Untitled Game'))

    def on_game_select(self, event=None):
        """Handles selection of a game from the listbox."""
        selected_indices = self.game_listbox.curselection()
        if selected_indices:
            self.selected_game_index = selected_indices[0]
            self.display_game_details(self.games[self.selected_game_index])
        else:
            self.selected_game_index = -1
            self.show_welcome_message() # Or clear details

    def display_game_details(self, game):
        """Displays the details of the selected game."""
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        # Labels for details (background set by ContentFrame.TFrame style)
        ttk.Label(self.details_frame, text="Game Details", style='DetailsTitle.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 20))

        ttk.Label(self.details_frame, text=f"Name: {game.get('name', 'N/A')}", style='GameName.TLabel').grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(self.details_frame, text=f"Platform: {game.get('platform', 'N/A')}", style='Platform.TLabel').grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(self.details_frame, text=f"Launch Path:", style='LaunchPath.TLabel').grid(row=3, column=0, sticky="w", pady=2)

        launch_path_entry = ttk.Entry(self.details_frame, width=50, state="readonly", style='TEntry')
        launch_path_entry.insert(0, game.get('launchPath', 'No launch path specified.'))
        launch_path_entry.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        launch_button = ttk.Button(self.details_frame, text="Launch Game", command=lambda: self.launch_game(game.get('launchPath', '')))
        self.style.map('Launch.TButton', background=[('active', '#006600'), ('!disabled', '#008000')]) # Green palette
        launch_button.config(style='Launch.TButton')
        launch_button.grid(row=5, column=0, pady=(15, 5), sticky="ew", padx=5)
        ttk.Label(self.details_frame, text="(Note: This will attempt to open the path. Success depends on correct path and system configuration.)",
                 style='SmallItalic.TLabel', wraplength=450).grid(row=6, column=0, sticky="w", padx=5, pady=(0, 15))

        ttk.Label(self.details_frame, text="Description:", style='Description.TLabel').grid(row=7, column=0, sticky="nw", pady=2)
        description_text = scrolledtext.ScrolledText(self.details_frame, wrap=tk.WORD, height=8, font=("Helvetica Neue", 10),
                                                   bd=0, relief="flat", bg='#4f4f4f', fg=self.COLOR_TEXT_LIGHT, padx=5, pady=5) # Dark bg, flat relief
        description_text.insert(tk.END, game.get('description', 'No description available.'))
        description_text.config(state=tk.DISABLED)
        description_text.grid(row=8, column=0, sticky="nsew", padx=5, pady=5)


    def launch_game(self, path):
        """Attempts to launch the game using its path or URI scheme, with admin mode for Windows executables."""
        if not path:
            messagebox.showinfo("Launch Game", "No launch path specified for this game.")
            return

        if sys.platform == "win32":
            if path.lower().endswith(".exe") and messagebox.askyesno("Launch as Admin?", f"Do you want to launch '{os.path.basename(path)}' as administrator?"):
                try:
                    # Attempt to launch .exe as administrator via PowerShell
                    command = f'powershell -Command "Start-Process -FilePath \\"{path}\\" -Verb RunAs"'
                    subprocess.Popen(command, shell=True)
                    messagebox.showinfo("Launch Game", f"Attempting to launch '{os.path.basename(path)}' as administrator. Please confirm UAC prompt if it appears.")
                    return
                except Exception as e:
                    messagebox.showerror("Launch Error", f"Could not launch '{os.path.basename(path)}' as administrator. Error: {e}\nFalling back to standard launch.")
                    # Fallback to standard launch if admin launch fails
                    try:
                        os.startfile(path)
                        messagebox.showinfo("Launch Game", f"Attempting standard launch for: {os.path.basename(path)}")
                        return
                    except Exception as e_fallback:
                        messagebox.showerror("Launch Error", f"Could not launch '{os.path.basename(path)}' via standard method. Error: {e_fallback}")
                        return
            elif path.startswith("steam://"):
                try:
                    subprocess.Popen(['explorer', path], shell=True) # Use explorer to handle URI schemes like steam://
                    messagebox.showinfo("Launch Game", f"Attempting to launch Steam game via URI: {path}")
                    return
                except Exception as e:
                    messagebox.showerror("Launch Error", f"Could not launch Steam game via URI. Error: {e}\n\nPlease ensure Steam is installed and running.")
                    return
            elif path.startswith("epicgames://"):
                try:
                    subprocess.Popen(['explorer', path], shell=True) # Use explorer for Epic Games URIs
                    messagebox.showinfo("Launch Game", f"Attempting to launch Epic Games via URI: {path}")
                    return
                except Exception as e:
                    messagebox.showerror("Launch Error", f"Could not launch Epic Games via URI. Error: {e}\n\nPlease ensure Epic Games Launcher is installed.")
                    return
            else: # Standard launch for other files/paths on Windows
                try:
                    os.startfile(path)
                    messagebox.showinfo("Launch Game", f"Attempting to launch: {path}")
                    return
                except FileNotFoundError:
                    messagebox.showerror("Launch Error", f"The specified path does not exist: {path}\n\nPlease check the launch path.")
                    return
                except Exception as e:
                    messagebox.showerror("Launch Error", f"Could not launch '{path}'. Error: {e}")
                    return
        elif sys.platform == "darwin": # macOS
            try:
                subprocess.Popen(['open', path])
                messagebox.showinfo("Launch Game", f"Attempting to launch: {path}")
            except FileNotFoundError:
                messagebox.showerror("Launch Error", f"The specified path does not exist: {path}\n\nPlease check the launch path.")
            except Exception as e:
                messagebox.showerror("Launch Error", f"Could not launch '{path}'. Error: {e}")
        else: # Linux/Unix
            try:
                subprocess.Popen(['xdg-open', path])
                messagebox.showinfo("Launch Game", f"Attempting to launch: {path}")
            except FileNotFoundError:
                messagebox.showerror("Launch Error", f"The specified path does not exist: {path}\n\nPlease check the launch path.")
            except Exception as e:
                messagebox.showerror("Launch Error", f"Could not launch '{path}'. Error: {e}")


    def show_add_game_form(self):
        """Displays the form for adding a new game."""
        self.show_game_form(None)

    def show_edit_game_form(self):
        """Displays the form for editing the selected game."""
        if self.selected_game_index == -1:
            messagebox.showwarning("No Game Selected", "Please select a game to edit from the list.")
            return
        self.show_game_form(self.games[self.selected_game_index])

    def show_game_form(self, game=None):
        """Generic function to display add/edit game form."""
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        is_edit_mode = game is not None
        title_text = "Edit Game" if is_edit_mode else "Add New Game"
        ttk.Label(self.details_frame, text=title_text, style='DetailsTitle.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Form fields with ttk widgets for better appearance
        current_row = 1

        ttk.Label(self.details_frame, text="Game Name (Required):", font=("Helvetica Neue", 10, "bold"), background=self.style.lookup('ContentFrame.TFrame', 'background')).grid(row=current_row, column=0, sticky="w", padx=5, pady=(5, 0))
        current_row += 1
        name_entry = ttk.Entry(self.details_frame, style='TEntry')
        name_entry.insert(0, game.get('name', '') if is_edit_mode else '')
        name_entry.grid(row=current_row, column=0, sticky="ew", padx=5, pady=(0, 10))
        current_row += 1


        ttk.Label(self.details_frame, text="Platform (Required):", font=("Helvetica Neue", 10, "bold"), background=self.style.lookup('ContentFrame.TFrame', 'background')).grid(row=current_row, column=0, sticky="w", padx=5, pady=(5, 0))
        current_row += 1
        platforms = ["", "Steam", "Epic Games", "GoG", "Origin/EA App", "Ubisoft Connect", "Battle.net", "Xbox App", "Local Install", "Other"]
        platform_combobox = ttk.Combobox(self.details_frame, values=platforms, state="readonly", font=("Helvetica Neue", 10), style='TCombobox')
        platform_combobox.set(game.get('platform', platforms[0]) if is_edit_mode else platforms[0])
        platform_combobox.grid(row=current_row, column=0, sticky="ew", padx=5, pady=(0, 10))
        current_row += 1


        ttk.Label(self.details_frame, text="Launch Path/Command:", font=("Helvetica Neue", 10, "bold"), background=self.style.lookup('ContentFrame.TFrame', 'background')).grid(row=current_row, column=0, sticky="w", padx=5, pady=(5, 0))
        current_row += 1
        launch_path_entry = ttk.Entry(self.details_frame, style='TEntry')
        launch_path_entry.insert(0, game.get('launchPath', '') if is_edit_mode else '')
        launch_path_entry.grid(row=current_row, column=0, sticky="ew", padx=5, pady=(0, 0))
        current_row += 1
        ttk.Label(self.details_frame, text="(e.g., C:\\Games\\MyGame\\Game.exe, steam://rungameid/12345, epicgames://apps/GameTitle)",
                  style='SmallItalic.TLabel').grid(row=current_row, column=0, sticky="w", padx=5, pady=(0, 10))
        current_row += 1


        ttk.Label(self.details_frame, text="Image URL (for reference):", font=("Helvetica Neue", 10, "bold"), background=self.style.lookup('ContentFrame.TFrame', 'background')).grid(row=current_row, column=0, sticky="w", padx=5, pady=(5, 0))
        current_row += 1
        image_entry = ttk.Entry(self.details_frame, style='TEntry')
        image_entry.insert(0, game.get('image', '') if is_edit_mode else '')
        image_entry.grid(row=current_row, column=0, sticky="ew", padx=5, pady=(0, 10))
        current_row += 1


        ttk.Label(self.details_frame, text="Description:", font=("Helvetica Neue", 10, "bold"), background=self.style.lookup('ContentFrame.TFrame', 'background')).grid(row=current_row, column=0, sticky="w", padx=5, pady=(5, 0))
        current_row += 1
        description_text_widget = scrolledtext.ScrolledText(self.details_frame, wrap=tk.WORD, height=5, font=("Helvetica Neue", 10),
                                                           bd=0, relief="flat", bg='#4f4f4f', fg=self.COLOR_TEXT_LIGHT, padx=5, pady=5)
        description_text_widget.insert(tk.END, game.get('description', '') if is_edit_mode else '')
        description_text_widget.grid(row=current_row, column=0, sticky="nsew", padx=5, pady=(0, 15))
        self.details_frame.grid_rowconfigure(current_row, weight=1)
        current_row += 1

        # Buttons
        button_container = ttk.Frame(self.details_frame, style='ContentFrame.TFrame')
        button_container.grid(row=current_row, column=0, sticky="e", pady=15)
        button_container.grid_columnconfigure(0, weight=1)
        button_container.grid_columnconfigure(1, weight=1)

        save_button = ttk.Button(button_container, text="Save Game",
                                command=lambda: self.save_game_from_form(name_entry, platform_combobox, launch_path_entry, image_entry, description_text_widget, is_edit_mode))
        self.style.map('Save.TButton', background=[('active', '#336699'), ('!disabled', '#4682B4')]) # Steel Blue palette
        save_button.config(style='Save.TButton')
        save_button.pack(side=tk.LEFT, padx=5, pady=8)

        cancel_button = ttk.Button(button_container, text="Cancel",
                                  command=self.show_welcome_message)
        self.style.map('Cancel.TButton', background=[('active', '#666666'), ('!disabled', '#808080')]) # Grey palette
        cancel_button.config(style='Cancel.TButton')
        cancel_button.pack(side=tk.LEFT, padx=5, pady=8)


    def save_game_from_form(self, name_entry, platform_combobox, launch_path_entry, image_entry, description_text_widget, is_edit_mode):
        """Saves or updates game data from the form fields."""
        name = name_entry.get().strip()
        platform = platform_combobox.get().strip()
        launch_path = launch_path_entry.get().strip()
        image = image_entry.get().strip()
        description = description_text_widget.get('1.0', tk.END).strip()

        if not name or not platform:
            messagebox.showwarning("Input Error", "Game Name and Platform are required.")
            return

        game_data = {
            "name": name,
            "platform": platform,
            "launchPath": launch_path,
            "image": image, # Storing image URL for reference, not displayed in this Tkinter version
            "description": description,
            "timestamp": datetime.now().isoformat()
        }

        if is_edit_mode and self.selected_game_index != -1:
            # Update existing game
            self.games[self.selected_game_index].update(game_data)
            messagebox.showinfo("Success", "Game updated successfully!")
        else:
            # Add new game
            self.games.append(game_data)
            messagebox.showinfo("Success", "Game added successfully!")

        save_games(self.games)
        self.populate_game_list()
        self.show_welcome_message() # Go back to welcome/empty details view

    def delete_game(self):
        """Deletes the selected game."""
        if self.selected_game_index == -1:
            messagebox.showwarning("No Game Selected", "Please select a game to delete.")
            return

        game_name = self.games[self.selected_game_index].get('name', 'selected game')
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{game_name}'?"):
            del self.games[self.selected_game_index]
            save_games(self.games)
            self.populate_game_list()
            self.selected_game_index = -1
            self.show_welcome_message()
            messagebox.showinfo("Deleted", "Game deleted successfully.")

# --- Run the Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = GameLibraryApp(root)
    root.mainloop()
