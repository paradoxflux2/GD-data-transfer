"""
this is (supposed to be) only the gui, most other stuff
is in transfersave.py

uses python 3.11
"""

import tkinter as tk
import subprocess
import transfersave

root = tk.Tk()

origin = None

def change_msg(new_message):
    """change message in window and print same message"""
    print(new_message)
    label.config(text = new_message)

# button functions

def set_origin(device):
    global origin
    if origin == device: # extra useless code yay
        change_msg(f"destination was already {device}, are you stupid?")
    else:
        origin = {device}
        change_msg(f"changed destination to {device}")

def phone_button_click():
    set_origin("phone")

def pc_button_click():
    set_origin("computer")

def transfer_button_click():
    """transfer button click"""
    if origin == None:
        change_msg("you didnt select anything")
    else:
        result = transfersave.transfersaves(origin)
        if transfersave.exitstatus == 0:
            change_msg("save files transferred succesfully!")
        else:
            change_msg(f"couldnt transfer files\n{result.stderr.strip()}")

# settings

def open_settings():
    settings_window = tk.Toplevel()
    settings_window.title("Settings")
    settings_window.resizable(0, 0)

    configlabel = tk.Label(settings_window, text="Settings", font=('Arial', 12))
    configlabel.grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.EW)

    # android dir entry
    android_dir_label = tk.Label(settings_window, text="Android Directory")
    android_dir_label.grid(row=1, column=0, padx=10, pady=10)
    android_dir_entry = tk.Entry(settings_window)
    android_dir_entry.grid(row=1, column=1, padx=10, pady=10)
    android_dir_entry.insert(0, transfersave.ANDROID_DIR)

    # pc dir entry
    pc_dir_label = tk.Label(settings_window, text="Computer Directory")
    pc_dir_label.grid(row=2, column=0, padx=10, pady=10)
    pc_dir_entry = tk.Entry(settings_window)
    pc_dir_entry.grid(row=2, column=1, padx=10, pady=10)
    pc_dir_entry.insert(0, transfersave.PC_DIR)

    # toggle backups
    backups_setting = tk.BooleanVar(value=transfersave.save_backups)
    backups_checkbox = tk.Checkbutton(settings_window, text='Make backups',variable=backups_setting, onvalue=True, offvalue=False)
    backups_checkbox.grid(row=4, column=0, padx=10, pady=10)

    def save_settings():
        # save directories
        transfersave.set_dir('android_dir', android_dir_entry.get())
        transfersave.set_dir('pc_dir', pc_dir_entry.get())

        # save backups setting
        backups_setting_value = backups_setting.get()
        transfersave.set_backups_setting(backups_setting_value)

        change_msg("saved settings!")

    save_button = tk.Button(settings_window, text='Save Settings', command=save_settings)
    save_button.grid(row=4, column=1, padx=10, pady=10)

    kill_button = tk.Button(settings_window, text='Kill ADB Server', command=kill_adb_server)
    kill_button.grid(row=5, column=1, padx=10, pady=10)

    start_button = tk.Button(settings_window, text='Start ADB Server', command=start_adb_server)
    start_button.grid(row=5, column=0, padx=10, pady=10)

def kill_adb_server():
    kill_server_command = [str(transfersave.path_adb), "kill-server"]
    subprocess.run(kill_server_command, capture_output=True, text=True, check=False)
    change_msg("adb server is kil")

def start_adb_server():
    start_server_command = [str(transfersave.path_adb), "start-server"]
    subprocess.run(start_server_command, capture_output=True, text=True, check=False)
    change_msg("adb server started")

def create_ui():
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

def main():
    root.title("GD Data Transfer")
    root.geometry("500x300")
    root.resizable(0, 0)

    create_ui()

    root.mainloop()

if __name__ == "__main__":
    main()
