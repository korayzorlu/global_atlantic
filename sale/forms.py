from django import forms
from django_select2 import forms as s2forms

from django.forms import formset_factory, modelformset_factory

from information.helpers import set_value_to_immutable_dict

from core.utils import WidgetStyle, set_form_widget

from .models import *
 
        
class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(RequestForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        self.fields['customer'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__customer = True)
        self.fields['requestDate'].input_formats = ["%d/%m/%Y"]
        self.fields['maker'].queryset = Maker.objects.filter(sourceCompany = self.user.profile.sourceCompany)
        self.fields['note'].widget.attrs.update(WidgetStyle(widget="TextInput",customParameters=[{"maxlength":"150"},{"data-mdb-showcounter":"true"}]).attr())

        #select'leri foreignkey'lerine göre filtreler
        if 'customer' in self.data:
            try:
                customer_id = int(self.data.get('customer'))
                self.fields['vessel'].queryset = Vessel.objects.filter(company_id=customer_id)
            except (ValueError, TypeError):
                self.fields['vessel'].queryset = Vessel.objects.none()
        elif self.instance and self.instance.customer_id:
            self.fields['vessel'].queryset = Vessel.objects.filter(company=self.instance.customer)
        else:
            self.fields['vessel'].queryset = Vessel.objects.none()

        if 'customer' in self.data:
            try:
                customer_id = int(self.data.get('customer'))
                self.fields['person'].queryset = Person.objects.filter(company_id=customer_id)
            except (ValueError, TypeError):
                self.fields['person'].queryset = Person.objects.none()
        elif self.instance and self.instance.customer_id:
            self.fields['person'].queryset = Person.objects.filter(company=self.instance.customer)
        else:
            self.fields['person'].queryset = Person.objects.none()

        if 'vessel' in self.data:
            try:
                vessel_id = int(self.data.get('vessel'))
                self.fields['vesselPerson'].queryset = Person.objects.filter(vessel_id=vessel_id)
            except (ValueError, TypeError):
                self.fields['vesselPerson'].queryset = Person.objects.none()
        elif self.instance and self.instance.vessel:
            self.fields['vesselPerson'].queryset = Person.objects.filter(vessel=self.instance.vessel)
        else:
            self.fields['vesselPerson'].queryset = Person.objects.none()

        if 'maker' in self.data:
            try:
                maker_id = int(self.data.get('maker'))
                self.fields['makerType'].queryset = MakerType.objects.filter(maker_id=maker_id)
            except (ValueError, TypeError):
                self.fields['makerType'].queryset = MakerType.objects.none()
        elif self.instance and self.instance.maker:
            self.fields['makerType'].queryset = MakerType.objects.filter(maker=self.instance.maker)
        else:
            self.fields['makerType'].queryset = MakerType.objects.none()  
        
class RequestPartForm(forms.ModelForm):
    class Meta:
        model = RequestPart
        fields = '__all__'
        
        widgets = {
            #"part" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select selectPart", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "quantity" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-requestPart-quantity", "rows" : "1", "style" :  "resize: none;"})
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(RequestPartForm, self).__init__(*args, **kwargs)
        #self.fields['city'].queryset = City.objects.none()
        self.fields['part'].empty_label = ""
        self.fields['part'].queryset = Part.objects.none()
        
        #select'leri foreignkey'lerine göre filtreler
        if self.instance and hasattr(self.instance, 'theRequest') and self.instance.theRequest:
            #self.fields['part'].queryset = Part.objects.filter(maker=self.instance.theRequest.maker)
            self.fields['part'].queryset = Part.objects.none()
            
        if "part" in self.data:
            self.fields['part'].queryset = Part.objects.filter(sourceCompany = self.user.profile.sourceCompany)
        
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
        
        #select'leri foreignkey'lerine göre filtreler
        if 'supplier' in self.data:
            try:
                supplier_id = int(self.data.get('supplier'))
                self.fields['person'].queryset = Person.objects.filter(company_id=supplier_id)
            except (ValueError, TypeError):
                self.fields['person'].queryset = Person.objects.none()
        elif self.instance and self.instance.supplier:
            self.fields['person'].queryset = Person.objects.filter(company=self.instance.supplier)
        else:
            self.fields['person'].queryset = Person.objects.none()  
        
class InquiryPartForm(forms.ModelForm):
    class Meta:
        model = InquiryPart
        fields = '__all__'
        
        widgets = {
            "requestPart" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "readonly" : "", "rows" : "1", "style" :  "resize: none;"}),
            "quantity" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "unitPrice" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "totalPrice" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "availability" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"})
        }

    def __init__(self, *args, **kwargs):
        super(InquiryPartForm, self).__init__(*args, **kwargs)
        #self.fields['city'].queryset = City.objects.none()
        self.fields['availabilityType'].empty_label = ""
        
