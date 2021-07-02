import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import config as cfg

df = pd.read_csv("./input.csv")
# TODO: lower caps
# TODO: remove trailing spaces


CLIENT_ID = cfg.spotify["CLIENT_ID"]
CLIENT_SECRET = cfg.spotify["CLIENT_SECRET"]
SPEAKER_NAME = cfg.spotify["SPEAKER_NAME"]

scope = "user-read-playback-state,user-modify-playback-state"
spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=scope,
                                            redirect_uri="http://google.com/"))

def get_spotify_context(artist, album, spotify):
    query = "artist:" + artist + ", album:" + album
    results = spotify.search(q=query, type='album')
    try:
        result = results["albums"]["items"][0]
        album_uri = result['uri']
        cover_url = result['images'][0]['url']
    except IndexError:
        album_uri = None
        cover_url = None
    return [album_uri, cover_url]


df[["album_uri", "cover_url"]] = df.apply(lambda x: get_spotify_context(x["artist"], x["album"], spotify),
                                          axis=1, result_type='expand')

