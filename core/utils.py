import random
import string

class WidgetStyle():
    def __init__(self, widget, textLength=None, customParameters=None, form=None):
        self.widget = widget
        self.textLength = textLength
        self.customParameters = customParameters

        if self.widget == "TextInput":
            self.attrs = {
                "class" : "form-control form-control-sm",
                "rows" : "1",
                "style" :  "resize: none;"
            }

        elif self.widget == "Textarea":
            self.attrs = {
                "class" : "form-control form-control-sm",
                "style" :  "resize: none;"
            }

        elif self.widget == "NumberInput":
            self.attrs = {
                "class" : "form-control form-control-sm",
                "step": "0.01",
                "rows" : "1",
                "style" :  "resize: none;"
            }

        elif self.widget == "CheckboxInput":
            self.attrs = {
                "class" : "form-check-input",
                "type" : "checkbox",
                "role" : "switch",
            }

        elif self.widget == "Select":
            self.attrs = {
                "class" : "form-control form-control-sm form-select select",
                "data-mdb-size" : "sm",
                "data-mdb-filter":"true"
            }

        elif self.widget == "FileInput":
            self.attrs = {
                "class" : "file-upload-input",
                "type" : "file",
                "data-mdb-file-upload" : "file-upload"
            }

        elif self.widget == "DateInput":
            self.attrs = {
                "class" : "form-control form-control-sm",
                "rows" : "1",
                "style" :  "resize: none;"
            }
        
        elif self.widget == "TextInput":
            self.attrs = {
                "class" : "form-control form-control-sm",
                "rows" : "1",
                "style" :  "resize: none;"
            }

        else:
            self.attrs = {}
        
        if self.customParameters:
            for parameter in self.customParameters:
                for key, value in parameter.items():
                    self.attrs[key] = value
                    
                    if key == "id":
                        appModelTag = f"{form._meta.model._meta.app_label}-{form._meta.model._meta.model_name}"
                        characters = string.ascii_letters + string.digits
                        digitKey = ''.join(random.choice(characters) for _ in range(6))
                        self.attrs['id'] = f"formOutline-{appModelTag}-{value}-{digitKey}"

    def attr(self):
        return self.attrs
    
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

        elif isinstance(field, forms.DateField):
            field.widget = forms.DateInput(attrs = WidgetStyle(widget="DateInput").attr(), format=('%d/%m/%Y'))

        field.widget.attrs['id'] = f"formOutline-{appModelTag}-{field_name}-{digitKey}"