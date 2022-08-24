from __future__ import print_function
import base64
import json
import requests
import sys

# Workaround to support both python 2 & 3
try:
    import urllib.request
    import urllib.error
    import urllib.parse as urllibparse
except ImportError:
    import urllib as urllibparse


# ----------------- 0. SPOTIFY BASE URL ----------------

SPOTIFY_API_BASE_URL = 'https://api.spotify.com'
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# ----------------- 1. USER AUTHORIZATION ----------------

# spotify endpoints
SPOTIFY_AUTH_BASE_URL = "https://accounts.spotify.com/{}"
SPOTIFY_AUTH_URL = SPOTIFY_AUTH_BASE_URL.format('authorize')
SPOTIFY_TOKEN_URL = SPOTIFY_AUTH_BASE_URL.format('api/token')

# client keys
CLIENT = json.load(open('conf.json', 'r+'))
CLIENT_ID = CLIENT['id']
CLIENT_SECRET = CLIENT['secret']

# server side parameter
# * feel free to change it if you want to, but make sure to change in your spotify dev account as well *
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8081
# REDIRECT_URI = ["{}:{}/callback".format(CLIENT_SIDE_URL, PORT),"{}:{}/callback2".format(CLIENT_SIDE_URL, PORT)]
REDIRECT_URI = ["http://spotify-ultimate-playlist.herokuapp.com/callback", "http://spotify-ultimate-playlist.herokuapp.com/callback2"]
SCOPE = "playlist-modify-public playlist-modify-private user-read-private user-library-read playlist-read-private user-library-modify playlist-read-collaborative user-follow-modify"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

# https://developer.spotify.com/web-api/authorization-guide/
auth_query_parameters1 = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI[0],
    "scope": SCOPE,
    "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID,
    "state": STATE
}

auth_query_parameters2 = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI[1],
    "scope": SCOPE,
    "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID,
    "state": STATE
}

URL_ARGS1 = "&".join(["{}={}".format(key, urllibparse.quote(val))
                         for key, val in list(auth_query_parameters1.items())])
AUTH_URL1 = "{}/?{}".format(SPOTIFY_AUTH_URL, URL_ARGS1)

URL_ARGS2 = "&".join(["{}={}".format(key, urllibparse.quote(val))
                         for key, val in list(auth_query_parameters2.items())])
AUTH_URL2 = "{}/?{}".format(SPOTIFY_AUTH_URL, URL_ARGS2)

'''
    This function must be used with the callback method present in the
    ../app.py file.

    And of course this will only works if ouath == True

'''
ACCESS_TOKEN = []
AUTH_HEAD = []

def set_state(state):
    global STATE
    STATE = state


def authorize(auth_token, x):

    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI[x]
    }

    # python 3 or above
    if sys.version_info[0] >= 3:
        base64encoded = base64.b64encode(
            ("{}:{}".format(CLIENT_ID, CLIENT_SECRET)).encode())
        headers = {"Authorization": "Basic {}".format(base64encoded.decode())}
    else:
        base64encoded = base64.b64encode(
            "{}:{}".format(CLIENT_ID, CLIENT_SECRET))
        headers = {"Authorization": "Basic {}".format(base64encoded)}

    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload,
                                 headers=headers)

    # tokens are returned to the app
    response_data = json.loads(post_request.text)
    token = response_data["access_token"]
    
    # use the access token to access Spotify API
    auth_header = {"Authorization": "Bearer {}".format(token)}
    # print("AUTH")
    # print(response_data)
    return token, auth_header


# ------------------ USER RELATED REQUESTS  ---------- #

# spotify endpoints
USER_PROFILE_ENDPOINT = "{}/{}".format(SPOTIFY_API_URL, 'me')
USER_PLAYLISTS_ENDPOINT = "{}/{}".format(USER_PROFILE_ENDPOINT, 'playlists')
GET_PLAYLISTS_ENDPOINT = "{}/{}".format(SPOTIFY_API_URL, 'playlists')

# https://developer.spotify.com/web-api/get-a-list-of-current-users-playlists/

def set_auth(auth_head_1, auth_head_2, token1, token2):
    AUTH_HEAD.append(auth_head_1)
    AUTH_HEAD.append(auth_head_2)
    ACCESS_TOKEN.append(token1)
    ACCESS_TOKEN.append(token2)


def get_users_playlists(x):
    auth_header = AUTH_HEAD[x]
    url = USER_PLAYLISTS_ENDPOINT
    resp = requests.get(url + "?limit=50", headers=auth_header)
    return resp.json()


def get_playlist_tracks(playlist_id, x):
    auth_header = AUTH_HEAD[x]
    url = "{}/{id}/tracks".format(GET_PLAYLISTS_ENDPOINT, id=playlist_id)
    resp = requests.get(url, headers=auth_header)
    return resp.json()

# ------------------ 6. USERS ---------------------------
# https://developer.spotify.com/web-api/user-profile-endpoints/


GET_USER_ENDPOINT = '{}/{}'.format(SPOTIFY_API_URL, 'me')


def get_users_profile(x):
    auth_header = AUTH_HEAD[x]
    url = USER_PROFILE_ENDPOINT
    resp = requests.get(url, headers=auth_header)
    return resp.json()

def get_users_profile_auth(auth_header):
    url = USER_PROFILE_ENDPOINT
    resp = requests.get(url, headers=auth_header)
    return resp.json()

def get_user_tracks(user_id, x):
    auth_header = AUTH_HEAD[x]
    url = "{}/{id}".format(GET_USER_ENDPOINT, id='tracks')
    resp = requests.get(url, headers=auth_header)
    return resp.json()


POST_PLAYLIST_URL = '{}/{}'.format(SPOTIFY_API_URL, 'users')


def create_playlist(user_id):
    #auth_header = AUTH_HEAD[0]
    request_body = json.dumps({
        "name": "your ultimate playlist!!",
        "description": "all of your shared favorite songs!",
        "public": False
    })

    query = "https://api.spotify.com/v1/users/{}/playlists".format(user_id)

    response = requests.post(
        query,
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(ACCESS_TOKEN[0])
        }
    )
    response_json = response.json()
    playlist_id = response_json["id"]
    return playlist_id

def create_playlist(user_id, token):
    request_body = json.dumps({
        "name": "your new playlist!!",
        "description": "all of your shared favorite songs!",
        "public": False
    })

    query = "https://api.spotify.com/v1/users/{}/playlists".format(user_id)

    response = requests.post(
        query,
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token)
        }
    )
    response_json = response.json()
    playlist_id = response_json["id"]

    return playlist_id


def get_auth_token():
    return AUTH_HEAD[0]


def follow_playlist(playlist_id, auth_header):
    url = "{}/{id}/followers".format(GET_PLAYLISTS_ENDPOINT, id=playlist_id)
    requests.put(url, headers=auth_header)
    return 'good'
