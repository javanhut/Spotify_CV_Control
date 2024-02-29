from setuptools import setup, find_packages

require = ['flask', 'spotipy', 'dotenv', 'functools', 'cv2', 'cvzone', 'mediapipe', 'black']

setup(name="Spotify Gesture Control", version="0.0.1",
      description='This app uses spotify api and opencv to control user player', author="Javan Hutchinson",
      author_email="javan.hutchinson18@gmail.com", keywords="web spotify flask", packages=find_packages(),
      include_package_data=True, requires=require)
