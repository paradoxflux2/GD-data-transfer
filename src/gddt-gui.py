"""
this is (supposed to be) only the gui, most other stuff
is in gddt.py

uses python 3.11
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import gddt

root = tk.Tk()

source = None
label = None

# === main window ===

def create_ui():
    """create the ui for the main window"""
    global label

    # create a menubar
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    help_menu = tk.Menu(menubar, tearoff=False)

    # Help menu buttons
    help_menu.add_command(label='Settings', command=open_settings)
    help_menu.add_command(label='Exit', command=root.destroy)

    # add the Help menu to the menubar
    menubar.add_cascade(label="Help", menu=help_menu)

    # title
    title = tk.Label(root, text="GD Data Transfer", font=('Arial', 18))
    title.pack(padx=20, pady=20)

    # message
    label = tk.Label(root, text="please select a destination first", font=('Arial', 12))
    label.pack(side=tk.BOTTOM, padx=20, pady=20)

    # transfer button
    transfer_button = tk.Button(root, text='Transfer', command=transfer_button_click)
    transfer_button.pack(side=tk.BOTTOM)

    # phone to computer button
    phone_button = tk.Button(root, text='Phone to computer', command=phone_button_click)
    phone_button.pack(pady=3)

    # computer to phone button
    pc_button = tk.Button(root, text='Computer to phone', command=pc_button_click)
    pc_button.pack(pady=3)

direction = {"phone": "computer", "computer": "phone"} # if source is phone, destination is computer, etc

# === main window functions ===

def set_source(device):
    global source
    if source == device: # extra useless code yay
        change_msg(f"destination was already {direction[source]}, are you stupid?")
    else:
        source = device
        change_msg(f"changed destination to {direction[source]}")

def phone_button_click():
    set_source("phone")

def pc_button_click():
    set_source("computer")

def transfer_button_click():
    """transfer button click"""
    if source is None:
        change_msg("you didnt select anything")
    else:
        result = gddt.transfersaves(source)
        if gddt.exitstatus == 0:
            change_msg("save files transferred succesfully!")
        else:
            error_msg = result.stderr.strip()
            if "no devices/emulators found" in error_msg:
                error_msg = "is your device connected?"
        
            change_msg(f"couldnt transfer save files\n{error_msg}")


def change_msg(new_message):
    """change message in window and print same message"""
    print(new_message)
    label.config(text = new_message)

# === settings ===

def open_settings():
    """open settings window"""

    def refresh_revert_button_state():
        """disable revert transfer button if backups are disabled or no transfers have been made"""
        if backups_setting.get() and gddt.config_data['last_transfer'] != "None":
            revert_transfer_button.config(state=tk.NORMAL)
        else:
            revert_transfer_button.config(state=tk.DISABLED)

    def save_settings():
        # save directories
        gddt.set_dir('android_dir', android_dir_entry.get())
        gddt.set_dir('pc_dir', pc_dir_entry.get())

        # save backups setting
        backups_setting_value = backups_setting.get()
        gddt.set_backups_setting(backups_setting_value)

        refresh_revert_button_state()

        change_msg("saved settings!")

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
    android_dir_entry.insert(0, gddt.config_data['android_dir'])

    # pc dir label
    pc_dir_label = tk.Label(settings_window, text="Computer Directory")
    pc_dir_label.grid(row=2, column=0, padx=10, pady=10)
    # pc dir entry
    pc_dir_entry = tk.Entry(settings_window)
    pc_dir_entry.grid(row=2, column=1, padx=10, pady=10)
    pc_dir_entry.insert(0, gddt.config_data['pc_dir'])

    # toggle backups
    backups_setting = tk.BooleanVar(value=gddt.config_data['save_backups'])
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
    change_msg("adb server is kil")

def start_adb_server():
    start_server_command = [str(gddt.path_adb), "start-server"]
    subprocess.run(start_server_command, capture_output=True, text=True, check=False)
    change_msg("adb server started")

def revert_last_transfer():
    # assign previous destination so it can be used in the messagebox
    if gddt.config_data['last_transfer'] == "phonetopc":
        prev_dest = "computer"
    else:
        prev_dest = "phone"

    response = messagebox.askyesno("Confirm action",
    "Doing this will revert the last transfer you have made, potentially" \
        f" making you lose progress if the save files in your {prev_dest} are newer than the" \
            f" backups made by GDDT. \n\nAre you sure you want to continue?")
    if response is True:
        gddt.revert_last_transfer()
        change_msg("last transfer reverted")
    if response is False:
        change_msg("action cancelled")


if __name__ == "__main__":
    root.title("GD Data Transfer")
    root.geometry("500x300")
    root.resizable(0, 0)

    create_ui()

    root.mainloop()
