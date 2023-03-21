import ffmpeg

from tkinter import filedialog as fd
import shutil
import customtkinter as ctk
import tkinter as tk
import json
import os

file_input = "Not yet set!"
destination_input = "Not yet set!"
ffmpeg_input = "Not yet set!           Hint - look for 'bin\\ffmpeg.exe' in your C drive!"
empty_save = {"ffmpeg_dir": "", "main_folder": ""}
saves = empty_save

def load_saves():
    global empty_save, saves, folder_input
    try:
        os.mkdir("save")

    except FileExistsError:
        try:
            # Load the save file if it is found

            with open("save/save.json", "r") as f:
                
                saves = (json.load(f))

                if saves["ffmpeg_dir"] != "":
                    ffmpeg_input = saves["ffmpeg_dir"]
                    ffmpeg_path_label.configure(text=f"FFMPEG Path: {ffmpeg_input}")
                
                if saves["main_folder"] != "":
                    destination_input = saves["main_folder"]
                    folder_input = destination_input
                    destination_label.configure(text=f"Destination: {destination_input}")
                
        except FileNotFoundError:
            # Create and write into the save if it is not found

            with open("save/save.json", "x") as f:
                json.dump(empty_save, f)

def open_target_file():
    global file_input
    file_input = fd.askopenfilename(filetypes=(('MP4 Video Files', '*.mp4'),))
    if file_input == "":
        pass
    else:
        f_path_label.configure(text=f"Selected File Path: {file_input}")

def open_destination_folder():
    global folder_input
    folder_input = fd.askdirectory(mustexist=True)
    destination_label.configure(text=f"Destination: {folder_input}")

def open_ffmpeg():
    global ffmpeg_input
    ffmpeg_input = fd.askopenfilename(filetypes=(("Executable File", "ffmpeg.exe"),))
    ffmpeg_path_label.configure(text=f"FFMPEG Path: {ffmpeg_input}")

def save_ffmpeg():
    with open("save/save.json", "w") as f:
        empty_save["ffmpeg_dir"] = ffmpeg_input
        empty_save["main_folder"] = saves["main_folder"]
        json.dump(empty_save, f)

def save_main_folder():
    with open("save/save.json", "w") as f:
        empty_save["ffmpeg_dir"] = saves["ffmpeg_dir"]
        empty_save["main_folder"] = folder_input
        json.dump(empty_save, f)


def compress():
    # Code mainly borrowed from from https://stackoverflow.com/questions/64430805/how-to-compress-video-to-target-size-by-python/64439347#64439347

    probe = ffmpeg.probe(file_input)

    # Minimum requirements
    total_bitrate_lower_bound = 10000
    min_audio_bitrate = 20000
    max_audio_bitrate = 256000
    min_video_bitrate = 100000

    # Find video duration in seconds
    duration = float(probe["format"]["duration"])

    # Find audio bitrate in b/s
    audio_bitrate = float(next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)["bit_rate"])


    # Get target size in mb
    target_size = int(var.get())
    
    # Convert target size to kb
    target_size *= 1000

    # Find target total bitrate in b/s
    target_total_bitrate = round((target_size * 1024 * 8) / (1.073741824 * duration), 2)

    # Calculate best min size. Changed to remove rate limit.
    best_min_size = (min_audio_bitrate + min_video_bitrate) * (1.073741824 * duration) / (8 * 1024)

    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
    if audio_bitrate < min_audio_bitrate < target_total_bitrate:
        audio_bitrate = min_audio_bitrate
    elif audio_bitrate > max_audio_bitrate:
        audio_bitrate = max_audio_bitrate

    video_bitrate = target_total_bitrate - audio_bitrate
    if video_bitrate < 1000:
        print('Bitrate {} is extremely low! Stop compress.'.format(video_bitrate))
        return False

    # Do the FFMPEG compression
    i = ffmpeg.input(file_input)
    filename = file_input.replace(".mp4", "")

    output_file_name = f"{filename}_Compressed.mp4"

    # Compress
    ffmpeg.output(i, output_file_name,
                **{'c:v': 'libx264', 'b:v': video_bitrate, 'c:a': 'aac', 'b:a': audio_bitrate}
                ).overwrite_output().run()

    if os.path.getsize(output_file_name) <= target_size * 1024:
        shutil.move(output_file_name, folder_input)
        return output_file_name
    elif os.path.getsize(output_file_name) < os.path.getsize(file_input):
        return compress(output_file_name, target_size)
    else:
        return False


# Window Configurations
root = ctk.CTk()
root.geometry("600x665")
root.resizable(False, False)
root.title("Discord Target Compressor")

# File path display
f_path_label = ctk.CTkLabel(root, text=f"Selected File Path: {file_input}", font=("", 20))
f_path_label.place(x=20, y=20)

# FFMPEG controls

# Locate FFMPEG
locate_ffmpeg_button = ctk.CTkButton(root, text="Locate FFMPEG", font=("", 20), command=open_ffmpeg).place(x=20, y=60)
ffmpeg_path_label = ctk.CTkLabel(root, text=f"FFMPEG path: {ffmpeg_input}")
ffmpeg_path_label.place(x=20, y=100)

# Save FFMPEG
save_ffmepg_button = ctk.CTkButton(root, text="Save FFMPEG location", font=("", 20), command=save_ffmpeg).place(x=200, y=60)


# File Selector
ctk.CTkButton(root, text="Select a file...", width=560, height=100, font=("", 40), command=open_target_file).place(x=20, y=140)

# Compression Target Selector
ctk.CTkLabel(root, text="Target compression:", font=("", 20)).place(x=20, y=260)

var = ctk.StringVar()

def updated_get():
    root.update()
    a = custom_mb.get()
    return a

custom_mb = ctk.CTkEntry(root)
custom_mb.place(x=120, y=375)


mb_button_8 = ctk.CTkRadioButton(root, text="Discord standard limit (8 MB)", variable=var, value=6)
mb_button_500 = ctk.CTkRadioButton(root, text="Discord nitro limit (100 MB)", variable=var, value=70)
mb_button_custom = ctk.CTkRadioButton(root, text="Custom:", variable=var, value=updated_get)

mb_button_8.select()

mb_button_8.place(x=20, y=300)
mb_button_500.place(x=20, y=340)
mb_button_custom.place(x=20, y=380)


# Destination Folder
ctk.CTkButton(root, text="Change Destination Folder", font=("", 20), command=open_destination_folder).place(x=20, y=425)
ctk.CTkButton(root, text="Save as Main Folder", font=("", 20), command=save_main_folder).place(x=290, y=425)
destination_label = ctk.CTkLabel(root, text=f"Destination: {destination_input}")
destination_label.place(x=20, y=465)

# Compressor
ctk.CTkButton(root, text="Compress!", width=560, height=100, font=("", 40), command=compress).place(x=20, y=505)

# Error Message Display
error_message = ctk.CTkLabel(root, text="", font=("", 20), text_color="dark red").place(x=20, y=620)

load_saves()
root.mainloop()
