import datetime
import os
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from information.models import Company, Vessel, Contact, Country
# Create your models here.
from parts.models import Maker, MakerType, Part
from user.models import Currency
from utilities.validators import ExtensionValidator

class Project(models.Model):
    STAGE_CHOICES = (
        ('request', _('Request')),
        ('inquiry', _('Inquiry')),
        ('quotation', _('Quotation')),
        ('purchase_order', _('Purchase Order')),
        ('delivery', _('Delivery')),
    )
    no = models.CharField(_("No"), max_length=16, unique=True, null=True)
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Responsible"), null=True,
                                    related_name="projects_responsible")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Creator"), null=True,
                                related_name="projects_created")
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default="")
    project_date = models.DateField(default=datetime.date.today)
    project_deadline = models.DateField(null=True)

    is_closed = models.BooleanField(_("Project Closed"), default=False)
    close_notes = models.TextField(_("Project Close Notes"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.no}"

    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def update_stage(self):
        """
        checks the all stages of project
        update the stage value to which stage validation fails
        need external save
        @return:
        """
        prev_stage = self.STAGE_CHOICES[0][0]
        for stage in self.STAGE_CHOICES:
            # print(stage, hasattr(self, stage[0]))
            if hasattr(self, stage[0]):
                stage_attr = getattr(self, stage[0])
                # print(stage)
                if isinstance(stage_attr, models.Model):
                    # print(stage_attr.is_finish())
                    if not stage_attr.is_finish():
                        self.stage = stage[0]
                        print(stage[0])
                        break
                else:
                    # if the stage has no objects, choose previous stage
                    if not stage_attr.all().exists():
                        self.stage = prev_stage[0]
                        print(prev_stage[0])
                        break
                    # if stage has objects and objects are not finished, choose the stage
                    if not any(obj.is_finish() for obj in stage_attr.all()):
                        self.stage = stage[0]
                        print(stage[0])
                        break
            prev_stage = stage

    def can_continue(self, stage_value):
        """
        can i go to that stage
        do manual check until the wanted stage
        if no error occurs while getting to it, then yes, return true and a warning message if necessary
        else return false, the stage that can continue to it, and an error message
        @param stage_value: wanted stage
        @return: Boolean, the stage value user can go, message
        """
        complete_error_message = _("Please complete this stage before going any further.")
        warning_message = _("Please be aware that every change that will be made at "
                            "this stage will affect the next stages.")
        can_not_modify_message = _("You can't modify this project due to it has been closed.")

        for stage in self.STAGE_CHOICES:
            # if wanted stage is already reached, then no error occurred on the way
            if stage[0] == stage_value:
                # if it is lower than current stage, warn the user to be careful
                if self.is_lt(stage_value):
                    return True, stage_value, warning_message if not self.is_closed else can_not_modify_message
                else:
                    # else return the wanted stage value and no message
                    return True, stage_value, None if not self.is_closed else can_not_modify_message
            # check for attribute is exist
            if hasattr(self, stage[0]):
                # get attribute
                attribute = getattr(self, stage[0])
                # is the connection Model or related (one to one field is model, which is request)
                if isinstance(attribute, models.Model):
                    if not attribute.is_finish():
                        return False, stage[0], complete_error_message if not self.is_closed else can_not_modify_message
                else:
                    # accept if any of the instance is okay
                    if not any(obj.is_finish() for obj in attribute.all()):
                        return False, stage[0], complete_error_message if not self.is_closed else can_not_modify_message
            else:
                return False, stage[0], complete_error_message if not self.is_closed else can_not_modify_message

    def is_gt(self, stage_value, current=None):
        """
        check if stage value is greater than current stage
        @param stage_value: check if it is greater than current
        @param current: self.stage if not provided
        @return: boolean
        """
        if not current:
            current = self.stage
        for stage in reversed(self.STAGE_CHOICES):
            if stage[0] == stage_value and stage[0] != current:
                return True
            elif stage[0] != stage_value and stage[0] == current:
                return False
            elif stage[0] == stage_value and stage[0] == current:
                return False
            else:
                continue
        return False

    def is_lt(self, stage_value, current=None):
        """
        check if stage value is lower than current stage
        @param stage_value: check if it is lower than current
        @param current: self.stage if not provided
        @return: boolean
        """
        if not current:
            current = self.stage
        for stage in self.STAGE_CHOICES:
            if stage[0] == stage_value and stage[0] != current:
                return True
            elif stage[0] != stage_value and stage[0] == current:
                return False
            elif stage[0] == stage_value and stage[0] == current:
                return False
            else:
                continue
        return False

    def get_next_stage(self, stage_value=None):
        """
        finds the next stage, by looping the stages by reverse
        @param stage_value: self.stage if not provided
        @return: next stage
        """
        if not stage_value:
            stage_value = self.stage
        temp = self.STAGE_CHOICES[-1][0]
        for stage in reversed(self.STAGE_CHOICES):
            if stage[0] == stage_value:
                return temp
            temp = stage[0]
        return stage_value

    def get_previous_stage(self, stage_value=None):
        """
        finds the previous stage
        @param stage_value: self.stage if not provided
        @return: previous stage
        """
        if not stage_value:
            stage_value = self.stage
        temp = self.STAGE_CHOICES[0][0]
        for stage in self.STAGE_CHOICES:
            if stage[0] == stage_value:
                return temp
            temp = stage[0]
        return stage_value

    def is_stage_finished(self, stage):
        """
        fast check for a stage only
        @param stage:
        @return:
        """
        if hasattr(self, stage):
            stage_attr = getattr(self, stage)
            if isinstance(stage_attr, models.Model):
                return stage_attr.is_finish()
            else:
                return any(obj.is_finish() for obj in stage_attr.all())
        else:
            return False
        
    def get_delta(self):
        """"""
        delta = self.project_deadline - datetime.datetime.now().date()
        humanized_days = delta.days
        if  datetime.datetime.now().date() > self.project_deadline:  
            humanized_days = -abs(delta.days)
        return humanized_days
    
    def is_confirmed(self):                  
        try:
           if self.quotation.filter(confirmation__isnull=False):
               return True
           else:
               return False
        except:
            return False
        
       
    def is_not_confirmed(self):     
        
        not_confirmation_message = _("You can't modify this project not confirmed.")
        
        try:
           if self.quotation.get(notconfirmation__isnull=False):
               return True, not_confirmation_message
           else:
               return False, ""
        except:
            return False, ""
        
    def is_claim_continue(self):     
        try:
           if self.delivery.filter(claimsfollowup__claim_status='continues'):
               return True
           else:
               return False
        except:
            return False
           

def get_upload_to(instance, filename):
    return f'documents/projects/{instance.project.no}/{filename}'


class ProjectDocument(models.Model):
    FILE_STAGE_CHOICES =(('request', _('Request')),('inquiry', _('Inquiry')), 
                        ('quotation', _('Quotation')),('order confirmation', _('Order Confirmation')),
                        ('purchase order', _('Purchase Order')),('delivery', _('Delivery')))
    
    FILE_TYPE_CHOICES =(('pdf', _('PDF')),('xlsx', _('XLSX')))
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(_("Document"), upload_to=get_upload_to,
                            validators=[ExtensionValidator(
                                ['pdf', 'doc', 'docx', 'odt', 'xls', 'xlsx', 'ods', 'ppt', 'pptx', 'txt'])])
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    file_stage = models.CharField(max_length=20, choices=FILE_STAGE_CHOICES, default='request',null=True,blank=True)
    file_type = models.CharField(max_length=4, choices=FILE_TYPE_CHOICES, default='pdf',null=True,blank=True)
    def __str__(self):
        return f"{self.project.no} -> {self.get_filename()}"

    def get_filename(self):
        return os.path.basename(str(self.file))

    def get_size(self):
        kb = self.file.size / 1024
        mb = kb / 1024
        return f"{round(mb, 1)} MB" if mb >= 1 else f"{round(kb, 1)} KB"


class Request(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True, related_name="request")
    no = models.CharField(_("No"), max_length=16, unique=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Creator"), null=True)
    customer = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, verbose_name=_("Customer"),
                                 limit_choices_to=Q(company_type__contains='Customer'))
    vessel = models.ForeignKey(Vessel, on_delete=models.SET_NULL, null=True, verbose_name=_("Vessel"))
    maker = models.ForeignKey(Maker, on_delete=models.SET_NULL, null=True, verbose_name=_("Maker"))
    maker_type = models.ForeignKey(MakerType, on_delete=models.SET_NULL, null=True, verbose_name=_("Maker Type"))
    person_in_contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True,
                                          verbose_name=_("Person in Contact"),
                                          limit_choices_to=Q(company__company_type__contains='Customer'))
    customer_ref = models.CharField(_("Customer Reference"), max_length=140)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, verbose_name=_("Currency"), null=True)
    request_date = models.DateField(default=datetime.date.today)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.project.no} -> {self.no}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # delete unmatched related parts to the maker type
        if self.maker_type:
            self.parts.filter(~Q(part__compatibilities__maker_type=self.maker_type)).delete()
        if self.project:
            print("stage updated by request save")
            self.project.update_stage()
            self.project.save()

    def is_finish(self):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "request not completed")
            return False
        # check if it has parts
        if not self.parts.all().exists():
            print("request parts missing")
            return False
        # check if the validation of parts are ok
        elif not all(part.is_finish() for part in self.parts.all()):
            print("request parts not completed")
            return False
        # else OK
        else:
            return True


