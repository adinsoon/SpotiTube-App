from section_youtube import *
from section_spotify import *


youtube = Youtube()
spotitube = Spotify()
listed = youtube.get_videos_from_liked()
playlist = spotitube.create_playlist()
spotitube.search_spotify_songs_from_list(listed, playlist)


