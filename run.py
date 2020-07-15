from googleapiclient.discovery import build
import json
from secret import api_key
import pprint

# google api for python https://github.com/googleapis/google-api-python-client
# api key taken from https://console.developers.google.com/

# remember to keep your api key safe
# it's good practice to store it in a separate file (like me for example here in the 'secret')
# and not pushing it to your repo

youtube = build('youtube', 'v3', developerKey=api_key)


def get_channel_id_from_username(username='google'):
    request = youtube.channels().list(
        part='statistics',
        forUsername=username
    )
    response = request.execute()
    response = response['items'][0]['id']
    return response


def get_stats_from_channel_username(username='google'):
    request = youtube.channels().list(
        part='statistics',
        forUsername=username
    )
    response = request.execute()
    response = response['items'][0]['statistics']
    json_response = json.dumps(response, indent=2)
    return json_response


def get_playlists_from_channel_id(channel_id='UCK8sQmJBp8GCxrOtXWBpyEA'):
    # show public playlists made by selected channel id
    # due to lot of unnecessary data, function returns playlist's id and title in a list
    request = youtube.playlists().list(
        part='contentDetails, snippet',
        channelId=channel_id,
        maxResults=50
    )
    playlists = []
    response = request.execute()
    for playlist in response['items']:
        playlist_id = playlist.get('id')
        playlist_title = playlist.get('snippet')
        playlists.append({'id': playlist_id, 'title': playlist_title['title']})
    # for better visibility of returned elements, please write as following:
    #
    # for item in get_playlists_from_channel_id():
    #   print("ID:", item.get('id'), "\t\tTITLE:", item.get('title'))
    return playlists


def get_content_of_playlist(playlist_id='PL590L5WQmH8eZnQfjoF91OImPfrmv-Vds'):
    # show content of the given playlist
    # note that only public videos from the public playlist will be shown
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50
    )
    videos = []
    response = request.execute()
    for video in response['items']:
        video_id = str(video['snippet']['resourceId']['videoId'])
        title = str(video['snippet']['title'])
        description = str(video['snippet']['description']).replace("\n", " ")
        videos.append({'id': video_id, 'title': title, 'desc': description})
    # for better visibility of returned elements, please write as following:
    #
    # for videos in get_content_of_playlist():
    #   print("ID:", videos.get('id'), "\tTITLE:", videos.get('title'), "\nDESC:", videos.get('desc'))
    return videos


for videos in get_content_of_playlist():
    print("ID:", videos.get('id'), "\tTITLE:", videos.get('title'), "\nDESC:", videos.get('desc'), '\n', "-"*50)
