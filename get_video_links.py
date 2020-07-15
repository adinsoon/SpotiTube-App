import re
from bs4 import BeautifulSoup
import os

'''
I had a struggle with importing my liked videos by API or to make a new playlist with these videos
in it because since late 2019 Youtube set 'Liked' playlist of every user as private. 
So, who's ready to open a playlist, then every single video and add it to the new playlist?
Definitely not me (about 600 videos in playlist), so I made a simple function that does it for you.
The only problem is that playlists bigger than 100 elements are wrapped on the displayed youtube page.
And they might be private, as for example that 'Liked' one. So all you have to do is to scroll down the 
page till the end and then copy and save html code of the page as .html file. You can of course use
Selenium to do it for you or catch request sent by youtube page. However, I simplify it to hold Space. 

Make sure that given file is in the same directory as this .py file.
You can check that by using get_cwd() below.
You can save results to a new file. Every new launch will overwrite the file. 
'''


def get_cwd():
    print(os.getcwd())


def get_videos_from_html_playlist(file='playlista.html', version="short", save_to_file=False):

    # In the html file you should rather find only shorter version of address, but just in case
    if version.lower() == "short":
        youtube_short_link = re.compile(r'(/watch\?v\=.{11})')
    elif version.lower() == "long":
        youtube_full_link = re.compile(r'href=\"https://www.(youtube.com/watch\?v\=.{11})')

    f = open(file, 'r', 3, encoding="utf8")
    content = f.read()
    matches = str(BeautifulSoup(content, 'html.parser'))
    f.close()

    results = None
    repetitions = 0

    if version.lower() == "short":
        results_short = youtube_short_link.findall(matches)
        results = results_short
    elif version.lower() == "long":
        results_full = youtube_full_link.findall(matches)
        results = results_full

    # In the html file you can find duplicated data. We can modify the regex or just remove every
    # second result if it's the same as the previous one
    for x, result in enumerate(results):
        try:
            if results[x] == results[x - 1]:
                repetitions += 1
                results.remove(results[x])
        except IndexError:
            print("Error")

    # printing full link
    how_much = len(results)
    for result in results:
        if version.lower() == "short":
            result = "youtube.com" + result
        elif version.lower() == "long":
            pass
        print(result)

    print("Videos found: ", how_much)

    # saving each link on a new line
    if save_to_file:
        to_save = "video_links.txt"
        f = open(to_save, 'w')
        for result in results:
            if version.lower() == "short":
                f.write("youtube.com" + result + "\n")
            elif version.lower() == "long":
                f.write(result+"\n")
        f.close()


# get_cwd()
get_videos_from_html_playlist('playlista.html', "short", True)

