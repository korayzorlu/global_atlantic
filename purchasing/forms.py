from django import forms
from django_select2 import forms as s2forms

from django.forms import formset_factory, modelformset_factory

from information.helpers import set_value_to_immutable_dict

from core.utils import WidgetStyle, set_form_widget

from .models import *
 
        
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["projectNo","supplier","customerRef","projectDate"]
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProjectForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        self.fields['supplier'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__supplier = True)
        self.fields['projectDate'].input_formats = ["%d/%m/%Y"]

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = '__all__'
   
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(InquiryForm, self).__init__(*args, **kwargs)
        
        #self.fields['supplier'] = forms.ModelMultipleChoiceField(queryset = Company.objects.filter(), widget=forms.CheckboxSelectMultiple(attrs = {"class" : "form-check-input", "id": "supplierCheck", "type":"checkbox", "style" : h"eight:50vh;"}))
        self.fields['supplier'] = forms.ModelMultipleChoiceField(queryset = Company.objects.filter(
            sourceCompany = self.user.profile.sourceCompany,
            supplierCheck = True
        ), widget=forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "multiple" : "", "data-mdb-size" : "sm", "data-mdb-filter":"true"}))
        self.fields['supplier'].empty_label = None

class InquiryDetailForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(InquiryDetailForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['note'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"note","rows":"2"}], form=self).attr())

        self.fields['supplier'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany)
        choices = [(related_model.id, related_model.code) for related_model in Currency.objects.all()]
        choices.sort(key=lambda x: x[1])
        #self.fields['currency'].choices = choices
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency'].empty_label = None
        self.fields['inquiryDate'].input_formats = ["%d/%m/%Y"]

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
   
        
    def __init__(self, *args, **kwargs):
        super(PurchaseOrderForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['note'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"note","rows":"2"}], form=self).attr())
        
        purchaseOrderChoices = [(related_model.id, related_model.code) for related_model in Currency.objects.all()]
        purchaseOrderChoices.sort(key=lambda x: x[1])
        #self.fields['currency'].choices = purchaseOrderChoices
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.initial['currency'] = "106"
        self.fields['purchaseOrderDate'].input_formats = ["%d/%m/%Y"]
        self.fields['orderDueDate'].input_formats = ["%d/%m/%Y"]

class PurchaseOrderDocumentForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderDocument
        fields = ["file"]
        
        widgets = {
            "file" : forms.FileInput(attrs = {"class" : "file-upload-input", "id" : "purchaseOrderDocumentUpload", "type" : "file", "data-mdb-file-upload" : "file-upload"})
        }
        
    def __init__(self, *args, **kwargs):
        super(PurchaseOrderDocumentForm, self).__init__(*args, **kwargs)