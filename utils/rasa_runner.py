import os
import time

from utils.cache import update_user_cache
from utils.messageEncoder import translateMessage


def run_rasa_server():
    print("running server")
    # os.system(
    #     "rasa run -m /home/lakshya/projects/mollifybot/bot/models/20210613-225726.tar.gz --enable-api --cors “*” --debug")


def update_cache(mongo):
    data = list(mongo.objects.mongo_find({}, {"_id": 0}))
    print(data)

    for i in data:
        i = dict(i)
        id = i.get("userId")
        if id is not None:
            if i.get("message_history") is not None:
                message_history = []
                for message in i.get("message_history"):
                    temp_message = translateMessage(id, message.get("message"), 'decrypt')
                    message["message"] = temp_message
                    message_history.append(message)
                i["message_history"] = message_history
            update_user_cache(id, i)
