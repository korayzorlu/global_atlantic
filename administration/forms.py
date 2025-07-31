from concurrent.futures.thread import ThreadPoolExecutor

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordResetForm
from django.contrib.auth.models import User

from administration.models import AccessAuthorization,DataAuthorization
from user.models import Profile
from source.models import Company as SourceCompany

from core.utils import WidgetStyle, set_form_widget

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

class UserAuthorizationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["accessAuthorization","dataAuthorization"]
        
        widgets = {
            "accessAuthorization" : forms.CheckboxSelectMultiple(attrs = {"class" : "form-check-input", "type" : "checkbox", "role" : "switch", "id" : "formOutline-profile-accessAuthoriation"}),
            "dataAuthorization" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "id" : "formOutline-profile-dataAuthorization", "data-mdb-size" : "sm", "data-mdb-filter":"true"})
        }
        
    def __init__(self, *args, **kwargs):
        super(UserAuthorizationForm, self).__init__(*args, **kwargs)
 
class AccessAuthorizationForm(forms.ModelForm):
    class Meta:
        model = AccessAuthorization
        fields = '__all__'
        
        widgets = {
            "name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-request-name", "rows" : "1", "style" :  "resize: none;"}),
            "code" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-request-code", "rows" : "1", "style" :  "resize: none;"})
        }
        
    
        
    def __init__(self, *args, **kwargs):
        super(AccessAuthorizationForm, self).__init__(*args, **kwargs)
        
class DataAuthorizationForm(forms.ModelForm):
    class Meta:
        model = DataAuthorization
        fields = '__all__'
        
        widgets = {
            "name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-request-name", "rows" : "1", "style" :  "resize: none;"}),
            "code" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-request-code", "rows" : "1", "style" :  "resize: none;"})
        }
        
    
        
    def __init__(self, *args, **kwargs):
        super(DataAuthorizationForm, self).__init__(*args, **kwargs)
        
class CompanyForm(forms.ModelForm):
    class Meta:
        model = SourceCompany
        fields = ["name","formalName","country","city","address","vatOffice","vatNo","phone1","fax","logo","saleRequestCode","saleInquiryCode",
                  "saleQuotationCode","saleOrderConfirmationCode","saleOrderNotConfirmationCode","salePurchaseOrderCode","saleDispatchOrderCode",
                  "serviceAcceptaneCode","serviceOfferCode","serviceOfferCode","purchasingProjectCode","purchasingInquiryCode",
                  "purchasingPurchaseOrderCode","accountIncomingInvoiceCode","accountSendInvoiceCode","accountProformaInvoiceCode",
                  "accountCommercialInvoiceCode","accountPaymentCode","mikroDBName"]
        
        widgets = {
            "name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-name", "rows" : "1", "style" :  "resize: none;"}),
            "formalName" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-code", "rows" : "1", "style" :  "resize: none;"}),
            "country" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "id" : "formOutline-sourceCompnay-country", "data-mdb-size" : "sm", "data-mdb-filter" : "true", "data-mdb-placeholder" : "Country", "style" : ""}),
            "city" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "id" : "formOutline-sourceCompnay-city", "data-mdb-size" : "sm", "data-mdb-filter" : "true", "data-mdb-placeholder" : "City", "style" : ""}),
            "address" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-address", "data-mdb-showcounter" : "true", "maxlength" : "100", "rows" : "1", "style" : " resize: none;"}),
            "vatOffice" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-vatOffice", "rows" : "1", "style" : " resize: none;"}),
            "vatNo" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-vatNo", "rows" : "1", "style" : " resize: none;"}),
            "phone1" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-phone1", "rows" : "1", "style" : " resize: none;"}),
            "fax" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-fax", "rows" : "1", "style" : " resize: none;"}),
            "logo" : forms.FileInput(attrs = {"class" : "file-upload-input", "id" : "formOutline-sourceCompnay-logo", "type" : "file", "data-mdb-file-upload" : "file-upload"}),
            "saleRequestCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-saleRequestCode", "rows" : "1", "style" :  "resize: none;"}),
            "saleInquiryCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-saleInquiryCode", "rows" : "1", "style" :  "resize: none;"}),
            "saleQuotationCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-saleQuotationCode", "rows" : "1", "style" :  "resize: none;"}),
            "saleOrderConfirmationCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-saleOrderConfirmationCode", "rows" : "1", "style" :  "resize: none;"}),
            "saleOrderNotConfirmationCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-saleOrderNotConfirmationCode", "rows" : "1", "style" :  "resize: none;"}),
            "salePurchaseOrderCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-salePurchaseOrderCode", "rows" : "1", "style" :  "resize: none;"}),
            "saleDispatchOrderCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-saleDispatchOrderCode", "rows" : "1", "style" :  "resize: none;"}),
            "serviceAcceptaneCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-serviceAcceptaneCode", "rows" : "1", "style" :  "resize: none;"}),
            "serviceOfferCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-serviceOfferCode", "rows" : "1", "style" :  "resize: none;"}),
            "purchasingProjectCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-purchasingProjectCode", "rows" : "1", "style" :  "resize: none;"}),
            "purchasingInquiryCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-purchasingInquiryCode", "rows" : "1", "style" :  "resize: none;"}),
            "purchasingPurchaseOrderCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-purchasingPurchaseOrderCode", "rows" : "1", "style" :  "resize: none;"}),
            "accountIncomingInvoiceCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-accountIncomingInvoiceCode", "rows" : "1", "style" :  "resize: none;"}),
            "accountSendInvoiceCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-accountSendInvoiceCode", "rows" : "1", "style" :  "resize: none;"}),
            "accountProformaInvoiceCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-accountProformaInvoiceCode", "rows" : "1", "style" :  "resize: none;"}),
            "accountCommercialInvoiceCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-accountCommercialgInvoiceCode", "rows" : "1", "style" :  "resize: none;"}),
            "accountPaymentCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-accountPaymentCode", "rows" : "1", "style" :  "resize: none;"}),
            "mikroDBName" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-sourceCompnay-mikroDBName", "rows" : "1", "style" :  "resize: none;"})
        }
        
    
        
    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)

