from django import forms

from django.forms import formset_factory, modelformset_factory

from information.helpers import set_value_to_immutable_dict

from core.utils import WidgetStyle, set_form_widget

from .models import *
from card.models import Company
from source.models import Bank as SourceBank
from source.models import Company as SourceCompany

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

class IncomingInvoiceForm(forms.ModelForm):
    class Meta:
        model = IncomingInvoice
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(IncomingInvoiceForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situation
        self.fields['seller'].widget.attrs.update(WidgetStyle(widget="Select", customParameters=[{"data-mdb-validation":"true","required":"true"}]).attr())
        self.fields['customerSource'].widget.attrs.update(WidgetStyle(widget="Select", customParameters=[{"data-mdb-validation":"true","required":"true"}]).attr())

        self.fields['paymentDate'].input_formats = ["%d/%m/%Y"]
        self.fields['incomingInvoiceDate'].input_formats = ["%d/%m/%Y"]
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency'].empty_label = None
        self.fields['seller'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__supplier = True)
        self.fields['customer'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__ourCompany = True)
        self.fields['customerSource'].queryset = SourceCompany.objects.filter(id = self.user.profile.sourceCompany.id)

# class IncomingInvoicePartForm(forms.ModelForm):
#     class Meta:
#         model = IncomingInvoicePart
#         fields = '__all__'
        
#         widgets = {
#             "part" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
#             "quantity" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"})
#         }
        
#     def __init__(self, *args, **kwargs):
#         super(IncomingInvoicePartForm, self).__init__(*args, **kwargs)
#         self.fields['part'].label_from_instance = lambda obj: f"{obj.partNo} - {obj.description} - {obj.unit}"

class IncomingInvoiceExpenseForm(forms.ModelForm):
    class Meta:
        model = IncomingInvoiceExpense
        fields = ["expense","name","description","quantity","unit"]
        
        widgets = {
            "expense" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "description" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "quantity" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : "resize: none;"}),
            "unit" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"})
            

        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(IncomingInvoiceExpenseForm, self).__init__(*args, **kwargs)
        self.fields['expense'].label_from_instance = lambda obj: f"{obj.code} - {obj.name}"
        self.fields['expense'].queryset = Expense.objects.filter(sourceCompany = self.user.profile.sourceCompany)

class SendInvoiceForm(forms.ModelForm):
    class Meta:
        model = SendInvoice
        fields = '__all__'
        
        # widgets = {
        #     "sendInvoiceNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
        #     "theRequest" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
        #     "vessel" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
        #     "billing" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
        #     "orderConfirmation" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
        #     "seller" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
        #     "customer" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
        #     "sendInvoiceDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
        #     "awb" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
        #     "extraDiscountPrice" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
        #     "vat" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
        #     "exchangeRate" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
        #     "paymentDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
        #     "deliveryDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
        #     "deliveryNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
        #     "deliveryNote" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
        #     "careOf" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
        #     "transport" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
        #     "only" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
        #     "ready" : forms.CheckboxInput(attrs = {"class" : "form-check-input", "type" : "checkbox", "role" : "switch", "id" : "textFormOutline"}),
        #     "currency" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "id":"formCurrencySI", "data-mdb-size" : "sm", "data-mdb-filter":"true"})
        # }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SendInvoiceForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)


        self.fields['paymentDate'].input_formats = ["%d/%m/%Y"]
        self.fields['sendInvoiceDate'].input_formats = ["%d/%m/%Y"]
        self.fields['deliveryDate'].input_formats = ["%d/%m/%Y"]
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency'].empty_label = None
        self.fields['seller'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__ourCompany = True)
        self.fields['customer'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__customer = True)
        self.fields['vessel'].queryset = Vessel.objects.filter(sourceCompany = self.user.profile.sourceCompany)
        self.fields['billing'].queryset = Billing.objects.filter(sourceCompany = self.user.profile.sourceCompany)
        
        # if self.instance and hasattr(self.instance, 'customer') and self.instance.customer:
        #     self.fields['vessel'].queryset = Vessel.objects.filter(company=self.instance.customer)
            
        # if self.instance and hasattr(self.instance, 'vessel') and self.instance.vessel:
        #     self.fields['billing'].queryset = Billing.objects.filter(vessel=self.instance.vessel)

        #select'leri foreignkey'lerine göre filtreler
        if 'customer' in self.data:
            try:
                customer_id = int(self.data.get('customer'))
                self.fields['vessel'].queryset = Vessel.objects.filter(company_id=customer_id)
            except (ValueError, TypeError):
                self.fields['vessel'].queryset = Vessel.objects.none()
        elif self.instance and self.instance.customer:
            self.fields['vessel'].queryset = Vessel.objects.filter(company=self.instance.customer)
        else:
            self.fields['vessel'].queryset = Vessel.objects.none()

        if 'vessel' in self.data:
            try:
                vessel_id = int(self.data.get('vessel'))
                self.fields['billing'].queryset = Billing.objects.filter(vessel_id=vessel_id)
            except (ValueError, TypeError):
                self.fields['billing'].queryset = Billing.objects.none()
        elif self.instance and self.instance.vessel:
            self.fields['billing'].queryset = Billing.objects.filter(vessel=self.instance.vessel)
        else:
            self.fields['billing'].queryset = Billing.objects.none()

