import time
import math
import threading
import json
import os
import tkinter as tk
from tkinter import ttk
from pynput import mouse, keyboard

# --- CONFIGURATION FILE ---
CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from config.json, create default if missing."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config
        except json.JSONDecodeError:
            print(f"Error reading {CONFIG_FILE}. Using defaults.")
            return get_default_config()
    else:
        print(f"{CONFIG_FILE} not found. Creating with defaults...")
        config = get_default_config()
        save_config(config)
        return config

def get_default_config():
    """Return default configuration."""
    return {
        "radius": 340,
        "steps": 2000,
        "draw_speed": 0.002,
        "start_key": "alt_l",
        "exit_key": "esc"
    }

def save_config(config):
    """Save configuration to config.json."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get_key_from_string(key_str):
    """Convert string key name to pynput key object."""
    key_str = key_str.lower().strip()
    key_map = {
        "alt_l": keyboard.Key.alt_l,
        "alt_r": keyboard.Key.alt_r,
        "ctrl_l": keyboard.Key.ctrl_l,
        "ctrl_r": keyboard.Key.ctrl_r,
        "shift_l": keyboard.Key.shift_l,
        "shift_r": keyboard.Key.shift_r,
        "esc": keyboard.Key.esc,
        "escape": keyboard.Key.esc,
        "space": keyboard.Key.space,
        "enter": keyboard.Key.enter,
        "return": keyboard.Key.enter,
    }
    return key_map.get(key_str, keyboard.Key.alt_l)

# Load configuration
config = load_config()
RADIUS = config["radius"]
STEPS = config["steps"]
DRAW_SPEED = config["draw_speed"]
START_KEY = get_key_from_string(config["start_key"])
EXIT_KEY = get_key_from_string(config["exit_key"])

# --- Global State ---
drawing_in_progress = threading.Event()
keep_program_running = threading.Event()
keep_program_running.set()

def draw_perfect_circle():
    """Draws a circle with maximum precision and returns the cursor to the start."""
    drawing_in_progress.set()
    mouse_controller = mouse.Controller()
    
    # We capture the starting position here. This is also where we'll return to.
    center_x, center_y = mouse_controller.position
    print(f"\nCenter detected at: ({center_x}, {center_y})")

    # Move to the starting point (angle = 0)
    start_x = center_x + RADIUS
    start_y = center_y
    mouse_controller.position = (round(start_x), round(start_y))
    time.sleep(0.1)
    
    mouse_controller.press(mouse.Button.left)
    print("Drawing... aiming for 100%!")

    try:
        # Loop through each step to draw the circle
        for i in range(1, STEPS + 1):
            if not keep_program_running.is_set():
                print("\nDrawing cancelled by exit command.")
                break

            angle = (i / STEPS) * 2 * math.pi
            x = center_x + RADIUS * math.cos(angle)
            y = center_y + RADIUS * math.sin(angle)
            
            mouse_controller.position = (round(x), round(y))
            
            # Only sleep if a delay is configured
            if DRAW_SPEED > 0:
                time.sleep(DRAW_SPEED)

    finally:
        # This block always runs, ensuring the mouse is released and returned.
        mouse_controller.release(mouse.Button.left)
        print("Drawing complete. Check your score!")
        
        # Move the mouse back to the original starting center point.
        print("Returning cursor to original position...")
        mouse_controller.position = (center_x, center_y)
        
        drawing_in_progress.clear()

def on_press(key):
    """Listens for the key to START the drawing."""
    if key == START_KEY and not drawing_in_progress.is_set():
        # Start the drawing in a non-blocking thread
        print("Starting drawing...")
        draw_thread = threading.Thread(target=draw_perfect_circle)
        draw_thread.start()

def on_release(key):
    """Listens for the manual EXIT key."""
    if key == EXIT_KEY:
        print("\nExit key pressed. Shutting down.")
        keep_program_running.clear()
        return False

# --- GUI CONFIGURATION TOOL ---
def open_settings():
    """Open the GUI settings window."""
    
    root = tk.Tk()
    root.title("Circle Drawer Configuration")
    root.geometry("400x350")
    root.resizable(False, False)

    # Load current config
    current_config = load_config()

    # Create variables
    radius_var = tk.IntVar(value=current_config["radius"])
    steps_var = tk.IntVar(value=current_config["steps"])
    draw_speed_var = tk.IntVar(value=int(current_config["draw_speed"] * 1000))
    start_key_var = tk.StringVar(value=current_config["start_key"].upper().replace("_", " "))
    exit_key_var = tk.StringVar(value=current_config["exit_key"].upper().replace("_", " "))

    def save_settings():
        """Save current settings to config.json."""
        new_config = {
            "radius": radius_var.get(),
            "steps": steps_var.get(),
            "draw_speed": float(draw_speed_var.get()) / 1000,
            "start_key": start_key_var.get().lower().replace(" ", "_"),
            "exit_key": exit_key_var.get().lower().replace(" ", "_")
        }
        save_config(new_config)
        status_label.config(text="✓ Settings saved!", fg="green")
        root.after(2000, lambda: status_label.config(text=""))

    def reset_defaults():
        """Reset all settings to defaults."""
        defaults = get_default_config()
        radius_var.set(defaults["radius"])
        steps_var.set(defaults["steps"])
        draw_speed_var.set(int(defaults["draw_speed"] * 1000))
        start_key_var.set("Alt L")
        exit_key_var.set("Esc")
        status_label.config(text="Reset to defaults", fg="blue")
        root.after(2000, lambda: status_label.config(text=""))

    # Title
    title = ttk.Label(root, text="⚙️ Circle Drawer Settings", font=("Arial", 14, "bold"))
    title.pack(pady=10)

    # Radius slider
    ttk.Label(root, text="Circle Radius (pixels):").pack(anchor="w", padx=20)
    radius_frame = ttk.Frame(root)
    radius_frame.pack(fill="x", padx=20, pady=(0, 10))
    radius_slider = ttk.Scale(radius_frame, from_=100, to=500, orient="horizontal", variable=radius_var)
    radius_slider.pack(side="left", fill="x", expand=True)
    radius_label = ttk.Label(radius_frame, text=f"{radius_var.get()}px", width=6)
    radius_label.pack(side="left", padx=(10, 0))
    radius_var.trace("w", lambda *args: radius_label.config(text=f"{radius_var.get()}px"))

    # Steps slider
    ttk.Label(root, text="Smoothness (steps):").pack(anchor="w", padx=20)
    steps_frame = ttk.Frame(root)
    steps_frame.pack(fill="x", padx=20, pady=(0, 10))
    steps_slider = ttk.Scale(steps_frame, from_=500, to=4000, orient="horizontal", variable=steps_var)
    steps_slider.pack(side="left", fill="x", expand=True)
    steps_label = ttk.Label(steps_frame, text=f"{steps_var.get()}", width=6)
    steps_label.pack(side="left", padx=(10, 0))
    steps_var.trace("w", lambda *args: steps_label.config(text=f"{steps_var.get()}"))

    # Draw speed slider
    ttk.Label(root, text="Draw Speed (milliseconds):").pack(anchor="w", padx=20)
    speed_frame = ttk.Frame(root)
    speed_frame.pack(fill="x", padx=20, pady=(0, 10))
    speed_slider = ttk.Scale(speed_frame, from_=0, to=10, orient="horizontal", variable=draw_speed_var)
    speed_slider.pack(side="left", fill="x", expand=True)
    speed_label = ttk.Label(speed_frame, text=f"{draw_speed_var.get()}ms", width=6)
    speed_label.pack(side="left", padx=(10, 0))
    draw_speed_var.trace("w", lambda *args: speed_label.config(text=f"{draw_speed_var.get()}ms"))

    # Key selection
    keys_frame = ttk.Frame(root)
    keys_frame.pack(fill="x", padx=20, pady=10)

    ttk.Label(keys_frame, text="Start Key:").pack(side="left")
    start_key_combo = ttk.Combobox(keys_frame, textvariable=start_key_var, 
                                   values=["Alt L", "Alt R", "Ctrl L", "Ctrl R", "Shift L", "Shift R", "Space", "Enter"], 
                                   state="readonly", width=12)
    start_key_combo.pack(side="left", padx=5)

    ttk.Label(keys_frame, text="Exit Key:").pack(side="left", padx=(20, 0))
    exit_key_combo = ttk.Combobox(keys_frame, textvariable=exit_key_var, 
                                  values=["Esc", "Escape", "Q", "Space"], 
                                  state="readonly", width=12)
    exit_key_combo.pack(side="left", padx=5)

    # Buttons
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=15)
    save_btn = ttk.Button(button_frame, text="💾 Save Settings", command=save_settings)
    save_btn.pack(side="left", padx=5)
    reset_btn = ttk.Button(button_frame, text="🔄 Reset", command=reset_defaults)
    reset_btn.pack(side="left", padx=5)

    # Status label
    status_label = ttk.Label(root, text="", font=("Arial", 10))
    status_label.pack(pady=5)

    root.mainloop()

# --- Main Execution ---
if __name__ == "__main__":
    import sys
    
    # Check for command-line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "config":
        # Run settings GUI
        print("Opening configuration tool...")
        open_settings()
    else:
        # Run the drawing script
        print("--- Perfect Circle Drawer ---")
        print("Configuration loaded from config.json:")
        print(f"  Radius: {RADIUS}px")
        print(f"  Steps: {STEPS}")
        print(f"  Draw Speed: {DRAW_SPEED}s")
        print()
        print("Instructions:")
        print("1. Open https://neal.fun/perfect-circle/ and wait for it to load.")
        print("2. Click on the canvas to focus it.")
        print("3. Move your mouse to the CENTER of the dot in the middle.")
        print(f"4. Press the START key (Left Alt by default) to draw a perfect {RADIUS}px radius circle.")
        print("   The cursor will return to where it started.")
        print(f"5. Press the EXIT key (Esc by default) at any time to stop.")
        print()
        print("To open the settings GUI, run: python circle_drawer.py config")
        print()
        print("Listening for key presses...")

        # Start the keyboard listeners
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            # The main thread waits here until the exit key is pressed
            listener.join()
            
        print("Script has finished. Exiting.")
