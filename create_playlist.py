# put all of user's songs from their playlists + liked songs
# into a list
# use track uri to add to playlist
import json
import os
import requests
import math
from secrets import spotify_token, spotify_user_id, spotify_token2, spotify_other_id

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

#sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


class CreatePlaylist:
    # user 1, we will create the playlist under this account
    def __init__(self):
        self.user_id = spotify_user_id
        self.all_songs = set()
        self.other_id = spotify_other_id
        self.other_all_songs = set()
        self.union_songs = set()

    def add_tracks(self, results):
        for item in results['items']:
            track = item['track']
            self.all_songs.add(track['uri'])

    def add_tracks2(self, results):
        for item in results['items']:
            track = item['track']
            self.other_all_songs.add(track['uri'])

    def get_all_songs_self(self):
        sp = spotipy.Spotify(spotify_token)
        playlists = sp.user_playlists(self.user_id, limit=50)

        for playlist in playlists['items']:
            if playlist['owner']['id'] == self.user_id:
                # print(playlist['name'])

                results = sp.playlist(playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                self.add_tracks(tracks)
                while tracks['next']:
                    tracks = sp.next(tracks)
                    self.add_tracks(tracks)

        results = sp.current_user_saved_tracks()
        self.add_tracks(results)
        while results['next']:
            results = sp.next(results)
            self.add_tracks(results)

    def get_all_songs_other(self):
        sp = spotipy.Spotify(spotify_token2)
        playlists = sp.user_playlists(self.other_id, limit=50)

        for playlist in playlists['items']:
            if playlist['owner']['id'] == self.other_id:
                print(playlist['name'])
                results = sp.playlist(playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                self.add_tracks2(tracks)
                while tracks['next']:
                    tracks = sp.next(tracks)
                    self.add_tracks2(tracks)

        results = sp.current_user_saved_tracks()
        self.add_tracks2(results)
        while results['next']:
            results = sp.next(results)
            self.add_tracks2(results)

    def create_playlist(self):
        request_body = json.dumps({
            "name": "your new playlist!!",
            "description": "all of your shared favorite songs!",
            "public": False
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            self.user_id)

        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        sp = spotipy.Spotify(spotify_token)
        sp.user_playlist_change_details(
            self.user_id, response_json["id"], collaborative=True)
        sp = spotipy.Spotify(spotify_token2)
        sp.user_playlist_follow_playlist(self.user_id, response_json["id"])

        return response_json["id"]

    def get_union(self):
        self.union_songs = self.all_songs.intersection(self.other_all_songs)

    def add_song(self):
        self.get_all_songs_self()
        self.get_all_songs_other()
        self.get_union()
        print(len(self.all_songs))
        print(len(self.other_all_songs))
        print(len(self.union_songs))
        # for song in self.union_songs:
        # print(song)
        playlist_id = self.create_playlist()

        # spotify does not let you add >100 songs to a playlist per iteration
        union = []
        x = len(self.union_songs)/100
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

            response = requests.post(
                query,
                data=request_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotify_token)
                }
            )


# if __name__ == '__main__':
cp = CreatePlaylist()
# cp.add_song()
cp.add_song()
