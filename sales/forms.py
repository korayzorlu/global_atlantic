import datetime

from django import forms
from django.db.models import fields
from django.utils.translation import gettext_lazy as _

from information.models import Vessel, Contact
from parts.models import MakerType
from sales.models import ClaimsFollowUp, QuotationPart, Request, Inquiry, Quotation, OrderConfirmation, OrderNotConfirmation, Delivery, DeliveryTransportation, DeliveryTax, \
    DeliveryPacking, DeliveryCustoms, DeliveryInsurance, PurchaseOrder, Reason

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
    "CheckboxSelectMultiple":{
        'class': 'column-checkbox',
        'style':'padding: 10px;'
    },
    "else": {
        'class': 'form-control'
    }
}


class DateInput(forms.DateInput):
    input_type = 'date'


class ProjectRequestForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    def clean(self):
        cleaned_data = super().clean()
        # customer, vessel, and contact match control -> All of them required!
        error_message = _("Select a valid choice. That choice is not one of the available choices.")
        if cleaned_data.get('customer') and cleaned_data.get('vessel') and cleaned_data.get('person_in_contact'):
            # no need to customer check, it is done by parent clean (check the request model)
            customer = cleaned_data.get('customer')
            try:
                vessel = customer.vessels.get(pk=cleaned_data.get('vessel').pk)
            except Vessel.DoesNotExist:
                self.add_error('vessel', error_message)
            try:
                person_in_contact = customer.contacts.get(pk=cleaned_data.get('person_in_contact').pk)
            except Contact.DoesNotExist:
                self.add_error('person_in_contact', error_message)
        else:
            pass
        # maker, and maker type match control -> All of them required!
        if cleaned_data.get('maker') and cleaned_data.get('maker_type'):
            maker = cleaned_data.get('maker')
            try:
                maker_type = maker.maker_types.get(pk=cleaned_data.get('maker_type').pk)
            except MakerType.DoesNotExist:
                self.add_error('maker_type', error_message)
        else:
            pass
        
        if cleaned_data.get('request_date'):
            error_message = _("You can't add a request date before project date")
            if self.instance.project.project_date > cleaned_data.get('request_date'):       
                self.add_error('request_date', error_message) 
            else:
                pass
        else:
            pass
        return cleaned_data

    class Meta:
        model = Request
        exclude = ['project', 'no', 'creator']
        widgets = {
            'request_date': DateInput()
        }


class ProjectCreateRequestForm(forms.ModelForm):
    project_date = forms.DateField(initial=datetime.date.today, widget=DateInput)
    project_deadline = forms.DateField(widget=DateInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    def clean(self):
        cleaned_data = super().clean()
        # customer, vessel, and contact match control -> All of them required!
        error_message = _("Select a valid choice. That choice is not one of the available choices.")
        if cleaned_data.get('customer') and cleaned_data.get('vessel') and cleaned_data.get('person_in_contact'):
            # no need to customer check, it is done by parent clean (check the request model)
            customer = cleaned_data.get('customer')
            try:
                vessel = customer.vessels.get(pk=cleaned_data.get('vessel').pk)
            except Vessel.DoesNotExist:
                self.add_error('vessel', error_message)
            try:
                person_in_contact = customer.contacts.get(pk=cleaned_data.get('person_in_contact').pk)
            except Contact.DoesNotExist:
                self.add_error('person_in_contact', error_message)
        else:
            pass
        # maker, and maker type match control -> All of them required!
        if cleaned_data.get('maker') and cleaned_data.get('maker_type'):
            maker = cleaned_data.get('maker')
            try:
                maker_type = maker.maker_types.get(pk=cleaned_data.get('maker_type').pk)
            except MakerType.DoesNotExist:
                self.add_error('maker_type', error_message)
        else:
            pass
        
        if cleaned_data.get('project_date') and cleaned_data.get('project_deadline'):
            error_message = _("You can't add a project deadline before project date")
            if cleaned_data.get('project_date') >= cleaned_data.get('project_deadline'):       
                self.add_error('project_deadline', error_message) 
            else:
                pass
        else:
            pass
        return cleaned_data

    class Meta:
        model = Request
        exclude = ['project', 'no', 'creator', 'request_date', 'currency', 'customer_ref']


class ProjectInquiryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = Inquiry
        exclude = ['project', 'no', 'creator']
        widgets = {
            'inquiry_date': DateInput()
        }


class ProjectQuotationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = Quotation
        exclude = ['project', 'no', 'creator','is_notified']
        widgets = {
            'quotation_date': DateInput()
        }


class OrderConfirmationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = OrderConfirmation
        fields = ['note']
        
        
class MySelectMultiple(forms.SelectMultiple):
    def render_option(self, selected_choices, option_value, option_label):
        # original forms.Select code #
        return u'<option custom_attribute="foo">...</option>' 
           
class OrderNotConfirmationForm(forms.ModelForm):
    REASON_CHOICES = (
        ('HP', _('High Price')),
        ('LQ', _('Low Quality')),
        ('DO', _('Delayed Order')),
        ('NN', _('No Need')),
        ('PO', _('Pending Order')),
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])
                
    reason_choices = forms.ChoiceField(choices = REASON_CHOICES, widget=MySelectMultiple(), required=True)         
    class Meta:
        model = OrderNotConfirmation
        fields = ['delievery_delay','delivery_process_type','customer_reaction','final_decision','suggestion']
        
        


class ProjectPurchaseOrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = PurchaseOrder
        exclude = ['project', 'no', 'creator', 'order_confirmation', 'inquiry']
        widgets = {
            'purchase_order_date': DateInput()
        }


class DeliverySupplierToCustomerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if kwargs.get('instance', None):
            self.fields['parts'] = forms.ModelChoiceField(queryset=kwargs['instance'].purchase_order.parts.all())
            del self.fields['purchase_order']
        else:
            self.fields['purchase_order'].queryset = project.purchase_order.all()

        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])
            self.fields[name].required = True
        self.fields['fax_address'].required = False

    class Meta:
        model = Delivery
        fields = ['purchase_order', 'parts', 'shipping_company', 'tracking_no', 'customer_location', 'waybill_no',
                  'dispatch_date', 'delivery_date', 'phone', 'fax_address', 'email', 'person_in_contact', 'weight',
                  'dimensions']
        widgets = {
            'dispatch_date': DateInput(),
            'delivery_date': DateInput(),
        }


class DeliverySupplierToVesselForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if kwargs.get('instance', None):
            self.fields['parts'] = forms.ModelChoiceField(queryset=kwargs['instance'].purchase_order.parts.all())
            del self.fields['purchase_order']
        else:
            self.fields['purchase_order'].queryset = project.purchase_order.all()

        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])
            self.fields[name].required = True
        self.fields['fax_address'].required = False

    class Meta:
        model = Delivery
        fields = ['purchase_order', 'parts', 'shipping_company', 'tracking_no', 'port', 'agent', 'country', 'eta',
                  'waybill_no', 'dispatch_date', 'delivery_date', 'phone', 'fax_address', 'email', 'person_in_contact',
                  'weight', 'dimensions']
        widgets = {
            'dispatch_date': DateInput(),
            'delivery_date': DateInput(),
        }


class DeliveryWarehouseToCustomerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if kwargs.get('instance', None):
            self.fields['parts'] = forms.ModelChoiceField(queryset=kwargs['instance'].purchase_order.parts.all())
            del self.fields['purchase_order']
        else:
            self.fields['purchase_order'].queryset = project.purchase_order.all()

        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])
            self.fields[name].required = True
        self.fields['fax_address'].required = False

    class Meta:
        model = Delivery
        fields = ['purchase_order', 'parts', 'shipping_company', 'tracking_no', 'customer_location', 'waybill_no',
                  'dispatch_date', 'delivery_date', 'phone', 'fax_address', 'email', 'person_in_contact', 'weight',
                  'dimensions']
        widgets = {
            'dispatch_date': DateInput(),
            'delivery_date': DateInput(),
        }


class DeliveryWarehouseToVesselForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if kwargs.get('instance', None):
            self.fields['parts'] = forms.ModelChoiceField(queryset=kwargs['instance'].purchase_order.parts.all())
            del self.fields['purchase_order']
        else:
            self.fields['purchase_order'].queryset = project.purchase_order.all()

        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])
            self.fields[name].required = True
        self.fields['fax_address'].required = False

    class Meta:
        model = Delivery
        fields = ['purchase_order', 'parts', 'shipping_company', 'tracking_no', 'port', 'agent', 'country', 'eta',
                  'waybill_no', 'dispatch_date', 'delivery_date', 'phone', 'fax_address', 'email', 'person_in_contact',
                  'weight', 'dimensions']
        widgets = {
            'dispatch_date': DateInput(),
            'delivery_date': DateInput(),
        }


class DeliverySupplierToWarehouseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if kwargs.get('instance', None):
            self.fields['parts'] = forms.ModelChoiceField(queryset=kwargs['instance'].purchase_order.parts.all())
            del self.fields['purchase_order']
        else:
            self.fields['purchase_order'].queryset = project.purchase_order.all()

        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])
            self.fields[name].required = True

    class Meta:
        model = Delivery
        fields = ['purchase_order', 'parts', 'shipping_company', 'tracking_no', 'waybill_no', 'dispatch_date',
                  'delivery_date', 'weight', 'dimensions']
        widgets = {
            'dispatch_date': DateInput(),
            'delivery_date': DateInput(),
        }


class DeliveryTransportationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = DeliveryTransportation
        exclude = ['delivery']


class DeliveryTaxForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = DeliveryTax
        exclude = ['delivery']


class DeliveryInsuranceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = DeliveryInsurance
        exclude = ['delivery']


class DeliveryCustomsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = DeliveryCustoms
        exclude = ['delivery']


class DeliveryPackingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

    class Meta:
        model = DeliveryPacking
        exclude = ['delivery']
        
class ClaimsFollowUpStartForm(forms.ModelForm):
    
    CLAIM_REASON_CHOICES = (
        ('WP', _('Wrong Part')),
        ('MP', _('Mismatched Part')),
        ('II', _('Customer Provided Incomplete Information')),
        ('PAU', _('Problems After Using (Material Quality etc.)')),
        ('DP', _('Damaged Part')),
        ('OR', _('Other Reasons')),
    )
    
    def __init__(self, is_disable=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

            if is_disable:
                self.fields[name].disabled = True

                
                
    claim_reason_choices = forms.ChoiceField(choices = CLAIM_REASON_CHOICES, widget=MySelectMultiple(), required=True)         
    class Meta:
        model = ClaimsFollowUp
        fields = ['delievery_delay','claim_responsible','claim_action']

class ClaimsFollowUpResultForm(forms.ModelForm):
    
    CLAIM_RESULT_CHOICES = (
        ('RESS', _("The Part Has Been Returned(In The Entech Semar's Stock)")),
        ('RSS', _("The Part Has Been Returned(In The Supplier's Stock)")),
        ('PR', _('Part Replaced')),
        ('CGUC', _('Customer Gave Up The Claim')),
        ('ACCP', _('The Amount Claimed On The Claim Has Been Paid')),
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])
                
    claim_results = forms.ChoiceField(choices = CLAIM_RESULT_CHOICES, widget=MySelectMultiple(), required=True)         

    class Meta:
        model = ClaimsFollowUp
        fields = ['claim_status','customer_happiness','claim_notes']
        
class ClaimsFollowUpAllFieldsForm(forms.ModelForm):
    
    CLAIM_REASON_CHOICES = (
        ('WP', _('Wrong Part')),
        ('MP', _('Mismatched Part')),
        ('II', _('Customer Provided Incomplete Information')),
        ('PAU', _('Problems After Using (Material Quality etc.)')),
        ('DP', _('Damaged Part')),
        ('OR', _('Other Reasons')),
    )
    
    CLAIM_RESULT_CHOICES = (
        ('RESS', _("The Part Has Been Returned(In The Entech Semar's Stock)")),
        ('RSS', _("The Part Has Been Returned(In The Supplier's Stock)")),
        ('PR', _('Part Replaced')),
        ('CGUC', _('Customer Gave Up The Claim')),
        ('ACCP', _('The Amount Claimed On The Claim Has Been Paid')),
    )
    
    def __init__(self, is_disable=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

            if is_disable:
                self.fields[name].disabled = True
           
    claim_reason_choices = forms.ChoiceField(choices = CLAIM_REASON_CHOICES, widget=MySelectMultiple(), required=True)         
    claim_results = forms.ChoiceField(choices = CLAIM_RESULT_CHOICES, widget=MySelectMultiple(), required=True)         

    class Meta:
        model = ClaimsFollowUp
        fields = ['delievery_delay','claim_responsible','claim_action','claim_status','customer_happiness','claim_notes']      
        
class QuotationPartNoteForm(forms.ModelForm):
    
    FIELDS = {  
        "part_note":{
            'class': 'form-control',
            'style': 'height: 227px; min-height: 36px; margin-top: 0px; margin-bottom: 0px;',
        },
    }
    
    def __init__(self, is_disable=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            # add some special classes depend on the element
            if self.fields[name].widget.__class__.__name__ in STYLES:
                self.fields[name].widget.attrs.update(STYLES[self.fields[name].widget.__class__.__name__])
            else:
                self.fields[name].widget.attrs.update(STYLES["else"])

            if is_disable:
                self.fields[name].disabled = True
            if name in self.FIELDS:
                self.fields[name].widget.attrs.update(self.FIELDS[name])
    
    class Meta:
        model = QuotationPart
        fields = ['part_note']