class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(QuotationForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['note'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"note","rows":"2"}], form=self).attr())

        quotationChoices = [(related_model.id, related_model.code) for related_model in Currency.objects.all()]
        quotationChoices.sort(key=lambda x: x[1])
        #self.fields['currency'].choices = quotationChoices
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency'].empty_label = None
        self.fields['quotationDate'].input_formats = ["%d/%m/%Y"]
        
class QuotationPartForm(forms.ModelForm):
    class Meta:
        model = QuotationPart
        fields = '__all__'
        
        widgets = {
            "inquiryPart" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "readonly" : "", "rows" : "1", "style" :  "resize: none;"}),
            "quantity" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "readonly" : "", "rows" : "1", "style" :  "resize: none;"}),
            "profit" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "discount" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "availability" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "note" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1"})
        }

    def __init__(self, *args, **kwargs):
        super(QuotationPartForm, self).__init__(*args, **kwargs)
        #self.fields['city'].queryset = City.objects.none()
        self.fields['availabilityType'].empty_label = ""

class QuotationExtraForm(forms.ModelForm):
    class Meta:
        model = QuotationExtra
        fields = ["name","description","quantity"]
        
    def __init__(self, *args, **kwargs):
        super(QuotationExtraForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)
        
        # if self.instance and hasattr(self.instance, 'maker') and self.instance.maker:
        #     self.fields['makerType'].queryset = MakerType.objects.filter(maker=self.instance.maker)
      
class OrderConfirmationForm(forms.ModelForm):
    class Meta:
        model = OrderConfirmation
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(OrderConfirmationForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['note'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"note","rows":"2"}], form=self).attr())

        self.fields['orderConfirmationDate'].input_formats = ["%d/%m/%Y"]
        
class OrderNotConfirmationForm(forms.ModelForm):
    class Meta:
        model = OrderNotConfirmation
        fields = '__all__'
        
        widgets = {
            "orderNotConfirmationNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "readonly" : "", "rows" : "1", "style" :  "resize: none;"}),
            "suggestion" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "4"}),
            "orderNotConfirmationDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "delay" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "selectFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "orderProcessType" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-placeholder" : "Order Process Type"}),
            "customerReaction" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select",  "data-mdb-size" : "sm", "data-mdb-placeholder" : "Customer Reaction"}),
            "finalDecision" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-placeholder" : "Final Decision"}),
            "suggestion" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "2"})
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OrderNotConfirmationForm, self).__init__(*args, **kwargs)
        self.fields['reasons'] = forms.ModelMultipleChoiceField(required = False, queryset = Reason.objects.filter(sourceCompany = self.user.profile.sourceCompany), widget=forms.CheckboxSelectMultiple(attrs = {"class" : "form-check-input", "id": "reasonCheck", "type":"checkbox"}))
        self.fields['reasons'].empty_label = None
        self.fields['orderNotConfirmationDate'].input_formats = ["%d/%m/%Y"]
        
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
        
class PurchaseOrderPartForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderPart
        fields = '__all__'
        
        widgets = {
            "inquiryPart" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "readonly" : "", "rows" : "1", "style" :  "resize: none;"}),
            "purchaseOrder" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "readonly" : "", "rows" : "1", "style" :  "resize: none;"}),
            "availability" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "readonly" : "", "rows" : "1", "style" :  "resize: none;"}),
            "availabilityType" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "id" : "selectFormOutline", "readonly" : "", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "orderType" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "id" : "selectFormOutline",  "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "quality" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"})
        }

    def __init__(self, *args, **kwargs):
        super(PurchaseOrderPartForm, self).__init__(*args, **kwargs)
        #self.fields['city'].queryset = City.objects.none()
        self.fields['orderType'].empty_label = ""
        self.fields['quality'].empty_label = ""
        
