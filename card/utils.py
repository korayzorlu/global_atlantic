import icu
import random
import string

from core.utils import WidgetStyle

def locale_upper(text, locale_str):
    # UnicodeString ile metni büyük harfe çeviriyoruz
    locale = icu.Locale(locale_str)
    ustring = icu.UnicodeString(text)
    return ustring.toUpper(locale)

def locale_lower(text, locale_str):
    # UnicodeString ile metni küçük harfe çeviriyoruz
    locale = icu.Locale(locale_str)
    ustring = icu.UnicodeString(text)
    return ustring.toLower(locale)

def locale_capitalize(text, locale_str):
    # UnicodeString ile metni baş harfi büyük yaparak çeviriyoruz
    locale = icu.Locale(locale_str)
    ustring = icu.UnicodeString(text)
    return ustring.capitalize(locale)

def set_form_widget(self, forms):
    appModelTag = f"{self._meta.model._meta.app_label}-{self._meta.model._meta.model_name}"
    characters = string.ascii_letters + string.digits
    digitKey = ''.join(random.choice(characters) for _ in range(6))
    
    for field_name, field in self.fields.items():
        if isinstance(field, forms.CharField):
            field.widget = forms.TextInput(attrs = WidgetStyle(widget="TextInput").attr())

        elif isinstance(field, forms.ModelChoiceField):
            field.widget = forms.Select(attrs = WidgetStyle(widget="Select").attr())

        elif isinstance(field, forms.TypedChoiceField):
            field.widget.attrs.update(WidgetStyle(widget="Select").attr())

        elif isinstance(field, forms.ChoiceField):
            field.widget = forms.Select(attrs = WidgetStyle(widget="Select").attr())

        elif isinstance(field, forms.FloatField) or isinstance(field, forms.IntegerField):
            field.widget = forms.NumberInput(attrs = WidgetStyle(widget="NumberInput").attr())

        elif isinstance(field, forms.Textarea):
            field.widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea").attr())

        elif isinstance(field, forms.BooleanField):
            field.widget = forms.CheckboxInput(attrs = WidgetStyle(widget="CheckboxInput").attr())

        elif isinstance(field, forms.FileField):
            field.widget = forms.FileInput(attrs = WidgetStyle(widget="FileInput").attr())

        field.widget.attrs['id'] = f"formOutline-{appModelTag}-{field_name}-{digitKey}"