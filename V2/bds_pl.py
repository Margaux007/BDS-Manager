import tkinter as tk
import os
import sys
import re

def fetch_player_list():
    log_file = "server_log.txt"
    if not os.path.exists(log_file):
        return []
    
    with open(log_file, "r") as file:
        log_content = file.readlines()
    
    players = set()
    for line in log_content:
        connect_match = re.search(r"Player connected: ([^,]+),", line)
        disconnect_match = re.search(r"Player disconnected: ([^,]+)", line)
        
        if connect_match:
            players.add(connect_match.group(1))
        elif disconnect_match and disconnect_match.group(1) in players:
            players.remove(disconnect_match.group(1))
    
    return list(players)

def refresh_players():
    player_listbox.delete(0, tk.END)
    players = fetch_player_list()
    for player in players:
        player_listbox.insert(tk.END, player)

# GUI Setup
root = tk.Tk()
root.title("Player List")
root.geometry("400x300")

player_listbox = tk.Listbox(root, height=10, width=50)
player_listbox.pack(pady=5)

refresh_button = tk.Button(root, text="Refresh Players", command=refresh_players)
refresh_button.pack(pady=5)

refresh_players()
root.mainloop()
