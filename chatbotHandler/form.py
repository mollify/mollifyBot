from django import forms


class UserForm(forms.Form):
    name = forms.CharField(max_length=200)


class MessageForm(forms.Form):
    message = forms.CharField(max_length=500)
    uuid_id = forms.CharField(max_length=100)