class RequestPart(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, verbose_name=_("Request"), related_name="parts")
    part = models.ForeignKey(Part, on_delete=models.CASCADE, verbose_name=_("Part"))
    quantity = models.PositiveIntegerField(_("Quantity"), default=1, validators=[MaxValueValidator(10)])
    order_no = models.PositiveIntegerField(_("Order No"), null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.part}"

    class Meta:
        unique_together = ('request', 'part',)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.request and self.request.project:
            print("stage updated by request part save")
            self.request.project.update_stage()
            self.request.project.save()

    def is_finish(self):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "request part not completed")
        return True


class Inquiry(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="inquiry")
    supplier = models.ForeignKey(Company, on_delete=models.SET_NULL, verbose_name=_("Supplier"),
                                 limit_choices_to=Q(company_type__contains='Supplier'), null=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, verbose_name=_("Currency"), null=True)
    no = models.CharField(_("No"), max_length=16, unique=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Creator"), null=True)
    supplier_ref = models.CharField(_("Supplier Reference"), max_length=140)
    inquiry_date = models.DateField(default=datetime.date.today)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.project.no} -> {self.no}"
    
    def get_inquiry_no(self):
         return f"{self.no}"

    class Meta:
        unique_together = ('project', 'supplier',)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.project:
            print("stage updated by inquiry save")
            self.project.update_stage()
            self.project.save()

    def is_finish(self):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "inquiry not completed")
            return False
        # check if it has parts
        if not self.parts.all().exists():
            print("inquiry parts missing")
            return False
        # check if the validation of parts are ok
        elif not all(part.is_finish() for part in self.parts.all()):
            print("inquiry parts not completed")
            return False
        # else OK
        else:
            return True

    def get_total_price_of_the_parts(self):
        return sum([part.get_total_price() for part in self.parts])


