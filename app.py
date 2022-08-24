'''
    This code was based on these repositories,
    so special thanks to:
        https://github.com/datademofun/spotify-flask
        https://github.com/drshrey/spotify-flask-auth-example
        https://github.com/mari-linhares/spotify-flask

'''

from flask import Flask, request, redirect, g, render_template, session
from spotify_requests import spotify
from ultimate_playlist import CreatePlaylist
from data import mongo, users
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = 'some key for session'
# app.config["MONGODB_DB"] = 'app12345678'

# ----------------------- AUTH API PROCEDURE -------------------------
ult_playlist = CreatePlaylist()
ctr = [2]
user_ids = []
# url = 'http://127.0.0.1:8081/'
url = "http://spotify-ultimate-playlist.herokuapp.com/"
user1_db = 0
playlist_id = 0

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/auth1")
def auth1():
    return redirect(spotify.AUTH_URL1)

@app.route("/auth2")
def auth2():
    print(spotify.AUTH_URL2)
    return redirect(spotify.AUTH_URL2)

def valid_token(resp):
    return resp is not None and not 'error' in resp


@app.route("/callback")
def callback():
    auth_token = request.args['code']
    token, auth_header = spotify.authorize(auth_token,0)
    session['auth_header'] = auth_header

    user = spotify.get_users_profile_auth(auth_header)
    userid = mongo.store_user_auth(user['id'], user['display_name'], token, auth_header)
    user1 = {'id': userid}
    share_link = url + 'share?' + urlencode(user1)

    return render_template('first_auth.html', link=share_link)

@app.route("/callback2")
def callback2():
    print('CALLBACK2')
    auth_token = request.args['code']
    print('STATE')
    global user1_db
    user1_db=request.args['state']
    print(request.args['state'])
    token, auth_header = spotify.authorize(auth_token,1)
    session['auth_header'] = auth_header
    print('HERE1')
    user = spotify.get_users_profile_auth(auth_header)

    global playlist_id
    playlist_id = spotify.create_playlist(user['id'], token)
    print('HERE2')
    try:
        ult_playlist.make_playlist_collaborative(token, playlist_id, user['id'])
    except:
        return 'something went wrong, try again!'
    return create_playlist(token, auth_header)

def create_playlist(token2, header2):
    global user1_db
    user1 = users.User.objects(id=user1_db).first()
    spotify.set_auth(user1.header, header2, user1.token, token2)
    
    for i in range(ctr[0]):
        # get profile data
        profile_data = spotify.get_users_profile(i)

        # get user playlist data
        playlist_data = spotify.get_users_playlists(i)
        user_id = profile_data['id']
        user_ids.append(user_id)
        print('PLAYLIST')
        for play in playlist_data['items']:
            if play['owner']['id'] == user_id:
                print(play['name'])
                if(i == 0):
                    ult_playlist.add_tracks(
                        spotify.get_playlist_tracks(play['id'], i))
                else:
                    ult_playlist.add_tracks2(
                        spotify.get_playlist_tracks(play['id'], i))

        if(i == 0):
            ult_playlist.add_tracks(spotify.get_user_tracks(user_id, i))
        else:
            ult_playlist.add_tracks2(spotify.get_user_tracks(user_id, i))

    global playlist_id
    ult_playlist.add_song(playlist_id, token2)
    spotify.follow_playlist(playlist_id, user1.header)
    return render_template('finish.html')


@app.route("/share")
def share():
    global user1_db
    user1_db = request.args.get('id')
    user1 = users.User.objects(id=user1_db).first()
    print('SET STATE')
    print(user1_db)
    spotify.set_state(user1_db)
    print(spotify.STATE)
    return render_template('second_auth.html', display_name = user1.username)


if __name__ == "__main__":
    app.run(debug=True, port=spotify.PORT)
