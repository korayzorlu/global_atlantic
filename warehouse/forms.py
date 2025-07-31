from django import forms
from django_select2 import forms as s2forms

from django.forms import formset_factory, modelformset_factory

from information.helpers import set_value_to_immutable_dict

from core.utils import WidgetStyle, set_form_widget

from .models import *

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ["code","name","country","city","address","phone1","about"]
    
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(WarehouseForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['about'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"about","rows":"2"}], form=self).attr())

        self.fields['country'].queryset = Country.objects.all().order_by("international_formal_name")
        self.fields['country'].label_from_instance = lambda obj: f"{obj.international_formal_name}"
        
        #select'leri foreignkey'lerine göre filtreler
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['city'].queryset = City.objects.filter(country_id=country_id)
            except (ValueError, TypeError):
                self.fields['city'].queryset = City.objects.none()
        elif self.instance and self.instance.country:
            self.fields['city'].queryset = City.objects.filter(country=self.instance.country)
        else:
            self.fields['city'].queryset = City.objects.none()
            
class PartItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["warehouse","part","location","barcode","currency","buyingPrice","cost","salePrice","vat","weight","width","height","quantity","note","itemDate"]
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PartItemForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['part'].widget.attrs = {}
        self.fields['note'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"note","rows":"2"}], form=self).attr())
        
        self.fields['part'].queryset = Part.objects.none()
        self.fields['itemDate'].input_formats = ["%d/%m/%Y"]
        self.fields['warehouse'].queryset = Warehouse.objects.filter(sourceCompany = self.user.profile.sourceCompany).order_by("-code")
        self.fields['warehouse'].label_from_instance = lambda obj: f"{obj.code} | {obj.name}"
        self.fields['warehouse'].empty_label = None
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency'].empty_label = None
        
        if "part" in self.data:
            self.fields['part'].queryset = Part.objects.filter(sourceCompany = self.user.profile.sourceCompany)
            
        elif self.instance.pk:
            self.fields['part'].queryset = Part.objects.filter(sourceCompany = self.user.profile.sourceCompany,pk=self.instance.part.pk)

class DispatchForm(forms.ModelForm):
    class Meta:
        model = Dispatch
        fields = ["note"]
    
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(DispatchForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['note'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"note","rows":"2"}], form=self).attr())