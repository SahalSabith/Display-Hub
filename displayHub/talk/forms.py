from django.forms import ModelForm
from django import forms
from .models import ChatGroup,GroupMessage

class ChatMessageCreateForm(ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body']
        widgets = {
            'body': forms.TextInput(attrs={
                'placeholder': 'Add Message.....',
                'class': 'p-4 text-black form-control',
                'maxlength': 300,
                'autofocus': True,
                'style': 'border-radius: 10px; width: 100%; height: 50px;',
            }),
        }
