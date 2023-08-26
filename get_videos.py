from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from moviepy.editor import *

import pytube as pt

from time import sleep

import json
import os



def get_video_links():
    # set the download directory
    chromeOptions = Options()
    chromeOptions.add_argument("--headless")

    # create the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chromeOptions)

    # get the playlist link
    print("Enter the playlist link: ")
    video_link = input()

    # open the website and enter the video link
    driver.get(video_link)
    numOfVideos = driver.find_element("xpath", "//*[@id=\"page-manager\"]/ytd-browse/ytd-playlist-header-renderer/div/div[2]/div[1]/div/div[1]/div[1]/ytd-playlist-byline-renderer/div/yt-formatted-string[1]/span[1]").text
    numOfVideos_list = str(numOfVideos).split(",")

    numOfVideos_list.reverse()
    columb = 0
    numOfVideos = 0

    for i in range(len(numOfVideos_list)):
        numOfVideos += int(numOfVideos_list[i]) * (pow(10, columb))
        columb += 3

    for i in range(len(numOfVideos_list)):
        numOfVideos_list[i] = numOfVideos_list[i].strip()

    print("Number of videos in the playlist: " + str(numOfVideos))

    print("\nGetting videos from the playlist...")

    video_links = []
    index = 0
    prevRowLen = 0

    while index < numOfVideos:
        sleep(5)
        table = driver.find_element("xpath", "//*[@id=\"contents\"]")
        rows = table.find_elements("xpath", ".//ytd-playlist-video-renderer")
        if prevRowLen == len(rows):
            print("No more videos to find")
            break

        # get the video link from each row
        while index < len(rows):
            video = rows[index].find_element("xpath", ".//a[@id=\"thumbnail\"]")
            video_link = video.get_attribute("href")
            video_link = video_link.split("&list=")[0]
            video_links.append(video_link)
            index += 1
            if(index % 10 == 0):
                print("Videos found: " + str(index) + "/" + str(numOfVideos))

        prevRowLen = len(rows)
        rows[index-1].find_element("xpath", ".//a[@id=\"thumbnail\"]").send_keys(Keys.PAGE_DOWN)

    print("Videos found: " + str(index) + "/" + str(numOfVideos))
    print("There are " + str(numOfVideos - index) + " videos hidden in the playlist")


    # add the videos in videos_list to videos.json
    with open('videos.json', 'w') as output:
        output.write(json.dumps(video_links, indent=4))

    return video_links

def download_videos_as_mp3(video_links = None):

    if video_links == None:
        # get the videos from the json file
        if not os.path.exists('videos.json'):
            print("No videos found")
            exit()
        else:
            with open('videos.json') as json_file:
                video_links = json.load(json_file)
    elif video_links.type() == str:
        video_links = [video_links]

    # # download the videos with youtube-dl
    # for video_link in video_links:
    #     video_info = youtube_dl.YoutubeDL().extract_info(url=video_link, download=False)
    #     filename = f"Videos/{video_info['title']}.mp3"
    #     options = {
    #         'format': 'bestaudio/best',
    #         'keepvideo': False,
    #         'outtmpl': filename,
    #     }
    #     with youtube_dl.YoutubeDL(options) as ydl:
    #         ydl.download([video_info['webpage_url']])
        
    #     print(f"Downloaded {video_info['title']}")

    #     exit()

    count = 0

    for video_link in video_links:
        yt = pt.YouTube(video_link)
        video = yt.streams.filter(file_extension='mp4').first()
        dest = "Videos\\"
        video.download(output_path=dest)
        print(yt.title + " has been successfully downloaded.")
        count += 1
    
    print("\nPreparing to convert videos to mp3...")
    sleep(10)
    print("Converting videos to mp3...")
    
    for files in os.listdir("Videos\\"):
        if files.endswith(".mp4"):
            video = VideoFileClip("Videos/" + files)
            video.audio.write_audiofile("Videos/" + files[:-4] + ".mp3")
            video.close()
            os.remove(r"Videos/" + files)
        

def remove_http():
    with open('videos.json') as json_file:
        video_links = json.load(json_file)
    
    for i in range(len(video_links)):
        video_links[i] = video_links[i].split("://")[1]
    
    with open('videos.json', 'w') as output:
        output.write(json.dumps(video_links, indent=4))
        
get_video_links()
# remove_http()
download_videos_as_mp3()