import numpy as np
import os
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
import requests
import config as cfg

df = pd.read_csv("./input.csv")
# TODO: lower caps
# TODO: remove trailing spaces

CLIENT_ID = cfg.spotify["CLIENT_ID"]
CLIENT_SECRET = cfg.spotify["CLIENT_SECRET"]

scope = "user-read-playback-state,user-modify-playback-state"
spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=scope,
                                            redirect_uri="http://google.com/"))


def get_spotify_context(artist, album, spotify):
    query = "artist:" + artist + ", album:" + album
    results = spotify.search(q=query, type='album')
    try:
        result = results["albums"]["items"][0]
        artist = result['artists'][0]['name']  # get official artist name
        album = re.sub(" [\(\[].*?[\)\]]", "", result["name"])  # official album name, remove info between brackets
        album_uri = result['uri']
        cover_url = result['images'][0]['url']
    except IndexError:
        artist = album = album_uri = cover_url = None  # store as None for filtering
    return [artist, album, album_uri, cover_url]

def save_images(filename, cover_url):
    covers = "./images/covers/" + filename + ".png"
    qr_path = "./images/qr"
    if not os.path.isfile(covers):
        img = requests.get(cover_url)
        with open(covers, "wb") as cover:
            cover.write(img.content)


df[["artist", "album", "album_uri", "cover_url"]] = \
    df.apply(lambda x: get_spotify_context(x["q_artist"], x["q_album"], spotify), axis=1, result_type='expand')

df = df.dropna()
df["filename"] = df.apply(lambda x: (x["artist"] + "-" + x["album"]).replace(" ", "_").lower(), axis=1)

df.apply(lambda x: save_images(x["filename"], x["cover_url"]), axis=1)
