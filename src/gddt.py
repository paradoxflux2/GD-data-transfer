"""
this is (supposed to be) only the gui, most other stuff
is in transfersave.py

uses python 3.11
"""

import tkinter as tk
import subprocess
import transfersave

root = tk.Tk()

# create window
root.title("GD Data Transfer")
root.geometry("500x300")

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

def open_settings():
    settings_window = tk.Toplevel()
    settings_window.title("Settings")
    settings_window.config(width=300, height=200)

    configlabel = tk.Label(settings_window, text="under construction", font=('Arial', 12))
    configlabel.pack(padx=20, pady=20)

    kill_button = tk.Button(settings_window, text='Kill ADB Server', command=kill_adb_server)
    kill_button.pack()

def kill_adb_server():
    kill_server_command = [str(transfersave.path_adb), "kill-server"]
    subprocess.run(kill_server_command, capture_output=True, text=True, check=False)
    print("adb server is kil")

# create a menubar
menubar = tk.Menu(root)
root.config(menu=menubar)

file_menu = tk.Menu(menubar)

# create file menu
file_menu.add_command(label='Settings', command=open_settings)
file_menu.add_command(label='Exit', command=root.destroy)

# add the File menu to the menubar
menubar.add_cascade(label="File", menu=file_menu)

# title
title = tk.Label(root, text="GD Data Transfer", font=('Arial', 18))

# transfer button
transfer_button = tk.Button(root, text='Transfer', command=transfer_button_click)

# phone to computer button
phone_button = tk.Button(root, text='Phone to computer', command=phone_button_click)

# computer to phone button
pc_button = tk.Button(root, text='Computer to phone', command=pc_button_click)

# message
label = tk.Label(root, text="please select a destination first", font=('Arial', 12))

#settings_button.pack(anchor="nw")
title.pack(padx=20, pady=20)
phone_button.pack() # phone to pc
pc_button.pack() # pc to phone
label.pack(side=tk.BOTTOM, padx=20, pady=20)
transfer_button.pack(side=tk.BOTTOM)

root.mainloop()
