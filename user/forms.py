from concurrent.futures.thread import ThreadPoolExecutor

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordResetForm
from django.contrib.auth.models import User

from user.models import Profile, User, AccessAuthorization,DataAuthorization

from core.utils import set_form_widget, WidgetStyle

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


class UserLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)


class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        read_only_fields = Profile.get_read_only_fields()
        for name in self.fields:
            # check if the field is can be changed
            # this will ensure the field security for backend
            if name in read_only_fields:
                self.fields[name].disabled = True

            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = Profile
        exclude = ['user', 'bonus_right', 'cv_resume', 'nondisclosure_agreement', 'employment_contract',
                   'ssi_statement_of_employment']


class UserInfoForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(UserInfoForm, self).__init__(*args, **kwargs)
        read_only_fields = ['first_name', 'last_name']
        for name in self.fields:
            # check if the field is can be changed
            # this will ensure the field security for backend
            if name in read_only_fields:
                self.fields[name].disabled = True

            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class CustomPasswordResetForm(PasswordResetForm):
    """
    send mails asynchronously when password resetting
    """
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        ThreadPoolExecutor().submit(super().send_mail, subject_template_name, email_template_name,
                                    context, from_email, to_email, html_email_template_name)

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
    username = forms.CharField(max_length = 50, label = "Username", widget = forms.TextInput(attrs = {"class" : "form-control form-control-sm", "readonly" : "", "id" : "textFormOutline", "rows" : "1", "style" : "resize: none;"}))
    first_name = forms.CharField(max_length = 50, label = "First Name", widget = forms.TextInput(attrs = {"class" : "form-control form-control-sm", "readonly" : "", "id" : "textFormOutline", "rows" : "1", "style" : "resize: none;"}))
    last_name = forms.CharField(max_length = 50, label = "Last Name", widget = forms.TextInput(attrs = {"class" : "form-control form-control-sm", "readonly" : "", "id" : "textFormOutline", "rows" : "1", "style" : "resize: none;"}))
    email = forms.EmailField(label = "E-Mail", widget = forms.EmailInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : "background-color: #fff; resize: none;"}))
    
    def clean(self):
        username = self.cleaned_data.get("username")
        first_name = self.cleaned_data.get("first_name")
        last_name = self.cleaned_data.get("last_name")
        email = self.cleaned_data.get("email")
        
        if username == "temp" or username == "root":
            raise forms.ValidationError("This username cannot be used!")    

        values = {
                    "username" : username,
                    "first_name" : first_name,
                    "last_name" : last_name,
                    "email" : email
                }
        
        return values
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'

    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

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