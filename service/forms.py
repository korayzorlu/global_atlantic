from django import forms
from django.forms import formset_factory, modelformset_factory
from information.helpers import set_value_to_immutable_dict
from django.utils.safestring import mark_safe
from django.utils.html import format_html

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

class AcceptanceForm(forms.ModelForm):
    class Meta:
        model = Acceptance
        fields = '__all__'
        
        widgets = {
            "acceptanceNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "readonly" : "", "rows" : "1", "style" :  "resize: none;"}),
            "customer" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "acceptanceDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "note" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "2"}),
            "vessel" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "person" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "equipment" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "customerRef" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "machineType" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "paymentType" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "deliveryMethod" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "period" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "currency" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "discount" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "discountAmount" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"})
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AcceptanceForm, self).__init__(*args, **kwargs)
        self.fields['customer'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__customer = True)
        self.fields['acceptanceDate'].input_formats = ["%d/%m/%Y"]
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency'].empty_label = None
        self.fields['equipment'].label_from_instance = lambda obj: f"{obj.maker.name} | {obj.makerType.type} | {obj.category} | {obj.serialNo} | Cyl: {obj.cyl} | Ver: {obj.version}"

        #select'leri foreignkey'lerine göre filtreler
        if self.instance and hasattr(self.instance, 'customer') and self.instance.customer:
            self.fields['vessel'].queryset = Vessel.objects.filter(company=self.instance.customer)
            self.fields['person'].queryset = Person.objects.filter(company=self.instance.customer)
        
class AcceptanceServiceCardForm(forms.ModelForm):
    class Meta:
        model = AcceptanceServiceCard
        fields = '__all__'
        
        widgets = {
            "serviceCard" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "quantity" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "profit" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "discount" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "tax" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "note" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1"})
        }
        
    def __init__(self, *args, **kwargs):
        super(AcceptanceServiceCardForm, self).__init__(*args, **kwargs)
        self.fields['serviceCard'].label_from_instance = lambda obj: format_html(f"<span style='font-weight:600!important;'>CODE:</span> {obj.code}, ACTION: {obj.name}, GROUP: {obj.group}")


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = '__all__'
        
        widgets = {
            "offerNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "readonly" : "", "rows" : "1", "style" :  "resize: none;"}),
            "customer" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "vessel" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "person" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "equipment" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "customerRef" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "machineType" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "offerDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "paymentType" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "deliveryMethod" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "period" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "currency" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "discount" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "discountAmount" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "confirmed" : forms.CheckboxInput(attrs = {"class" : "form-check-input", "type" : "checkbox", "role" : "switch", "id" : "textFormOutline"}),
            "finished" : forms.CheckboxInput(attrs = {"class" : "form-check-input", "type" : "checkbox", "role" : "switch", "id" : "textFormOutline"}),
            "note" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "2"})
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OfferForm, self).__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency'].empty_label = None
        self.fields['customer'].queryset = Company.objects.select_related().filter(sourceCompany = self.user.profile.sourceCompany,role__customer = True)
        self.fields['offerDate'].input_formats = ["%d/%m/%Y"]
        #self.fields['equipment'].label_from_instance = lambda obj: f"{obj.maker.name} | {obj.makerType.type} | {obj.category} | {obj.serialNo} | Cyl: {obj.cyl} | Ver: {obj.version}"
        #self.fields['equipment'].queryset = EnginePart.objects.none()
        # self.fields['vessel'].queryset = Vessel.objects.none()
        # self.fields['person'].queryset = Person.objects.none()
        # self.fields['equipment'].queryset = EnginePart.objects.none()

        #select'leri foreignkey'lerine göre filtreler
        if self.instance and hasattr(self.instance, 'customer') and self.instance.customer:
            self.fields['vessel'].queryset = Vessel.objects.filter(sourceCompany = self.user.profile.sourceCompany,company=self.instance.customer)
            self.fields['person'].queryset = Person.objects.filter(sourceCompany = self.user.profile.sourceCompany,company=self.instance.customer)
        if self.instance and hasattr(self.instance, 'vessel') and self.instance.vessel:
            self.fields['equipment'].queryset = EnginePart.objects.select_related().filter(sourceCompany = self.user.profile.sourceCompany,vessel=self.instance.vessel)
            self.fields['equipment'].label_from_instance = lambda obj: f"{obj.maker.name} | {obj.makerType.type} | {obj.category} | {obj.serialNo} | {obj.cyl} | {obj.version}"

class FinishedOfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["finished"]
        
        widgets = {
            "finished" : forms.CheckboxInput(attrs = {"class" : "form-check-input", "type" : "checkbox", "role" : "switch", "id" : "textFormOutline"})
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(FinishedOfferForm, self).__init__(*args, **kwargs)
class OfferServiceCardForm(forms.ModelForm):
    class Meta:
        model = OfferServiceCard
        fields = ["serviceCard","quantity","profit","discount","tax","note"]
        
        widgets = {
            "serviceCard" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "quantity" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "profit" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "discount" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "tax" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "note" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1"})
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OfferServiceCardForm, self).__init__(*args, **kwargs)
        self.fields['serviceCard'].queryset = ServiceCard.objects.filter(sourceCompany = self.user.profile.sourceCompany).order_by("code")
        self.fields['serviceCard'].label_from_instance = lambda obj: format_html(f"<span style='font-weight:600!important;'>CODE:</span> {obj.code}, ACTION: {obj.name}, GROUP: {obj.group}")

class OfferExpenseForm(forms.ModelForm):
    class Meta:
        model = OfferExpense
        fields = '__all__'
        
        widgets = {
            "expense" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "quantity" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"})
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OfferExpenseForm, self).__init__(*args, **kwargs)
        self.fields['expense'].queryset = Expense.objects.filter(sourceCompany = self.user.profile.sourceCompany).order_by("code")
        self.fields['expense'].label_from_instance = lambda obj: f"{obj.code} - {obj.name} - {obj.unit}"

class OfferPartForm(forms.ModelForm):
    class Meta:
        model = OfferPart
        fields = '__all__'
        
        widgets = {
            "part" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "quantity" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"})
        }
        
    def __init__(self, *args, **kwargs):
        super(OfferPartForm, self).__init__(*args, **kwargs)
        self.fields['part'].label_from_instance = lambda obj: f"{obj.partNo} - {obj.description} - {obj.unit}"

class OfferImageForm(forms.ModelForm):
    class Meta:
        model = OfferImage
        fields = ["image"]
        
        widgets = {
            "image" : forms.FileInput(attrs = {"class" : "file-upload-input", "id" : "offerImageUpload", "type" : "file", "data-mdb-file-upload" : "file-upload"})
        }
        
    def __init__(self, *args, **kwargs):
        super(OfferImageForm, self).__init__(*args, **kwargs)

class OfferDocumentForm(forms.ModelForm):
    class Meta:
        model = OfferDocument
        fields = ["file"]
        
        widgets = {
            "file" : forms.FileInput(attrs = {"class" : "file-upload-input", "id" : "offerDocumentUpload", "type" : "file", "data-mdb-file-upload" : "file-upload"})
        }
        
    def __init__(self, *args, **kwargs):
        super(OfferDocumentForm, self).__init__(*args, **kwargs)