from django import forms

from information.helpers import set_value_to_immutable_dict
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from core.utils import WidgetStyle, set_form_widget

from .models import *
from data.models import Maker, MakerType

import random
import string

def sendAlert(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "send_alert",
            "message": message,
            "location" : location
        }
    )





class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["name", "title", "company", "email", "phone"]
        
        widgets = {
            "name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "company" : forms.Select(attrs = {"class" : "form-control form-select", "style" : ""}),
            "title" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "email" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "phone" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"})
        }
        
class CustomMMCF(forms.ModelMultipleChoiceField):
    def label_from_instance(self, member):
        return "%s" % member.name       
        
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

        # widgets = {
        #     "name" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "customerCheck" :
        #         forms.CheckboxInput(attrs = WidgetStyle(widget="CheckboxInput").attr()),
        #     "supplierCheck" :
        #         forms.CheckboxInput(attrs = WidgetStyle(widget="CheckboxInput").attr()),
        #     "agentCheck" :
        #         forms.CheckboxInput(attrs = WidgetStyle(widget="CheckboxInput").attr()),
        #     "ourCompany" :
        #         forms.CheckboxInput(attrs = WidgetStyle(widget="CheckboxInput").attr()),
        #     "companyNo" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "country" :
        #         forms.Select(attrs = WidgetStyle(widget="Select").attr()),
        #     "city" :
        #         forms.Select(attrs = WidgetStyle(widget="Select").attr()),
        #     "address" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput",customParameters=[{"maxlength":"100"},{"data-mdb-showcounter":"true"}]).attr()),
        #     "addressChar" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "vatOffice" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "vatNo" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "phone1" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "phone2" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "phone3" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "phone4" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "phone5" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "fax" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "email" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "web" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "hesapKodu" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "satisTemsilcisi" :
        #         forms.Select(attrs = WidgetStyle(widget="Select").attr()),
        #     "creditPeriot" :
        #         forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr()),
        #     "creditPeriod" :
        #         forms.NumberInput(attrs = WidgetStyle(widget="NumberInput").attr()),
        #     "logo" :
        #         forms.FileInput(attrs = WidgetStyle(widget="FileInput").attr()),
        #     "creditLimit" :
        #         forms.NumberInput(attrs = WidgetStyle(widget="NumberInput").attr()),
        #     "currency" :
        #         forms.Select(attrs = WidgetStyle(widget="Select").attr()),
        #     "currency2" :
        #         forms.Select(attrs = WidgetStyle(widget="Select").attr()),
        #     "currency3" :
        #         forms.Select(attrs = WidgetStyle(widget="Select").attr()),
        #     "unlimitedCheck" :
        #         forms.CheckboxInput(attrs = WidgetStyle(widget="CheckboxInput").attr()),
        #     "eFatura" :
        #         forms.CheckboxInput(attrs = WidgetStyle(widget="CheckboxInput").attr()),
        #     "about" :
        #         forms.Textarea(attrs = WidgetStyle(widget="Textarea",customParameters=[{"rows":"1"}]).attr())
        # }
        
    def clean(self):
        cleaned_data = super().clean()
        customerCheck = cleaned_data.get("customerCheck")
        supplierCheck = cleaned_data.get("supplierCheck")
        agentCheck = cleaned_data.get("agentCheck")
        
        # class MyException(Exception):
        #     pass
        
        # if not customerCheck and not supplierCheck and not agentCheck:
        #     data = {
        #                 "status":"secondary",
        #                 "icon":"triangle-exclamation",
        #                 "message":"At least one company role(customer or supplier) must be selected!"
        #         }
            
        #     sendAlert(data,"default")
        #     raise forms.ValidationError(
        #         {"role": "At least one company type must be selected."},
        #         code='invalid'
        #     )
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CompanyForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['about'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"about","rows":"1"}], form=self).attr())
        self.fields['address'].widget.attrs.update(WidgetStyle(widget="TextInput",customParameters=[{"maxlength":"100"},{"data-mdb-showcounter":"true"}]).attr())

        #self.fields['city'].queryset = City.objects.none()
        companyCurrencyChoices = [(related_model.id, related_model.code) for related_model in Currency.objects.all()]
        companyCurrencyChoices.sort(key=lambda x: x[1])
        #self.fields['currency'].choices = companyCurrencyChoices
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency2'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency2'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency3'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency3'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['country'].queryset = Country.objects.all().order_by("international_formal_name")
        self.fields['country'].label_from_instance = lambda obj: f"{obj.international_formal_name}"
        #self.initial['currency'] = "106"
        self.fields['satisTemsilcisi'].queryset = Profile.objects.filter(
            sourceCompany = self.user.profile.sourceCompany,
            positionType__name__icontains='Sale'
        ).order_by("user__first_name")
        self.fields['satisTemsilcisi'].label_from_instance = lambda obj: f"{obj.user.first_name} {obj.user.last_name}"
        
        #select'leri foreignkey'lerine göre filtreler
        # if self.instance and hasattr(self.instance, 'country') and self.instance.country:
        #     self.fields['city'].queryset = City.objects.filter(country=self.instance.country)
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
class VesselForm(forms.ModelForm):
    class Meta:
        model = Vessel
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(VesselForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)
        
        self.fields['company'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany).order_by("name")

        

