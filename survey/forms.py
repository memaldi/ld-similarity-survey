from django import forms
from django.contrib.auth.models import User

class SurveyForm(forms.Form):
    source_dataset_id = forms.IntegerField(widget=forms.HiddenInput)
    target_dataset_id = forms.IntegerField(widget=forms.HiddenInput)
    choices = [('yes', 'Yes'), ('no', 'No'), ('undefined', 'Undefined')]
    similarity = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, required=True)
    sim_id = forms.IntegerField(widget=forms.HiddenInput)

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
