import os
import configparser
import pytube
import time
import sys
import re
import colorama
from colorama import Fore, Style
import youtube_dl
import ctypes
import platform
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".TT-YTDL_config.ini")
colorama.init()
def download_video_with_opts(video_url, ydl_opts):
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            return True
    except youtube_dl.utils.DownloadError:
        return False
def get_fallback_resolution(video_info, resolution):
    available_resolutions = [fmt['height'] for fmt in video_info['formats'] if fmt['acodec'] == 'none' and fmt['vcodec'] != 'none']
    available_resolutions.sort(reverse=True)
    for res in available_resolutions:
        if res <= resolution:
            return res
    return available_resolutions[-1]
def handle_download_error():
    print("An error occurred! Check the Python debugger for the error.")
    print("Returning to the main menu...\n")
def sanitize_filename(filename):
    return re.sub(r'[\\/:"*?<>|]', "", filename)
def save_resolution(resolution):
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    config["DEFAULT"]["resolution"] = str(resolution)
    with open(CONFIG_PATH, "w") as f:
        config.write(f)
    print(f"Video resolution set to {resolution}p.")
def get_resolution():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    resolution = config["DEFAULT"].get("resolution", "720")
    return int(resolution)
def on_progress(progress):
    global start_time
    if progress['status'] == 'downloading':
        if 'total_bytes' in progress and 'downloaded_bytes' in progress:
            bytes_remaining = progress['total_bytes'] - progress['downloaded_bytes']
            current = progress['total_bytes'] - bytes_remaining
            percent = (current / progress['total_bytes']) * 100
            speed = current / (time.time() - start_time)
            sys.stdout.write(
                f"\rDownloading... {current / (1024 * 1024):.2f}MB of {progress['total_bytes'] / (1024 * 1024):.2f}MB ({percent:.2f}%) at {speed / (1024 * 1024):.2f}MB/s")
            sys.stdout.flush()
        else:
            sys.stdout.write("\rDownloading")
            sys.stdout.flush()
def check_downloaded(title, extension, download_type):
    sanitized_title = sanitize_filename(title)
    file_path = os.path.join(DOWNLOAD_DIR, download_type, sanitized_title + extension)
    return os.path.exists(file_path)