class InquiryPart(models.Model):
    QUALITY_CHOICES = (
        ('original', _('Original')),
        ('oem', _('OEM')),
        ('other', _('Other')),
    )
    AVAILABILITY_CHOICES = (
        ('day', _('Day')),
        ('week', _('Week')),
        ('tba', _('TBA')),
        ('ex_stock', _('Ex Stock')),
        ('ex_stock_istanbul', _('Ex Stock Istanbul')),
    )
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, verbose_name=_("Inquiry"), related_name="parts")
    request_part = models.ForeignKey(RequestPart, on_delete=models.CASCADE, verbose_name=_("Request Part"),
                                     related_name="inquiries")
    quantity = models.PositiveIntegerField(_("Quantity"), default=1, validators=[MaxValueValidator(10)])
    order_no = models.PositiveIntegerField(_("Order No"), null=True)

    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES, default='original')
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, default=1.00,
                                     validators=[MinValueValidator(Decimal('1.0'))])

    is_added_in_quotation = models.BooleanField(_("Is Added in Quotation"), default=False)
    availability = models.CharField(max_length=30, choices=AVAILABILITY_CHOICES, default='week')
    availability_period = models.IntegerField(_("Availability Period"), default=1, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.inquiry.no} -> {self.request_part}"

    def get_part_name(self):
        return f"{self.request_part}"

    def is_selected_all(self, quotation):
        value = True
        for part in self.quotations.all():
            if self.quotations.filter(quotation = quotation):  
                if part.quotation == quotation and (part.checked == False or part.checked is None):
                    value = False
            else:
                value = False
        return value
        
        
    class Meta:
        unique_together = ('inquiry', 'request_part',)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.inquiry and self.inquiry.project:
            print("stage updated by inquiry part save")
            self.inquiry.project.update_stage()
            self.inquiry.project.save()

    def is_finish(self):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "inquiry part not completed")
        return True

    def get_total_price(self):
        return float(self.unit_price) * float(self.quantity)


