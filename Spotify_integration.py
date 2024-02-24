import os
from flask import Flask, redirect, request, url_for, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from dotenv import load_dotenv
from Gesture_Control import GestureControl
from functools import partial

load_dotenv()
app = Flask(__name__)
app.config["SESSION_COOKIE_NAME"] = "Gesture cookie"
app.secret_key = "sfnuvniwnoido5793402uj&*%^TGT&"
TOKEN_INFO = "token_info"
scope = "user-modify-playback-state user-read-playback-state app-remote-control user-read-currently-playing"


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=redirect(
            url_for("redirect_page", _external=False)
        ),  # Ensure this matches your Spotify app settings
        scope=scope,
    )


@app.route("/")
def login():
    spotify_oauth = create_spotify_oauth()
    auth_url = spotify_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/redirect_page")
def redirect_page():
    session.clear()
    spotify_oauth = create_spotify_oauth()
    code = request.args.get("code")
    token_info = spotify_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    session["expires_on"] = int(time.time()) + token_info["expires_in"]
    return redirect(url_for("oauth_function", _external=False))


@app.route("/auth_page")
def oauth_function():
    try:
        token_info = get_token()
        if not token_info:
            raise Exception("Failed to get token info")
    except Exception as e:
        print("Unauthorized User:", e)
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info["access_token"])
    token = token_info["access_token"]
    gesture_action_callback = partial(gesture_action_handler, enable_info=False)
    gc = GestureControl(gesture_callback=gesture_action_callback)
    gc.run_hands(token=token)
    return {"Access Token": token_info["access_token"]}


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        return redirect(url_for("login", _external=False))
    now = int(time.time())
    is_expired = session.get("expires_at", now) - now < 60
    if is_expired:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info["refresh_token"])
    return token_info


def gesture_action_handler(
    gesture: str,
    hand: dict,
    finger_array: list,
    token: str,
    volume_level: int = None,
    enable_info: bool = False,
) -> None:
    sp = spotipy.Spotify(auth=token)
    devices = sp.devices()
    device_id = devices["devices"][0]["id"]
    if gesture == "Swipe Right":
        sp.next_track(device_id=device_id)
    elif gesture == "Swipe Left":
        sp.previous_track(device_id=device_id)
    elif gesture == "Stop":
        sp.pause_playback(device_id=device_id)
    elif gesture == "Play":
        sp.start_playback(device_id=device_id)
    elif volume_level is not None:
        sp.volume(volume_percent=int(volume_level), device_id=device_id)


if __name__ == "__main__":
    app.run(debug=True)
    print(get_token())
