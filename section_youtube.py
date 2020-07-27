import youtube_dl
from youtube_dl.utils import ExtractorError, DownloadError
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import json
import logging

logging.basicConfig(level=logging.ERROR, format='%(message)s')

# *********************************************************
# https://console.cloud.google.com/apis/credentials/consent
# select the Create credentials button, then select OAuth client ID. It may take some time to be verified by Google
# Select Other, then select the Create button. Select the OK button after the success dialogue appears.
# Download the credentials by selecting the Download JSON button for the client ID.
# Save the credentials file to client_secrets.json. This file must be distributed with your application.
client_secret = "client_secret.json"


class Youtube:

    def __init__(self):
        self.youtube_client_auth()
        self.client: googleapiclient.discovery.build

        self.videos_listing = []
        self.videos_urls = []

    def youtube_client_auth(self):
        api_service_name = "youtube"
        api_version = "v3"

        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secret, scopes)

        # Set up a Flow object to be used if needed to authenticate.
        credentials = flow.run_console()

        # Construct a service object via the discovery service.
        self.client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

    def get_videos_from_liked(self, save_to_file=False):
        """
        :param save_to_file: boolean
        """
        # using youtube_client_login() before using is required
        # please make sure that you didn't like any ultra-super-long video like youtube radio transmission,
        # it causes an error

        next_page_token = None
        video = None
        index = 0

        print("This will cover all liked videos.")
        print("Loading data. Please wait... ")
        while True:
            request = self.client.videos().list(
                part='snippet,contentDetails,statistics',
                myRating='like',
                maxResults='50',
                pageToken=next_page_token
            )
            response = request.execute()

            for content in enumerate(response['items']):
                title = content[1]['snippet']['title']
                # when yt_url = 'youtube.com/watch?v={}'.format(content['id']) then
                # WARNING: The url doesn't specify the protocol, trying with http
                # so it's better to use full address
                yt_url = 'https://www.youtube.com/watch?v={}'.format(content[1]['id'])

                # It may take some time depending of the quantity of videos
                try:
                    video = youtube_dl.YoutubeDL({}).extract_info(yt_url, download=False)
                except ExtractorError:
                    logging.error("An error on the position {} occured: {}".format(content[0], ExtractorError))
                    logging.error("Could not save following data: {}".format(content[1]['snippet']['title']))
                    print()
                except DownloadError:
                    logging.error("An error on the position {} occured: {}".format(content[0], DownloadError))
                    logging.error("Could not save following data: {}".format(content[1]['snippet']['title']))
                    print()
                name = video["track"]
                author = video["artist"]
                uploader = video["uploader"]
                duration = video["duration"]
                listed = {"title": title, "uploader": uploader, "duration (in sec)": duration, "name": name,
                          "author": author}
                self.videos_listing.append(listed)
                self.videos_urls.append(yt_url)
                print("No. {} ".format(index), end="")
                index += 1
                print(listed)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        if save_to_file:

            to_save = "video_data.txt"
            f = open(to_save, 'w', errors='replace')
            print("Saving to video_data.txt")
            for element in enumerate(self.videos_listing):
                json.dump(element[1], f)
                f.write("\n")
                '''
                for line in open("video_data.txt", "r"):
                    sth = json.loads(line)
                    print(sth['title'])     <-- for example
                '''
            f.close()

            to_save = "video_links.txt"
            f = open(to_save, 'w')
            print("Saving to video_links.txt")
            for element in enumerate(self.videos_urls):
                line = str(element[1])
                f.write(line)
                f.write("\n")
            f.close()

        return self.videos_listing