class Quotation(models.Model):
    PAYMENT_CHOICES = (
        ('as_agreed', _('As Agreed')),
        ('as_advanced', _('As Advanced')),
        ('as_credit', _('As Credit')),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="quotation")
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, verbose_name=_("Currency"), null=True)
    note = models.TextField(_("Note"), null=True)
    quotation_date = models.DateField(default=datetime.date.today)

    no = models.CharField(_("No"), max_length=16, unique=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Creator"), null=True)

    payment = models.CharField(_("Payment"), max_length=50, choices=PAYMENT_CHOICES, null=True)
    validity = models.CharField(_("Validity"), max_length=50, null=True)
    delivery = models.CharField(_("Delivery"), max_length=50, null=True)
    vat = models.DecimalField(_("Vat %"), max_digits=6, decimal_places=3, default=0,
                                 validators=[MinValueValidator(Decimal('0.0'))])
    is_notified = models.BooleanField(_("Is Notified"), default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.project.no} -> {self.no}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.project:
            print("stage updated by quotation save")
            self.project.update_stage()
            self.project.save()

    def is_finish(self, check_confirmation=True):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "quotation not completed")
            return False
        # check if it has parts
        if hasattr(self, "notconfirmation"):
            print("Confirmation Rejected")
            return False
        elif not self.parts.all().exists():
            print("quotation parts missing")
            return False
        # check if the validation of parts are ok
        elif not all(part.is_finish() for part in self.parts.all()):
            print("quotation parts not completed")
            return False
        elif check_confirmation and not hasattr(self, "confirmation"):
            print("quotation has not been confirmed")
            return False
        # else OK
        else:
            return True

    def get_total_price_3_of_the_parts(self):
        return sum([part.get_total_price_3() for part in self.parts])


class QuotationPart(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, verbose_name=_("Quotation"),
                                  related_name="parts")
    inquiry_part = models.ForeignKey(InquiryPart, on_delete=models.CASCADE, verbose_name=_("Inquiry Part"),
                                     related_name="quotations")
    profit = models.DecimalField(_("Profit %"), max_digits=6, decimal_places=3, default=0,
                                 validators=[MinValueValidator(Decimal('0.0'))])
    discount = models.DecimalField(_("Discount %"), max_digits=6, decimal_places=2, default=0,
                                   validators=[MinValueValidator(Decimal('0.0'))])
    checked = models.BooleanField(null= True, default=False)
    part_note = models.TextField(_("Part Note"), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.quotation.no} -> {self.inquiry_part}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if hasattr(self.quotation,"notconfirmation"):
            return False
        if hasattr(self.quotation,"confirmation"):
            return False
        if not self._state.adding and hasattr(self.quotation, "confirmation"):
            print("order confirmation deleted by quotation part save")
            self.quotation.confirmation.delete()
        if self.quotation and self.quotation.project:
            
            if self.inquiry_part:
                self.inquiry_part.is_added_in_quotation = True
                self.inquiry_part.save()
            
            print("stage updated by quotation part save")
            self.quotation.project.update_stage()
            self.quotation.project.save()
            
    def delete(self, *args, **kwargs):
        if self.inquiry_part:
                self.inquiry_part.is_added_in_quotation = False
                self.inquiry_part.save()
        super(QuotationPart, self).delete(*args, **kwargs)
        
    def is_finish(self):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "quotation part not completed")
        return True

    def get_total_price_1(self):
        return self.inquiry_part.quantity * float(self.inquiry_part.unit_price)

    def get_currency_value(self):
        value = Currency.get_currencies(base=self.quotation.currency)['rates'][self.inquiry_part.inquiry.currency.name]
        return float(value)
    
    def get_currency_unit_price(self):
        value = self.get_currency_value()
        result =  float(self.inquiry_part.unit_price) * value
        return round(result,2)

    def get_currency_total_price_1(self):
        value = self.get_currency_value()
        result = float(self.get_total_price_1()) * value
        return round(result,2)

    def get_unit_profit_value(self):
        return round((float(self.get_currency_unit_price()) / 100) * float(self.profit), 2)

    def get_total_profit_value(self):
        return round((self.get_currency_total_price_1() / 100) * float(self.profit), 2)

    def get_unit_price_2(self):
        return round(float(self.get_currency_unit_price()) + self.get_unit_profit_value(), 2)

    def get_total_price_2(self):
        return round(self.get_currency_total_price_1() + self.get_total_profit_value(), 2)

    def get_unit_discount_value(self):
        return round((self.get_unit_price_2() / 100) * float(self.discount), 2)

    def get_total_discount_value(self):
        return round((self.get_total_price_2() / 100) * float(self.discount), 2)

    def get_unit_price_3(self):
        return round(self.get_unit_price_2() - self.get_unit_discount_value(), 2)

    def get_total_price_3(self):
        return round(self.get_total_price_2() - self.get_total_discount_value(), 2)

    def is_used_in_purchase(self):
        return True if hasattr(self, 'purchased') else False
       
class OrderConfirmation(models.Model):
    quotation = models.OneToOneField(Quotation, on_delete=models.CASCADE, related_name="confirmation", primary_key=True)
    no = models.CharField(_("No"), max_length=16, unique=True, null=True)
    note = models.CharField(_("Note"), max_length=140)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Creator"), null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.quotation.no}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.quotation and self.quotation.project:
            print("stage updated by order confirmation save")
            self.quotation.project.update_stage()
            self.quotation.project.save()

