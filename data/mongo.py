import mongoengine
from data import users
import os

alias_core = 'core'
dbname = 'spotify_app'
mongoengine.connect(alias=alias_core,name=dbname,host=os.environ.get('MONGODB_URI', None))

def store_user_auth(user_id, username, auth_token, auth_header):
    print('IN STORE')
    print(os.environ.get('MONGODB_URI', None))
    user = users.User()
    user.user_id = user_id
    user.username = username
    user.token = auth_token
    user.header = auth_header
    
    try:
        user.save()
    except:
        print("something went wrong")

    return user.id