import tkinter as tk
from PIL import Image, ImageTk
import pygame
import threading
import time
import sys
import os
import random

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# -------------------------------------------------
# pygame
# -------------------------------------------------
pygame.mixer.init()

# load normal meow sounds
normal_sounds = []
for i in range(1,6):
    try:
        s = pygame.mixer.Sound(resource_path(f"meow{i}.mp3"))
        normal_sounds.append(s)
    except pygame.error as e:
        print(f"Normal sound meow{i} load error: {e}")

# load rare sounds
try:
    rare_sound1 = pygame.mixer.Sound(resource_path("rare1.mp3"))
except pygame.error as e:
    print(f"Rare1 sound load error: {e}")
    rare_sound1 = None

try:
    rare_sound2 = pygame.mixer.Sound(resource_path("rare2.mp3"))
except pygame.error as e:
    print(f"Rare2 sound load error: {e}")
    rare_sound2 = None

try:
    pygame.mixer.music.load(resource_path("background.mp3"))
    default_music_volume = 0.5
    pygame.mixer.music.set_volume(default_music_volume)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Music load error: {e}")

# -------------------------------------------------
# Tk window
# -------------------------------------------------
root = tk.Tk()
root.title("niko speak (made with <3 by pixel1nova)")
root.configure(bg="#1e1e1e")
root.minsize(400, 400)

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# -------------------------------------------------
# Load images
# -------------------------------------------------
try:
    niko_normal_img = Image.open(resource_path("Niko.webp")).convert("RGBA")
    niko_speak_img = Image.open(resource_path("Niko_speak.webp")).convert("RGBA")
    niko_rare1_img = Image.open(resource_path("Niko_rare1.png")).convert("RGBA")
    niko_rare2_img = Image.open(resource_path("Niko_rare2.png")).convert("RGBA")
except FileNotFoundError as e:
    print(f"Image load error: {e}")
    exit(1)

current_sprite_image = niko_normal_img

# -------------------------------------------------
# Canvas
# -------------------------------------------------
canvas = tk.Canvas(root, bg="#1e1e1e", highlightthickness=0)
canvas.grid(row=0, column=0, sticky="nsew")

padding = 15
border_color = "#888888"

# border rectangle
border_id = canvas.create_rectangle(0, 0, 0, 0, outline=border_color, width=4, fill="#2a2a2a")

# sprite
init_photo = ImageTk.PhotoImage(niko_normal_img)
sprite_id = canvas.create_image(0, 0, anchor="nw", image=init_photo)
canvas.sprite_refs = [init_photo]

# -------------------------------------------------
# Control panel
# -------------------------------------------------
control_frame = tk.Frame(root, bg="#2a2a2a")
control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
root.grid_rowconfigure(1, weight=0)

click_count = tk.IntVar(value=0)

click_count_label = tk.Label(
    control_frame, text="Clicks: 0",
    fg="#f0f0f0", bg="#2a2a2a",
    font=("Segoe UI", 12, "bold")
)
click_count_label.grid(row=0, column=0, padx=5)

def update_click_label():
    click_count_label.config(text=f"Clicks: {click_count.get()}")

def styled_button(parent, text, command):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg="#444444",
        fg="white",
        activebackground="#555555",
        activeforeground="white",
        relief="flat",
        font=("Segoe UI", 11, "bold"),
        padx=10,
        pady=5
    )
    btn.configure(highlightthickness=0, bd=0)
    def on_enter(e):
        btn.config(bg="#666666")
    def on_leave(e):
        btn.config(bg="#444444")
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

music_muted = tk.BooleanVar(value=False)

def toggle_music():
    if music_muted.get():
        pygame.mixer.music.set_volume(volume_slider.get())
        music_muted.set(False)
        mute_button.config(text="Mute Music")
    else:
        pygame.mixer.music.set_volume(0)
        music_muted.set(True)
        mute_button.config(text="Unmute Music")

mute_button = styled_button(control_frame, "Mute Music", toggle_music)
mute_button.grid(row=0, column=1, padx=5, sticky="ew")

