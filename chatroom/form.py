from django import forms


class ChatRoom(forms.Form):
    chatroomId = forms.CharField(max_length=500)
    doctorId = forms.CharField(max_length=100)
    clientId = forms.CharField(max_length=100)
    timestamp = forms.DateTimeField()
    