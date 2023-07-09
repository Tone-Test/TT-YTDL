## TT-YTDL
 
TT-YTDL is a simple CLI tool to download youtube videos simply and efficiently.
 
## Features 
 
- Download YouTube videos in MP4 format 
- Download audio files from YouTube videos in MP3 format 
- Download both video and audio files simultaneously
- Download Playlists in Audio and Video
- Customize the download directory 
- Change the text color in the command-line interface 
- Check for existing downloads to avoid duplicate files
- Download videos up to 4K
- Automatically retrys downloads if resolution is not available untill 144p.

 
## Installation 
 
1. Install Python (version 3.11 or higher) on your system. 
2. Download the TT-YTDL.py  script and save it to a directory of your choice.
3. Install the required Python packages by running:  ```pip install -r requirements.txt```  


## To fix youtube-dl downloading error "unable to extract uploader id"
   Run ```python3 -m pip install --force-reinstall https://github.com/yt-dlp/yt-dlp/archive/master.tar.gz``` on your system. This will work with Windows and Linux. Im not too sure on MacOS 


## Usage 
 
1. Open a terminal or command prompt. 
2. Navigate to the directory where you saved the  tt-ytdl.py  script. 
3. Run the script using the command:  ```python tt-ytdl.py```  
4. Follow the on-screen prompts to download videos, audio files, or both. You can also change the download directory and text color in the settings menu. 
ALT. Just double click in your file manager. For linux, makesure to make it executable, to do so, right click the file, click proporties, and in the window that pops up, click permissions, and click "Allow Executing" or similar.

## Downloading above 720p
   Go to settings, advanced, and Choose video resolution. Then you can pick the resolution you want your videos to be downloaded in. As mentioned above, the script will automatically retry downloading the video if the resolution you picked is not available for the video you are downloading.

## Customizing Text Color 
 
When changing the text color, the command-line interface will display the available color options in their respective colors. The available colors are: 
 
- Green 
- Red 
- Blue 
- Cyan 
 
To change the text color, simply enter the desired color when prompted. 
 
## Contributing 
 
I welcome contributions to TT-YTDL! If you'd like to contribute, please feel free to submit a pull request or open an issue on GitHub. 
 