class Reason(models.Model):
    REASON_CHOICES = (
        ('HP', _('High Price')),
        ('LQ', _('Low Quality')),
        ('DO', _('Delayed Order')),
        ('NN', _('No Need')),
        ('PO', _('Pending Order')),
    )
    name = models.CharField(max_length=2,choices=REASON_CHOICES, unique=True)

    def __str__(self):
        return self.name
            
class OrderNotConfirmation(models.Model):
    DELIVERY_PROCESS_TYPE_CHOICES = (
        ('email', _('By Email')),
        ('phone', _('By Phone')),
        ('verbal', _('Verbal')),
    )
    CUSTOMER_REACTION_CHOICES = (
        ('OS', _('Optimistic and Satisfied')),
        ('HU', _('Harsh and Unsatisfied')),
        ('CN', _('Calm and Normal')),
        )
    
    BOOL_CHOICES = ((True, 'Yes, order will not be fulfilled'), (False, 'No, order pending'))

    quotation = models.OneToOneField(Quotation, on_delete=models.CASCADE, related_name="notconfirmation", primary_key=True)
    no = models.CharField(_("No"), max_length=17, unique=True, null=True,blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Creator"), null=True)
     
    delievery_delay = models.PositiveIntegerField(_("Delivered Delay"),default=1)
    delivery_process_type = models.CharField(_("Delivery Process Type"), max_length=6, choices=DELIVERY_PROCESS_TYPE_CHOICES, default='email')
    customer_reaction = models.CharField(_("Customer Reaction"), max_length=6, choices=CUSTOMER_REACTION_CHOICES, default='OS')
    final_decision = models.BooleanField(_("Final Decision"),choices=BOOL_CHOICES, default=False)
    reason_choices = models.ManyToManyField(Reason) 
    suggestion = models.TextField(_("Suggestion"), null=True) 
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.quotation.project.no} -> {self.quotation.no}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.quotation and self.quotation.project:
            print("order not confirmation save")
            self.quotation.project.is_closed = True
            self.quotation.project.save()


class PurchaseOrder(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="purchase_order")
    order_confirmation = models.ForeignKey(OrderConfirmation, on_delete=models.CASCADE, related_name="purchases")
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name="purchases")
    no = models.CharField(_("No"), max_length=16, unique=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Creator"), null=True)

    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, verbose_name=_("Currency"), null=True)
    purchase_order_date = models.DateField(default=datetime.date.today)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.project.no} -> {self.no}"

    class Meta:
        unique_together = ('order_confirmation', 'inquiry',)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.project:
            print("stage updated by purchase order save")
            self.project.update_stage()
            self.project.save()

    def is_finish(self):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "purchase order not completed")
            return False
        # check if it has parts
        if not self.parts.all().exists():
            print("purchase order parts missing")
            return False
        # check if the validation of parts are ok
        elif not all(part.is_finish() for part in self.parts.all()):
            print("purchase order parts not completed")
            return False
        # else OK
        else:
            return True


class PurchaseOrderPart(models.Model):
    ORDER_TYPE_CHOICES = (
        ('stock', _('Stock')),
        ('customer', _('Customer'))
    )
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="parts")
    quotation_part = models.OneToOneField(QuotationPart, on_delete=models.CASCADE, related_name="purchased")
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='stock')

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.purchase_order.no} -> {self.quotation_part}"

    class Meta:
        unique_together = ('purchase_order', 'quotation_part',)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.purchase_order and self.purchase_order.project:
            print("stage updated by purchase order part save")
            self.purchase_order.project.update_stage()
            self.purchase_order.project.save()

    def is_finish(self):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "purchase order part not completed")
        return True
    
    def get_total_price_1(self):
        return self.quotation_part.inquiry_part.quantity * float(self.quotation_part.inquiry_part.unit_price)

    def get_currency_value(self):
        value = Currency.get_currencies(base=self.purchase_order.currency)['rates'][self.quotation_part.quotation.currency.name]
        return float(value)
    
    def get_currency_unit_price(self):
        value = self.get_currency_value()
        result =  float(self.quotation_part.get_currency_unit_price()) * value
        return round(result,2)

    def get_currency_total_price_1(self):
        value = self.get_currency_value()
        result = float(self.quotation_part.get_currency_total_price_1()) * value
        return round(result,2)

    def get_unit_profit_value(self):
        return round((float(self.get_currency_unit_price()) / 100) * float(self.quotation_part.profit), 2)

    def get_total_profit_value(self):
        return round((self.get_currency_total_price_1() / 100) * float(self.quotation_part.profit), 2)

    def get_unit_price_2(self):
        return round(float(self.get_currency_unit_price()) + self.get_unit_profit_value(), 2)

    def get_total_price_2(self):
        return round(self.get_currency_total_price_1() + self.get_total_profit_value(), 2)

    def get_unit_discount_value(self):
        return round((self.get_unit_price_2() / 100) * float(self.quotation_part.discount), 2)

    def get_total_discount_value(self):
        return round((self.get_total_price_2() / 100) * float(self.quotation_part.discount), 2)

    def get_unit_price_3(self):
        return round(self.get_unit_price_2() - self.get_unit_discount_value(), 2)

    def get_total_price_3(self):
        return round(self.get_total_price_2() - self.get_total_discount_value(), 2)


