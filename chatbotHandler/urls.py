from django.conf.urls import url
from . import views

urlpatterns = [
    url("createUser", views.create_user),
    url('chatbot', views.chatbot)
]