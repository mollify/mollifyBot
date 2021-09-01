from django.conf.urls import url
from . import views

urlpatterns = [
    url("create", views.create_chatroom),
    url("update", views.update_chat),
    url("get", views.get_chat)
]