from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from hr.helpers import set_value_to_immutable_dict
from hr.models import TheCompany, BankAccount
from card.models import Currency
from user.models import  EmployeeType, Team, Department,Certification, Profile, Education, AdditionalPayment

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

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]
    username = forms.CharField(max_length = 50, label = "Username", widget = forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}))
    first_name = forms.CharField(max_length = 50, label = "First Name", widget = forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}))
    last_name = forms.CharField(max_length = 50, label = "Last Name", widget = forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}))
    email = forms.EmailField(label = "E-Mail", widget = forms.EmailInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}))
    password = forms.CharField(min_length = 6, max_length = 20, label = "Password", widget = forms.PasswordInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}))
    confirm = forms.CharField(min_length = 6, max_length = 20, label = "Confirm Password", widget = forms.PasswordInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}))

    def clean(self):
        username = self.cleaned_data.get("username")
        first_name = self.cleaned_data.get("first_name")
        last_name = self.cleaned_data.get("last_name")
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        confirm = self.cleaned_data.get("confirm")

        checkusers = User.objects.all()
        checkmails = User.objects.filter(email = email)
        
        if username == "temp" or username == "root":
            raise forms.ValidationError("This username cannot be used!")
        
        for a in checkusers:
            if str(a) == username:
                raise forms.ValidationError("Already registered with this username!")

        for a in checkmails:
            if str(a.email) == email:
                raise forms.ValidationError("Already registered with this e-mail address!")

        if password and confirm and password != confirm:
            raise forms.ValidationError("Password unconfirmed!")     

        values = {
                    "username" : username,
                    "first_name" : first_name,
                    "last_name" : last_name,
                    "email" : email,
                    "password" : password
                }
        
        return values

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
    username = forms.CharField(max_length = 50, label = "Username", widget = forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}))
    first_name = forms.CharField(max_length = 50, label = "First Name", widget = forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}))
    last_name = forms.CharField(max_length = 50, label = "Last Name", widget = forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}))
    email = forms.EmailField(label = "E-Mail", widget = forms.EmailInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}))
    
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

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        
        widgets = {
            "user" : forms.Select(attrs = {"class" : "form-control form-select", "rows" : "1"}),
            "image" : forms.FileInput(attrs = {"class" : "file-upload-input", "type" : "file", "data-mdb-file-upload" : "file-upload"}),
            "registrationNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "identificationNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "gender" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "birthday" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "motherName" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "fatherName" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "drivingLicence" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "militaryStatus" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "militaryPostponedDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "phone" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "address" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1"}),
            "note" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "2"}),
            "criminalRegistrationNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "socialSecurityNo" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "startDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "socialSecuirtyStartDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "professionCode" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "rows" : "1", "style" :  "resize: none;"}),
            "retirementStatus" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "company" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "degree" : forms.TextInput(attrs = {"class" : "form-control", "rows" : "1", "style" :  "resize: none;"}),
            "education_level" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "salary" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "salaryPerMonth", "rows" : "1", "style" :  "resize: none;"}),
            "salaryCurrency" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "id" : "cselectFormOutline", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "department" : forms.Select(attrs = {"class" : "form-control form-select", "rows" : "1"}),
            "positionType" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true"}),
            "position" : forms.TextInput(attrs = {"class" : "form-control", "rows" : "1", "style" :  "resize: none;"}),
            "language" : forms.Select(attrs = {"class" : "form-control form-select", "rows" : "1"}),
            "theme" : forms.Select(attrs = {"class" : "form-control form-select", "rows" : "1"}),
            "cv" : forms.FileInput(attrs = {"class" : "file-upload-input", "type" : "file", "data-mdb-file-upload" : "file-upload"}),
            "nondisclosureAgreement" : forms.FileInput(attrs = {"class" : "form-control"}),
            "employmentContract" : forms.FileInput(attrs = {"class" : "form-control"}),
        }
        
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['birthday'].input_formats = ["%d/%m/%Y"]
        self.fields['militaryPostponedDate'].input_formats = ["%d/%m/%Y"]
        self.fields['startDate'].input_formats = ["%d/%m/%Y"]
        self.fields['socialSecuirtyStartDate'].input_formats = ["%d/%m/%Y"]
        self.fields['salaryCurrency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['salaryCurrency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"

        

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
        
class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'
        
        widgets = {
            "name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "required" : "", "data-mdb-validation" : "true", "rows" : "1", "style" :  "resize: none;"}),
            "about" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "11"}),
            "members" : forms.SelectMultiple(attrs = {"class" : "form-control form-select select","multiple" : ""}),
        }


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

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'
        
        widgets = {
            "name" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "required" : "", "data-mdb-validation" : "true", "rows" : "1", "style" :  "resize: none;"}),
            "about" : forms.Textarea(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "11"})
        }
        

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ["school","department","education_status","startDate","finishDate"]
        
        widgets = {
            "school" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "department" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "education_status" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true", "style" : ""}),
            "startDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "finishDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"})
            
        }
        
    def __init__(self, *args, **kwargs):
        super(EducationForm, self).__init__(*args, **kwargs)
        self.fields['startDate'].input_formats = ["%d/%m/%Y"]
        self.fields['finishDate'].input_formats = ["%d/%m/%Y"]
        
class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ["school","department","education_status","startDate","finishDate"]
        
        widgets = {
            "school" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "department" : forms.TextInput(attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline", "rows" : "1", "style" : " resize: none;"}),
            "education_status" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true", "style" : ""}),
            "startDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"}),
            "finishDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"})
            
        }
        
    def __init__(self, *args, **kwargs):
        super(EducationForm, self).__init__(*args, **kwargs)
        self.fields['startDate'].input_formats = ["%d/%m/%Y"]
        self.fields['finishDate'].input_formats = ["%d/%m/%Y"]

class AdditionalPaymentForm(forms.ModelForm):
    class Meta:
        model = AdditionalPayment
        fields = ["amount","currency","payment_type","additionalPaymentDate"]
        
        widgets = {
            "amount" : forms.NumberInput(attrs = {"class" : "form-control form-control-sm", "id" : "salaryPerMonth", "rows" : "1", "style" :  "resize: none;"}),
            "currency" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true", "style" : ""}),
            "payment_type" : forms.Select(attrs = {"class" : "form-control form-control-sm form-select select", "data-mdb-size" : "sm", "data-mdb-filter":"true", "style" : ""}),
            "additionalPaymentDate" : forms.DateInput(format=('%d/%m/%Y'),attrs = {"class" : "form-control form-control-sm", "id" : "textFormOutline"})
            
        }
        
    def __init__(self, *args, **kwargs):
        super(AdditionalPaymentForm, self).__init__(*args, **kwargs)
        self.fields['additionalPaymentDate'].input_formats = ["%d/%m/%Y"]
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"

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

