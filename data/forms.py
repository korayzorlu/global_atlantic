from django import forms

from information.helpers import set_value_to_immutable_dict

from core.utils import WidgetStyle, set_form_widget

from .models import *  
        
class MakerForm(forms.ModelForm):
    class Meta:
        model = Maker
        fields = ["name", "info"]
        
    def __init__(self, *args, **kwargs):
        super(MakerForm, self).__init__(*args, **kwargs)
        
        set_form_widget(self, forms)

        self.fields['info'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"rows":"1"}]).attr())
        
class MakerTypeForm(forms.ModelForm):
    class Meta:
        model = MakerType
        fields = ["name", "type", "note"]

    def __init__(self, *args, **kwargs):
        super(MakerForm, self).__init__(*args, **kwargs)
        
        set_form_widget(self, forms)
        
class PartUniqueForm(forms.ModelForm):
    class Meta:
        model = PartUnique
        fields = ["description"]
        
        widgets = {
            "description" : forms.TextInput(attrs = {"class" : "form-control", "rows" : "1", "style" : "resize: none;"})
        }
        
class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = '__all__'
        
    def clean(self):
        cleaned_data = super().clean()
        
        part = cleaned_data.get("partUnique")
        
        maker = cleaned_data.get("maker")
        type = cleaned_data.get("type")
        manufacturer = cleaned_data.get("manufacturer")
        partNo = cleaned_data.get("partNo")
        group = cleaned_data.get("group")
        techncialSpecification = cleaned_data.get("techncialSpecification")
        description = cleaned_data.get("description")
        hsCode = cleaned_data.get("hsCode")
        crossRef = cleaned_data.get("crossRef")
        ourRef = cleaned_data.get("ourRef")
        drawingNr = cleaned_data.get("drawingNr")
        barcode = cleaned_data.get("barcode")
        quantity = cleaned_data.get("quantity")
        unit = cleaned_data.get("unit")
        buyingPrice = cleaned_data.get("buyingPrice")
        retailPrice = cleaned_data.get("retailPrice")
        dealerPrice = cleaned_data.get("dealerPrice")
        wholesalePrice = cleaned_data.get("wholesalePrice")
        currency = cleaned_data.get("currency")
        note = cleaned_data.get("note")
        
        # if not maker:
        #     raise forms.ValidationError(
        #         {"maker": "You must be fill required fields."},
        #         code='invalid'
        # )
        
        if not description:
            raise forms.ValidationError(
                {"description": "You must be fill required fields."},
                code='invalid'
            )

        if part:
            #unique = part.partUnique
            unique = part
        
            values = {
                "unique" : unique,
                "maker" : maker,
                "type" : type,
                "manufacturer" : manufacturer,
                "partNo" : partNo,
                "group" : group,
                "techncialSpecification" : techncialSpecification,
                "description" : description,
                "crossRef" : crossRef,
                "ourRef" : ourRef,
                "drawingNr" : drawingNr,
                "barcode" : barcode,
                "quantity" : quantity,
                "unit" : unit,
                "buyingPrice" : buyingPrice,
                "retailPrice" : retailPrice,
                "dealerPrice" : dealerPrice,
                "wholesalePrice" : wholesalePrice,
                "currency" : currency,
                "note" : note
            }
        
        else:
            values = {
                "maker" : maker,
                "type" : type,
                "manufacturer" : manufacturer,
                "partNo" : partNo,
                "group" : group,
                "techncialSpecification" : techncialSpecification,
                "description" : description,
                "crossRef" : crossRef,
                "ourRef" : ourRef,
                "drawingNr" : drawingNr,
                "barcode" : barcode,
                "quantity" : quantity,
                "unit" : unit,
                "buyingPrice" : buyingPrice,
                "retailPrice" : retailPrice,
                "dealerPrice" : dealerPrice,
                "wholesalePrice" : wholesalePrice,
                "currency" : currency,
                "note" : note
            }
        
        return values
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PartForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['partUnique'].widget.attrs = {}
        self.fields['techncialSpecification'].widget.attrs = {}
        self.fields['description'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"rows":"1","data-mdb-validation":"true","required":"true"}]).attr())
        self.fields['note'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"note","rows":"2"}], form=self).attr())

        #self.fields['about'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"rows":"1"}]).attr())

        #self.fields['maker'].empty_label = None
        #self.fields['type'].queryset = MakerType.objects.none()
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        #self.fields['partUnique'].queryset = Part.objects.all().order_by("-partUnique")
        self.fields['partUnique'].queryset = PartUnique.objects.none()
        #self.fields['partUnique'].label_from_instance = lambda obj: f"{obj.partUnique}.{str(obj.partUniqueCode).zfill(3)} | {obj.partNo} | {obj.maker} | {obj.type}"
        self.fields['partUnique'].queryset = PartUnique.objects.none()
        self.fields['maker'].queryset = Maker.objects.filter(sourceCompany = self.user.profile.sourceCompany).order_by("name")

        if 'maker' in self.data:
            try:
                maker_id = int(self.data.get('maker'))
                self.fields['type'].queryset = MakerType.objects.filter(maker_id=maker_id)
            except (ValueError, TypeError):
                self.fields['type'].queryset = MakerType.objects.none()
        elif self.instance and self.instance.maker:
            self.fields['type'].queryset = MakerType.objects.filter(maker=self.instance.maker)
        else:
            self.fields['type'].queryset = MakerType.objects.none()
        
        #select'leri foreignkey'lerine göre filtreler
        # if self.instance and hasattr(self.instance, 'maker') and self.instance.maker:
        #     self.fields['type'].queryset = MakerType.objects.filter(sourceCompany = self.user.profile.sourceCompany,maker=self.instance.maker)
        
        if "partUnique" in self.data:
            self.fields['partUnique'].queryset = PartUnique.objects.filter(sourceCompany = self.user.profile.sourceCompany)
            
        elif self.instance.pk:
            self.fields['partUnique'].queryset = PartUnique.objects.filter(sourceCompany = self.user.profile.sourceCompany,pk=self.instance.partUnique.pk)