class OrderTrackingForm(forms.ModelForm):
    class Meta:
        model = OrderTracking
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(OrderTrackingForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['note'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"note","rows":"3"}], form=self).attr())

        self.fields['orderTrackingDate'].input_formats = ["%d/%m/%Y"]
    
class OrderTrackingDocumentForm(forms.ModelForm):
    class Meta:
        model = OrderTrackingDocument
        fields = ["file"]
        
        widgets = {
            "file" : forms.FileInput(attrs = {"class" : "file-upload-input", "id" : "orderTrackingDocumentUpload", "type" : "file", "data-mdb-file-upload" : "file-upload"})
        }
        
    def __init__(self, *args, **kwargs):
        super(OrderTrackingDocumentForm, self).__init__(*args, **kwargs)
   
class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        exclude = ["sourceCompany","orderTracking","purchaseOrder"]
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CollectionForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['address'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"address","rows":"11"}], form=self).attr())
        self.fields['note'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"note","rows":"4"}], form=self).attr())

        collectionCountries = [(related_model.id, related_model.international_formal_name) for related_model in Country.objects.all()]
        collectionCountries.sort(key=lambda x: x[1])
        self.fields['country'].choices = collectionCountries
        self.fields['dispatchDate'].input_formats = ["%d/%m/%Y"]
        self.fields['deliveryDate'].input_formats = ["%d/%m/%Y"]
        self.fields['agent'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__agent = True)
        collectionCurrencies = [(related_model.id, related_model.code) for related_model in Currency.objects.all()]
        collectionCurrencies.sort(key=lambda x: x[1])
        #self.fields['buyingTransportationCurrency'].choices = collectionCurrencies
        #self.fields['buyingPackingCurrency'].choices = collectionCurrencies
        #self.fields['buyingInsuranceCurrency'].choices = collectionCurrencies
        #self.fields['sellingTransportationCurrency'].choices = collectionCurrencies
        #self.fields['sellingPackingCurrency'].choices = collectionCurrencies
        #self.fields['sellingInsuranceCurrency'].choices = collectionCurrencies
        self.fields['buyingTransportationCurrency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['buyingTransportationCurrency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['buyingPackingCurrency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['buyingPackingCurrency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['buyingInsuranceCurrency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['buyingInsuranceCurrency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"

CollectionFormSet = modelformset_factory(Collection, form = CollectionForm, extra=0)

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(DeliveryForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['address'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"address","rows":"11"}], form=self).attr())
        self.fields['note'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"note","rows":"4"}], form=self).attr())


        collectionCountries = [(related_model.id, related_model.international_formal_name) for related_model in Country.objects.all()]
        collectionCountries.sort(key=lambda x: x[1])
        self.fields['country'].choices = collectionCountries
        self.fields['dispatchDate'].input_formats = ["%d/%m/%Y"]
        self.fields['deliveryDate'].input_formats = ["%d/%m/%Y"]
        self.fields['agent'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__agent = True)
        collectionCurrencies = [(related_model.id, related_model.code) for related_model in Currency.objects.all()]
        collectionCurrencies.sort(key=lambda x: x[1])
        #self.fields['buyingTransportationCurrency'].choices = collectionCurrencies
        #self.fields['buyingPackingCurrency'].choices = collectionCurrencies
        #self.fields['buyingInsuranceCurrency'].choices = collectionCurrencies
        #self.fields['sellingTransportationCurrency'].choices = collectionCurrencies
        #self.fields['sellingPackingCurrency'].choices = collectionCurrencies
        #self.fields['sellingInsuranceCurrency'].choices = collectionCurrencies
        self.fields['sellingTransportationCurrency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['sellingTransportationCurrency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['sellingPackingCurrency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['sellingPackingCurrency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['sellingInsuranceCurrency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['sellingInsuranceCurrency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        
DeliveryFormSet = modelformset_factory(Delivery, form = DeliveryForm, extra=0)

class DispatchOrderForm(forms.ModelForm):
    class Meta:
        model = DispatchOrder
        exclude = ["sourceCompany","user","sessionKey","dispatchOrderNo"]
    
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(DispatchOrderForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['note'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"note","rows":"2"}], form=self).attr())