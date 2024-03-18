#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import *
import tkinter.font as tkfont
import os, subprocess
from subprocess import STDOUT,PIPE
import configparser
import os
import configparser
import time
from getToken import *
from pullProjects import *
import pickle5 as pickle
from tkinter import Toplevel, Label, Entry, Button, StringVar, ttk
import time
from tkinter import font as tkFont

current_file_path = None
CONFIG_FILE = "config.ini"
loginInfo = "loginInfo.ini"

def update_last_opened(file_path):
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.add_section('Settings')
        config.set('Settings', 'last_opened', '')
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
    config.read(CONFIG_FILE)
    if file_path is not None:
        config.set('Settings', 'last_opened', file_path)
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

def open_file(filepath):
    global current_file_path
    update_last_opened(filepath)
    txt_edit.delete(1.0, tk.END)
    with open(filepath, "r") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)
    console.insert(tk.END, f"Opened file: {filepath}\n")
    window.title(f"Text Editor Application - {filepath}")

def save_file():
    global current_file_path
    if not current_file_path:
        current_file_path = get_last_opened_file()
    if current_file_path and os.path.isfile(current_file_path):
        with open(current_file_path, "w") as output_file:
            text = txt_edit.get(1.0, tk.END)
            output_file.write(text)
        console.insert(tk.END, f"Saved changes to: {current_file_path}\n")
        window.title(f"Text Editor Application - {current_file_path}")

def my_view():
    global trv
    trv = ttk.Treeview(window, selectmode='browse', show='tree')
    trv.grid(row=0, column=0, rowspan=1, padx=10, pady=10, sticky="nsew")
    trv.bind('<ButtonRelease-1>', open_selected_file)

def my_insert(my_dir, path="", parent=""):
    global trv
    if not path:
        path = my_dir
    items = sorted(os.listdir(path))
    for item in items:
        item_path = os.path.join(path, item)
        item_id = trv.insert(parent, 'end', text=item, values=(item_path,), open=False)
        if os.path.isdir(item_path):
            my_insert(my_dir, item_path, parent=item_id)

def open_selected_file(event):
    global trv
    selected_item = trv.selection()
    if selected_item:
        item_path = trv.item(selected_item, 'values')[0]
        if os.path.isdir(item_path):
            if trv.item(selected_item, 'open'):
                trv.item(selected_item, open=False)
            else:
                trv.item(selected_item, open=True)
        else:
            open_file_in_editor(item_path)

def open_file_in_editor(file_path):
    save_file()
    global current_file_path
    current_file_path = file_path
    open_file(current_file_path)
    txt_edit.delete(1.0, tk.END)
    if os.path.exists(file_path):
        with open(file_path, "r") as input_file:
            text = input_file.read()
            txt_edit.insert(tk.END, text)
        console.insert(tk.END, f"Opened file: {file_path}\n")
        window.title(f"Text Editor Application - {file_path}")
    else:
        txt_edit.insert(tk.END, f"File not found: {file_path}")
        console.insert(tk.END, f"Error: File not found - {file_path}\n")
        window.title("Text Editor Application")

def get_last_opened_file():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
    return config.get("Settings", "last_opened", fallback="")

def get_username():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "loginInfo.ini"))
    return config.get("LoginInfo", "username")

def update_console_width(event):
    new_width = paned_window.sash_coord(0)[0]
    console.config(width=new_width)

def update_console_text(text):
    """Update the text in the console."""
    console.config(state='normal') 
    console.insert(tk.END, text)
    console.see(tk.END)   
    console.config(state='disabled')  

def compile_java(java_file):
    subprocess.check_call(['javac', java_file])

def execute_java(java_file, stdin):
    java_class,ext = os.path.splitext(java_file)
    cmd = ['java', java_class]
    proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    stdout,stderr = proc.communicate(stdin)
    return stdout

def run_code():
    save_file()
    update_console_text(execute_java(current_file_path+".java", ""))
    print(current_file_path)

def submit_confirmation_window():
    window = tk.Tk()
    window.title("Submit Confirmation")
    def submit_action():
        parent = os.path.dirname(current_file_path)
        assignments_dict = load_dict_from_file("assignmentsDict.pkl")
        assignment = assignments_dict[parent]
        submitAssignment(current_file_path, assignment)
        window.destroy()  

    def cancel_action():
        window.destroy()  

    confirmation_label = tk.Label(window, text='Are you sure you want to submit "' + os.path.basename(current_file_path) + '"?')
    confirmation_label.pack(pady=10)

    submit_button = tk.Button(window, text="Submit", command=submit_action)
    submit_button.pack(side=tk.LEFT, padx=10)

    cancel_button = tk.Button(window, text="Cancel", command=cancel_action)
    cancel_button.pack(side=tk.RIGHT, padx=10)

    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')

def on_press(event):
    run_code()


def login_popup():
    top = Toplevel(window)
    top.geometry("480x150") 
    top.title("Login")

    username_var = StringVar()
    password_var = StringVar()

    Label(top, text="Canvas username:").place(x=80, y=20)
    username_entry = Entry(top, textvariable=username_var)
    username_entry.place(x=220, y=20)

    Label(top, text="Canvas password:").place(x=80, y=50)
    password_entry = Entry(top, textvariable=password_var, show='*')  
    password_entry.place(x=220, y=50)

    status_label = Label(top, text="")
    status_label.place(x=80, y=80)

    submit_button = Button(top, text="Submit", command=lambda: submit_login(top, username_var.get(), password_var.get(), status_label))
    submit_button.place(x=200, y=110)

def submit_login(top, username, password, status_label):
    progress_bar = ttk.Progressbar(top, mode='indeterminate')
    progress_bar.place(x=200, y=80)
    progress_bar.start()
    top.update() 
    finish_login(top, status_label, progress_bar, username, password)
    progress_bar.stop()
    progress_bar.destroy()


