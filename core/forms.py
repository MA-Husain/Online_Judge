from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, PasswordChangeForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth.models import User
from .models import User_Details, Problem
from coding.models import TestCase
from django.forms import formset_factory, modelformset_factory, BaseFormSet

class Login_Form(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus' : 'True', 'class' : 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={ 'autocomplete' : 'current-password' , 'class' : 'form-control'}))

class Sign_Up_form(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': 'True', 'class': 'form-control'}), max_length=100)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use. Please supply a different email address.")
        return email
    
class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput(attrs={'autofocus': 'True','autocomplete' : 'current-password', 'class': 'form-control'}))
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'autocomplete' : 'new-password', 'class': 'form-control'}))
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput(attrs={'autocomplete' : 'new-password', 'class': 'form-control'}))


class MyPasswordRestForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

class MyPasswordSetForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'autocomplete' : 'new-password', 'class': 'form-control'}))
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput(attrs={'autocomplete' : 'new-password', 'class': 'form-control'}))

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User_Details
        fields = ['name', 'location', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = user.email

    def save(self, commit=True):
        user_details = super(UserProfileForm, self).save(commit=False)
        user_details.user.email = self.cleaned_data['email']
        if commit:
            user_details.user.save()
            user_details.save()
        return user_details

# core/forms.py
from django import forms
from .models import Problem, Tag

class CreateProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['title', 'description', 'difficulty', 'tags']

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'style': 'width: 100%;'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'style': 'width: 100%;'})
        self.fields['difficulty'].widget.attrs.update({'class': 'form-control', 'style': 'width: 100%;'})
        self.fields['tags'].widget.attrs.update({'class': 'form-check-input'})

class CreateTestCaseForm(forms.ModelForm):
    DELETE = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput())

    class Meta:
        model = TestCase
        fields = ['input', 'expected_output']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['DELETE'].widget.attrs.update({'class': 'form-check-input'})

class BaseTestCaseFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.problem = kwargs.pop('problem', None)
        super().__init__(*args, **kwargs)

    def _construct_forms(self):
        self.forms = []
        for i in range(self.total_form_count()):
            self.forms.append(self._construct_form(i, problem=self.problem))