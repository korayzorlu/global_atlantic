from django import forms

from information.helpers import set_value_to_immutable_dict

from .models import *

STYLES = {
    "Select": {
        'class': 'form-control select-search'
    },
    "SelectMultiple": {
        'class': 'form-control select-search'
    },
    "Textarea": {
        'class': 'form-control',
        'style': 'height:38px; min-height:36px',
    },
    "else": {
        'class': 'form-control'
    }
}     
        
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = '__all__'
        
        widgets = {
            "title" : forms.TextInput(attrs = {"class" : "form-control", "rows" : "1", "style" : "background-color: #fff; resize: none;"}),
            "text" : forms.Textarea(attrs = {"class" : "form-control", "rows" : "4", "style" : "background-color: #fff;"})
        }
        
    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)