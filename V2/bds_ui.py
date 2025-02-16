import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import threading
import time
import os

LOG_FILE = "server_log.txt"

class BedrockServerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bedrock Server Manager")
        self.root.geometry("700x600")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)
        
        self.server_process = None
        self.playit_process = None
        
        # Start Playit.gg button
        self.start_playit_button = tk.Button(root, text="Start Playit.gg", command=self.start_playit)
        self.start_playit_button.grid(row=0, column=0, columnspan=2, pady=5, sticky='ew')
        
        # Start BDS button
        self.start_bds_button = tk.Button(root, text="Start BDS", command=self.start_bds)
        self.start_bds_button.grid(row=1, column=0, columnspan=2, pady=5, sticky='ew')
        
        # Stop button
        self.stop_button = tk.Button(root, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')
        
        # Console log
        self.log = scrolledtext.ScrolledText(root, width=85, height=20, state=tk.DISABLED)
        self.log.grid(row=3, column=0, columnspan=2, pady=5, sticky='nsew')
        
        # Command input
        self.command_entry = tk.Entry(root, width=60)
        self.command_entry.grid(row=4, column=0, pady=5, sticky='ew')
        
        self.send_button = tk.Button(root, text="Send Command", command=self.send_command)
        self.send_button.grid(row=4, column=1, pady=5, sticky='ew')
        
        # Open Player List Button
        self.player_list_button = tk.Button(root, text="Open Player List", command=self.open_player_list)
        self.player_list_button.grid(row=5, column=0, columnspan=2, pady=5, sticky='ew')
        
    def open_player_list(self):
        try:
            import sys
            subprocess.Popen([sys.executable, "bds_pl.py"], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open player list: {e}")
        
    def start_playit(self):
        try:
            playit_path = os.path.join(r"D:\\BedrockServer", "playit.exe")
            playit_shortcut = os.path.join(r"D:\\BedrockServer", "playit.exe.lnk")
            
            if os.path.exists(playit_shortcut):
                self.playit_process = subprocess.Popen(f'start "" "{playit_shortcut}"', shell=True)
            elif os.path.exists(playit_path):
                self.playit_process = subprocess.Popen([playit_path], shell=True)
            else:
                raise FileNotFoundError("Playit.exe or its shortcut was not found in the server directory.")
            self.start_playit_button.config(state=tk.DISABLED)
            messagebox.showinfo("Success", "Playit.gg started successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start Playit.gg: {e}")
    
    def start_bds(self):
        try:
            self.server_process = subprocess.Popen([r"D:\\BedrockServer\\bedrock_server.exe"], 
                                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
            self.start_bds_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            threading.Thread(target=self.read_output, daemon=True).start()
            messagebox.showinfo("Success", "BDS started successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start BDS: {e}")
    
    def stop_server(self):
        if self.server_process:
            self.server_process.stdin.write("stop\n")
            self.server_process.stdin.flush()
            self.server_process.wait()
            self.server_process = None
        
        self.start_bds_button.config(state=tk.NORMAL)
        self.start_playit_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        messagebox.showinfo("Server Stopped", "The server has been stopped.")
    
    def read_output(self):
        with open(LOG_FILE, "w") as log_file:
            while self.server_process:
                line = self.server_process.stdout.readline()
                if not line:
                    break
                log_file.write(line)
                log_file.flush()
                self.log.config(state=tk.NORMAL)
                self.log.insert(tk.END, line)
                self.log.config(state=tk.DISABLED)
                self.log.yview(tk.END)
    
    def send_command(self, command=None):
        if not command:
            command = self.command_entry.get()
        if self.server_process and command:
            self.server_process.stdin.write(command + "\n")
            self.server_process.stdin.flush()
            self.command_entry.delete(0, tk.END)
    
if __name__ == "__main__":
    root = tk.Tk()
    app = BedrockServerUI(root)
    root.mainloop()