class EnginePartForm(forms.ModelForm):
    class Meta:
        model = EnginePart
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EnginePartForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        self.fields['maker'].queryset = Maker.objects.filter(sourceCompany = self.user.profile.sourceCompany).order_by("name")
        self.fields['makerType'].queryset = MakerType.objects.filter(sourceCompany = self.user.profile.sourceCompany).order_by("type")
        
        # if self.instance and hasattr(self.instance, 'maker') and self.instance.maker:
        #     self.fields['makerType'].queryset = MakerType.objects.filter(maker=self.instance.maker)

        #html'deki id'leri atar
        appModelTag = f"{self._meta.model._meta.app_label}-{self._meta.model._meta.model_name}"
        for field_name, field in self.fields.items():
            field.widget.attrs['id'] = f"formOutline-{appModelTag}-{field_name}"
            
class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ["bankName", "accountNo", "ibanNo", "swiftNo", "branchName", "branchCode", "currency"]
        
        widgets = {
            "bankName" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "accountNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "ibanNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "swiftNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "branchName" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "branchCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "currency" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter" : "true", "data-mdb-placeholder" : "Company", "style" : ""})
        }

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ["ownerCompany"]
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OwnerForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        self.fields['ownerCompany'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany).order_by("name")
        
class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ["name","address","vessel","hesapKodu","country","city","email","vatOffice","vatNo","currency","currency2","currency3"]
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(BillingForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)
        #special situations
        self.fields['address'].widget.attrs.update(WidgetStyle(widget="TextInput",customParameters=[{"maxlength":"100"},{"data-mdb-showcounter":"true"}]).attr())

        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency2'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency2'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency3'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency3'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['vessel'].queryset = Vessel.objects.filter(sourceCompany = self.user.profile.sourceCompany).order_by("name")
        
        self.fields['country'].queryset = Country.objects.all().order_by("international_formal_name")
        self.fields['country'].label_from_instance = lambda obj: f"{obj.international_formal_name}"
        
        #select'leri foreignkey'lerine göre filtreler
        # if self.instance and hasattr(self.instance, 'country') and self.instance.country:
        #     self.fields['city'].queryset = City.objects.filter(country=self.instance.country)
        # else:
        #     self.fields['city'].queryset = City.objects.filter(country=self.instance.country).none()
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


class ExcelForm(forms.ModelForm):
    class Meta:
        model = Excel
        fields = ["file"]
        
        widgets = {
            "file" : forms.FileInput(attrs = {"class" : "form-control", "accept" : ".xlsx", "style" : ""})
        }
