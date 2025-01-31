"""
this is (supposed to be) only the gui, most other stuff
is in gddt.py

uses python 3.11
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import gddt

# === main window ===

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()

        self.source = None
        self.dest = None
        self.label = None

        self.title = None
        self.menubar = None
        self.help_menu = None
        self.transfer_button = None
        self.phone_button = None
        self.pc_button = None
        self.result = None
        self.error_msg = None

    def create_ui(self):
        """create the ui for the main window"""

        self.title = tk.Label(self.root, text="GD Data Transfer", font=('Arial', 18))

        # create a menubar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        self.help_menu = tk.Menu(self.menubar, tearoff=False)

        # Help menu buttons
        self.help_menu.add_command(label='Settings', command=open_settings)
        self.help_menu.add_command(label='Exit', command=self.root.destroy)

        # add the Help menu to the menubar
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        # title
        self.title.pack(padx=20, pady=20)

        # message
        self.label = tk.Label(self.root, text="please select a destination first", font=('Arial', 12))
        self.label.pack(side=tk.BOTTOM, padx=20, pady=20)

        # transfer button
        self.transfer_button = tk.Button(self.root, text='Transfer', command=self.transfer_button_click)
        self.transfer_button.pack(side=tk.BOTTOM)

        # phone to computer button
        self.phone_button = tk.Button(self.root, text='Phone to computer', command=self.phone_button_click)
        self.phone_button.pack(pady=3)

        # computer to phone button
        self.pc_button = tk.Button(self.root, text='Computer to phone', command=self.pc_button_click)
        self.pc_button.pack(pady=3)

    # === main window functions ===

    def set_direction(self, new_source, new_dest):

        if self.source == new_source:
            self.change_msg(f"destination was already {new_dest}, are you stupid?")
        else:
            self.source = new_source
            self.dest = new_dest
            self.change_msg(f"changed destination to {new_dest}")

    def phone_button_click(self):
        self.set_direction("phone", "computer")

    def pc_button_click(self):
        self.set_direction("computer", "phone")

    def transfer_button_click(self):
        """transfer button click"""
        if self.source is None:
            self.change_msg("you didnt select anything")
        else:
            self.result = gddt.transfersaves(self.source, self.dest)

            if self.result.returncode == 0:
                self.change_msg("save files transferred succesfully!")
            else:
                self.error_msg = self.result.stderr.strip()

                # replace some error messages
                if "no devices/emulators found" in self.error_msg:
                    self.error_msg = "no devices found, is your device connected?"

                self.change_msg(f"couldnt transfer save files\n{self.error_msg}")

    def change_msg(self, new_message):
        """change message in window and print same message"""
        print(new_message)
        self.label.config(text=new_message)

main_window = MainWindow()

# === settings ===

def open_settings():
    """open settings window"""

    def refresh_revert_button_state():
        """disable revert transfer button if backups are disabled or no transfers have been made"""
        if backups_setting.get() and gddt.config_manager.last_transfer != "None":
            revert_transfer_button.config(state=tk.NORMAL)
        else:
            revert_transfer_button.config(state=tk.DISABLED)

    def save_settings():
        # save directories
        gddt.config_manager.set_dir('android_dir', android_dir_entry.get())
        gddt.config_manager.set_dir('pc_dir', pc_dir_entry.get())

        # save backups setting
        backups_setting_value = backups_setting.get()
        gddt.config_manager.set_backups_setting(backups_setting_value)

        refresh_revert_button_state()

        main_window.change_msg("saved settings!")

    settings_window = tk.Toplevel()
    settings_window.title("Settings")
    settings_window.resizable(0, 0)

    configlabel = tk.Label(settings_window, text="Settings", font=('Arial', 12))
    configlabel.grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.EW)

    # android dir label
    android_dir_label = tk.Label(settings_window, text="Android Directory")
    android_dir_label.grid(row=1, column=0, padx=10, pady=10)
    # android dir entry
    android_dir_entry = tk.Entry(settings_window)
    android_dir_entry.grid(row=1, column=1, padx=10, pady=10)
    android_dir_entry.insert(0, gddt.config_manager.android_dir)

    # pc dir label
    pc_dir_label = tk.Label(settings_window, text="Computer Directory")
    pc_dir_label.grid(row=2, column=0, padx=10, pady=10)
    # pc dir entry
    pc_dir_entry = tk.Entry(settings_window)
    pc_dir_entry.grid(row=2, column=1, padx=10, pady=10)
    pc_dir_entry.insert(0, gddt.config_manager.pc_dir)

    # toggle backups
    backups_setting = tk.BooleanVar(value=gddt.config_manager.save_backups)
    backups_checkbox = tk.Checkbutton(settings_window, text='Make backups',variable=backups_setting, onvalue=True, offvalue=False)
    backups_checkbox.grid(row=4, column=0, padx=10, pady=10)

    # revert transfer button
    revert_transfer_button = tk.Button(settings_window, text='Revert Last Transfer', command=revert_last_transfer)
    revert_transfer_button.grid(row=4, column=1, padx=10, pady=10)

    refresh_revert_button_state()

    # kill adb server button
    kill_button = tk.Button(settings_window, text='Kill ADB Server', command=kill_adb_server)
    kill_button.grid(row=5, column=1, padx=10, pady=10)

    # start adb server button
    start_button = tk.Button(settings_window, text='Start ADB Server', command=start_adb_server)
    start_button.grid(row=5, column=0, padx=10, pady=10)

    # save settings button
    save_button = tk.Button(settings_window, text='Save Settings', command=save_settings)
    save_button.grid(row=6, column=1, padx=10, pady=10)

# === settings functions ===

def kill_adb_server():
    kill_server_command = [str(gddt.path_adb), "kill-server"]
    subprocess.run(kill_server_command, capture_output=True, text=True, check=False)
    main_window.change_msg("adb server is kil")

def start_adb_server():
    start_server_command = [str(gddt.path_adb), "start-server"]
    subprocess.run(start_server_command, capture_output=True, text=True, check=False)
    main_window.change_msg("adb server started")

def revert_last_transfer():
    # assign previous destination so it can be used in the messagebox
    if gddt.config_manager.last_transfer == "phonetopc":
        prev_dest = "computer"
    else:
        prev_dest = "phone"

    response = messagebox.askyesno("Confirm action",
    "Doing this will revert the last transfer you have made, potentially" \
        f" making you lose progress if the save files in your {prev_dest} are newer than the" \
            f" backups made by GDDT. \n\nAre you sure you want to continue?")
    if response is True:
        gddt.revert_last_transfer()
        main_window.change_msg("last transfer reverted")
    else:
        main_window.change_msg("revert cancelled")


if __name__ == "__main__":
    main_window.root.title("GD Data Transfer")
    main_window.root.geometry("500x300")
    main_window.root.resizable(0, 0)

    main_window.create_ui()

    main_window.root.mainloop()
