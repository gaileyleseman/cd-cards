import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import numpy as np
import cv2
import qrcode
from homeassistant_api import Client
import config as cfg

# get credentials from config
CLIENT_ID = cfg.spotify["CLIENT_ID"]
CLIENT_SECRET = cfg.spotify["CLIENT_SECRET"]
SPEAKER_NAME = cfg.spotify["SPEAKER_NAME"]
url = cfg.homeassistant["url"]
TOKEN = cfg.homeassistant["TOKEN"]
entity = cfg.homeassistant["entity"]

# set up services
scope = "user-read-playback-state,user-modify-playback-state"
spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=scope,
                                            redirect_uri="http://google.com/"))
homeassistant = Client(url, TOKEN).get_services()

# import data
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
            return decodedText
            break
    camera.release()


def play_album(uri):
    for device in spotify.devices()['devices']:
        if device['name'] == SPEAKER_NAME:
            speaker_id = device['id']
    spotify.start_playback(context_uri=uri, device_id=speaker_id)
    print("Now playing: " + album_ref)
    spotify.volume(4)


def change_lights(color, transition=2, brightness=255):
    homeassistant.light.services.turn_on.trigger(entity_id=entity,
                                                 transition=str(transition),
                                                 brightness=str(brightness),
                                                 rgb_color=color)


if __name__ == '__main__':
    while True:
        q = input("Enter 'q' to start QR Scanner: ")

        if q == "q":
            print("starting qr-reader")
            album_ref = read_qr()

            uri = data[album_ref]["album_uri"]
            color = data[album_ref]["color"]

            play_album(uri)  # play on album on speakers
            change_lights(color)  # change hue lights to album color
        else:
            break
