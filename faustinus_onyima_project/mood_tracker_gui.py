import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime

# File to store mood data
DATA_FILE = "mood_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_data(mood):
    data = load_data()
    entry = {"date": datetime.now().strftime("%Y-%m-%d"), "mood": mood}
    data.append(entry)
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)
    messagebox.showinfo("Success", f"Mood '{mood}' saved!")

def view_moods():
    data = load_data()
    mood_list.delete(0, tk.END)
    for entry in data[-10:]:  # Show last 10 entries
        mood_list.insert(tk.END, f"{entry['date']} - {entry['mood']}")

def export_data():
    data = load_data()
    with open("mood_export.csv", "w") as file:
        file.write("Date,Mood\n")
        for entry in data:
            file.write(f"{entry['date']},{entry['mood']}\n")
    messagebox.showinfo("Exported", "Mood data exported to mood_export.csv!")

# GUI setup
root = tk.Tk()
root.title("Mood Tracker")
root.geometry("400x500")

# Title
tk.Label(root, text="Mood Tracker", font=("Arial", 16, "bold")).pack(pady=10)

# Mood Buttons
moods = ["😀", "😢", "😡", "🤩"]
for mood in moods:
    tk.Button(root, text=mood, font=("Arial", 14), width=5, command=lambda m=mood: save_data(m)).pack(pady=5)

# View Moods Button
tk.Button(root, text="View Mood History", font=("Arial", 12), command=view_moods).pack(pady=10)

# Mood Listbox
mood_list = tk.Listbox(root, font=("Arial", 12), width=30, height=10)
mood_list.pack()

# Export Data Button
tk.Button(root, text="Export to CSV", font=("Arial", 12), command=export_data).pack(pady=10)

# Run the application
root.mainloop()
