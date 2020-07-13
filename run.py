from googleapiclient.discovery import build
import json
from secret import api_key

# google api for python https://github.com/googleapis/google-api-python-client
# api key taken from https://console.developers.google.com/

# remember to keep your api key safe
# it's good practice to store it in a separate file (like me for example here in the 'secret')
# and not pushing it to your repo

youtube = build('youtube', 'v3', developerKey=api_key)


def get_stats_from_channel(username='google'):
    request = youtube.channels().list(
        part='statistics',
        forUsername=username
    )
    response = request.execute()
    response = response['items'][0]['statistics']
    json_response = json.dumps(response, indent=4)
    return json_response


print(get_stats_from_channel('twitter'))


