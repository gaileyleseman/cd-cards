import numpy as np
import os
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
import requests
import qrcode
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

def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img

def save_images(filename, cover_url):
    covers_path = "./images/covers/" + filename + ".png"
    qr_path = "./images/qr/" + filename + "--qr.png"
    if not os.path.isfile(covers_path):
        img = requests.get(cover_url)
        with open(covers_path, "wb") as cover:
            cover.write(img.content)
    if not os.path.isfile(qr_path):
        qr = generate_qr(filename)
        qr.save(qr_path)



df[["artist", "album", "album_uri", "cover_url"]] = \
    df.apply(lambda x: get_spotify_context(x["q_artist"], x["q_album"], spotify), axis=1, result_type='expand')

df = df.dropna()
df["filename"] = df.apply(lambda x: (x["artist"] + "-" + x["album"]).replace(" ", "_").lower(), axis=1)

df.apply(lambda x: save_images(x["filename"], x["cover_url"]), axis=1)
