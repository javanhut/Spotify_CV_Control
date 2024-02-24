# Spotify_CV_Control
This repositiory controls a spotify player use web API and uses Computer Vision to control player via Hand gestures.

This is a python script built with Flask.
Install dependencies : 
Win: python.exe -m pip install -r requirments.txt
Linux: python3 -m pip install -r requirements.txt
Run Server by running the Spotify_integration.py file

Part of the code uses the dotenv to get hidden information such as the the client_id and client_secret so make a .env file with CLIENT_ID, CLIENT_SECRET or replace values in code.
There are a few issues with the volume control but it's a permission issue with spotify.