class Delivery(models.Model):
    PROCESS_TYPE_CHOICES = (
        ('STV', _('Supplier To Vessel')),
        ('STC', _('Supplier To Customer')),
        ('WTV', _('Warehouse To Vessel')),
        ('WTC', _('Warehouse To Customer')),
        ('STW', _('Supplier To Warehouse')),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="delivery")
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="delivery")
    parts = models.ManyToManyField(PurchaseOrderPart, related_name="delivery")
    no = models.CharField(_("No"), max_length=16, unique=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Creator"), null=True)
    process_type = models.CharField(_("Process Type"), max_length=3, choices=PROCESS_TYPE_CHOICES)
    is_delivered = models.BooleanField(_('Is Delivered?'), default=False)

    shipping_company = models.CharField(_("Shipping Company"), max_length=50)
    tracking_no = models.CharField(_("Tracking No"), max_length=16, default="")
    port = models.CharField(_("Port"), max_length=50, blank=True, null=True)
    agent = models.CharField(_("Agent"), max_length=50, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=True, null=True)
    eta = models.CharField(_("ETA"), max_length=50, blank=True, null=True)
    customer_location = models.CharField(_("Customer Location"), max_length=255, blank=True, null=True)
    waybill_no = models.CharField(_("Waybill No"), max_length=16)
    dispatch_date = models.DateField()
    delivery_date = models.DateField(default=datetime.date.today)
    phone = models.CharField(_("Direct Phone"), max_length=50, blank=True, null=True)
    fax_address = models.CharField(_("Fax Address"), max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    person_in_contact = models.CharField(_("Person in Contact"), max_length=255, blank=True, null=True)
    weight = models.CharField(_("Weight"), max_length=50)
    dimensions = models.CharField(_("Dimensions"), max_length=50)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.project.no} -> {self.no}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.project:
            print("stage updated by delivery save")
            self.project.update_stage()
            self.project.save()

    def is_finish(self, check_delivery=True):
        charges = [
            'transportation',
            'tax',
            'insurance',
            'customs',
            'packing'
        ]
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "delivery not completed")
            return False
        if not all(getattr(self, charge).is_finish() for charge in charges if hasattr(self, charge)):
            print("delivery charges not completed")
            return False
        # check if it has parts
        elif not self.parts.all().exists():
            print("delivery parts missing")
            return False
        elif check_delivery and not self.is_delivered:
            print("delivery not delivered")
            return False
        # else OK
        else:
            return True


class DeliveryTransportation(models.Model):
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, related_name="transportation", primary_key=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, verbose_name=_("Currency"), null=True, blank=True)
    insurance_and_inland_haulage_expense = models.DecimalField(_("Insurance and Inland Haulage Expense"), max_digits=10,
                                                               decimal_places=2, default=0.00,
                                                               validators=[MinValueValidator(Decimal('0.0'))])
    insurance_and_inland_haulage_charged_amount = models.DecimalField(_("Insurance and Inland Haulage Charged Amount"),
                                                                      max_digits=10, decimal_places=2, default=0.00,
                                                                      validators=[MinValueValidator(Decimal('0.0'))])
    extra_expense = models.DecimalField(_("Extra Expense"), max_digits=10, decimal_places=2, default=0.00,
                                        validators=[MinValueValidator(Decimal('0.0'))])
    extra_charged_amount = models.DecimalField(_("Extra Charged Amount"), max_digits=10, decimal_places=2, default=0.00,
                                               validators=[MinValueValidator(Decimal('0.0'))])
    other_expense = models.DecimalField(_("Other Expense"), max_digits=10, decimal_places=2, default=0.00,
                                        validators=[MinValueValidator(Decimal('0.0'))])
    other_charged_amount = models.DecimalField(_("Other Charged Amount"), max_digits=10, decimal_places=2, default=0.00,
                                               validators=[MinValueValidator(Decimal('0.0'))])
    atr_expense = models.DecimalField(_("Atr Expense"), max_digits=10, decimal_places=2, default=0.00,
                                      validators=[MinValueValidator(Decimal('0.0'))])
    atr_charged_amount = models.DecimalField(_("Atr Charged Amount"), max_digits=10, decimal_places=2, default=0.00,
                                             validators=[MinValueValidator(Decimal('0.0'))])
    certificate_expense = models.DecimalField(_("Certificate Expense"), max_digits=10, decimal_places=2, default=0.00,
                                              validators=[MinValueValidator(Decimal('0.0'))])
    certificate_charged_amount = models.DecimalField(_("Certificate Charged Amount"), max_digits=10, decimal_places=2,
                                                     default=0.00, validators=[MinValueValidator(Decimal('0.0'))])

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.delivery.no}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.delivery and self.delivery.project:
            print("stage updated by delivery transportation save")
            self.delivery.project.update_stage()
            self.delivery.project.save()

    def is_finish(self):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "delivery transportation not completed")
            return False
        return True

    def get_total_charged_amount(self):
        return sum(
            [self.insurance_and_inland_haulage_charged_amount, self.extra_charged_amount, self.other_charged_amount,
             self.atr_charged_amount, self.certificate_charged_amount])