def download_video(video_url, resolution=None):
    if resolution is None:
        resolution = get_resolution()  # Get the resolution from the config file
    ydl_opts = {
        'outtmpl': os.path.join(VIDEO_DIR, '%(title)s.%(ext)s'),
        'progress_hooks': [on_progress],
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            sanitized_title = sanitize_filename(info['title'])
            video_path = os.path.join(VIDEO_DIR, sanitized_title + ".mp4")
            if check_downloaded(info['title'], ".mp4", "Video-TT-YTDL"):
                print("Video has already been downloaded:", video_path)
                return
             # Get the fallback resolution
            resolution = get_fallback_resolution(info, resolution)
            ydl_opts['format'] = f'bestvideo[height<={resolution}][fps<=60]+bestaudio/best[height<={resolution}][fps<=60]'
            ydl.download([video_url])
            print("\nVideo downloaded successfully:", video_path)
    except youtube_dl.utils.DownloadError:
        handle_download_error()
def download_audio(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(AUDIO_DIR, '%(title)s.%(ext)s'),
        'progress_hooks': [on_progress],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        sanitized_title = sanitize_filename(info['title'])
        audio_path = os.path.join(AUDIO_DIR, sanitized_title + ".mp3")
        if check_downloaded(info['title'], ".mp3", "Audio-TT-YTDL"):
            print("Audio has already been downloaded:", audio_path)
            return
        ydl.download([video_url])
        print("\nAudio downloaded successfully:", audio_path)
def download_both(video_url, resolution=None):
    download_video(video_url, resolution)
    download_audio(video_url)
def download_playlist_videos(playlist_url, resolution=None):
    if resolution is None:
        resolution = get_resolution()
    ydl_opts = {
        'quiet': True,
        'ignoreerrors': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)
        playlist_title = sanitize_filename(playlist_info.get('title', 'Untitled_Playlist'))
    playlist_dir = os.path.join(VIDEO_DIR, playlist_title)
    if not os.path.exists(playlist_dir):
        os.makedirs(playlist_dir)
    video_urls = [entry['webpage_url'] for entry in playlist_info['entries'] if entry is not None]
    print(f"Downloading {len(video_urls)} videos from the playlist...")
    for video_url in video_urls:
        ydl_opts = {
            'outtmpl': os.path.join(playlist_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [on_progress],
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                # Get the fallback resolution
                fallback_resolution = get_fallback_resolution(info, resolution)
                for res in range(resolution, fallback_resolution - 1, -1):
                    print(f"Trying {res}p resolution...")
                    ydl_opts['format'] = f'bestvideo[height<={res}][fps<=60]+bestaudio/best[height<={res}][fps<=60]'
                    if download_video_with_opts(video_url, ydl_opts):
                        break
                    else:
                        print(f"Failed at {res}p, trying another resolution...")
                else:
                    print("Failed to download video:", video_url)
        except youtube_dl.utils.DownloadError as e:
            print(f"Error downloading video: {e}")
def download_playlist_audios(playlist_url):
    playlist = Playlist(playlist_url)
    playlist_title = sanitize_filename(playlist.title)
    playlist_dir = os.path.join(AUDIO_DIR, playlist_title)
    if not os.path.exists(playlist_dir):
        os.makedirs(playlist_dir)
    print(f"Downloading {len(playlist.video_urls)} audios from the playlist...")
    for video_url in playlist.video_urls:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(playlist_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [on_progress],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
def download_playlist_both(playlist_url, resolution=None):
    playlist = Playlist(playlist_url)
    playlist_title = sanitize_filename(playlist.title)
    video_playlist_dir = os.path.join(VIDEO_DIR, playlist_title)
    audio_playlist_dir = os.path.join(AUDIO_DIR, playlist_title)
    if not os.path.exists(video_playlist_dir):
        os.makedirs(video_playlist_dir)
    if not os.path.exists(audio_playlist_dir):
        os.makedirs(audio_playlist_dir)
    print(f"Downloading {len(playlist.video_urls)} videos and audios from the playlist...")
    for video_url in playlist.video_urls:
        download_video(video_url, resolution, video_playlist_dir)
        download_audio(video_url, audio_playlist_dir)
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
    AUDIO_DIR = os.path.join(DOWNLOAD_DIR, "Audio-TT-YTDL")
    VIDEO_DIR = os.path.join(DOWNLOAD_DIR, "Video-TT-YTDL")
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)
    if not os.path.exists(VIDEO_DIR):
        os.makedirs(VIDEO_DIR)
    return DOWNLOAD_DIR
def is_admin():
    if platform.system() == "Windows":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except AttributeError:
            return False
    else:
        return os.getuid() == 0  
def set_download_dir(download_dir):  
    if not os.path.exists(download_dir):  
        create_folder = input(f"The directory '{download_dir}' does not exist. Do you want to create it? (y/N): ")  
        if create_folder.lower() == "y":  
            if not is_admin():  
                print("Please restart the script with administrator privileges.")  
                if platform.system() == "Windows":  
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)  
                sys.exit(1)  
            try:  
                if platform.system() == "Windows":  
                    os.makedirs(download_dir)  
                else:  
                    os.system(f"sudo mkdir -p {download_dir}")  
                print("Directory created:", download_dir)  
            except OSError as e:  
                print(f"Error creating directory: {e}")  
                return  
        else:  
            print("Directory not created.")  
            return  
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
def settings_menu():  
    while True:  
        print("Settings:")  
        print("(1) Change download location")  
        print("(2) Change text color")  
        print("(3) Advanced mode")  
        print("(4) Back to main menu")  
        choice = input("Pick an option:")  
        if choice == "1":  
            download_dir = input("Please enter the new download directory: ")  
            set_download_dir(download_dir)  
            DOWNLOAD_DIR = download_dir  
        elif choice == "2":  
            color = input("Please enter the new text color (Green, Red, Blue, Cyan): ")  
            set_text_color(color)  
            TEXT_COLOR = get_text_color()  
        elif choice == "3":  
            advanced_mode()  
        elif choice == "4":  
            break  
        else:  
            print("Invalid choice, please try again.")  
def advanced_mode():  
    while True:  
        print("Advanced mode:")  
        print("(1) Choose video resolution")  
        print("(2) Back to settings menu")  
        choice = input("Pick an option:")  
        if choice == "1":  
            resolution = choose_resolution()  
            if resolution:  
                print(f"Resolution set to {resolution}p.")  
                save_resolution(resolution)  # Add this line to save the resolution to the config file  
            else:  
                print("Invalid resolution. Resolution not set.")  
        elif choice == "2":  
            break  
        else:  
            print("Invalid choice, please try again.")  
def choose_resolution():   
    resolutions = [144, 240, 360, 480, 720, 1080, 2160]   
    print("Choose a resolution from the list:")   
    for i, res in enumerate(resolutions):   
        print(f"({i + 1}) {res}p")   
    choice = input("Pick an option:")   
    try:   
        index = int(choice) - 1   
        if 0 <= index < len(resolutions):   
            return resolutions[index]   
        else:   
            return None   
    except ValueError:   
        return None   
  
  
  
if __name__ == "__main__":  
    TEXT_COLOR = get_text_color()  
    print(TEXT_COLOR + "Welcome to TT-YTDL!")  
    DOWNLOAD_DIR = get_download_dir()  
    print("Your default download directory is:", DOWNLOAD_DIR)  
  
    RESOLUTION = get_resolution()  
    print("Your default video resolution is:", RESOLUTION, "p")  
    while True:  
        TEXT_COLOR = get_text_color()  
        print(TEXT_COLOR + "Options:")  
        print("(1) Video")   
        print("(2) Audio")   
        print("(3) Both")   
        print("(4) Playlist Video")   
        print("(5) Playlist Audio")   
        print("(6) Playlist Both")   
        print("(7) Settings")   
        print("(8) Exit")   
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
            playlist_url = input("Please enter the YouTube playlist URL: ")   
            confirm = input("This will download video for each item in the playlist. Are you sure? (y/N): ")  # Add this line   
            if confirm.lower() == "y":  # Add this line   
                download_playlist_videos(playlist_url)   
            else:   
                print("Cancelled playlist video download.")   
            print("\n")   
        elif choice == "5":   
            playlist_url = input("Please enter the YouTube playlist URL: ")   
            download_playlist_audios(playlist_url)   
            print("\n")   
        elif choice == "6":   
            playlist_url = input("Please enter the YouTube playlist URL: ")   
            confirm = input("This will download both video and audio for each item in the playlist. Are you sure? (y/N): ")   
            if confirm.lower() == "y":   
                download_playlist_both(playlist_url)   
            else:   
                print("Cancelled playlist download.")   
            print("\n")   
        elif choice == "7":   
            settings_menu()   
        elif choice == "8":   
            print("Thank you for using TT-YTDL!")   
            break   
        else:   
            print("Invalid choice, please try again.")   