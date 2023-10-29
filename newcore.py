import yt_dlp as youtube_dl
from youtube_search import YoutubeSearch
def search(term,res=10):
    query = term
    results = YoutubeSearch(query, max_results=res).to_dict()
      #  title = video['title']
       # video_id = video['id']
    return results

import os

import re

def coolname(name):
    # Remove characters other than Persian and English alphabets and numbers
    cleaned_name = re.sub(r'[^ء-يA-Za-z0-9|ژکچگیپ() ]', '', name)
    # cleaned_name = re.sub(r'[^\u0621-\u064A\u067E\u0686\u06AF\u06CC\u0698A-Za-z0-9() ]', '', name)

    return cleaned_name.replace("|", "").replace("#", "")



def dl(link, title=""):
    try:
        # Define the options
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
                'ffmpeg_location': 'bin/ffmpeg.exe',  # Specify the path to ffmpeg executable
            # 'outtmpl': r'downloads\%(title)s.%(ext)s', 
            'outtmpl': 'downloads\/'+ coolname(title) + r'.%(ext)s', 


        }

        # Specify the video URL
    #    video_url = 'https://www.youtube.com/watch?v=eO23weLKT8M'
        video_url = link

        # Create a YouTubeDL object with the options
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Download the audio
            t = ydl.download([video_url])
            print(t,"\n",title)
            #os.rename("downloads/"+title+".mp3", "downloads/"+coolname(title) + ".mp3")
            return True
    except:
        return False