def finish_login(top, status_label, progress_bar, username, password):
    top.update()
    successfulLogin = False
    userToken = ""
    try:
        userToken = getToken(username, password)
        successfulLogin = True
    except:
        pass
    if successfulLogin:
        config = configparser.ConfigParser()
        config.add_section('LoginInfo')
        config.set('LoginInfo', 'username', username)
        config.set('LoginInfo', 'password', password)
        config.set('LoginInfo', 'token', userToken)
        with open(loginInfo, 'w') as configfile:
            config.write(configfile)
        status_label.config(text="Token generated")
        loginText.config(text="Signed in as: "+username)
        loginButton.config(text="Log out", command=logOut)


        time.sleep(1)
        top.destroy()
    else:
        status_label.config(text="Invalid username or password", fg='#a00')

def logOut():
    loginText.config(text="You are not logged in")
    loginButton.config(text="Login", command=login_popup)
    config=configparser.ConfigParser()
    config.read("loginInfo.ini")
    config["LoginInfo"] = {}
    with open(loginInfo, 'w') as configfile:
        print(configfile)
        config.write(configfile)

def save_dict_to_file(data_dict, filename):
    with open(filename, 'wb') as file:
        pickle.dump(data_dict, file)

def load_dict_from_file(filename):
    try:
        with open(filename, 'rb') as file:
            loaded_dict = pickle.load(file)
        return loaded_dict
    except FileNotFoundError:
        return {}

def pull():
    config = configparser.ConfigParser()
    config.read("loginInfo.ini")
    token = config.get("LoginInfo", "token")
    assignmentsDict = pullAssignments(token, initial_dir)
    save_dict_to_file(assignmentsDict, "assignmentsDict.pkl")
    my_view()
    my_insert(initial_dir)


def get_indentation_width():
    font_object = tkFont.Font(font=txt_edit['font'])
    indent_char_width = font_object.measure(' ')
    if indent_char_width < 2:
        return indent_char_width
    else:
        return font_object.measure('    ')

def on_return(event):
    cursor_pos = txt_edit.index(tk.INSERT)
    line, char_index = map(int, cursor_pos.split('.'))
    current_line_text = txt_edit.get(f"{line}.0", f"{line}.end")
    indentation = len(current_line_text) - len(current_line_text.lstrip())
    indent_width = get_indentation_width()
    txt_edit.insert(tk.INSERT, "\n" + " " * indentation)
    return "break"


window = tk.Tk()
window.title("Text Editor with File Tree")

try:
    os.mkdir("./csaLabs")
except:
    pass
try:
    open("config.ini", "x")
except:
    pass
try:
    open("loginInfo.ini", "x")
except:
    pass

window.rowconfigure(0, weight=100000)
window.rowconfigure(1, minsize = 50, weight=10)  
window.rowconfigure(2, minsize = 20, weight=1)  
window.columnconfigure(0, weight=1)
window.columnconfigure(1, minsize=900, weight=2)

my_view()

btn_frame = tk.Frame(window)
btn_frame.grid(row=1, column=0, sticky="nsew", pady=4, padx=10)

btn_save = tk.Button(btn_frame, text="Save", command=save_file)
btn_save.grid(row=0, column=0, sticky="e", padx=10, pady=5)
btn_save.place(relwidth=1/4, relx=0, relheight=1)

btn_submit = tk.Button(btn_frame, text="Submit", command=submit_confirmation_window)  
btn_submit.grid(row=0, column=1, sticky="e", padx=5, pady=5)
btn_submit.place(relwidth=1/4, relx=1/4, relheight=1)

btn_run = tk.Button(btn_frame, text="Run", command=run_code)
btn_run.grid(row=0, column=2, sticky="e", padx=10, pady=5)
btn_run.place(relwidth=1/4, relx=2/4, relheight=1)

btn_pull = tk.Button(btn_frame, text="Pull", command=pull)
btn_pull.grid(row=0, column=3, sticky="e", padx=10, pady=5)
btn_pull.place(relwidth=1/4, relx=3/4, relheight=1)

login_frame = tk.Frame(window)
login_frame.grid(row=2, column=0, sticky="nsew", pady=2, padx=10)
login_frame.columnconfigure(1, weight=1)
custom_font = tkfont.Font(size=10)

loginText = tk.Label(login_frame, text="You are not logged in", font=custom_font)
loginText.grid(row=0, column=0)
loginButton = tk.Button(login_frame, text="Login", command=login_popup)
loginButton.grid(row=0, column=1, sticky="e")
try:
    loginText.config(text=get_username())
    loginButton.config(text="Log out", command=logOut)
except:
    pass

paned_window = ttk.PanedWindow(window, orient=tk.VERTICAL)
paned_window.grid(row=0, column=1, sticky="nsew", rowspan=3)

txt_edit = tk.Text(paned_window, wrap="word", undo=True)
txt_edit.config(tabs=tkfont.Font(font=txt_edit['font']).measure('    '))
txt_edit.pack(expand=True, fill="both")
txt_edit.bind("<Return>", on_return)

paned_window.add(txt_edit)

console_frame = tk.Frame(paned_window)
console_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10)) 
console = tk.Text(console_frame, state='disabled', wrap='word', height=4)
console.pack(fill="both", expand=True)

paned_window.add(console_frame)

initial_dir = os.path.abspath("csaLabs")
print(initial_dir)
my_insert(initial_dir)


last_opened_file = get_last_opened_file()
if last_opened_file and os.path.exists(last_opened_file):
    open_file(last_opened_file)

window.bind('<F5>', on_press)
window.mainloop()

