from django import forms

from django.forms import formset_factory, modelformset_factory

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

class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = '__all__'
        
        widgets = {
            "bankName" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "company" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "accountType" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "accountNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "ibanNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "swiftNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "branchName" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "branchCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "balance" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "currency" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "id":"formCurrencySI", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(BankForm, self).__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency'].empty_label = None
        self.fields['company'].queryset = Company.objects.filter(id = self.user.profile.sourceCompany.id)
        self.fields['company'].empty_label = None