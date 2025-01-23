"""
this is (supposed to be) only the gui, most other stuff
is in transfersave.py

uses python 3.11
"""

import tkinter as tk
import subprocess
import transfersave

root = tk.Tk()

origin = "nothingselected"

def change_msg(new_message):
    """change message in window and print same message"""
    print(new_message)
    label.config(text = new_message)

# button functions

def phone_button_click():
    """phone to computer click"""
    global origin
    if origin == "phone": # extra useless code yay
        change_msg("destination was already computer, are you stupid?")
    else:
        origin = "phone"
        change_msg("changed destination to computer")

def pc_button_click():
    """computer to phone click"""
    global origin
    if origin == "computer":
        change_msg("destination was already phone, are you stupid?")
    else:
        origin = "computer"
        change_msg("changed destination to phone")

def transfer_button_click():
    """transfer button click"""
    if origin == "nothingselected":
        change_msg("you didnt select anything")
    else:
        transfersave.transfersaves(origin)
        if transfersave.exitstatus == 0:
            change_msg("save files transferred succesfully!")
        else:
            change_msg(f"couldnt transfer files\nADB return code: {transfersave.exitstatus}")

# settings

def open_settings():
    settings_window = tk.Toplevel()
    settings_window.title("Settings")
    settings_window.geometry("300x250")

    configlabel = tk.Label(settings_window, text="Settings", font=('Arial', 12))
    configlabel.pack(padx=40, pady=20)

    # android dir entry
    android_dir_entry = tk.Entry(settings_window)
    android_dir_entry.pack()
    android_dir_entry.insert(0, transfersave.ANDROID_DIR)

    # pc dir entry
    pc_dir_entry = tk.Entry(settings_window)
    pc_dir_entry.pack()
    pc_dir_entry.insert(0, transfersave.PC_DIR)

    def save_settings():
        transfersave.set_dir('android_dir', android_dir_entry.get())
        transfersave.set_dir('pc_dir', pc_dir_entry.get())
        print(transfersave.ANDROID_DIR)
        change_msg("saved settings!")

    save_button = tk.Button(settings_window, text='Save Settings', command=save_settings)
    save_button.pack(side=tk.BOTTOM, pady=10)

    kill_button = tk.Button(settings_window, text='Kill ADB Server', command=kill_adb_server)
    kill_button.pack(side=tk.BOTTOM)

    start_button = tk.Button(settings_window, text='Start ADB Server', command=start_adb_server)
    start_button.pack(side=tk.BOTTOM)

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