class SendInvoiceExpenseForm(forms.ModelForm):
    class Meta:
        model = SendInvoiceExpense
        fields = ["expense","name","description","quantity","unit"]
        
        widgets = {
            "expense" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "description" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "quantity" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : "resize: none;"}),
            "unit" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"})
            

        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SendInvoiceExpenseForm, self).__init__(*args, **kwargs)
        self.fields['expense'].label_from_instance = lambda obj: f"{obj.code} - {obj.name}"
        self.fields['expense'].queryset = Expense.objects.filter(sourceCompany = self.user.profile.sourceCompany)



class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["customer","type","paymentDate","sourceBank","amount","currency","description"]
        
        widgets = {
            "paymentNo" : forms.TextInput(attrs = {
                "class" : "form-control form-control-sm",
                "id" : "formOutline-payment-paymentNo",
                "readonly" : "true",
                "rows" : "1",
                "style" : "resize: none;"}),
            "customer" : forms.Select(attrs = {
                "id" : "formOutline-payment-customer"}),
            "type" : forms.Select(attrs = {
                "class" : "form-control form-control-sm form-select select",
                "id" : "formOutline-payment-type",
                "data-mdb-size" : "sm",
                "name" : "paymentType",
                "data-mdb-filter":"true"}),
            "paymentDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {
                "class" : "form-control form-control-sm",
                "id" : "formOutline-payment-paymentDate"}),
            "sourceBank" : forms.Select(attrs = {
                "id" : "formOutline-payment-sourceBank"}),
            "amount" : forms.NumberInput(attrs = {
                "class" : "form-control form-control-sm",
                "id" : "formOutline-payment-amount",
                "rows" : "1",
                "style" : "resize: none;"}),
            "currency" : forms.Select(attrs = {
                "class" : "form-control form-control-sm form-select select",
                "id" : "formOutline-payment-currency",
                "data-mdb-size" : "sm",
                "data-mdb-filter":"true"}),
            "description" : forms.Textarea(attrs = {
                "class" : "form-control form-control-sm",
                "id" : "formOutline-payment-description",
                "rows" : "2"})
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['type'].empty_label = None
        self.fields['paymentDate'].input_formats = ["%d/%m/%Y"]
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency'].empty_label = None
        # self.fields['customer'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany)
        # self.fields['sourceBank'].empty_label = None
        # self.fields['sourceBank'].queryset = SourceBank.objects.filter(company = self.user.profile.sourceCompany)
        # self.fields['sourceBank'].initial = SourceBank.objects.filter(company = self.user.profile.sourceCompany, currency = 106).first()
        # self.fields['sourceBank'].label_from_instance = lambda obj: f"{obj.currency.code} - {obj.ibanNo} - {obj.bankName}"

