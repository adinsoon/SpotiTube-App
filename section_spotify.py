import json
import requests
import logging
import datetime
from urllib import parse
from secrets import spotify_client_id

logging.basicConfig(level=logging.ERROR, format='%(message)s')


# *********************************************************
# https://developer.spotify.com/dashboard/applications
# select the Create an app button, fill data in the fields and tick the boxes
# get the Client ID from your app
# https://developer.spotify.com/dashboard/applications/{your_client_id_here}
# Save the credentials file to secrets.py in variable named spotify_client_id.
# This file must be distributed with your application.


class Spotify:

    def __init__(self):
        self.parsed_auth_url = self.spotify_auth()
        self.access_token = self.parsed_auth_url[0][1]
        self.token_type = self.parsed_auth_url[1][1]
        self.expiration_time = self.parsed_auth_url[2][1]
        self.token_validity_start: datetime.datetime.time
        self.token_validity_end: datetime.datetime.now

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.access_token)}

        self.song_uris = []
        self.song_not_found = []
        self.user_profile = self.get_user_profile()
        self.user_display_name = self.user_profile['display_name']
        self.user_id = self.user_profile['id']

        self.playlists = []

    ########################################################################

    def spotify_auth(self):
        response = self.auth_request()
        print("Please visit this URL to authorize this application: {}".format(response.url))
        print("Enter the entire url of the google page that will be displayed to you after access grant: ", end='')
        url_token = input()
        url_parsed = parse.parse_qsl(parse.urlsplit(url_token).fragment)
        self.token_validity_start = datetime.datetime.now()
        self.token_validity_end = self.token_validity_start + datetime.timedelta(seconds=float(url_parsed[2][1]))
        self.get_current_time_token()
        return url_parsed

    def auth_request(self):
        # makes an authorization request
        query = "https://accounts.spotify.com/authorize"
        payload = {
            "client_id": spotify_client_id,
            "response_type": "token",
            "redirect_uri": "http://google.com/",
            "scope": "playlist-read-private%20playlist-modify-private%20playlist-modify-public%20 \
                             playlist-read-collaborative%20user-library-modify%20user-library-read"
        }
        response = requests.get(
            query,
            params=payload
        )
        return response

    def check_token_validity(self):
        # checks if the token is still valid by getting the response from the spotify server
        response = self.get_user_profile()
        try:
            if response["error"]["status"] == "401":
                return False
        except KeyError:
            return True

    def refresh_token(self):
        # receives a new token
        # the reason this is a way to get a new token is that it doesn't require base64 secret key
        if not self.check_token_validity():
            logging.error("It might be due to the token expiration.")
            parsed_auth_url = self.spotify_auth()
            self.access_token = parsed_auth_url[0][1]
            self.token_type = parsed_auth_url[1][1]
            self.expiration_time = parsed_auth_url[2][1]

    def get_user_profile(self):
        query = "https://api.spotify.com/v1/me"
        response = requests.get(
            query,
            headers=self.headers
        )
        response_json = response.json()
        return response_json

    ########################################################################

    def search_song_on_spotify(self, title, artist, number=-1, playlist=None):
        """
        :param title: title of song
        :param artist: author of song
        :param number: used to show indexing while searching songs (useful when this method is used in searching from
        playlist)
        :param playlist: if playlist is not None, add song to the passed playlist
        """
        # this method based on the title or title and artist tries to find song on spotify
        # if the song cannot be found, it asks user to find it himself
        # depending on the user's decision, the song can be added to the found songs (and to the given playlist)
        # or to the not found list
        index = ""
        if number != -1:
            index = "[" + str(number) + "]"
        ###################
        is_song_found_good = "asdf"
        find_song_by_yourself = "asdf"
        should_skip = "asdf"
        ask_if_skip = None
        is_unable_to_find = None
        first_search = None
        error_occur = None
        ###################

        # search song by title only
        print("#" * 100)
        print("{} Data of current song: ".format(index) + str(title) + " from: " + str(artist))
        query_title = "https://api.spotify.com/v1/search?q={}&type=track,artist".format(title)
        result = self.make_request_tracks(query_title)

        if bool(result) is False:
            # if it fails, search song by title and uploader's name
            logging.error("Unable to find given song by title. Trying with the uploader/artist data")
            query_title_author = "https://api.spotify.com/v1/search?q={}%20{}&type=track,artist".format(title,
                                                                                                        artist)
            result = self.make_request_tracks(query_title_author)

            if bool(result) is False:
                logging.error("Unable to find given video by title and uploader/artist.")
                is_unable_to_find = True

        if is_unable_to_find:
            if is_unable_to_find:
                # try to find it independently
                print("Do you want to find a song on your own? [y/n]")
                find_song_by_yourself = input()

        first_search = True
        while True:
            # song found
            if bool(result) is True:
                # clear string every time song is found
                is_song_found_good = "clear"
                try:
                    print("Did you mean {} by {} ? [y/n/skip]".format(result[0]['name'],
                                                                      result[0]['album']['artists'][0]['name']))
                    print("Link: " + str(result[0]["external_urls"]["spotify"]))
                except KeyError:
                    logging.error("An error: KeyError occurred. [song_found]")
                    error_occur = True
                    self.refresh_token()
                if not error_occur:
                    is_song_found_good = input()
                else:
                    is_song_found_good = "n"
                    error_occur = False
                if is_song_found_good.lower() == ("y" or "t"):
                    uri = result[0]['uri']
                    self.song_uris.append(uri)
                    if playlist is not None:
                        self.add_song_to_playlist(uri, playlist)
                    break
                if is_song_found_good.lower() == "skip":
                    self.song_not_found.append({"title": title, "artist": artist})
                    print("Video added to the \'unfounded\' dict. You can view this dict later.")
                    break
                else:
                    ask_if_skip = True

            if ask_if_skip:
                if not first_search:
                    print("Do you want to continue searching? [y/n]")
                    should_skip = input()
                first_search = False

            if should_skip.lower() != "n" and (
                    is_song_found_good.lower() == "n" or find_song_by_yourself.lower() == "y"):
                print("Write a phrase related to the song that can be most easily recognized by Spotify")
                print("Data of current song: " + str(title) + " from: " + str(artist))
                phrase = input()
                query = "https://api.spotify.com/v1/search?q={}&type=track,artist".format(phrase)
                result = self.make_request_tracks(query)
                ask_if_skip = False

            if bool(result) is False and find_song_by_yourself.lower() != 'n':
                print("Oops, unable to find given song again.")
                ask_if_skip = True

            if should_skip.lower() == "n" or find_song_by_yourself.lower() == "n":
                self.song_not_found.append({"title": title, "artist": artist})
                print("Video added to the \'unfounded\' dict. You can view this dict later.")
                break

    def search_spotify_songs_from_list(self, listing, playlist=None):
        """
        :param listing: a list of data imported from youtube playlist
        :param playlist: if playlist is not None, add song(s) to the passed playlist
        """
        # listed = {"title": title, "uploader": uploader, "duration (in sec)": duration, "name": name, "author": author}
        number = 0
        for element in listing:
            title = element["title"]
            uploader = element["uploader"]
            number += 1
            self.search_song_on_spotify(title, uploader, number, playlist)

        return self.song_uris

    ########################################################################

    def get_user_playlists(self):
        query = "https://api.spotify.com/v1/me/playlists"
        response = requests.get(
            query,
            headers=self.headers,
        )
        response_json = response.json()
        for playlist in response_json['items']:
            self.playlists.append({"name": playlist['name'], "id": playlist['id'],
                                   "total tracks": playlist['tracks']['total'], "description": playlist['description']})
        return response_json

    def create_playlist(self, name="default", description="Created by SpotiTube App"):
        """
        :param name: name of the playlist to be created
        :param description: description of the playlist to be created
        """
        if name == "default":
            name = datetime.datetime.today().strftime('%d/%m %H:%M') + " by SpotiTube App"
        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            self.user_id)
        request_data = json.dumps({
            "name": name,
            "description": description,
            "public": False
        })
        response = requests.post(
            query,
            data=request_data,
            headers=self.headers
        )
        response_json = response.json()
        print("Playlist {} created. ID: {}".format(name, response_json["id"]))
        return response_json["id"]

    def add_song_to_playlist(self, song_uri=None, playlist_id=None):
        """
        :param song_uri: uri of the song already found on spotify
        :param playlist_id: id of the playlist, if its None then create a new one and add to it
        """
        if playlist_id is None:
            playlist_id = self.create_playlist()
        if song_uri is None:
            request_data = json.dumps(song_uri)
        else:
            request_data = json.dumps([song_uri])
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id)
        response = requests.post(
            query,
            data=request_data,
            headers=self.headers
        )
        response_json = response.json()
        print("Song added to the playlist with ID: {}".format(playlist_id))
        return response_json

    ########################################################################

    def make_request_tracks(self, query):
        """
        :param query: q u e r y
        convenience method
        """
        response = requests.get(
            query,
            headers=self.headers
        )
        response_json = response.json()
        result = response_json
        try:
            result = response_json['tracks']['items']
        except KeyError:
            logging.error("An error occured. [make_request_track")
        return result

    def get_current_time_token(self):
        # it allows to view remaining time of the granted token
        remaining_time = self.token_validity_end - datetime.datetime.now()
        print("Token granted at: {} for one hour.".format(self.token_validity_start.strftime('%H:%M')))
        print("Token time remaining: {}".format(remaining_time))
