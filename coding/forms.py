# coding/forms.py

from django import forms
from .models import Submission

LANGUAGE_CHOICES = [
    ("py", "Python"),
    ("java", "Java"),
    ("cpp", "C++"),
    # Add other languages as needed
]

class CodeSubmissionForm(forms.Form):
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    code = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10}))
    input_data = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}), required=False)
