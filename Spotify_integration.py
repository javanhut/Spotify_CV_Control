import base64
import os
import requests
from flask import Flask, redirect, request, url_for, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from dotenv import load_dotenv
from Gesture_Control import GestureControl
from custom_exception import (TokenInfoNotFound, SessionDataNotFound)
from functools import partial

load_dotenv()
app = Flask(__name__)
app.config["SESSION_COOKIE_NAME"] = "spotify control cookie"
app.secret_key = "sfnuvniwnoido5793402uj&*%^TGT&"
scope = "user-modify-playback-state user-read-playback-state app-remote-control user-read-currently-playing streaming"
TOKEN_INFO = "token_info"
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')

@app.route('/')
def login():
    spotify_oauth = create_spotify_oauth()
    auth_url = spotify_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect_page')
def redirect_page():
    spotify_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = spotify_oauth.get_access_token(code=code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for("run_gesture_control", _external=True))


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise (TokenInfoNotFound("Could retrieve token data."))
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info


@app.route('/app_run')
def run_gesture_control():
    try:
        token_info = get_token()
    except TokenInfoNotFound:
        print("User info not found")
        redirect(url_for('login', _external=False))
    token = token_info['access_token']
    spotify_oauth = create_spotify_oauth()
    sp = spotipy.Spotify(auth_manager=spotify_oauth, auth=token)
    gesture_action_callback = partial(gesture_action_handler, token=token)
    gc = GestureControl(gesture_callback=gesture_action_callback)
    gc.run_hands(token=token)
    return "Run gesture control App"


def set_spotify_volume(access_token, volume_percent, device_id=None):
    """
    Set the volume for the user's current playback device.

    Parameters:
    - access_token (str): Spotify OAuth access token.
    - volume_percent (int): Volume level to set (0-100).
    - device_id (str, optional): The id of the device this command is targeting. If not supplied, the user's currently active device is the target.
    """
    # Endpoint for setting volume
    endpoint = "https://api.spotify.com/v1/me/player/volume"

    # Parameters
    params = {
        "volume_percent": volume_percent,
    }
    if device_id:
        params["device_id"] = device_id

    # Headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {"grant_type": "client_credentials"}

    # Sending the PUT request to Spotify
    response = requests.put(endpoint,data=data, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 204:
        print("Volume set successfully.")
    else:
        print(f"Failed to set volume. Status code: {response.status_code}, Message: {response.text}")


def create_spotify_oauth():
    return SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                        redirect_uri=url_for('redirect_page', _external=True), scope=scope)
def gesture_action_handler(
        gesture: str,
        hand: dict,
        finger_array: list,
        token: str,
        volume_level: int = None,
        enable_info: bool = False,
) -> None:
    spotify_oauth = create_spotify_oauth()
    sp = spotipy.Spotify(auth=token)
    devices = sp.devices()
    device_id = devices["devices"][1]["id"]
    if gesture == "Swipe Right":
        sp.next_track(device_id=device_id)
    elif gesture == "Swipe Left":
        sp.previous_track(device_id=device_id)
    elif gesture == "Stop":
        sp.pause_playback(device_id=device_id)
    elif gesture == "Play":
        sp.start_playback(device_id=device_id)
    elif volume_level is not None:
        # set_spotify_volume(access_token=token, volume_percent=int(volume_level), device_id=device_id)
        sp.volume(volume_percent=int(volume_level), device_id=device_id)

if __name__ == "__main__":
    app.run(debug=True)
    print(client_id)
    print(client_secret)