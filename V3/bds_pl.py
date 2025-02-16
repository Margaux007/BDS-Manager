import csv
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
import re

LOG_FILE = "server_log.txt"
COMMAND_FILE = "server_commands.txt"
ITEMS_CSV = "GiveItemList.csv"

# Enchantments categorized by item type (removed Curse of Vanishing)
ENCHANTMENTS = {
    "all": {"mending": 1, "unbreaking": 3},
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

    if command == "teleport":
        teleport_window = tk.Toplevel(root)
        teleport_window.title("Teleport Command")

        destination_var = tk.StringVar()
        destination_label = tk.Label(teleport_window, text="Enter destination (coordinates or player):")
        destination_label.pack(pady=5)
        destination_entry = tk.Entry(teleport_window, textvariable=destination_var)
        destination_entry.pack(pady=5)

        check_blocks_var = tk.BooleanVar(value=False)
        check_blocks_check = tk.Checkbutton(teleport_window, text="Check for blocks", variable=check_blocks_var)
        check_blocks_check.pack(pady=5)

        def confirm_teleport():
            destination = destination_var.get()
            check_for_blocks = check_blocks_var.get()

            if not destination:
                messagebox.showwarning("Warning", "No destination provided!")
                return

            check_blocks_str = "true" if check_for_blocks else "false"
            for player_name in selected_players:
                send_command(f"teleport {player_name} {destination} {check_blocks_str}")
            
            messagebox.showinfo("Command Sent", f"Teleported {', '.join(selected_players)} to {destination}.")
            teleport_window.destroy()

        confirm_button = tk.Button(teleport_window, text="Teleport", command=confirm_teleport)
        confirm_button.pack(pady=5)

    elif command == "gamemode":
        gamemode_window = tk.Toplevel(root)
        gamemode_window.title("Select Gamemode")

        def select_gamemode(mode):
            if mode == "Adventure":
                gamemode_code = 0
            elif mode == "Creative":
                gamemode_code = 1
            elif mode == "Survival":
                gamemode_code = 2
            else:
                gamemode_code = 0  # Default to Adventure mode if unknown mode

            for player_name in selected_players:
                send_command(f"gamemode {gamemode_code} {player_name}")
            messagebox.showinfo("Command Sent", f"Set {', '.join(selected_players)} to {mode} mode (gamemode {gamemode_code}).")
            gamemode_window.destroy()

        # Create buttons for each gamemode
        gamemodes = ["Survival", "Creative", "Adventure"]
        for mode in gamemodes:
            btn = tk.Button(gamemode_window, text=mode, command=lambda m=mode: select_gamemode(m))
            btn.pack(pady=5)

    elif command == "effect":
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

    elif command == "enchant":
        enchant_item(selected_players)
    
    elif command == "give":
        give_item(selected_players)
    
    else:
        for player_name in selected_players:
            send_command(f"{command} {player_name}")
        messagebox.showinfo("Command Sent", f"Executed {command} on {', '.join(selected_players)}")

def enchant_item(selected_players):
    enchant_window = tk.Toplevel(root)
    enchant_window.title("Select Item Type")

    def select_item(item_type):
        enchant_window.destroy()
        show_enchants(selected_players, item_type)
    
    # Display buttons for item types
    for item_type in ITEM_CATEGORIES:
        btn = tk.Button(enchant_window, text=item_type.capitalize(), command=lambda it=item_type: select_item(it))
        btn.pack(pady=5)

def show_enchants(selected_players, selected_item):
    enchant_window = tk.Toplevel(root)
    enchant_window.title(f"Enchant {selected_item.capitalize()}")
    
    selected_enchants = {}
    
    def apply_enchants():
        for enchant, level_var in selected_enchants.items():
            level = level_var.get()
            if level > 0:  # Only apply if a level is selected
                for player_name in selected_players:
                    send_command(f"enchant {player_name} {enchant.lower().replace(' ', '_')} {level}")
        enchant_window.destroy()
    
    # Display applicable enchantments based on the selected item
    applicable_enchants = ENCHANTMENTS.get(selected_item.lower(), {})
    
    for enchant, max_level in applicable_enchants.items():
        frame = tk.Frame(enchant_window)
        frame.pack(pady=5)
        
        label = tk.Label(frame, text=enchant)
        label.pack(side="left", padx=10)
        
        level_var = tk.IntVar(value=0)
        selected_enchants[enchant] = level_var
        
        level_spinbox = tk.Spinbox(frame, from_=0, to=max_level, textvariable=level_var, width=5)
        level_spinbox.pack(side="left")
    
    apply_button = tk.Button(enchant_window, text="Apply Enchantments", command=apply_enchants)
    apply_button.pack(pady=10)

# Function to read the CSV and filter columns 2 and 3 (index 1 and 2)
def load_item_list():
    if not os.path.exists(ITEMS_CSV):
        messagebox.showerror("Error", f"{ITEMS_CSV} not found!")
        return []
    
    item_list = []
    with open(ITEMS_CSV, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            # Use column 3 for the command
            if len(row) > 2:
                item_name = row[1]  # Column 2 (displayed to user)
                command_item = row[2]  # Column 3 (used in command)
                item_list.append(f"{item_name} - {command_item}")
    return item_list

# Function for the give command with dropdown selection and quantity
def give_item(selected_players):
    item_list = load_item_list()
    if not item_list:
        messagebox.showerror("Error", "Item list is empty or unavailable.")
        return

    give_window = tk.Toplevel(root)
    give_window.title("Select Item to Give")

    # Create a combobox for item selection (with search functionality)
    item_var = tk.StringVar()
    item_dropdown = ttk.Combobox(give_window, textvariable=item_var, values=item_list)
    item_dropdown.pack(pady=10)
    item_dropdown.focus_set()

    # Make the dropdown searchable
    def on_type(event):
        value = event.widget.get().lower()
        filtered_items = [item for item in item_list if value in item.lower()]
        item_dropdown["values"] = filtered_items

    item_dropdown.bind("<KeyRelease>", on_type)

    # Add entry for quantity
    quantity_var = tk.IntVar(value=1)
    quantity_label = tk.Label(give_window, text="Quantity:")
    quantity_label.pack(pady=5)
    quantity_entry = tk.Entry(give_window, textvariable=quantity_var)
    quantity_entry.pack(pady=5)

    def confirm_give():
        selected_item = item_var.get().split(" - ")[1]  # Use column 3 (command format)
        quantity = quantity_var.get()  # Get the quantity

        if not selected_item:
            messagebox.showwarning("Warning", "No item selected!")
            return

        for player_name in selected_players:
            send_command(f"give {player_name} {selected_item} {quantity}")
        messagebox.showinfo("Command Sent", f"Gave {quantity}x {selected_item} to {', '.join(selected_players)}")
        give_window.destroy()

    give_button = tk.Button(give_window, text="Give Item", command=confirm_give)
    give_button.pack(pady=10)

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
