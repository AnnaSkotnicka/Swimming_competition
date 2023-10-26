from django import forms
from .models import Contestant


class PolTekstowe(forms.Form):
    code = forms.CharField(max_length=30, label="Zeskanowany kod")