class DeliveryTax(models.Model):
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, related_name="tax", primary_key=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, verbose_name=_("Currency"), null=True, blank=True)
    customs_expense = models.DecimalField(_("Customs Expense"), max_digits=10, decimal_places=2, default=0.00,
                                          validators=[MinValueValidator(Decimal('0.0'))])
    customs_charged_amount = models.DecimalField(_("Customs Charged Amount"), max_digits=10, decimal_places=2,
                                                 default=0.00, validators=[MinValueValidator(Decimal('0.0'))])
    surtax_expense = models.DecimalField(_("Surtax Expense"), max_digits=10, decimal_places=2, default=0.00,
                                         validators=[MinValueValidator(Decimal('0.0'))])
    surtax_charged_amount = models.DecimalField(_("Surtax Charged Amount"), max_digits=10, decimal_places=2,
                                                default=0.00, validators=[MinValueValidator(Decimal('0.0'))])

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.delivery.no}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.delivery and self.delivery.project:
            print("stage updated by delivery tax save")
            self.delivery.project.update_stage()
            self.delivery.project.save()

    def is_finish(self):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "delivery tax not completed")
            return False
        return True

    def get_total_charged_amount(self):
        return sum([self.customs_charged_amount, self.surtax_charged_amount])


class DeliveryInsurance(models.Model):
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, related_name="insurance", primary_key=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, verbose_name=_("Currency"), null=True, blank=True)
    insurance_expense = models.DecimalField(_("Insurance Expense"), max_digits=10, decimal_places=2, default=0.00,
                                            validators=[MinValueValidator(Decimal('0.0'))])
    insurance_charged_amount = models.DecimalField(_("Insurance Charged Amount"), max_digits=10, decimal_places=2,
                                                   default=0.00, validators=[MinValueValidator(Decimal('0.0'))])

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.delivery.no}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.delivery and self.delivery.project:
            print("stage updated by delivery insurance save")
            self.delivery.project.update_stage()
            self.delivery.project.save()

    def is_finish(self):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "delivery insurance not completed")
            return False
        return True

    def get_total_charged_amount(self):
        return sum([self.insurance_charged_amount])


class DeliveryCustoms(models.Model):
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, related_name="customs", primary_key=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, verbose_name=_("Currency"), null=True, blank=True)
    customs_commission_expense = models.DecimalField(_("Customs Commission Expense"), max_digits=10, decimal_places=2,
                                                     default=0.00, validators=[MinValueValidator(Decimal('0.0'))])
    customs_commission_charged_amount = models.DecimalField(_("Customs Commission Charged Amount"), max_digits=10,
                                                            decimal_places=2, default=0.00,
                                                            validators=[MinValueValidator(Decimal('0.0'))])
    delivery_order_expense = models.DecimalField(_("Delivery Order Expense"), max_digits=10, decimal_places=2,  # ordino
                                                 default=0.00, validators=[MinValueValidator(Decimal('0.0'))])
    delivery_order_charged_amount = models.DecimalField(_("Delivery Order Charged Amount"), max_digits=10,
                                                        decimal_places=2, default=0.00,
                                                        validators=[MinValueValidator(Decimal('0.0'))])
    warehouse_expense = models.DecimalField(_("Warehouse Expense"), max_digits=10, decimal_places=2,  # ardiye
                                            default=0.00, validators=[MinValueValidator(Decimal('0.0'))])
    warehouse_charged_amount = models.DecimalField(_("Warehouse Charged Amount"), max_digits=10, decimal_places=2,
                                                   default=0.00, validators=[MinValueValidator(Decimal('0.0'))])
    labour_expense = models.DecimalField(_("Labour Expense"), max_digits=10, decimal_places=2,  # ardiye
                                         default=0.00, validators=[MinValueValidator(Decimal('0.0'))])
    labour_charged_amount = models.DecimalField(_("Labour Charged Amount"), max_digits=10, decimal_places=2,
                                                default=0.00, validators=[MinValueValidator(Decimal('0.0'))])
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.delivery.no}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.delivery and self.delivery.project:
            print("stage updated by delivery customs save")
            self.delivery.project.update_stage()
            self.delivery.project.save()

    def is_finish(self):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "delivery customs not completed")
            return False
        return True

    def get_total_charged_amount(self):
        return sum([self.customs_commission_charged_amount, self.labour_charged_amount, self.warehouse_charged_amount,
                    self.delivery_order_charged_amount])


