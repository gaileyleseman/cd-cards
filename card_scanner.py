import spotipy
from spotipy.oauth2 import SpotifyOAuth

import config as cfg

CLIENT_ID = cfg.spotify["CLIENT_ID"]
CLIENT_SECRET = cfg.spotify["CLIENT_SECRET"]
SPEAKER_NAME = cfg.spotify["SPEAKER_NAME"]

scope = "user-read-playback-state,user-modify-playback-state"
spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=scope,
                                            redirect_uri="http://google.com/"))


# Search for Album
artist = input("Artist: ")
album = input("Album: ")
query = "artist:" + artist + ", album:" + album
results = spotify.search(q=query, type='album')
uri = results["albums"]["items"][0]['uri']
cover_art_url = results["albums"]["items"][0]['images'][0]['url']

# Play on Speakers
for device in spotify.devices()['devices']:
    if device['name'] == SPEAKER_NAME:
        speaker_id = device['id']
spotify.start_playback(context_uri=uri, device_id=speaker_id)
spotify.volume(4)
