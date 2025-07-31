from django import forms
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.utils.translation import gettext as _

from information.helpers import set_value_to_immutable_dict
from information.models import Company, Contact, Country, City, CompanyGroup, Vessel
from user.models import Team

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


class DateInput(forms.DateInput):
    input_type = 'date'


class CompanyAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CompanyAddForm, self).__init__(*args, **kwargs)
        # if request data is exist
        if self.data:
            # check company_group value to if integer
            # else means, they are sending a new group name as a string
            # or same group name?
            if 'company_group' in self.data and self.data['company_group'] and not self.data['company_group'].isdigit():
                obj, created = CompanyGroup.objects.get_or_create(name=self.data['company_group'])
                # if that company group already exists, change str to of its id
                # if not exist, then use pk of new object
                new_data = set_value_to_immutable_dict(self.data, 'company_group', obj.pk)
                self.data = new_data

        self.fields['key_account'].queryset = User.objects.filter(profile__bonus_right=True)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    def clean(self):
        cleaned_data = super().clean()
        # country and city match control -> Country required! City is not!
        error_message = _("Select a valid choice. That choice is not one of the available choices.")
        if cleaned_data.get('country'):
            try:
                country = Country.objects.get(pk=cleaned_data.get('country').pk)
                if cleaned_data.get('city'):
                    city = City.objects.get(pk=cleaned_data.get('city').pk)
                else:
                    pass
            except Country.DoesNotExist:
                self.add_error('country', error_message)
            except City.DoesNotExist:
                self.add_error('city', error_message)
        else:
            pass

        # team and user match control -> Team required! User (customer representative) required!
        error_message = _("Select a valid choice. That choice is not one of the available choices.")
        if cleaned_data.get('sales_team'):
            if cleaned_data.get('customer_representative'):
                try:
                    team = Team.objects.get(pk=cleaned_data.get('sales_team').pk)
                    user = team.members.get(pk=cleaned_data.get('customer_representative').pk)
                except Team.DoesNotExist:
                    self.add_error('sales_team', error_message)
                except User.DoesNotExist:
                    self.add_error('customer_representative', error_message)
            else:
                pass
        else:
            pass

        return cleaned_data

    class Meta:
        model = Company
        fields = '__all__'


class ContactAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContactAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    def clean(self):
        cleaned_data = super().clean()

        error_message = _("Select a valid choice. That choice is not one of the available choices.")
        already_has = _("This company has already a default person in contact.")

        # default person in contact of and company field match control
        if cleaned_data.get('default_person_in_contact_of') and cleaned_data.get('company'):
            try:
                pic_of = Company.objects.get(pk=cleaned_data.get('default_person_in_contact_of').pk)
                cleaned_data.get('company').get(pk=pic_of.pk)
                if self.instance.default_person_in_contact_of != cleaned_data.get('default_person_in_contact_of'):
                    if hasattr(cleaned_data.get('default_person_in_contact_of'), "default_person_in_contact"):
                        self.add_error('default_person_in_contact_of', already_has)

            except Company.DoesNotExist:
                self.add_error('default_person_in_contact_of', error_message)

        return cleaned_data

    class Meta:
        model = Contact
        fields = '__all__'
        widgets = {
            'birthday': DateInput()
        }


class VesselAddForm(forms.ModelForm):
    flag_url = forms.URLField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(VesselAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    def clean(self):
        cleaned_data = super().clean()

        error_message = _("Select a valid choice. That choice is not one of the available choices.")

        # customer company validation
        if cleaned_data.get('owner_company'):
            try:
                Company.objects.get(pk=cleaned_data.get('owner_company').pk,
                                    company_type__in=["Customer", "Customer & Supplier"])
            except Company.DoesNotExist:
                self.add_error('owner_company', error_message)

        # imo validation
        if cleaned_data.get('imo'):
            try:
                int(cleaned_data.get('imo'))
                if not len(str(cleaned_data.get('imo'))) == 7:
                    self.add_error('imo', _("IMO must consist of 7 digits."))
            except ValueError:
                self.add_error('imo', _("IMO must consist of 7 digits."))

        # company group, company and contacts match control -> company and contact required, group not
        if cleaned_data.get('owner_company'):
            if cleaned_data.get('person_in_contacts'):
                try:
                    # special note: if manager company (group) not selected, then check the company
                    # in the company group null results
                    if not cleaned_data.get('manager_company'):
                        company = Company.objects.get(pk=cleaned_data.get('owner_company').pk,
                                                      company_group__isnull=True)
                    else:
                        company_group = CompanyGroup.objects.get(pk=cleaned_data.get('manager_company').pk)
                        company = company_group.companies.get(pk=cleaned_data.get('owner_company').pk)
                    for contact in cleaned_data.get('person_in_contacts'):
                        company.contacts.get(pk=contact.pk)
                except CompanyGroup.DoesNotExist:
                    self.add_error('manager_company', error_message)
                except Company.DoesNotExist:
                    self.add_error('owner_company', error_message)
                except Contact.DoesNotExist:
                    self.add_error('person_in_contacts', error_message)
            else:
                pass
        else:
            pass

        return cleaned_data

    class Meta:
        model = Vessel
        exclude = ['flag', 'status']
