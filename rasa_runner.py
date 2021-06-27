import os
import time

from cache import update_user_cache


def run_rasa_server():
    print("running server")
    os.system(
        "rasa run -m /home/lakshya/projects/mollifybot/bot/models/20210613-225726.tar.gz --enable-api --cors “*” --debug")


def update_cache(mongo):
    data = list(mongo.objects.mongo_find({}, {"_id":0}))
    print(data)

    for i in data:
        i = dict(i)
        id = i.get("userId")
        if id is not None:
            update_user_cache(id, i)
