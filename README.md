# Spotify_CV_Control
This repositiory controls a spotify player use web API and uses Computer Vision to control player via Hand gestures.

This is a python script built with Flask.
Install dependencies : 
Win: python.exe -m pip install -r requirments.txt
Linux: python3 -m pip install -r requirements.txt
Run Server by running the Spotify_integration.py file

Part of the code uses the dotenv to get hidden information such as the the client_id and client_secret so make a .env file with CLIENT_ID, CLIENT_SECRET or replace values in code.
There are a few issues with the volume control but it's a permission issue with spotify.

*Note volume control doesn't seem to work on Android Samsung Galaxy s22 ultra not sure why but all gestures work for web player for spotify

When using available devices for gesture control change device select correct device from available devices or the gesture code won't call api.

# Gestures:
## Right hand:
Index and middle finger up with other fingers down:

Swipe right - next song

Swipe left - previous song

open hand:
Volume control 0-100 depending on hand height (* no depth estimation yet so decent control for now)

# Left Hand:

Open Hand: Play

Closed Hand: Stop
 