class ProformaInvoiceForm(forms.ModelForm):
    class Meta:
        model = ProformaInvoice
        fields = '__all__'
        
        widgets = {
            "proformaInvoiceNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "theRequest" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "vessel" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "id":"formVesselPO", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "billing" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "id":"formBillingPO", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "orderConfirmation" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "seller" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "customer" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "proformaInvoiceDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "awb" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "vat" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "exchangeRate" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "paymentDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "deliveryDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "deliveryNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "deliveryNote" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "careOf" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "transport" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "only" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "ready" : forms.CheckboxInput(attrs = {"class" : "form-check-input", "type" : "checkbox", "role" : "switch", "id" : "textFormOutline"}),
            "currency" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "id":"formCurrencyPO", "data-mdb-size" : "sm", "data-mdb-filter":"true"})
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProformaInvoiceForm, self).__init__(*args, **kwargs)
        self.fields['paymentDate'].input_formats = ["%d/%m/%Y"]
        self.fields['proformaInvoiceDate'].input_formats = ["%d/%m/%Y"]
        self.fields['deliveryDate'].input_formats = ["%d/%m/%Y"]
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency'].empty_label = None
        self.fields['seller'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__ourCompany = True)
        self.fields['customer'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__customer = True)
        
        if self.instance and hasattr(self.instance, 'customer') and self.instance.customer:
            self.fields['vessel'].queryset = Vessel.objects.filter(company=self.instance.customer)
            
        if self.instance and hasattr(self.instance, 'vessel') and self.instance.vessel:
            self.fields['billing'].queryset = Billing.objects.filter(vessel=self.instance.vessel)
        
class ProformaInvoiceExpenseForm(forms.ModelForm):
    class Meta:
        model = ProformaInvoiceExpense
        fields = ["expense","name","description","quantity","unitPrice","totalPrice","vat","vatPrice"]
        
        widgets = {
            "expense" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "description" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : ""}),
            "quantity" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : "resize: none;"}),
            "unitPrice" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : "resize: none;"}),
            "totalPRice" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : "resize: none;"}),
            "vat" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : "resize: none;"}),
            "vatPrice" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : "resize: none;"})
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProformaInvoiceExpenseForm, self).__init__(*args, **kwargs)
        self.fields['expense'].queryset = Expense.objects.filter(sourceCompany = self.user.profile.sourceCompany)

class CommericalInvoiceForm(forms.ModelForm):
    class Meta:
        model = CommericalInvoice
        fields = '__all__'
        
        widgets = {
            "commericalInvoiceNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "theRequest" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "vessel" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "billing" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "orderTracking" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "seller" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "customer" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "commericalInvoiceDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "awb" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "vat" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "exchangeRate" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" :  "resize: none;"}),
            "paymentDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "deliveryDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "deliveryNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "deliveryNote" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "", "rows" : "7"}),
            "transport" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"}),
            "currency" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "id":"formCurrencySI", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "only" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" : "resize: none;"})
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CommericalInvoiceForm, self).__init__(*args, **kwargs)
        self.fields['paymentDate'].input_formats = ["%d/%m/%Y"]
        self.fields['commericalInvoiceDate'].input_formats = ["%d/%m/%Y"]
        self.fields['deliveryDate'].input_formats = ["%d/%m/%Y"]
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['currency'].empty_label = None
        self.fields['seller'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__ourCompany = True)
        self.fields['customer'].queryset = Company.objects.filter(sourceCompany = self.user.profile.sourceCompany,role__customer = True)
        
        if self.instance and hasattr(self.instance, 'customer') and self.instance.customer:
            self.fields['vessel'].queryset = Vessel.objects.filter(company=self.instance.customer)
            
        if self.instance and hasattr(self.instance, 'vessel') and self.instance.vessel:
            self.fields['billing'].queryset = Billing.objects.filter(vessel=self.instance.vessel)


class CommericalInvoiceExpenseForm(forms.ModelForm):
    class Meta:
        model = CommericalInvoiceExpense
        fields = ["expense","name","description","quantity","unit"]
        
        widgets = {
            "expense" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "description" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "quantity" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : "resize: none;"}),
            "unit" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"})
            

        }
        
    def __init__(self, *args, **kwargs):
        super(CommericalInvoiceExpenseForm, self).__init__(*args, **kwargs)
        self.fields['expense'].label_from_instance = lambda obj: f"{obj.code} - {obj.name}"

   
class ProformaInvoiceExpenseForm(forms.ModelForm):
    class Meta:
        model = ProformaInvoiceExpense
        fields = ["expense", "name","description","quantity","unit"]
        
        widgets = {
            "expense" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "description" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "quantity" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : "resize: none;"}),
            "unit" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"})
            

        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProformaInvoiceExpenseForm, self).__init__(*args, **kwargs)
        self.fields['expense'].label_from_instance = lambda obj: f"{obj.code} - {obj.name}"
        self.fields['expense'].queryset = Expense.objects.filter(sourceCompany = self.user.profile.sourceCompany)
        
        # if self.instance and hasattr(self.instance, 'maker') and self.instance.maker:
        #     self.fields['makerType'].queryset = MakerType.objects.filter(maker=self.instance.maker)