def on_button_click():
    click_count.set(click_count.get() + 1)
    update_click_label()

    chance = random.randint(1,50)  # 2% rare chance

    if chance == 1:
        # rare 1
        change_sprite(niko_rare1_img)
        def reset():
            if rare_sound1:
                rare_sound1.play()
                time.sleep(rare_sound1.get_length())
            change_sprite(niko_normal_img)
        threading.Thread(target=reset, daemon=True).start()
    elif chance == 2:
        # rare 2
        change_sprite(niko_rare2_img)
        def reset():
            if rare_sound2:
                rare_sound2.play()
                time.sleep(rare_sound2.get_length())
            change_sprite(niko_normal_img)
        threading.Thread(target=reset, daemon=True).start()
    else:
        # normal
        change_sprite(niko_speak_img)
        normal_sound = random.choice(normal_sounds) if normal_sounds else None
        def reset():
            if normal_sound:
                normal_sound.play()
                time.sleep(normal_sound.get_length())
            change_sprite(niko_normal_img)
        threading.Thread(target=reset, daemon=True).start()

click_button = styled_button(control_frame, "nikomeow", on_button_click)
click_button.grid(row=0, column=2, padx=5, sticky="ew")

# Volume slider with separate percentage label
volume_percent_var = tk.StringVar()
volume_percent_var.set(f"{int(default_music_volume * 100)}%")

def set_volume(val):
    vol = float(val)
    if not music_muted.get():
        pygame.mixer.music.set_volume(vol)
    volume_percent_var.set(f"{int(vol*100)}%")

volume_slider = tk.Scale(
    control_frame,
    from_=0.0, to=1.0,
    orient="horizontal",
    resolution=0.01,
    length=150,
    label="Volume",
    command=set_volume,
    bg="#2a2a2a",
    fg="white",
    troughcolor="#444444",
    highlightthickness=0,
    font=("Segoe UI", 10, "bold"),
    showvalue=0
)
volume_slider.set(default_music_volume)
volume_slider.grid(row=0, column=3, padx=5)

volume_percent_label = tk.Label(
    control_frame,
    textvariable=volume_percent_var,
    fg="white",
    bg="#2a2a2a",
    font=("Segoe UI", 10, "bold")
)
volume_percent_label.grid(row=0, column=4, padx=5)

control_frame.grid_columnconfigure(0, weight=1)
control_frame.grid_columnconfigure(1, weight=1)
control_frame.grid_columnconfigure(2, weight=1)
control_frame.grid_columnconfigure(3, weight=1)
control_frame.grid_columnconfigure(4, weight=1)

# -------------------------------------------------
# Sprite drawing
# -------------------------------------------------
def change_sprite(new_image):
    global current_sprite_image
    current_sprite_image = new_image
    draw_sprite()

def draw_sprite():
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w < 50 or h < 50:
        return

    available_w = w - 2 * padding
    available_h = h - 2 * padding

    img_w, img_h = current_sprite_image.size
    ratio = min(available_w / img_w, available_h / img_h)
    new_size = (int(img_w * ratio), int(img_h * ratio))

    sprite_resized = current_sprite_image.resize(new_size, Image.LANCZOS)
    sprite_photo = ImageTk.PhotoImage(sprite_resized)

    total_w = new_size[0] + 2 * padding
    total_h = new_size[1] + 2 * padding

    x0 = (w - total_w) // 2
    y0 = (h - total_h) // 2
    x1 = x0 + total_w
    y1 = y0 + total_h

    canvas.coords(border_id, x0, y0, x1, y1)

    x_img = x0 + padding
    y_img = y0 + padding
    canvas.itemconfig(sprite_id, image=sprite_photo)
    canvas.coords(sprite_id, x_img, y_img)

    canvas.sprite_refs.append(sprite_photo)
    if len(canvas.sprite_refs) > 5:
        canvas.sprite_refs = canvas.sprite_refs[-5:]

canvas.bind("<Configure>", lambda e: draw_sprite())

root.mainloop()
