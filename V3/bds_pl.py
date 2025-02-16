import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
import re

LOG_FILE = "server_log.txt"
COMMAND_FILE = "server_commands.txt"
ITEMS_CSV = "GiveItemList.csv"

# Enchantments categorized by item type
ENCHANTMENTS = {
    "all": {"mending": 1, "unbreaking": 3, "vanishing_curse": 1},
    "armor": {"aqua_affinity": 1, "blast_protection": 4, "fire_protection": 4, "protection": 4, "thorns": 3},
    "swords": {"bane_of_arthropods": 5, "fire_aspect": 2, "knockback": 2, "sharpness": 5, "smite": 5},
    "bows": {"flame": 1, "infinity": 1, "power": 5, "punch": 2},
    "tridents": {"channeling": 1, "loyalty": 3, "riptide": 3},
    "tools": {"efficiency": 5, "fortune": 3, "silk_touch": 1}
}

EFFECTS = ["speed", "slowness", "haste", "mining_fatigue", "strength", "instant_health", "instant_damage", "jump_boost", "regeneration", "resistance", "fire_resistance", "water_breathing", "invisibility", "blindness", "night_vision", "hunger", "weakness", "poison", "wither", "health_boost", "absorption", "saturation"]

# Item categories
ITEM_CATEGORIES = list(ENCHANTMENTS.keys())

def fetch_player_list():
    if not os.path.exists(LOG_FILE):
        return []
    
    with open(LOG_FILE, "r") as file:
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
    for widget in player_listbox_frame.winfo_children():
        widget.destroy()
    players = fetch_player_list()
    for player in players:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(player_listbox_frame, text=player, variable=var)
        chk.var = var
        chk.pack(anchor='w')
        player_checkboxes[player] = var

def send_command(command):
    try:
        with open(COMMAND_FILE, "a") as cmd_file:
            cmd_file.write(command + "\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send command: {e}")

def execute_command():
    selected_players = [player for player, var in player_checkboxes.items() if var.get()]
    if not selected_players:
        messagebox.showwarning("Warning", "No player selected!")
        return
    
    command = command_var.get()
    if command == "effect":
        effect_window = tk.Toplevel(root)
        effect_window.title("Select Effect")
        
        def select_effect(effect):
            if effect == "clear":
                for player_name in selected_players:
                    send_command(f"effect {player_name} clear")
                messagebox.showinfo("Command Sent", f"Cleared all effects on {', '.join(selected_players)}")
                effect_window.destroy()
                return
            
            duration = simpledialog.askinteger("Duration", "Enter duration (seconds):", minvalue=1, maxvalue=1000)
            amplifier = simpledialog.askinteger("Amplifier", "Enter amplifier level (0-255):", minvalue=0, maxvalue=255)
            if duration is not None and amplifier is not None:
                for player_name in selected_players:
                    send_command(f"effect {player_name} {effect} {duration} {amplifier}")
                messagebox.showinfo("Command Sent", f"Executed effect {effect} {duration} {amplifier} on {', '.join(selected_players)}")
            effect_window.destroy()
        
        for effect in EFFECTS + ["clear"]:
            btn = tk.Button(effect_window, text=effect, command=lambda e=effect: select_effect(e))
            btn.pack()
    else:
        for player_name in selected_players:
            send_command(f"{command} {player_name}")
        messagebox.showinfo("Command Sent", f"Executed {command} on {', '.join(selected_players)}")

# GUI Setup
root = tk.Tk()
root.title("Player List & Commands")
root.geometry("400x500")

player_checkboxes = {}
player_listbox_frame = tk.Frame(root)
player_listbox_frame.pack(pady=5)

refresh_button = tk.Button(root, text="Refresh Players", command=refresh_players)
refresh_button.pack(pady=5)

# Command Selection
command_var = tk.StringVar()
command_dropdown = ttk.Combobox(root, textvariable=command_var, state='readonly')
command_dropdown["values"] = ["op", "deop", "kick", "ban", "teleport", "give", "kill", "effect", "gamemode", "clear", "difficulty", "summon", "enchant"]
command_dropdown.pack(pady=5)
command_dropdown.current(0)

execute_button = tk.Button(root, text="Execute Command", command=execute_command)
execute_button.pack(pady=5)

refresh_players()
root.mainloop()