class PartImageForm(forms.ModelForm):
    class Meta:
        model = PartImage
        fields = ["image"]
        
        widgets = {
            "image" : forms.FileInput(attrs = {"class" : "file-upload-input", "id" : "offerImageUpload", "type" : "file", "data-mdb-file-upload" : "file-upload"})
        }
        
    def __init__(self, *args, **kwargs):
        super(PartImageForm, self).__init__(*args, **kwargs)
        
class PartUpdateForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PartUpdateForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['partUnique'].widget.attrs = {}
        self.fields['description'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"rows":"1","data-mdb-validation":"true","required":"true"}]).attr())
        self.fields['note'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"rows":"2"}]).attr())

        #self.fields['maker'].empty_label = None
        self.fields['currency'].queryset = Currency.objects.all().order_by("-code")
        self.fields['currency'].label_from_instance = lambda obj: f"{obj.code} {obj.symbol}"
        self.fields['maker'].queryset = Maker.objects.filter(sourceCompany = self.user.profile.sourceCompany).order_by("name")

        if 'maker' in self.data:
            try:
                maker_id = int(self.data.get('maker'))
                self.fields['type'].queryset = MakerType.objects.filter(maker_id=maker_id)
            except (ValueError, TypeError):
                self.fields['type'].queryset = MakerType.objects.none()
        elif self.instance and self.instance.maker:
            self.fields['type'].queryset = MakerType.objects.filter(maker=self.instance.maker)
        else:
            self.fields['type'].queryset = MakerType.objects.none()

class ServiceCardForm(forms.ModelForm):
    class Meta:
        model = ServiceCard
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(ServiceCardForm, self).__init__(*args, **kwargs)
        
        set_form_widget(self, forms)

        #special situations
        self.fields['name'].widget.attrs.update(WidgetStyle(widget="TextInput", customParameters=[{"data-mdb-validation":"true","required":"true"}]).attr())
        self.fields['code'].widget.attrs.update(WidgetStyle(widget="TextInput", customParameters=[{"data-mdb-validation":"true","required":"true"}]).attr())
        self.fields['about'].widget = forms.Textarea(attrs = WidgetStyle(widget="Textarea", customParameters=[{"id":"about","rows":"2"}], form=self).attr())

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)

        set_form_widget(self, forms)

        #special situations
        self.fields['name'].widget.attrs.update(WidgetStyle(widget="TextInput", customParameters=[{"data-mdb-validation":"true","required":"true"}]).attr())
        self.fields['code'].widget.attrs.update(WidgetStyle(widget="TextInput", customParameters=[{"data-mdb-validation":"true","required":"true"}]).attr())

        #self.fields['city'].queryset = City.objects.none()
        
class ExcelForm(forms.ModelForm):
    class Meta:
        model = Excel
        fields = ["file"]
        
        widgets = {
            "file" : forms.FileInput(attrs = {"class" : "form-control", "accept" : ".xlsx"})
        }