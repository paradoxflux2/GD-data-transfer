"""
this is (supposed to be) only the gui, most other stuff
is in gddt.py

uses python 3.11
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import gddt
from ttkthemes import ThemedTk


class MainWindow:
    """main window management"""

    def __init__(self):
        self.root = ThemedTk(theme=gddt.config_manager.theme)

        # window
        self.root.title("GD Data Transfer")
        self.root.geometry("500x300")
        self.root.resizable(0, 0)

        # bg color
        self.style = ttk.Style(self.root)
        self.bg_color = self.style.lookup("TFrame", "background")
        self.root.configure(bg=self.bg_color)

        self.source = None
        self.dest = None
        self.label = None
        self.title = None
        self.menubar = None
        self.help_menu = None
        self.transfer_button = None
        self.phone_button = None
        self.pc_button = None
        self.transfer_result = None
        self.error_msg = None

    def create_ui(self):
        """create the ui for the main window"""

        self.title = ttk.Label(self.root, text="GD Data Transfer", font=("Arial", 18))

        # create a menubar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        self.help_menu = tk.Menu(self.menubar, tearoff=False)

        # Help menu buttons
        self.help_menu.add_command(label="Settings", command=settings_window.create_ui)
        self.help_menu.add_command(label="Exit", command=self.root.destroy)

        # add the Help menu to the menubar
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        # title
        self.title.pack(padx=20, pady=20)

        # message
        self.label = ttk.Label(
            self.root, text="please select a destination first", font=("Arial", 12)
        )
        self.label.pack(side=tk.BOTTOM, padx=20, pady=20)

        # transfer button
        self.transfer_button = ttk.Button(
            self.root, text="Transfer", command=self.transfer_button_click
        )
        self.transfer_button.pack(side=tk.BOTTOM)

        # phone to computer button
        self.phone_button = ttk.Button(
            self.root,
            text="Phone to computer",
            command=lambda: self.set_direction("phone", "computer"),
        )
        self.phone_button.pack(pady=3)

        # computer to phone button
        self.pc_button = ttk.Button(
            self.root,
            text="Computer to phone",
            command=lambda: self.set_direction("computer", "phone"),
        )
        self.pc_button.pack(pady=3)

    # === main window functions ===

    def set_direction(self, new_source, new_dest):
        """sets new source and destination"""

        if self.source == new_source:
            self.change_msg(f"destination was already {new_dest}, are you stupid?")
        else:
            self.source = new_source
            self.dest = new_dest
            self.change_msg(f"changed destination to {new_dest}")

    # error messages that will be replaced
    # if a key is found in the command output, it will be replaced by its value
    error_messages = {
        "no devices/emulators found": "no devices found, is your device connected?",
        "No such file": "please verify that directories are correct",
    }

    def transfer_button_click(self):
        """transfer button click"""
        if self.source is None:
            self.change_msg("you didnt select anything")
        else:
            self.transfer_result = gddt.transfersaves(self.source, self.dest)

            if self.transfer_result.returncode == 0:
                self.change_msg("save files transferred succesfully!")
            else:
                self.error_msg = self.transfer_result.stderr.strip()

                # replace some error messages
                for key, value in self.error_messages.items():
                    if key in self.error_messages:
                        self.error_msg = value
                        break

                self.change_msg(f"couldnt transfer save files\n{self.error_msg}")

    def change_msg(self, new_message):
        """change message in window and print same message"""
        print(new_message)
        self.label.config(text=new_message)


# === settings ===


class SettingsWindow:
    def __init__(self):
        self.settings_window = None
        self.fileslabel = None
        self.android_dir_label = None
        self.android_dir_entry = None
        self.pc_dir_label = None
        self.pc_dir_entry = None
        self.backups_setting = None
        self.backups_checkbox = None
        self.revert_transfer_button = None
        self.kill_button = None
        self.start_button = None
        self.save_button = None

        self.backups_setting_value = None
        self.prev_dest = None
        self.response = None
        
        self.otherlabel = None
        self.kill_server_command = None
        self.start_server_command = None

        self.style = None
        self.bg_color = None
        self.theme_label = None
        self.theme = None
        self.theme_dropdown = None
        self.current_theme = None

    def create_ui(self):
        """open settings window"""

        self.settings_window = tk.Toplevel()
        self.settings_window.title("Settings")
        self.settings_window.resizable(0, 0)

        # bg color
        self.style = ttk.Style(self.settings_window)
        self.bg_color = self.style.lookup("TFrame", "background")
        self.settings_window.configure(bg=self.bg_color)

        # files label
        self.fileslabel = ttk.Label(
            self.settings_window, text="Files", font=("Arial", 12)
        )
        self.fileslabel.grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.N)

        # android dir label
        self.android_dir_label = ttk.Label(
            self.settings_window, text="Android Directory"
        )
        self.android_dir_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
        # android dir entry
        self.android_dir_entry = ttk.Entry(self.settings_window)
        self.android_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        self.android_dir_entry.insert(0, gddt.config_manager.android_dir)

        # pc dir label
        self.pc_dir_label = ttk.Label(
            self.settings_window, text="Computer Directory"
        )
        self.pc_dir_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.E)
        # pc dir entry
        self.pc_dir_entry = ttk.Entry(self.settings_window)
        self.pc_dir_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        self.pc_dir_entry.insert(0, gddt.config_manager.pc_dir)

        # toggle backups
        self.backups_setting = tk.BooleanVar(value=gddt.config_manager.save_backups)
        self.backups_checkbox = ttk.Checkbutton(
            self.settings_window,
            text="Make backups",
            variable=self.backups_setting,
            onvalue=True,
            offvalue=False,
        )
        self.backups_checkbox.grid(row=3, column=0, padx=10, pady=10)

        # revert transfer button
        self.revert_transfer_button = ttk.Button(
            self.settings_window,
            text="Revert Last Transfer",
            command=self.revert_last_transfer,
        )
        self.revert_transfer_button.grid(row=3, column=1, padx=10, pady=10)

        self.refresh_revert_button_state()

        # other label
        self.otherlabel = ttk.Label(
            self.settings_window, text="Other", font=("Arial", 12)
        )
        self.otherlabel.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.N)

        # theme label
        self.theme_label = ttk.Label(self.settings_window, text="Theme")
        self.theme_label.grid(row=5, column=0, padx=10, pady=10, sticky=tk.E)

        # theme dropdown menu
        theme_options = self.filter_themes(main_window.root.get_themes())
        theme_options.sort()
        self.theme = tk.StringVar(self.settings_window)
        self.theme.set(gddt.config_manager.theme)

        self.theme_dropdown = ttk.OptionMenu(
            self.settings_window, self.theme, gddt.config_manager.theme, *theme_options
        )

        self.theme_dropdown.grid(row=5, column=1, padx=10, pady=10, sticky=tk.W)

        # kill adb server button
        self.kill_button = ttk.Button(
            self.settings_window,
            text="Kill ADB Server",
            command=lambda: self.toggle_adb_server("kill-server"),
        )
        self.kill_button.grid(row=6, column=1, padx=10, pady=10)

        # start adb server button
        self.start_button = ttk.Button(
            self.settings_window,
            text="Start ADB Server",
            command=lambda: self.toggle_adb_server("start-server"),
        )
        self.start_button.grid(row=6, column=0, padx=10, pady=10)

        # save settings button
        self.save_button = ttk.Button(
            self.settings_window, text="Save Settings", command=self.save_settings
        )
        self.save_button.grid(row=7, column=1, padx=10, pady=10)

        self.current_theme = gddt.config_manager.theme

    # === settings functions ===

    def refresh_revert_button_state(self):
        """disable revert transfer button if backups are disabled or no transfers have been made"""
        if self.backups_setting.get() and gddt.config_manager.last_transfer != "None":
            self.revert_transfer_button.config(state=tk.NORMAL)
        else:
            self.revert_transfer_button.config(state=tk.DISABLED)

    def save_settings(self):
        # save directories
        gddt.config_manager.set_dir("android_dir", self.android_dir_entry.get())
        gddt.config_manager.set_dir("pc_dir", self.pc_dir_entry.get())

        # save backups setting
        self.backups_setting_value = self.backups_setting.get()
        gddt.config_manager.set_backups_setting(self.backups_setting_value)

        self.refresh_revert_button_state()

        # save new theme
        gddt.config_manager.write_config("Other", "theme", self.theme.get())
        self.change_theme()

        main_window.change_msg("saved settings!")

    def change_theme(self):
        main_window.root.set_theme(self.theme.get())
        main_window.root.update()

        # change bg color
        self.bg_color = self.style.lookup("TFrame", "background")
        self.settings_window.configure(bg=self.bg_color)

        main_window.bg_color = main_window.style.lookup("TFrame", "background")
        main_window.root.configure(bg=main_window.bg_color)

    def filter_themes(self, themes):
        """filter out themes that suck"""
        if gddt.config_manager.hide_ugly_themes:
            ugly_themes = [
                "default",
                "alt",
                "aquativo",
                "black",
                "blue",
                "clam",
                "clearlooks",
                "elegance",
                "itft1",
                "keramik",
                "kroc",
                "plastik",
                "radiance",
                "scidblue",
                "scidgreen",
                "scidgrey",
                "scidmint",
                "scidpink",
                "scidpurple",
                "scidsand",
                "smog",
                "ubuntu"
            ]
            good_themes = []

            for theme in themes:
                if theme not in ugly_themes:
                    good_themes.append(theme)

            return good_themes
        else:
            return themes

    def toggle_adb_server(self, command):
        adb_command = [str(gddt.path_adb), command]
        subprocess.run(adb_command, capture_output=True, text=True, check=False)
        if command == "start-server":
            state = "started"
        else:
            state = "is kil"

        main_window.change_msg(f"adb server {state}")

    def revert_last_transfer(self):
        # assign previous destination so it can be used in the messagebox
        if gddt.config_manager.last_transfer == "phonetopc":
            self.prev_dest = "computer"
        else:
            self.prev_dest = "phone"

        self.response = messagebox.askyesno(
            "Confirm action",
            "Doing this will revert the last transfer you have made, potentially"
            f" making you lose progress if the save files in your {self.prev_dest} are newer than"
            f" the backups made by GDDT. \n\nAre you sure you want to continue?",
        )
        if self.response is True:
            gddt.revert_last_transfer()
            main_window.change_msg("last transfer reverted")
        else:
            main_window.change_msg("revert cancelled")


main_window = MainWindow()
settings_window = SettingsWindow()

if __name__ == "__main__":

    main_window.create_ui()

    main_window.root.mainloop()
