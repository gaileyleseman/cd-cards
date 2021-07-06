import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import numpy as np
import cv2
import qrcode
import config as cfg


CLIENT_ID = cfg.spotify["CLIENT_ID"]
CLIENT_SECRET = cfg.spotify["CLIENT_SECRET"]
SPEAKER_NAME = cfg.spotify["SPEAKER_NAME"]

scope = "user-read-playback-state,user-modify-playback-state"
spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=scope,
                                            redirect_uri="http://google.com/"))


df = pd.read_pickle("./data.pkl")
df = df[["reference", "album_uri", "color"]]  # remove unnecessary columns
data = df.set_index("reference").T.to_dict()  # save info in dictionary

def read_qr():
    camera = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    while True:
        success, img = camera.read()
        decodedText, points, _ = detector.detectAndDecode(img)
        if decodedText:
            print(decodedText)
            break
    camera.release()


# Search for Album
album_ref = "joni_mitchell-blue"

if __name__ == '__main__':
    uri = data[album_ref]["album_uri"]
    color = data[album_ref]["color"]

    q = input("wait for it...")
    print("starting qr-reader")
    read_qr()

    # Play on Speakers
    for device in spotify.devices()['devices']:
        if device['name'] == SPEAKER_NAME:
            speaker_id = device['id']
    spotify.start_playback(context_uri=uri, device_id=speaker_id)
    spotify.volume(4)