class CompanySendInvoicePdfHtmlForm(forms.ModelForm):
    class Meta:
        model = SourceCompany
        fields = ["sendInvoicePdfHtml"]
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CompanySendInvoicePdfHtmlForm, self).__init__(*args, **kwargs)

        # set_form_widget(self, forms)

        # #special situations
        # print(self.fields['sendInvoicePdfHtml'].widget)

        # self.fields['sendInvoicePdfHtml'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"about","rows":"1"}], form=self).attr())


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username","first_name","last_name","password","email"]
        
        widgets = {
            "username" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-userList-username", "rows" : "1", "style" :  "resize: none;"}),
            "first_name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-userList-firstName", "rows" : "1", "style" :  "resize: none;"}),
            "last_name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-userList-lastName", "rows" : "1", "style" :  "resize: none;"}),
            "password" : forms.PasswordInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-userList-password", "rows" : "1", "style" :  "resize: none;"}),
            "email" : forms.EmailInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-userList-email", "rows" : "1", "style" :  "resize: none;"})
        }
        
    
        
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        
class UserDetailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username","first_name","last_name","email"]
        
        widgets = {
            "username" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-userList-username", "rows" : "1", "style" :  "resize: none;"}),
            "first_name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-userList-firstName", "rows" : "1", "style" :  "resize: none;"}),
            "last_name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-userList-lastName", "rows" : "1", "style" :  "resize: none;"}),
            "email" : forms.EmailInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-userList-email", "rows" : "1", "style" :  "resize: none;"})
        }
        
    
        
    def __init__(self, *args, **kwargs):
        super(UserDetailForm, self).__init__(*args, **kwargs)

class UserSourceCompany(forms.ModelForm):
    class Meta:
        model = SourceCompany
        fields = '__all__'
        
        widgets = {
            #"part" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select selectPart", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "formOutline-userSourceCompany-name", "rows" : "1", "style" :  "resize: none;"})
        }
        
    def __init__(self, *args, **kwargs):
        super(UserSourceCompany, self).__init__(*args, **kwargs)