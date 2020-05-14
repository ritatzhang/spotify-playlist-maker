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

app = Flask(__name__)
app.secret_key = 'some key for session'

# ----------------------- AUTH API PROCEDURE -------------------------
ult_playlist = CreatePlaylist()
ctr = [0]
users = []


@app.route("/auth")
def auth():
    return redirect(spotify.AUTH_URL)


@app.route("/callback/")
def callback():

    auth_token = request.args['code']
    auth_header = spotify.authorize(auth_token)
    session['auth_header'] = auth_header

    return profile()


def valid_token(resp):
    return resp is not None and not 'error' in resp

# -------------------------- API REQUESTS ----------------------------


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/profile')
def profile():

    if 'auth_header' in session:

        # auth_header = session['auth_header']
        # get profile data
        profile_data = spotify.get_users_profile(ctr[0])

        # get user playlist data
        playlist_data = spotify.get_users_playlists(ctr[0])

        user_id = profile_data['id']
        # user_id = profile_data.id
        users.append(user_id)
        for play in playlist_data['items']:
            if(ctr[0] == 0):
                ult_playlist.add_tracks(
                    spotify.get_playlist_tracks(play['id'], ctr[0]))
            else:
                ult_playlist.add_tracks2(
                    spotify.get_playlist_tracks(play['id'], ctr[0]))

        if(ctr[0] == 0):
            ult_playlist.add_tracks(spotify.get_user_tracks(user_id, ctr[0]))
        else:
            ult_playlist.add_tracks2(spotify.get_user_tracks(user_id, ctr[0]))

        ctr[0] = ctr[0]+1
    if ctr[0] == 1:
        return render_template('first_auth.html')
    elif ctr[0] == 2:
        return render_template('second_auth.html')

    return render_template('index.html')


@app.route('/create_playlist')
def create_playlist():
    if len(users) != 2:
        return 'bad! authorizations incomplete, go back and try again'

    if 'auth_header' in session:

        playlist_id = spotify.create_playlist(users[0])
        auth_token = spotify.get_auth_token()
        ult_playlist.add_song(playlist_id, auth_token)
        ult_playlist.make_playlist_collaborative(
            auth_token, playlist_id, users[0])
        spotify.follow_playlist(playlist_id)
        # if valid_token(hot):
        # return render_template('featured_playlists.html', hot=hot)

    return render_template('finish.html')


if __name__ == "__main__":
    app.run(debug=True, port=spotify.PORT)
