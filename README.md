# Spotube
Listen to Youtube music videos, Save them like Spotify

## Project Status:
Works fine on windows  
not tested on linux  
dont care about mac  

## TODO:
- Make executable pyinstaller  
- ship ffmpeg with it on windows  
- make it compatible with the linux systems  
- Make some banner for this repo  
- maybe Persian Language
- make it modular
- Sexier readme.md 
- multi theme if people liked this project
- exception for weird or corrupt playlist files
- multi playlist feature
- some good hotkeys (or make it compatible with multimedia buttons on laptops)
- Shuffle Button (or a Scramble Playlist Button)
- maybe kill the whole ffmpeg setting and follow system's env.

## Known issues:
- acting weird while internet is unstable and crashes when you are disconnected
- you tell me.

## How this project works
well, when you open it, it creates settings.json and keeps [ffmpeg path, proxy settings] in it
first you should setup ffmpeg.exe path (relative or absolute) then set proxy or enable your vpn if you live in a cave  
then add your favorite songs with add panel and play them.  
you can save current playlist by save button, it goes on playlist.json  

## Credits:
yt_dlp backbone of the project  
[YoutubeSearch](https://github.com/joetats/youtube_search) (btw i forked it and added proxy support)  
ffmpeg for conversion stuff (webm -> mp3)  
PyQt5 For GUI     

## Disclaimer
im just a developer, i made my hobby which is this project in this case, i dont care if you burn your computer or even your house with my program  
sure, my program is unable to do this stuff but still i dont take any responsibility for any damage that happen to your stuff  
this program is opensource, if you dont trust it, read the fcking code first.
