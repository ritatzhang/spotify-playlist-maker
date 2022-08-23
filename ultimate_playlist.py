# put all of user's songs from their playlists + liked songs
# into a list
# use track uri to add to playlist
import json
import os
import requests
import math

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

#sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


class CreatePlaylist:
    # user 1, we will create the playlist under this account
    def __init__(self):
        self.all_songs = set()
        self.other_all_songs = set()
        self.union_songs = set()

    def add_tracks(self, results):
        for item in results['items']:
            track = item['track']
            # print(track['name'])
            self.all_songs.add(track['uri'])

    def add_tracks2(self, results):
        for item in results['items']:
            track = item['track']
            self.other_all_songs.add(track['uri'])

    def make_playlist_collaborative(self, spotify_token, playlist_id, user_id):
        sp = spotipy.Spotify(spotify_token)
        sp.user_playlist_change_details(
            user_id, playlist_id, collaborative=True)

    def get_union(self):  # i got confused so union actually means intersection
        self.union_songs = self.all_songs.intersection(self.other_all_songs)

    def add_song(self, playlist_id, spotify_token):

        self.get_union()
        print(len(self.all_songs))
        print(len(self.other_all_songs))
        print(len(self.union_songs))
        # for song in self.union_songs:
        #     print(song)

        # spotify does not let you add >100 songs to a playlist per iteration
        union = []
        a = []
        count = 0
        for elem in iter(self.union_songs):
            if(count != 0 and count % 100 == 0):
                union.append(a)
                a = []
            a.append(elem)
            count += 1
        union.append(a)

        # had to do this cuz spotify only lets you add 100 songs at a time
        for songs in union:
            request_data = json.dumps(songs)
            query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
                playlist_id)
            print(request_data)
            response = requests.post(
                query,
                data=request_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotify_token)
                }
            )
