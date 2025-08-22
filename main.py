#!/usr/bin/env python
# coding: utf-8

# In[1]:


# main.py

import tkinter as tk
from tkinter import messagebox
from email_processor import process_emails
import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(client_id, tenant_id,openai_key):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"client_id": client_id, "tenant_id": tenant_id,"openai_key": openai_key}, f)

def run_processing():
    client_id = entry_client_id.get().strip()
    tenant_id = entry_tenant_id.get().strip()
    openai_key = entry_openai_key.get().strip()
    category = entry_category.get().strip()

    if not category:
        messagebox.showerror("Missing Info", "Please enter the project/category name.")
        return

    if not client_id or not tenant_id or not openai_key:
        messagebox.showerror("Missing Info", "Client ID, Tenant ID, and OpenAI API Key are required.")
        return
    
    btn_process.config(state="disabled", text="Processing...")
    app.update_idletasks()
    
    try:
        save_config(client_id, tenant_id, openai_key)
        result = process_emails(client_id, tenant_id, openai_key, category)
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, result)
        messagebox.showinfo("Success", "Email processing completed.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        btn_process.config(state="normal", text="Process Emails")


# GUI Setup
app = tk.Tk()
app.title("Email Processor with OpenAI")
app.geometry("500x400")



tk.Label(app, text="Client ID").pack()
Client_ID_key_var = tk.StringVar()
#entry_client_id = tk.Entry(app, width=60)
entry_client_id = tk.Entry(app, textvariable=Client_ID_key_var, show="*", width=60)
entry_client_id.pack()

def toggle_key_visibility2():
    if entry_client_id.cget('show') == '*':
        entry_client_id.config(show='')
    else:
        entry_client_id.config(show='*')

show_key_check = tk.Checkbutton(app, text="Show Client ID", command=toggle_key_visibility2)
show_key_check.pack()

tk.Label(app, text="Tenant ID").pack()
Tenant_ID_key_var = tk.StringVar()
#entry_tenant_id = tk.Entry(app, width=60)
entry_tenant_id = tk.Entry(app, textvariable=Tenant_ID_key_var, show="*", width=60)
entry_tenant_id.pack()

def toggle_key_visibility1():
    if entry_tenant_id.cget('show') == '*':
        entry_tenant_id.config(show='')
    else:
        entry_tenant_id.config(show='*')

show_key_check = tk.Checkbutton(app, text="Show Tenant ID", command=toggle_key_visibility1)
show_key_check.pack()

tk.Label(app, text="OpenAI API Key").pack()
openai_key_var = tk.StringVar()
entry_openai_key = tk.Entry(app, textvariable=openai_key_var, show="*", width=60)
entry_openai_key.pack()

def toggle_key_visibility():
    if entry_openai_key.cget('show') == '*':
        entry_openai_key.config(show='')
    else:
        entry_openai_key.config(show='*')

show_key_check = tk.Checkbutton(app, text="Show API Key", command=toggle_key_visibility)
show_key_check.pack()

tk.Label(app, text="Project / Category Name").pack()
entry_category = tk.Entry(app, width=60)
entry_category.pack()


btn_process = tk.Button(app, text="Process Emails", command=run_processing)
btn_process.pack(pady=10)

text_output = tk.Text(app, height=10, wrap="word")
text_output.pack(expand=True, fill="both")

# Load saved config
config = load_config()
entry_client_id.insert(0, config.get("client_id", ""))
entry_tenant_id.insert(0, config.get("tenant_id", ""))
entry_openai_key.insert(0, config.get("openai_key", ""))

app.mainloop()


# In[ ]:




