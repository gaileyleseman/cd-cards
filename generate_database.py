import numpy as np
import os
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
import requests
import qrcode
from PIL import Image
from scripts.spotify_background_color import SpotifyBackgroundColor
import config as cfg

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
        print("No results found for: " + artist, album)
        artist = album = album_uri = cover_url = np.nan  # store as NaN for filtering
    return [artist, album, album_uri, cover_url]


def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=1)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill='black', back_color='white')


def save_images(reference, cover_url):
    covers_path = "./images/covers/" + reference + ".png"
    qr_path = "./images/qr/" + reference + "--qr.png"
    if not os.path.isfile(covers_path):
        img = requests.get(cover_url)
        with open(covers_path, "wb") as cover:
            cover.write(img.content)
    if not os.path.isfile(qr_path):
        qr = generate_qr(reference)
        qr.save(qr_path)


def get_background_color(reference):
    background_path = "./images/background/" + reference + ".png"
    if not os.path.isfile(background_path):
        print("Determining background color for " + reference)
        cover = np.array(Image.open("./images/covers/" + reference + ".png"))
        bgc = SpotifyBackgroundColor(img=cover)
        color = bgc.best_color(8)
        img = Image.new('RGB', (300, 200), color)
        img.save(background_path, "PNG")
    else:
        img = Image.open(background_path)
        color = img.getpixel((0, 0))
    return [i for i in color]  # save as a list for future use


if __name__ == '__main__':
    # read input data, remove trailing spaces
    df = pd.read_csv("./input.csv", converters={'q_artist': str.strip,
                                                'q_album': str.strip})

    # get data via Spotify API
    spotify_cols = ["artist", "album", "album_uri", "cover_url"]
    df[["artist", "album", "album_uri", "cover_url"]] = \
        df.apply(lambda x: get_spotify_context(x["q_artist"], x["q_album"], spotify), axis=1, result_type='expand')

    # save failed searches for manual correction
    df_failed = df[df.isna().any(axis=1)]
    df_failed.drop(spotify_cols, axis=1)
    df_failed.to_csv("failed_input.csv")
    df = df.dropna()

    # save cover art and generate QR code
    df["reference"] = df.apply(lambda x: (x["artist"] + "-" + x["album"]).replace(" ", "_").lower(), axis=1)
    df.apply(lambda x: save_images(x["reference"], x["cover_url"]), axis=1)

    # determine background color
    df["color"] = df.apply(lambda x: get_background_color(x["reference"]), axis=1)

    # save dataframe
    df.to_pickle("./data.pkl")


