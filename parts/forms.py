from django import forms
from django.utils.translation import gettext_lazy as _

from information.models import Company
from parts.helpers import set_value_to_immutable_dict
from parts.models import Maker, MakerType, Manufacturer, Part, PartManufacturer, PartCompatibility, PartSupplier, \
    RelatedSet, PartUnit, MakerCategory, MakerTypeCategory, PartCategory

STYLES = {
    "Select": {
        'class': 'form-control select-search'
    },
    "SelectMultiple": {
        'class': 'form-control select-search'
    },
    "Textarea": {
        'class': 'form-control',
        'style': 'height:38px; min-height:38px',
    },
    "ClearableFileInput": {
        'class': 'form-control-uniform upload-preview',
    },
    "else": {
        'class': 'form-control'
    }
}


class MakerAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MakerAddForm, self).__init__(*args, **kwargs)
        # dynamically creating new objects ans adding to request post
        if self.data:
            if 'category' in self.data and self.data.getlist('category'):
                category_new = []
                for category in self.data.getlist('category'):
                    if not category.isdigit():
                        obj, created = MakerCategory.objects.get_or_create(name=category)
                        category_new.append(obj.pk)
                    else:
                        category_new.append(category)
                new_data = set_value_to_immutable_dict(self.data, 'category', category_new)
                self.data = new_data
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = Maker
        fields = '__all__'


class MakerTypeAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MakerTypeAddForm, self).__init__(*args, **kwargs)
        # dynamically creating new objects ans adding to request post
        if self.data:
            if 'category' in self.data and self.data.getlist('category'):
                category_new = []
                for category in self.data.getlist('category'):
                    if not category.isdigit():
                        obj, created = MakerTypeCategory.objects.get_or_create(name=category)
                        category_new.append(obj.pk)
                    else:
                        category_new.append(category)
                new_data = set_value_to_immutable_dict(self.data, 'category', category_new)
                self.data = new_data
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = MakerType
        exclude = ['maker']


class ManufacturerAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ManufacturerAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = Manufacturer
        fields = '__all__'


class PartAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartAddForm, self).__init__(*args, **kwargs)
        # if request data is exist
        if self.data:
            # check unit value to if it is integer
            # else means, they are sending a new unit as a string
            # or already existed unit?
            if 'unit' in self.data and self.data['unit'] and not self.data['unit'].isdigit():
                obj, created = PartUnit.objects.get_or_create(name=self.data['unit'])
                # if the unit already exists, change str to it's id
                # if not exist, then use pk of the new object
                new_data = set_value_to_immutable_dict(self.data, 'unit', obj.pk)
                self.data = new_data
            if 'category' in self.data and self.data['category'] and not self.data['category'].isdigit():
                obj, created = PartCategory.objects.get_or_create(name=self.data['category'])
                new_data = set_value_to_immutable_dict(self.data, 'category', obj.pk)
                self.data = new_data

        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = Part
        fields = '__all__'


class PartManufacturerAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartManufacturerAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = PartManufacturer
        fields = '__all__'


class PartCompatibilityAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartCompatibilityAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    def clean(self):
        cleaned_data = super().clean()
        # maker and maker type match control -> both of them required!
        error_message = _("Select a valid choice. That choice is not one of the available choices.")
        if cleaned_data.get('maker'):
            if cleaned_data.get('maker_type'):
                try:
                    maker = Maker.objects.get(pk=cleaned_data.get('maker').pk)
                    maker_type = maker.maker_types.get(pk=cleaned_data.get('maker_type').pk)
                except Maker.DoesNotExist:
                    self.add_error('maker', error_message)
                except MakerType.DoesNotExist:
                    self.add_error('maker_type', error_message)
            else:
                pass
        else:
            pass

        return cleaned_data

    class Meta:
        model = PartCompatibility
        fields = '__all__'


class PartSupplierAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartSupplierAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = PartSupplier
        fields = '__all__'


class RelatedSetAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RelatedSetAddForm, self).__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = RelatedSet
        fields = '__all__'