class DeliveryPacking(models.Model):
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, related_name="packing", primary_key=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, verbose_name=_("Currency"), null=True, blank=True)
    packing_expense = models.DecimalField(_("Packing Expense"), max_digits=10, decimal_places=2, default=0.00,
                                          validators=[MinValueValidator(Decimal('0.0'))])
    packing_charged_amount = models.DecimalField(_("Packing Charged Amount"), max_digits=10, decimal_places=2,
                                                 default=0.00, validators=[MinValueValidator(Decimal('0.0'))])

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.delivery.no}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.delivery and self.delivery.project:
            print("stage updated by delivery packing save")
            self.delivery.project.update_stage()
            self.delivery.project.save()

    def is_finish(self):
        # check basic field validations
        try:
            self.full_clean()
        except ValidationError as ve:
            print(ve, "delivery packing not completed")
            return False
        return True

    def get_total_charged_amount(self):
        return sum([self.packing_charged_amount])
    
class ClaimReason(models.Model):
    CLAIM_REASON_CHOICES = (
        ('WP', _('Wrong Part')),
        ('MP', _('Mismatched Part')),
        ('II', _('Customer Provided Incomplete Information')),
        ('PAU', _('Problems After Using (Material Quality etc.)')),
        ('DP', _('Damaged Part')),
        ('OR', _('Other Reasons')),
    )
    name = models.CharField(max_length=3,choices=CLAIM_REASON_CHOICES, unique=True)

    def __str__(self):
        return self.name

class ClaimResult(models.Model):
    CLAIM_RESULT_CHOICES = (
        ('RESS', _("The Part Has Been Returned(In The Entech Semar's Stock)")),
        ('RSS', _("The Part Has Been Returned(In The Supplier's Stock)")),
        ('PR', _('Part Replaced')),
        ('CGUC', _('Customer Gave Up The Claim')),
        ('ACCP', _('The Amount Claimed On The Claim Has Been Paid')),
    )
    
    name = models.CharField(max_length=4,choices=CLAIM_RESULT_CHOICES, unique=True)

    def __str__(self):
        return self.name
    
class ClaimsFollowUp(models.Model):
    YES_NO_CHOICES = (("yes", 'Yes'), ("no", 'No'))
    CLAIM_STATUS_CHOICES = (
        ('continues' ,_('Continues')),
        ('completed', _('Completed'))
    )
        
    CLAIM_RESPONSIBLE_CHOICES = (
        ('ESO', _('Operation')),
        ('HSU', _('Sales')),
        ('F', _('Forwarder')),
        ('C', _('Customer')),
        ('S', _('Shipper')),
        ('M', _('Manufacturer')),
    )
    CLAIM_ACTION_CHOICES = (
        ('NAT', _('No Action Taken')),
        ('PR', _('Parts Replacement')),
        ('OC', _('Order Cancellation and Part Return')),
        ('other', _('Other')),
    )
    
    
    no = models.CharField(_("No"), max_length=18, unique=True, null=True,blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Creator"), null=True)
    
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name="claimsfollowup")
    delievery_delay = models.PositiveIntegerField(_("Delivered Delay"),default=1)
    claim_responsible = models.CharField(_("Claim Follow Up Responsible"), max_length=3, choices=CLAIM_RESPONSIBLE_CHOICES, default='ESO')
    claim_action = models.CharField(_("Claim Follow Up Followed Action"), max_length=5, choices=CLAIM_ACTION_CHOICES, default='NAT')
    claim_reason_choices = models.ManyToManyField(ClaimReason) 
    
    claim_status = models.CharField(_("Claim Follow Up Status"), max_length=9, choices=CLAIM_STATUS_CHOICES, default='continues')
    customer_happiness = models.CharField(_("Is The Customer Happy With Result?"), max_length=3, choices=YES_NO_CHOICES, null=True)
    claim_results = models.ManyToManyField(ClaimResult)
    claim_notes = models.TextField(_("Notes"), null=True) 
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.delivery.project.no} -> {self.no}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print("here")
        if self.delivery and self.delivery.project:
            print("claims follow up save")
            self.delivery.save()
            
