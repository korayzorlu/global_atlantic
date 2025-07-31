from concurrent.futures.thread import ThreadPoolExecutor

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordResetForm
from django.contrib.auth.models import User

from beta_profile.models import Profile

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
