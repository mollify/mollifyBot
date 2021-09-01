# Create your views here.
import time

from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import TemporaryUploadedFile
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from utils.cache import update_chatroom_chats, get_chatroom_chats
from django.template.loader import get_template

from utils.common import upload_to_s3
from .models import MongoModel
from utils.messageEncoder import translateMessage
from .form import ChatRoom
from utils.properties import DEFAULT_EXPIRE_TIME, FILE_SUFFIXS


# TODO create database useing models for large dataset
# sockets event handling, online offline,
def translate_message_for_mongo(userId, message):
    return translateMessage(userId, message, 'encrypt')


def return_response(data=None, message="", code=200):
    if data is None:
        data = {}
    return JsonResponse({"data": data, "message": message, "code": code}, status=code, safe=False)


@api_view(["GET", "POST"])
@csrf_exempt
def create_chatroom(request):
    if request.method == "POST":
        # socket,
        try:
            room_id: str = request.data.get("chatroomId")
            if room_id is None:
                return return_response({}, "roomid is none", 400)
            doctor: str = request.data.get("doctorId")
            if doctor is None:
                return return_response({}, "doctor id is none", 400)
            client: str = request.data.get("clientId")
            if client is None:
                return return_response({}, "client id is none", 400)
            if get_chatroom_chats(room_id) is not None:
                return_response({}, "room already exist", 200)
            else:
                current_time = time.time()
                to_save = {"chatroomId": room_id,
                           "doctorId": doctor,
                           "clientId": client,
                           "createdAt": int(current_time * 1000),
                           "messages": []}
                update_chatroom_chats(room_id, to_save)
                MongoModel.objects.mongo_insert_one(to_save)
                # template = get_template("index.html")
                # form = ChatRoom()
                return return_response(to_save, "Success", code=200)
                # return HttpResponse(
                #     template.render({"form": form},
                #                     request))
        except Exception as e:
            print(f"error due to {e}")
            return_response({"error": f"e"}, f"e", 400)
    else:
        template = get_template("chatroom.html")
        return HttpResponse(template.render({'form': ChatRoom()}, request))


@api_view(["POST"])
@csrf_exempt
def update_chat(request):
    if request.method == "POST":
        try:
            room_id: str = request.data.get("chatroomId")
            if room_id is None:
                return return_response({}, "room id is none", 400)
            sender: str = request.data.get("sender")
            if sender is None:
                return return_response({}, "senderId is none", 400)
            chat = get_chatroom_chats(room_id)
            if chat is None:
                chat = MongoModel.objects.mongo_find_one({"chatroomId": room_id})
            timestamp = time.time() * 1000
            data = {"sender": sender,
                    "message": request.data.get("message"),
                    "time": timestamp}
            if chat is not None:
                if len(request.FILES.getlist('files')) > 0:
                    is_file = True
                    files = []
                    for i in request.FILES.getlist('files'):
                        print(i.name)
                        if str(i.name).endswith(FILE_SUFFIXS):
                            fs = FileSystemStorage()
                            filename = fs.save(i.name, i)
                            files.append({"type": i.content_type,
                                          "url": upload_to_s3(None,
                                                              fs.base_location + "/" + filename)})
                        else:
                            return return_response({"fileName": i.name}, "file does not support", 400)
                    data["isFile"] = files
                messages = chat.get("messages")
                messages.append(data)
                chat["messages"] = messages
                update_chatroom_chats(room_id, chat)
                data['message'] = translate_message_for_mongo(room_id, request.data.get("message"))
                MongoModel.objects.mongo_update_one({"chatroomId": room_id},
                                                    {"$push": {"messages": data}})
                return return_response({}, "message_updated", 200)
        except Exception as e:
            print(f"error due to {e}")
            return return_response({"error": f"{e}"}, f"{e}", 400)
        else:
            return return_response({}, "room does not exist", 400)


@api_view(["POST"])
@csrf_exempt
def get_chat(request):
    try:
        room_id = request.query_params.get("chatroomId")
        user_name = request.query_params.get("user")
        count: int = request.query_params.get("count")
        messages = get_chatroom_chats(room_id)
        if messages is None:
            response = list(MongoModel.objects.mongo_find({"chatroomId": room_id}))
            if response is not None and len(response) > 0:
                for i in response[0].get("messages"):
                    temp_message = i.get("message")
                    i["message"] = translateMessage(room_id, temp_message, 'decrypt')
                update_chatroom_chats(room_id, response[0])
                messages = response[0]
            else:
                return return_response([], "chatroom not found", 200)
        final_message = []
        if messages is not None:
            for i in messages.get("messages")[-50 * count:]:
                if i.get("sender") == user_name:
                    i["sender"] = "you"
                final_message.append(i)
            template = get_template("index_chatroom.html")
            return HttpResponse(
                template.render(
                    {'userName': user_name, 'messages': final_message},
                    request))
        else:
            return return_response([], "chatroom not found", 200)
    except Exception as e:
        return return_response({"error": str(e)}, str(e), 400)
