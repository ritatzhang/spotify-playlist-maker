import mongoengine

class User(mongoengine.Document):
    db_id = mongoengine.ObjectIdField()
    user_id = mongoengine.StringField()
    username = mongoengine.StringField()
    token = mongoengine.StringField()
    header = mongoengine.DictField()

    meta = {
        'db_alias': 'core',
        'collection': 'users'
    }