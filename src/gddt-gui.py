"""
the gui for gddt
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from ttkwidgets.autocomplete import AutocompleteCombobox
import tktooltip
import gddt

TITLE = "GD Data Transfer"
WINDOW_SIZE = "400x280"

FIRST_RUN_INFO = (
    "Before clicking 'transfer', please go to the settings "
    "and make sure that the values are correct.\n"
    "Also always make sure GD is closed, otherwise"
    " GD will rewrite the saved data, making the transfer useless :("
    "\n\nThis message won't be shown again",
)


class MainWindow:
    """
    main window management
    """

    def __init__(self):
        self.root = ThemedTk(theme=gddt.config_manager.theme, themebg=True)

        # window
        self.root.title(TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)

        self.set_window_icon()

        self.source: str = None
        self.dest: str = None

        self.command_output = "Command output will show here"
        self.error_msg: str = None

        self.place_widgets()

        self.first_run_messagebox()

    def set_window_icon(self):
        if gddt.IS_BUNDLE:
            icon_path = gddt.path_current_directory / "icon.png"
        else:
            icon_path = gddt.path_current_directory.parent / "assets" / "icon.png"

        self.root.iconphoto(True, tk.PhotoImage(file=icon_path))

    def place_widgets(self):
        """place widgets in the main window"""

        self.settings_button = ttk.Label(self.root, text="Settings", cursor="hand2")
        self.settings_button.place(x=0, y=0)
        self.settings_button.bind(
            "<Button-1>", func=lambda event: settings_window.create_ui()
        )

        self.title = ttk.Label(self.root, text="Transfer from:", font=("Arial", 14))
        self.title.place(x=75, y=80)

        self.phone_to_pc_button = ttk.Button(
            self.root,
            text="Phone to computer",
            command=lambda: self.set_direction("phone", "computer"),
        )
        self.phone_to_pc_button.place(x=215, y=60)

        self.pc_to_phone_button = ttk.Button(
            self.root,
            text="Computer to phone",
            command=lambda: self.set_direction("computer", "phone"),
        )
        self.pc_to_phone_button.place(x=215, y=110)

        self.transfer_button = ttk.Button(
            self.root,
            text="Transfer",
            command=self.transfer_button_click,
            state=tk.DISABLED,
        )
        self.transfer_button.place(relx=0.5, y=200, anchor=tk.CENTER)

        self.label = ttk.Label(
            self.root,
            text="please select a destination first",
            font=("Arial", 12),
        )
        self.label.pack(side=tk.BOTTOM, padx=20, pady=20)
        self.label.bind(
            "<Button-1>",
            func=lambda event: messagebox.showinfo(
                "Command Output", self.command_output
            ),
        )

    # === main window functions ===

    def set_direction(self, new_source: str, new_dest: str):
        """sets new source and destination"""

        if self.source == new_source:
            self.change_msg(f"destination was already {new_dest}, are you stupid?")
        else:
            self.source = new_source
            self.dest = new_dest
            self.change_msg(f"changed destination to {new_dest}")

        self.transfer_button.config(state=tk.NORMAL)

    def transfer_button_click(self):
        """transfer button click event"""

        result = gddt.transfer_saves(self.source, self.dest)
        self.command_output = result.stderr.strip()

        if result.returncode == 0:
            self.change_msg("save files transferred succesfully!")
        else:
            if gddt.config_manager.show_actual_error_messages is False:
                error_message = self.replace_error_msg(self.command_output)
            else:
                error_message = self.command_output

            self.change_msg(f"couldnt transfer save files\n{error_message}")

    def replace_error_msg(self, output: str) -> str:
        """replaces error messages with a bit more user-friendly ones"""

        # error messages to be replaced if found in command output
        error_messages = {
            "no devices/emulators found": "no devices found, is your device connected?",
            "No such file": "please verify that directories are correct",
            "Try 'adb kill-server'": "try going to the settings and killing the ADB server",
        }
        for key, value in error_messages.items():
            if key in output:
                error_message = value
                break

        return error_message

    def change_msg(self, new_message: str, fontsize=12):
        """change message in window"""
        # change text size depending on the message length
        chars_before_resize = 70

        message_length = len(new_message)
        if message_length > chars_before_resize:
            fontsize = fontsize * (0.995 ** (message_length - chars_before_resize))
            fontsize = round(max(fontsize, 5))

        self.label.config(text=new_message, font=("Arial", fontsize), justify="center")

    def first_run_messagebox(self):
        """display a message box on first run"""
        if gddt.config_manager.first_run:
            messagebox.showinfo("Info", FIRST_RUN_INFO)
            gddt.config_manager.write_config("Other", "first_run", "False")


# === settings ===


class SettingsWindow:
    """
    the fucking settings window
    """

    def __init__(self):
        # i tried moving some of the declarations in
        # create_ui to here but that broke some things so uhh yeah
        self.settings_window = None
        self.files_label = None
        self.android_dir_label = None
        self.android_dir_entry = None
        self.pc_dir_label = None
        self.pc_dir_entry = None
        self.backups_setting = None
        self.backups_checkbox = None
        self.revert_transfer_button = None
        self.kill_button = None
        self.show_devices_button = None
        self.save_button = None
        self.other_label = None

        self.style = ttk.Style(self.settings_window)
        self.bg_color = self.style.lookup("TFrame", "background")
        self.fg_color = self.style.lookup("TFrame", "foreground")
        self.theme_label = None
        self.new_theme = None
        self.current_theme = gddt.config_manager.theme
        self.themes_combo = None
        self.theme_options = None
        self.last_transfer_label = None

    def create_ui(self):
        """open settings window"""

        # this always broke the default value of the
        # backups checkbox for some reason idk why :((
        # self.settings_window = ThemedTk(theme=gddt.config_manager.theme, themebg=True)
        self.settings_window = tk.Toplevel()
        self.settings_window.title("Settings")
        self.settings_window.resizable(0, 0)

        self.settings_window.configure(bg=self.bg_color)

        sticky = {"sticky": "nswe"}

        # files label
        self.files_label = ttk.Label(
            self.settings_window, text="Files", font=("Arial", 12)
        )
        self.files_label.grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.N)

        # android dir label
        self.android_dir_label = ttk.Label(
            self.settings_window, text="Phone save files"
        )
        self.android_dir_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
        # android dir entry
        self.android_dir_entry = ttk.Entry(self.settings_window)
        self.android_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        self.android_dir_entry.insert(0, gddt.config_manager.android_dir)
        # android dir tooltip
        self.add_tooltip(
            self.android_dir_entry,
            msg="The folder where GD save files are, in the Android device",
        )

        # pc dir label
        self.pc_dir_label = ttk.Label(self.settings_window, text="Computer save files")
        self.pc_dir_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.E)
        # pc dir entry
        self.pc_dir_entry = ttk.Entry(self.settings_window)
        self.pc_dir_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        self.pc_dir_entry.insert(0, gddt.config_manager.pc_dir)
        # pc dir tooltip
        self.add_tooltip(
            self.pc_dir_entry,
            msg="The folder where GD save files are, in this computer",
        )

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
        self.add_tooltip(
            self.backups_checkbox,
            msg="If backups will be saved every time the transfer button is clicked",
        )

        # revert transfer button
        self.revert_transfer_button = ttk.Button(
            self.settings_window,
            text="Revert Last Transfer",
            command=self.revert_last_transfer,
        )
        self.revert_transfer_button.grid(row=3, column=1, padx=10, pady=10)

        self.refresh_revert_button_state()

        self.add_tooltip(
            self.revert_transfer_button,
            msg="Reverts the previous transfer.\nUseful if, for example, you accidentally"
            " clicked the wrong destination so you lost\nsome progress there\n\n"
            "Only works with 'Make Backups' enabled",
        )

        # last transfer label
        if gddt.config_manager.last_transfer == "pctophone":
            last_transfer = "Computer to phone"
        elif gddt.config_manager.last_transfer == "phonetopc":
            last_transfer = "Phone to computer"
        else:
            last_transfer = "None"

        self.last_transfer_label = ttk.Label(
            self.settings_window,
            text=f"Last transfer: {last_transfer}",
            font=("Arial", 7),
        )
        self.last_transfer_label.grid(row=3, column=1, sticky=tk.S)

        # other label
        self.other_label = ttk.Label(
            self.settings_window, text="Other", font=("Arial", 12)
        )
        self.other_label.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.N)

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
        self.add_tooltip(
            self.themes_combo,
            msg="The TTK Theme that the program will use"
            "\nMost of the default themes are hidden because they suck,"
            " you can still type them in though. Or you can also change"
            " hide_ugly_themes in settings.ini if you prefer",
        )

        # kill adb server button
        self.kill_button = ttk.Button(
            self.settings_window,
            text="Kill ADB Server",
            command=self.kill_adb,
        )
        self.kill_button.grid(row=6, column=1, padx=10, pady=10)
        # kill adb server tooltip
        self.add_tooltip(
            self.kill_button,
            msg="Kills the ADB server."
            "\nI recommend always doing this after transferring",
        )

        # show devices button
        self.show_devices_button = ttk.Button(
            self.settings_window,
            text="Show Devices",
            command=self.show_devices,
        )
        self.show_devices_button.grid(row=6, column=0, padx=10, pady=10)
        # show devices tooltip
        self.add_tooltip(
            self.show_devices_button,
            msg="Show devices attached",
        )

        # save settings button
        self.save_button = ttk.Button(
            self.settings_window, text="Save Settings", command=self.save_settings
        )
        self.save_button.grid(row=7, padx=10, pady=10, columnspan=2, **sticky)

    # === settings functions ===

    def add_tooltip(self, button, msg):
        """creates a tooltip with preset parameters"""
        tktooltip.ToolTip(
            button,
            msg=msg,
            delay=2,
            bg=self.bg_color,
            fg=self.fg_color,
        )

    def save_settings(self):
        """save settings button event"""
        # save directories
        gddt.config_manager.write_config(
            "Directories", "android_dir", self.android_dir_entry.get()
        )
        gddt.config_manager.write_config(
            "Directories", "pc_dir", self.pc_dir_entry.get()
        )

        # save backups setting
        gddt.config_manager.write_config(
            "Files", "save_backups", self.backups_setting.get()
        )

        self.refresh_revert_button_state()

        # save new theme
        if self.new_theme.get() in main_window.root.get_themes():
            gddt.config_manager.write_config("Other", "theme", self.new_theme.get())
            self.update_theme()

        main_window.change_msg("saved settings!")

    def update_theme(self):
        """updates the theme for both windows"""
        main_window.root.set_theme(self.themes_combo.get())
        main_window.root.update()

        # manually update bg color for the settings window
        self.bg_color = self.style.lookup("TFrame", "background")
        self.settings_window.configure(bg=self.bg_color)

        self.current_theme = self.new_theme.get()

    def filter_themes(self, themes: list[str]) -> list[str]:
        """filter out themes that suck"""
        if gddt.config_manager.hide_ugly_themes is True:
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

    def kill_adb(self):
        """runs an adb command"""
        adb_command = [str(gddt.path_adb), "kill-server"]
        gddt.subprocess_run(adb_command)
        main_window.change_msg("adb server is kil")

    def show_devices(self):
        """shows a popup with connected devices"""
        adb_command = [str(gddt.path_adb), "devices"]
        result = gddt.subprocess_run(adb_command)

        messagebox.showinfo(title="Devices", message=result.stdout.strip())

    def revert_last_transfer(self):
        """reverts the last transfer"""

        # assign previous destination so it can be used in the messagebox
        if gddt.config_manager.last_transfer == "phonetopc":
            prev_dest = "computer"
        else:
            prev_dest = "phone"

        response = messagebox.askyesno(
            "Confirm action",
            "Doing this will revert the last transfer you have made, potentially"
            f" making you lose progress if the save files in your {prev_dest} are newer than"
            f" the backups made by GDDT. \n\nAre you sure you want to continue?",
        )
        if response is True:
            gddt.revert_last_transfer()
            self.refresh_revert_button_state()

            main_window.change_msg("last transfer reverted")
        else:
            main_window.change_msg("revert cancelled")

    def refresh_revert_button_state(self):
        """disable revert transfer button if backups are disabled or no transfers have been made"""
        if self.backups_setting.get() and gddt.config_manager.last_transfer != "None":
            self.revert_transfer_button.config(state=tk.NORMAL)
        else:
            self.revert_transfer_button.config(state=tk.DISABLED)


main_window = MainWindow()
settings_window = SettingsWindow()

if __name__ == "__main__":
    main_window.root.mainloop()
