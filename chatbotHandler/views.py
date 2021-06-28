import time

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rasa_runner import run_rasa_server, update_cache
import uuid
from .form import UserForm, MessageForm
from django.http import JsonResponse, HttpResponse
from cache import get_user_details, update_user_cache
from concurrent.futures.thread import ThreadPoolExecutor
from django.template.loader import get_template
from .models import MongoModel

# TODO create database useing models for large dataset
# TODO encript data
#
thread = ThreadPoolExecutor(2)
thread.submit(run_rasa_server)
thread.submit(update_cache, MongoModel)


def rasa_chatboot(user_id, message):
    import requests
    import json
    payload = json.dumps({"sender": user_id, "message": message})
    headers = {'content-type': 'application/json'}
    r = requests.post('http://localhost:5005/webhooks/rest/webhook', data=payload, headers=headers)
    response_to_list = json.loads(r.text)
    if len(response_to_list) > 0:
        return response_to_list[0].get("text")
    else:
        return "sorry repeat please"


def return_response(data=None, message="", code=200):
    if data is None:
        data = {}
    return JsonResponse({"data": data, "message": message, "code": code}, status=code, safe=False)


@api_view(["GET", "POST"])
@csrf_exempt
def create_user(request):
    if request.method == "POST":
        name = request.data.get("name")
        unique_id = str(uuid.uuid1()).replace("-", "")

        msg1st = {"sender": "system", "message": f"hey {name}.", "time": time.time()}
        msg2st = {"sender": "system", "message": "how are you felling today.", "time": time.time()}
        update_user_cache(unique_id, {"name": name, "userId": unique_id, "message_history": [msg1st, msg2st]})
        MongoModel.objects.mongo_insert_one({"name": name, "userId": unique_id, "message_history": [msg1st, msg2st]})
        template = get_template("index.html")
        form = MessageForm(initial={"userId": unique_id})
        # return return_response(message_history, "Success", code=200)
        return HttpResponse(
            template.render({"form": form, 'userName': name, "UserId": unique_id, 'messages': [msg1st, msg2st]},
                            request))
    else:
        template = get_template("userForm.html")
        return HttpResponse(template.render({'form': UserForm()}, request))


@api_view(["POST"])
@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        user_id = request.data.get("userId")
        message = request.data.get("message")
        user_message = {"sender": user_id, "message": message, "time": time.time()}
        response = rasa_chatboot(user_id, message)
        system_message = {"sender": "system", "message": response, "time": time.time()}
        data = get_user_details(user_id)
        message_history = data.get("message_history")
        if message_history is None:
            message_history = [user_message, system_message]
        else:
            message_history.append(user_message)
            message_history.append(system_message)
        data["message_history"] = message_history
        MongoModel.objects.mongo_update_one({"userId": user_id},
                                            {"$push": {"message_history": {"$each": [user_message, system_message]}}})
        update_user_cache(user_id, data)
        template = get_template("index.html")
        form = MessageForm(initial={"userId": user_id})
        return HttpResponse(
            template.render(
                {"form": form, 'userName': data.get("name"), "UserId": user_id, 'messages': message_history},
                request))
