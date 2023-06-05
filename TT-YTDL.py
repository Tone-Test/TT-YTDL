import os
import configparser
import pytube
import threading
import time
import sys
import re
import imageio_ffmpeg as ffmpeg
import colorama
from colorama import Fore, Style
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".TT-YTDL_config.ini")
colorama.init()
def sanitize_filename(filename):
    return re.sub(r'[\\/:"*?<>|]', "", filename)
def on_progress(stream, chunk, bytes_remaining):
    global start_time
    current = stream.filesize - bytes_remaining
    percent = (current / stream.filesize) * 100
    speed = current / (time.time() - start_time)
    sys.stdout.write(
        f"\rDownloading... {current / (1024 * 1024):.2f}MB of {stream.filesize / (1024 * 1024):.2f}MB ({percent:.2f}%) - {speed / (1024 * 1024):.2f}MB/s")
    sys.stdout.flush()
def check_downloaded(title, extension, download_type):
    sanitized_title = sanitize_filename(title)
    file_path = os.path.join(DOWNLOAD_DIR, download_type, sanitized_title + extension)
    return os.path.exists(file_path)
def download_video(video_url):
    global start_time
    youtube = pytube.YouTube(video_url)
    video = youtube.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
    if video is None:
        print("No matching video stream found.")
        return
    youtube.register_on_progress_callback(on_progress)
    sanitized_title = sanitize_filename(video.title)
    video_path = os.path.join(VIDEO_DIR, sanitized_title + ".mp4")
    if check_downloaded(video.title, ".mp4", "Video-MYTDL"):
        print("Video has already been downloaded:", video_path)
        return
    start_time = time.time()
    video.download(output_path=VIDEO_DIR, filename=sanitized_title + ".mp4", timeout=300)
    print("\nVideo downloaded successfully:", video_path)
def download_audio(video_url):
    global start_time
    youtube = pytube.YouTube(video_url)
    audio = youtube.streams.filter(only_audio=True).order_by("abr").desc().first()
    if audio is None:
        print("No matching audio stream found.")
        return
    youtube.register_on_progress_callback(on_progress)
    sanitized_title = sanitize_filename(audio.title)
    audio_path = os.path.join(AUDIO_DIR, sanitized_title + ".mp3")
    if check_downloaded(audio.title, ".mp3", "Audio-MYTDL"):
        print("Audio has already been downloaded:", audio_path)
        return
    start_time = time.time()
    audio.download(output_path=AUDIO_DIR, filename=sanitized_title + ".mp3", timeout=300)
    print("\nAudio downloaded successfully:", audio_path)
def download_both(video_url):
    download_video(video_url)
    download_audio(video_url)
def get_download_dir():
    global DOWNLOAD_DIR, AUDIO_DIR, VIDEO_DIR
    if not os.path.isfile(CONFIG_PATH):
        config = configparser.ConfigParser()
        config["DEFAULT"] = {"download_dir": os.path.join(os.path.expanduser("~"), "Downloads")}
        with open(CONFIG_PATH, "w") as f:
            config.write(f)
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    DOWNLOAD_DIR = config["DEFAULT"]["download_dir"]
    AUDIO_DIR = os.path.join(DOWNLOAD_DIR, "Audio-MYTDL")
    VIDEO_DIR = os.path.join(DOWNLOAD_DIR, "Video-MYTDL")
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)
    if not os.path.exists(VIDEO_DIR):
        os.makedirs(VIDEO_DIR)
    return DOWNLOAD_DIR
def set_download_dir(download_dir):
    config = configparser.ConfigParser()
    config["DEFAULT"] = {"download_dir": download_dir}
    with open(CONFIG_PATH, "w") as f:
        config.write(f)
    print("Default download directory set to:", download_dir)
def set_text_color(color):
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    config["DEFAULT"]["text_color"] = color
    with open(CONFIG_PATH, "w") as f:
        config.write(f)
    print(f"Text color set to {color}.")
def get_text_color():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    color = config["DEFAULT"].get("text_color", "green").lower()
    if color == "green":
        return Fore.GREEN
    elif color == "red":
        return Fore.RED
    elif color == "blue":
        return Fore.BLUE
    elif color == "cyan":
        return Fore.CYAN
    else:
        return Fore.GREEN
if __name__ == "__main__":
    TEXT_COLOR = get_text_color()
    print(TEXT_COLOR + "Welcome to TT-YTDL!")
    DOWNLOAD_DIR = get_download_dir()
    print("Your default download directory is:", DOWNLOAD_DIR)
    while True:
        print(TEXT_COLOR + "Options:")
        print("(1) Video")
        print("(2) Audio")
        print("(3) Both")
        print("(4) Change download location")
        print("(5) Change text color")
        print("(6) Exit")
        choice = input("Pick an option:")
        if choice == "1":
            video_url = input("Please enter the YouTube video URL: ")
            download_video(video_url)
            print("\n")
        elif choice == "2":
            video_url = input("Please enter the YouTube video URL: ")
            download_audio(video_url)
            print("\n")
        elif choice == "3":
            video_url = input("Please enter the YouTube video URL: ")
            download_both(video_url)
            print("\n")
        elif choice == "4":
            download_dir = input("Please enter the new download directory: ")
            set_download_dir(download_dir)
            DOWNLOAD_DIR = download_dir
        elif choice == "5":
            color = input("Please enter the new text color (Green, Red, Blue, Cyan): ")
            set_text_color(color)
            TEXT_COLOR = get_text_color()
        elif choice == "6":
            print("Thank you for using TT-YTDL!")
            break
        else:
            print("Invalid choice, please try again.")