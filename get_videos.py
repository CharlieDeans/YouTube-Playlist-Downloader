from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from moviepy.editor import *
from threading import Thread
from inputimeout import inputimeout

import pytube as pt

from time import sleep

import json
import os

os.system("pip install selenium==4.11.2 webdriver-manager==4.0.0 pytube==15.0.0 moviepy==1.0.3")

if not os.path.exists('Playlist'):
    os.mkdir("Playlist")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

bufferSize = 1

try:
    bufferSize = int(inputimeout("Set buffer size (DEFAULT: 5): ", timeout=10))
except Exception:
    bufferSize = 5

print("Using buffer size of " + str(bufferSize))

clear()

def get_video_links():
    # set the download directory
    chromeOptions = Options()
    chromeOptions.add_argument("--headless")

    

    clear()
    
    # get the playlist link
    print("Enter the playlist link: ")
    video_link = input()
    
    sleep(2)
    clear()
    
    driverMade = False
    count = 0

    while driverMade == False:
        try:
            # create the driver
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chromeOptions)
            driver.get(video_link)
            driverMade = True
        except:
            print("Trying to create driver again...")
            count += 1
            if count >= 5:
                print("Failed")
                exit()
    
    # open the website and enter the video link
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

    clear()

    print("Number of videos in the playlist: " + str(numOfVideos))

    print("\nGetting videos from the playlist...")

    sleep(2)
    clear()

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
                clear()
                print("Videos found: " + str(index) + "/" + str(numOfVideos))

        prevRowLen = len(rows)
        rows[index-1].find_element("xpath", ".//a[@id=\"thumbnail\"]").send_keys(Keys.PAGE_DOWN)

    print("Videos found: " + str(index) + "/" + str(numOfVideos))
    print("There are " + str(numOfVideos - index) + " videos hidden in the playlist")


    # add the videos in videos_list to playlist.json
    with open('playlist.json', 'w') as output:
        output.write(json.dumps(video_links, indent=4))

    sleep(2)
    clear()

    return video_links

def download_videos_as_mp3(video_links = None, bufferSize = 5, identify = 0, logEnable = True):

    clear()

    if video_links == None:
        # get the videos from the json file
        if not os.path.exists('playlist.json'):
            if(logEnable):
                print("No videos found")
            exit()
        else:
            with open('playlist.json') as json_file:
                video_links = json.load(json_file)

    # # download the videos with youtube-dl
    # for video_link in video_links:
    #     video_info = youtube_dl.YoutubeDL().extract_info(url=video_link, download=False)
    #     filename = f"Playlist/{video_info['title']}.mp3"
    #     options = {
    #         'format': 'bestaudio/best',
    #         'keepvideo': False,
    #         'outtmpl': filename,
    #     }
    #     with youtube_dl.YoutubeDL(options) as ydl:
    #         ydl.download([video_info['webpage_url']])
        
    #     print(f"Downloaded {video_info['title']}")

    #     exit()
    

    clear()

    if bufferSize == "":
        bufferSize = 5
    else:
        bufferSize = int(bufferSize)

    count = 0
    successCount = 0
    failedFiles = []
    
    

    while count < len(video_links):
        failed = False
        titles = []

        downloadCount = 0
        while downloadCount < bufferSize and count + downloadCount < len(video_links):
            try:
                yt = pt.YouTube(video_links[count + downloadCount])
                video = yt.streams.filter(file_extension='mp4').first()
                dest = "Playlist\\"
                test = video.download(output_path=dest)
                title = (test.split("\\Playlist\\")[1]).split(".mp4")[0]
                if(logEnable):
                    print("\"" + title + "\" has been successfully downloaded.")
                newTitle = title + "_" + str(identify + count + downloadCount + 1)
                os.rename(r"Playlist/" + title + ".mp4", r"Playlist/" + newTitle + ".mp4")
                title = newTitle
                titles.append(title)
                successCount += 1
            except:
                if(logEnable):
                    print("Failed to download video")
                failed = True
                failedFiles.append(video_links[count + downloadCount])
                
            downloadCount += 1
            
        
        if failed:
            if(logEnable):
                print("Failed to download video")
            
        
        else:
            sleep(1)
            clear()
            
            if(logEnable):
                print("Preparing to convert videos to mp3...")
                sleep(2)
                print("Converting videos to mp3...")
            else:
                sleep(2)
            
            sleep(2)
            clear()
            
            for files in titles:
                video = VideoFileClip("Playlist/" + files + ".mp4")
                video.audio.write_audiofile("Playlist/" + files + ".mp3", verbose=False, logger=None)
                video.close()
                if(logEnable):
                    print("\"" + files + ".mp3" + "\" - CREATED")
                sleep(0.2)
                os.remove(r"Playlist/" + files + ".mp4")
                if(logEnable):
                    print("\"" + files + ".mp4\" - DELETED\n")
        
        count += downloadCount
        if count % 10 == 0:
            if(logEnable):
                print("\nVideos downloaded: " + str(successCount) + "/" + str(len(video_links)), end="\n\n")
        
        if count < len(video_links):
            sleep(1)
            clear()
            
            if(logEnable):
                print("Preparing to convert more videos...")
                sleep(2)
                print("Converting videos...")
            else:
                sleep(2)
            
            sleep(2)
            clear()
        else:
            sleep(1)
            clear()
    
    if len(failedFiles) > 0:
        with open('Playlist/failed.json', 'w') as output:
            output.write(json.dumps(failedFiles, indent=4))
    
    if(logEnable):
        print("Videos downloaded: " + str(successCount) + "/" + str(len(video_links)), end="\n\n")
        

