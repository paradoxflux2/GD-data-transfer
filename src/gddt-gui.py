"""
the gui for gddt
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import gddt
from ttkthemes import ThemedTk
from ttkwidgets.autocomplete import AutocompleteCombobox
import tktooltip


class MainWindow:
    """
    main window management
    """

    def __init__(self):
        self.root = ThemedTk(theme=gddt.config_manager.theme, themebg=True)

        # window
        self.root.title("GD Data Transfer")
        self.root.geometry("500x300")
        self.root.resizable(0, 0)

        # set icon
        if gddt.IS_BUNDLE:
            icon_path = gddt.path_current_directory / "icon.png"
        else:
            icon_path = gddt.path_current_directory.parent / "assets" / "icon.png"

        self.root.iconphoto(True, tk.PhotoImage(file=icon_path))

        self.source = None
        self.dest = None

        self.transfer_result = None
        self.error_msg = None

        # create widgets
        # settings button
        self.settings_button = ttk.Label(self.root, text="Settings", cursor="hand2")

        # title
        self.title = ttk.Label(self.root, text="GD Data Transfer", font=("Arial", 18))

        # message
        self.label = ttk.Label(
            self.root, text="please select a destination first", font=("Arial", 12)
        )

        # transfer button
        self.transfer_button = ttk.Button(
            self.root, text="Transfer", command=self.transfer_button_click
        )

        # phone to computer button
        self.phone_button = ttk.Button(
            self.root,
            text="Phone to computer",
            command=lambda: self.set_direction("phone", "computer"),
        )

        # computer to phone button
        self.pc_button = ttk.Button(
            self.root,
            text="Computer to phone",
            command=lambda: self.set_direction("computer", "phone"),
        )

        self.pack_widgets()

        self.check_settings_messagebox()

    def pack_widgets(self):
        """
        create the ui for the main window
        """

        # settings button
        self.settings_button.pack(anchor=tk.NW)
        self.settings_button.bind(
            "<Button-1>", func=lambda event: settings_window.create_ui()
        )

        # title
        self.title.pack(padx=20, pady=20)

        # message
        self.label.pack(side=tk.BOTTOM, padx=20, pady=20)

        # transfer buttons
        self.transfer_button.pack(side=tk.BOTTOM)
        self.phone_button.pack(pady=3)
        self.pc_button.pack(pady=3)

    # === main window functions ===

    def set_direction(self, new_source, new_dest):
        """
        sets new source and destination
        """

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
        """
        transfer button click
        """
        if self.source is None:
            self.change_msg("you didnt select anything")
        else:
            self.transfer_result = gddt.transfersaves(self.source, self.dest)

            if self.transfer_result.returncode == 0:
                self.change_msg("save files transferred succesfully!")
            else:
                self.error_msg = self.transfer_result.stderr.strip()

                # replace some error messages
                if not gddt.config_manager.show_actual_error_messages:
                    for key, value in self.error_messages.items():
                        if key in self.error_msg:
                            self.error_msg = value
                            break

                self.change_msg(f"couldnt transfer save files\n{self.error_msg}")

    def change_msg(self, new_message):
        """
        change message in window and print same message
        """
        print(new_message)
        self.label.config(text=new_message)

    def check_settings_messagebox(self):
        if gddt.config_manager.first_run:
            messagebox.showinfo(
                "Info",
                "Before attempting to transfer, please go to the settings "
                "and make sure that the values are correct.",
            )
            gddt.config_manager.write_config("Other", "first_run", "False")


# === settings ===


class SettingsWindow:
    """
    the fucking settings window
    """

    def __init__(self):
        # "i wish there was an easier way to do this" ahh
        # i tried moving some of the declarations in
        # create_ui to here but that broke some things so uhh yeah
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

        self.style = ttk.Style(self.settings_window)
        self.bg_color = None
        self.theme_label = None
        self.new_theme = None
        self.current_theme = gddt.config_manager.theme
        self.themes_combo = None
        self.theme_options = None

    def create_ui(self):
        """
        open settings window
        """

        # this always broke the default value of the backups checkbox for some reason
        # self.settings_window = ThemedTk(theme=gddt.config_manager.theme, themebg=True)
        self.settings_window = tk.Toplevel()
        self.settings_window.title("Settings")
        self.settings_window.resizable(0, 0)

        # manually set bg color
        self.bg_color = self.style.lookup("TFrame", "background")
        self.settings_window.configure(bg=self.bg_color)

        sticky = {"sticky": "nswe"}

        # files label
        self.fileslabel = ttk.Label(
            self.settings_window, text="Files", font=("Arial", 12)
        )
        self.fileslabel.grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.N)

        # android dir label
        self.android_dir_label = ttk.Label(
            self.settings_window, text="Phone save files"
        )
        self.android_dir_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
        # android dir entry
        self.android_dir_entry = ttk.Entry(self.settings_window)
        self.android_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        self.android_dir_entry.insert(0, gddt.config_manager.android_dir)

        # pc dir label
        self.pc_dir_label = ttk.Label(self.settings_window, text="Computer save files")
        self.pc_dir_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.E)
        # pc dir entry
        self.pc_dir_entry = ttk.Entry(self.settings_window)
        self.pc_dir_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        self.pc_dir_entry.insert(0, gddt.config_manager.pc_dir)

        # save backups
        self.backups_setting = tk.BooleanVar(value=gddt.config_manager.save_backups)
        self.backups_checkbox = ttk.Checkbutton(
            self.settings_window,
            text="Make backups",
            variable=self.backups_setting,
            onvalue=True,
            offvalue=False,
        )
        self.backups_checkbox.grid(row=3, column=0, padx=10, pady=10)
        # save backups tooltip
        tktooltip.ToolTip(
            self.backups_checkbox,
            msg="If backups will be saved every "
            "time the transfer button is clicked.",
            delay=1.0,
        )

        # revert transfer button
        self.revert_transfer_button = ttk.Button(
            self.settings_window,
            text="Revert Last Transfer",
            command=self.revert_last_transfer,
        )
        self.revert_transfer_button.grid(row=3, column=1, padx=10, pady=10)

        self.refresh_revert_button_state()

        tktooltip.ToolTip(
            self.revert_transfer_button,
            msg="Reverts the previous transfer. Useful if, for example, you accidentally"
            " clicked the wrong destination so you lost some progress there."
            "\n\nOnly works with 'Make Backups' enabled.",
            delay=1.0,
        )

        # other label
        self.otherlabel = ttk.Label(
            self.settings_window, text="Other", font=("Arial", 12)
        )
        self.otherlabel.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.N)

        # theme label
        self.theme_label = ttk.Label(self.settings_window, text="Theme")
        self.theme_label.grid(row=5, column=0, padx=10, pady=10, sticky=tk.E)

        # theme combo
        self.theme_options = self.filter_themes(main_window.root.get_themes())
        self.theme_options.sort()
        self.new_theme = tk.StringVar(self.settings_window)

        self.themes_combo = AutocompleteCombobox(
            self.settings_window,
            completevalues=self.theme_options,
            textvariable=self.new_theme,
        )
        self.themes_combo.set(self.current_theme)
        self.themes_combo.grid(row=5, column=1, padx=10, pady=10, sticky=tk.W)

        # theme combo tooltip
        tktooltip.ToolTip(
            self.themes_combo,
            msg="The TTK Theme that the program will use."
            "\nMost of the default themes are hidden because they suck,"
            " you can still type them in though. Or you can also change"
            " hide_ugly_themes in settings.ini if you prefer.",
            delay=1.0,
        )

        # kill adb server button
        self.kill_button = ttk.Button(
            self.settings_window,
            text="Kill ADB Server",
            command=lambda: self.toggle_adb_server("kill-server"),
        )
        self.kill_button.grid(row=6, column=1, padx=10, pady=10)
        # kill adb server tooltip
        tktooltip.ToolTip(
            self.kill_button,
            msg="Kills the ADB server."
            "\nI recommend always doing this after"
            " transferring.",
            delay=1.0,
        )

        # start adb server button
        self.start_button = ttk.Button(
            self.settings_window,
            text="Start ADB Server",
            command=lambda: self.toggle_adb_server("start-server"),
        )
        self.start_button.grid(row=6, column=0, padx=10, pady=10)
        # start adb server tooltip
        tktooltip.ToolTip(
            self.start_button,
            msg="Starts the ADB server."
            "\nThis is automatically done when transferring"
            " so this button is kinda useless but I already added"
            " 'Kill ADB Server' so it would feel kinda weird not to have"
            " this button too",
            delay=1.0,
        )

        # save settings button
        self.save_button = ttk.Button(
            self.settings_window, text="Save Settings", command=self.save_settings
        )
        self.save_button.grid(row=7, padx=10, pady=10, columnspan=2, **sticky)

    # === settings functions ===

    def refresh_revert_button_state(self):
        """
        disable revert transfer button if backups are disabled or no transfers have been made
        """
        if self.backups_setting.get() and gddt.config_manager.last_transfer != "None":
            self.revert_transfer_button.config(state=tk.NORMAL)
        else:
            self.revert_transfer_button.config(state=tk.DISABLED)

    def save_settings(self):
        """
        saves settings to config file
        """
        # save directories
        gddt.config_manager.write_config(
            "Directories", "android_dir", self.android_dir_entry.get()
        )
        gddt.config_manager.write_config(
            "Directories", "pc_dir", self.pc_dir_entry.get()
        )

        # save backups setting
        self.backups_setting_value = self.backups_setting.get()
        gddt.config_manager.write_config(
            "Files", "save_backups", str(self.backups_setting.get())
        )

        self.refresh_revert_button_state()

        # save new theme
        if self.new_theme.get() in main_window.root.get_themes():
            gddt.config_manager.write_config("Other", "theme", self.new_theme.get())
            self.update_theme()

        main_window.change_msg("saved settings!")

    def update_theme(self):
        """
        updates the theme
        """
        main_window.root.set_theme(self.themes_combo.get())
        main_window.root.update()

        # manually update bg color for the settings window
        self.bg_color = self.style.lookup("TFrame", "background")
        self.settings_window.configure(bg=self.bg_color)

        self.current_theme = self.new_theme.get()

    def filter_themes(self, themes):
        """
        filter out themes that suck
        """
        if gddt.config_manager.hide_ugly_themes:
            ugly_themes = [
                "alt",
                "aquativo",
                "black",
                "blue",
                "clam",
                "clearlooks",
                "default",
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
                "ubuntu",
            ]
            good_themes = []

            for theme in themes:
                if theme not in ugly_themes:
                    good_themes.append(theme)

            return good_themes

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
    main_window.root.mainloop()
