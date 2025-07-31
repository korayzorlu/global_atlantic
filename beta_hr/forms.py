from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from beta_hr.helpers import set_value_to_immutable_dict
from beta_hr.models import TheCompany, BankAccount
from beta_profile.models import  Document, EmployeeType, Team, Department,Certification, Profile, Title

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
    "CheckboxInput": {
        'class': 'custom-control-input'
    },
    "ClearableFileInput": {
        'class': 'file',
        'data-show-preview': 'false'
    },
    "else": {
        'class': 'form-control'
    }
}


class TheCompanyForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = TheCompany
        exclude = ['updated_by']


class BankAccountAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = BankAccount
        exclude = ['the_company']


class DateInput(forms.DateInput):
    input_type = 'date'


class UserCreateForm(UserCreationForm):
    set_default_password = False
    # team = forms.ModelMultipleChoiceField(
    #     queryset=Team.objects.all(), required=False
    # )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        default_password = kwargs.pop("default_password", None)
        super(UserCreateForm, self).__init__(*args, **kwargs)
        if self.data:
            # check if the passwords entered else auto-generate
            if not self.data.get('password1', None) and not self.data.get('password2', None):
                self.set_default_password = True
                new_data = set_value_to_immutable_dict(self.data, 'password1', default_password)
                new_data = set_value_to_immutable_dict(new_data, 'password2', default_password)
                self.data = new_data
        for name in self.fields:
            # custom help text for passwords and make them not required in frontend
            if 'password' in name:
                self.fields[name].widget.attrs.update({"placeholder": _("Leave this field blank for auto-generation")})
                self.fields[name].required = False
            else:
                self.fields[name].help_text = ""

            # add some special classes depends on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])


class UserEditForm(forms.ModelForm):
    # team = forms.ModelMultipleChoiceField(
    #     queryset=Team.objects.all(), required=False
    # )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depends on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])


class ProfileAddForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(ProfileAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # if name == 'department':
            #     self.fields[name] =  forms.ModelChoiceField(queryset=Department.objects.all())
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])
                    

    class Meta:
        model = Profile
        exclude = ['user','bonus_rate', 'language', 'theme']
        widgets = {
            'birthday': DateInput()
        }


class EmployeeTypeAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EmployeeTypeAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = EmployeeType
        fields = '__all__'


class TeamAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TeamAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    def clean_lead(self):
        members = self.cleaned_data['members']
        lead = self.cleaned_data['lead']
        if lead not in members:
            self.add_error('lead', "Lead must be in Team")
        return lead
    class Meta:
        model = Team
        fields = '__all__'


class DepartmentAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DepartmentAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = Department
        fields = '__all__'
        
        
        
class CertifcationAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = Certification
        fields = '__all__'


class TitleAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TitleAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = Title
        fields = '__all__'
        
class DocumentAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TitleAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = Document
        fields = '__all__'