# def remove_http():
#     with open('playlist.json') as json_file:
#         video_links = json.load(json_file)
    
#     for i in range(len(video_links)):
#         video_links[i] = video_links[i].split("://")[1]
    
#     with open('playlist.json', 'w') as output:
#         output.write(json.dumps(video_links, indent=4))

clear()
response = False
if os.path.exists('playlist.json'):
    value = input("Do you want to use the videos stored in playlist.json? (y/n): ")
    
    if value.lower() == "y" or value.lower() == "yes":
        response = True
        
list = []
        
if not response:
    list = get_video_links()

else:
    with open('playlist.json') as json_file:
        list = json.load(json_file)
    sleep(3)

clear()

numOfThreadsToUse = os.cpu_count()

try:
    numOfThreadsToUse = int(inputimeout("How many Threads do you want to use? (DEFAULT: Max Number of Logical Processors): ", timeout=20))
except Exception:
    None
    
print("Using " + str(numOfThreadsToUse) + " Thread" + ("s" if numOfThreadsToUse > 1 else ""))

sleep(3)
clear()

cpus = []

count = numOfThreadsToUse

if len(list) < numOfThreadsToUse:
    count = len(list)

cpuSize = len(list) // count

numOfElement = len(list)
index = 0


for i in range(count):
    newList = []
    
    numToAdd = cpuSize
    
    if numOfElement - numToAdd < numToAdd:
        numToAdd = numOfElement
        
    for j in range(index, index + numToAdd):
        newList.append(list[j])
        numOfElement -= 1
    
    index += numToAdd
    
    cpus.append(newList)
    
threads = []

clear()

log = False

if(numOfThreadsToUse > 1):
    try:
        print("--PLEASE BE ADVISED, THIS PRINTING IS NOT VERY READABLE--")
        log = inputimeout("Do you want progress to be printed to screen? (y/n): ", timeout=10)
        if log.lower() == "y" or log.lower() == "yes":
            log = True
        else:
            log = False
    except Exception:
        clear()
else:
    log = True

identify = 0
for thread in cpus:
    threads.append(Thread(target=download_videos_as_mp3, args=(thread,bufferSize,identify,log)))
    identify += len(thread)
    # download_videos_as_mp3(thread)

for thread in threads:
    thread.start()

clear()
print("Finished!")