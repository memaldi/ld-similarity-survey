from django import forms

class SurveyForm(forms.Form):
    source_dataset_id = forms.IntegerField(widget=forms.HiddenInput)
    target_dataset_id = forms.IntegerField(widget=forms.HiddenInput)
    choices = [('yes', 'Yes'), ('no', 'No'), ('undefined', 'Undefined')]
    similarity = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, required=True)