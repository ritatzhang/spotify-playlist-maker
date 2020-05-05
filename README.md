# spotify-playlist-maker
makes collaborative playlist featuring music from two user's spotify accounts

to use, two spotify users need to access their authentication tokens from this website: 

https://developer.spotify.com/console/put-playlist/?playlist_id=&body=%7B%22name%22%3A%22Updated%20Playlist%20Name%22%2C%22description%22%3A%22Updated%20playlist%20description%22%2C%22public%22%3Afalse%7D

scroll down to see where it says o auth token, click get token, and then check off these boxes: 
playlist-modify-public
playlist-modify-private
user-library-read
user-read-private
playlist-read-private
user-library-modify
playlist-read-collaborative
user-file-modify

after you get the token, put it into the secrets.py file along with the usernames of both users.

then just run

python3 create_playlist.py
