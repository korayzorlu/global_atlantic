import datetime, os
from enum import unique
from io import BytesIO
from django.core.files import File
from django.utils import timezone
import time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework import fields
from rest_framework.fields import empty

from hr.models import BankAccount, TheCompany
from information.api.serializers import CompanyListSerializer, VesselListSerializer, ContactListSerializer, \
    CountryListSerializer
from information.models import Vessel, Contact
from parts.api.serializers import MakerTypeListSerializer, MakerListSerializer, PartListSerializer
from parts.models import MakerType
from sales.models import ClaimReason, ClaimResult, ClaimsFollowUp, OrderNotConfirmation, Request, Project, RequestPart, Inquiry, InquiryPart, QuotationPart, Quotation, \
    OrderConfirmation, PurchaseOrder, PurchaseOrderPart, Delivery, DeliveryTransportation, DeliveryTax, \
    DeliveryInsurance, DeliveryCustoms, DeliveryPacking, ProjectDocument, Reason
from user.api.serializers import UserListSerializer, CurrencyListSerializer
from utilities.send_mail import custom_send_mail
from utilities.render_pdf import render_to_pdf


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ["created_at", "updated_at"]
        extra_kwargs = {
            'project_date': {'allow_null': False, 'required': True},
            'project_deadline': {'allow_null': False, 'required': True}
        }

    def validate(self, data):
        responsible = data.get('responsible', getattr(self.instance, 'responsible', None))
    
        if self.instance and getattr(self.instance, 'is_closed', None):
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
            
        if self.instance.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))

        # if user try to change the responsible user, check the user if is admin (temporary)
        if data.get("responsible") and not self.context['request'].user.is_superuser:
            raise serializers.ValidationError(_("Only the superusers can change the responsible user."))

        # if user try to close the project, check the user if is responsible
        if data.get("is_closed") and self.context['request'].user != responsible:
            raise serializers.ValidationError(_("Only the responsible user can finish the project."))

        return data

class ProjectDuplicateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ["id"]

    def create(self, validated_data):
        project = self.context['project']
        request = project.request
        parts = self.context['parts']  
        
        project.id = None
        project.no = self.define_project_no(project)
        project.is_closed = False
        project.save()
                     
        request.id = None
        request.no = self.define_request_no(request)
        request.project = project           
        project.request.save(request)
        
        for part in parts:
            part.id = None
            part.request = request
            part.save()
            
        request.parts.add(*parts)
        return project
    
    def define_project_no(self, instance):
        year = int(time.strftime("%y"))
        last_project = Project.objects.filter(no__regex=f'^ESP-{year:03}-[0-9]{{8}}$').order_by('-no').first()
        if last_project:
            last_no = int(last_project.no.split('-')[2])
            instance.no = f'ESP-{year:03}-{last_no + 1:08}'
        else:
            instance.no = f'ESP-{year:03}-{1:08}'
        
        return instance.no
    
    def define_request_no(self, instance):
        year = int(time.strftime("%y"))
        last_request = Request.objects.filter(no__regex=f'^ESR-{year:03}-[0-9]{{8}}$').order_by('-no').first()
        if last_request:
            last_no = int(last_request.no.split('-')[2])
            instance.no = f'ESR-{year:03}-{last_no + 1:08}'
        else:
            instance.no = f'ESR-{year:03}-{1:08}'
    
        
        
class ProjectDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDocument
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        project = data.get('project', getattr(self.instance, 'project', None))

        if project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))

        return data


class ProjectDocumentListSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source='get_filename')
    size = serializers.CharField(source='get_size')
    created_at = serializers.DateTimeField(format="%d %b %Y %H:%m")

    class Meta:
        model = ProjectDocument
        exclude = ["updated_at"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    creator = UserListSerializer(read_only=True)
    responsible = UserListSerializer(read_only=True)

    class Meta:
        model = Project
        exclude = ["created_at", "updated_at"]


class ProjectListSerializer(serializers.ModelSerializer):
    responsible = UserListSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ["id", "no", "stage","project_date", "responsible", "is_closed", "created_at", "updated_at"]


class RequestCreateSerializer(serializers.ModelSerializer):
    """
    project not required but you need to enter project date and deadline
    project date and deadline not required if you select project that has no request
    """
    project_date = serializers.DateField(initial=datetime.date.today, allow_null=True, write_only=True)
    project_deadline = serializers.DateField(allow_null=True, write_only=True)

    class Meta:
        model = Request
        exclude = ["created_at", "updated_at"]
        extra_kwargs = {
            'project': {'allow_null': True},
            'customer': {'allow_null': False, 'required': True},
            'vessel': {'allow_null': False, 'required': True},
            'maker': {'allow_null': False, 'required': True},
            'maker_type': {'allow_null': False, 'required': True},
            'person_in_contact': {'allow_null': False, 'required': True}
        }

    def validate(self, data):
        error_message = _("Select a valid choice. That choice is not one of the available choices.")
        blank_message = _("This field may not be blank.")
        customer = data.get('customer', getattr(self.instance, 'customer', None))
        vessel = data.get('vessel', getattr(self.instance, 'vessel', None))
        person_in_contact = data.get('person_in_contact', getattr(self.instance, 'person_in_contact', None))
        maker = data.get('maker', getattr(self.instance, 'maker', None))
        maker_type = data.get('maker_type', getattr(self.instance, 'maker_type', None))
        project = data.get('project', getattr(self.instance, 'project', None))
        project_date = data.pop('project_date', None)
        project_deadline = data.pop('project_deadline', None)

        if project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        try:
            customer.vessels.get(pk=vessel.pk)
        except Vessel.DoesNotExist:
            raise serializers.ValidationError({'vessel': error_message})
        try:
            customer.contacts.get(pk=person_in_contact.pk)
        except Contact.DoesNotExist:
            raise serializers.ValidationError({'person_in_contact': error_message})
        try:
            maker.maker_types.get(pk=maker_type.pk)
        except MakerType.DoesNotExist:
            raise serializers.ValidationError({'maker_type': error_message})

        if not project:
            if not project_date:
                raise serializers.ValidationError({'project_date': blank_message})
            if not project_deadline:
                raise serializers.ValidationError({'project_deadline': blank_message})
            data['project'] = Project.objects.create(responsible=self.context['request'].user,
                                                     creator=self.context['request'].user,
                                                     project_date=project_date,
                                                     project_deadline=project_deadline)

        return data


class RequestDetailSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    customer = CompanyListSerializer(read_only=True)
    vessel = VesselListSerializer(read_only=True)
    maker = MakerListSerializer(read_only=True)
    maker_type = MakerTypeListSerializer(read_only=True)
    person_in_contact = ContactListSerializer(read_only=True)

    class Meta:
        model = Request
        exclude = ["created_at", "updated_at"]


class RequestListSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    customer = CompanyListSerializer(read_only=True)
    vessel = VesselListSerializer(read_only=True)
    maker_type = MakerTypeListSerializer(read_only=True)

    class Meta:
        model = Request
        fields = ["pk", "no", "project", "customer", "vessel", "maker_type"]


class ProjectProcessListSerializer(serializers.ModelSerializer):
    responsible = UserListSerializer(read_only=True)
    request = RequestListSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%d %b %Y %H:%m")
    updated_at = serializers.DateTimeField(format="%d %b %Y %H:%m")
    is_claim_continue = serializers.SerializerMethodField()
    
    def get_is_claim_continue(self, obj):
        return obj.is_claim_continue()

    class Meta:
        model = Project
        fields = ["id", "no", "stage", "responsible", "request", "is_closed", "created_at", "updated_at", "is_claim_continue",]



class RequestPartCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestPart
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        request = data.get('request', getattr(self.instance, 'request', None))
        maker_type = request.maker_type
        part = data.get('part', getattr(self.instance, 'part', None))

        if request.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if request.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if not maker_type:
            raise serializers.ValidationError({"maker_type": _("This field may not be null.")})
        else:
            if not part.compatibilities.filter(maker_type=maker_type):
                raise serializers.ValidationError(
                    {"part": _("Select a valid choice. That choice is not one of the available choices.")})
        return data


class RequestPartDetailSerializer(serializers.ModelSerializer):
    request = RequestListSerializer(read_only=True)
    part = PartListSerializer(read_only=True)
    str = serializers.CharField(source='__str__')

    class Meta:
        model = RequestPart
        exclude = ["created_at", "updated_at"]


class RequestPartListSerializer(serializers.ModelSerializer):
    request = RequestListSerializer(read_only=True)
    part = PartListSerializer(read_only=True)
    str = serializers.CharField(source='__str__')

    class Meta:
        model = RequestPart
        fields = ["id", "request", "part", "quantity", "str"]


class InquiryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        exclude = ["created_at", "updated_at"]
        extra_kwargs = {
            'supplier': {'allow_null': False},
            'currency': {'allow_null': False}
        }

    def validate(self, data):
        project = data.get('project', getattr(self.instance, 'project', None))

        if project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if data.get('inquiry_date'):
            error_message = _("You can't add a inquiry date before project date")
            if project.project_date > data.get('inquiry_date'):       
                raise serializers.ValidationError(error_message)
            else:
                pass
        else:
            pass
        return data


class InquiryDetailSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    supplier = CompanyListSerializer(read_only=True)
    currency = CurrencyListSerializer(read_only=True)
    creator = UserListSerializer(read_only=True)

    class Meta:
        model = Inquiry
        exclude = ["created_at", "updated_at"]


class InquiryListSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    supplier = CompanyListSerializer(read_only=True)
    currency = CurrencyListSerializer(read_only=True)

    class Meta:
        model = Inquiry
        fields = ["id", "project", "supplier", "no", "supplier_ref", "currency"]


class InquiryPartCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryPart
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        inquiry = data.get('inquiry', getattr(self.instance, 'inquiry', None))
        request_part = data.get('request_part', getattr(self.instance, 'request_part', None))

        if inquiry.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if inquiry.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if not inquiry.supplier:
            raise serializers.ValidationError({"supplier": _("This field may not be null.")})
        if request_part.request.project != inquiry.project:
            raise serializers.ValidationError(
                {"request_part": _("Select a valid choice. That choice is not one of the available choices.")})
        return data


class InquiryPartDetailSerializer(serializers.ModelSerializer):
    inquiry = InquiryListSerializer(read_only=True)
    request_part = RequestPartListSerializer(read_only=True)
    str = serializers.CharField(source='__str__')

    class Meta:
        model = InquiryPart
        exclude = ["created_at", "updated_at"]


class InquiryPartListSerializer(serializers.ModelSerializer):
    inquiry = InquiryListSerializer(read_only=True)
    request_part = RequestPartListSerializer(read_only=True)
    quality = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()
    str = serializers.CharField(source='__str__')

    def get_quality(self, obj):
        return {'name': obj.get_quality_display(), 'value': obj.quality}

    def get_availability(self, obj):
        return {'name': obj.get_availability_display(), 'value': obj.availability}

    class Meta:
        model = InquiryPart
        fields = ["id", "inquiry", "request_part", "quantity", "unit_price", "availability_period", "availability",
                  "quality", "str"]

class InquiryPartAddListSerializer(serializers.ModelSerializer):
    inquiry = InquiryListSerializer(read_only=True)
    request_part = RequestPartListSerializer(read_only=True)
    quality = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()
    is_added_in_quotation = serializers.SerializerMethodField()
    is_selected_all = serializers.SerializerMethodField()
    str = serializers.CharField(source='get_part_name')

    def get_quality(self, obj):
        return {'name': obj.get_quality_display(), 'value': obj.quality}

    def get_availability(self, obj):
        return {'name': obj.get_availability_display(), 'value': obj.availability}
    
    def get_is_added_in_quotation(self, obj):
        quotation = self.context["quotation"]
        for part in obj.quotations.all():
            if part.checked is True and part.quotation == quotation:
                return True

    def get_is_selected_all(self, obj):
        quotation = self.context["quotation"]
        return obj.is_selected_all(quotation)

    class Meta:
        model = InquiryPart
        fields = ["id", "inquiry", "request_part", "quantity", "unit_price", "availability_period", "availability",
                  "quality", "str","is_added_in_quotation", "is_selected_all"]

class QuotationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        exclude = ["created_at", "updated_at"]
        extra_kwargs = {
            'currency': {'allow_null': False},
            'payment': {'allow_null': False},
            'validity': {'allow_null': False},
            'delivery': {'allow_null': False}
        }

    def validate(self, data):
        project = data.get('project', getattr(self.instance, 'project', None))
        if hasattr(self.instance, "notconfirmation"):
            raise serializers.ValidationError(
                {"quotation": _("You can't update the notconfirmed quotations!")})
            
        if project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if hasattr(self.instance, "confirmation"):
            raise serializers.ValidationError(
                {"quotation": _("You can't update the confirmed quotations!")})
        if data.get('quotation_date'):
            error_message =  _("You can't add a quotation date before project date")
            if project.project_date > data.get('quotation_date'):       
                raise serializers.ValidationError(error_message)
            else:
                pass
        else:
            pass
        return data


class QuotationDetailSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    currency = CurrencyListSerializer(read_only=True)
    creator = UserListSerializer(read_only=True)

    class Meta:
        model = Quotation
        exclude = ["created_at", "updated_at"]


class QuotationListSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)

    class Meta:
        model = Quotation
        fields = ["id", "project", "no", "note", "payment", "validity", "delivery"]


class QuotationPartCreateSerializer(serializers.ModelSerializer):
    # inquiry_part = serializers.ListField(child=serializers.IntegerField())

    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(QuotationPartCreateSerializer, self).__init__(many=many, *args, **kwargs)
        
    class Meta:
        model = QuotationPart
        exclude = ["created_at", "updated_at"]
    
    # def create(self, validated_data):
    #     print("-------------------------")
    #     inquiry_part=validated_data.get('inquiry_part')  
    #     quotation=validated_data.get('quotation')
    #     inquiry_parts = InquiryPart.objects.filter(id__in=inquiry_part)    
    #     for part in inquiry_parts:
    #         context = {'inquiry_part': part, 'quotation': quotation }
    #         print(context)
    #         instance = QuotationPart.objects.create(context)
    #     return instance
         
         
    def validate(self, data):
        quotation = data.get('quotation', getattr(self.instance, 'quotation', None))
        inquiry_part = data.get('inquiry_part', getattr(self.instance, 'inquiry_part', None))
        print("------------------------")
        print("normal create")
        # inquiry_parts = InquiryPart.objects.filter(id__in=inquiry_part)
        if quotation.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if quotation.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if hasattr(quotation, "notconfirmation"):
              raise serializers.ValidationError(
                  {"quotation": _("You can't add a new part to or edit an existing part in the notconfirmed quotations!")})
        if hasattr(quotation, "confirmation"):
            raise serializers.ValidationError(
                {"quotation": _("You can't add a new part to or edit an existing part in the confirmed quotations!")})
        # for part in inquiry_parts:
        if inquiry_part.inquiry.project != quotation.project:
            raise serializers.ValidationError(
                {"inquiry_part": _("Select a valid choice. That choice is not one of the available choices.")})
        return data
    
    
class QuotationPartBulkSerializer(serializers.ModelSerializer):
        
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(QuotationPartBulkSerializer, self).__init__(many=many, *args, **kwargs)
           
    class Meta:
        model = QuotationPart
        exclude = ["created_at", "updated_at"]
    
    
    def create(self, validated_data):
        checked = validated_data.get('checked', getattr(self.instance, 'checked', None))
        quotation = validated_data.get('quotation', getattr(self.instance, 'quotation', None))
        inquiry_part = validated_data.get('inquiry_part', getattr(self.instance, 'inquiry_part', None))
        print(checked)
        if checked is True:
            instance, _ = QuotationPart.objects.get_or_create(**validated_data)
        else: 
            try:
                instance = QuotationPart.objects.get(inquiry_part=inquiry_part, quotation=quotation, checked=True)
                if instance:
                    print("part deleted")
                    instance.delete()            
            except:
                return QuotationPart()
            # it is fake part, we don't use but a quotation part has to return
            return QuotationPart() 
        return instance
         
    def validate(self, data):
        quotation = data.get('quotation', getattr(self.instance, 'quotation', None))
        inquiry_part = data.get('inquiry_part', getattr(self.instance, 'inquiry_part', None))

        if quotation.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if quotation.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if hasattr(quotation, "notconfirmation"):
              raise serializers.ValidationError(
                  {"quotation": _("You can't add a new part to or edit an existing part in the notconfirmed quotations!")})
        if hasattr(quotation, "confirmation"):
            raise serializers.ValidationError(
                {"quotation": _("You can't add a new part to or edit an existing part in the confirmed quotations!")})
        if inquiry_part.inquiry.project != quotation.project:
            raise serializers.ValidationError(
                {"inquiry_part": _("Select a valid choice. That choice is not one of the available choices.")})
        return data


class QuotationPartDetailSerializer(serializers.ModelSerializer):
    quotation = QuotationListSerializer(read_only=True)
    inquiry_part = InquiryPartListSerializer(read_only=True)
    str = serializers.CharField(source='__str__')

    class Meta:
        model = QuotationPart
        exclude = ["created_at", "updated_at"]


class QuotationPartListSerializer(serializers.ModelSerializer):
    quotation = QuotationListSerializer(read_only=True)
    inquiry_part = InquiryPartListSerializer(read_only=True)
    is_used_in_purchase = serializers.BooleanField()
    unit_price = serializers.SerializerMethodField()
    total_price_3 = serializers.DecimalField(source="get_total_price_3", max_digits=10, decimal_places=2)
    str = serializers.CharField(source='__str__')

    def get_unit_price(self, obj):
        return obj.get_currency_unit_price()
    class Meta:
        model = QuotationPart
        fields = ["id","unit_price", "quotation", "inquiry_part", "profit", "discount", "total_price_3", "is_used_in_purchase",
                  "str", "part_note"]


class OrderConfirmationCreateSerializer(serializers.ModelSerializer):
    send_mail = serializers.BooleanField(write_only=True, allow_null=True, required=False)

    class Meta:
        model = OrderConfirmation
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        self.send_mail = data.pop('send_mail', False)  # used for mailing when updating
        quotation = data.get('quotation', getattr(self.instance, 'quotation', None))

        if quotation.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if quotation.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if not quotation.is_finish(check_confirmation=False):
            raise serializers.ValidationError(
                {"quotation": _("You can't confirm a not completed quotation.")})
        try:
            validate_email(quotation.project.request.person_in_contact.email)
        except ValidationError as e:
            raise serializers.ValidationError(_('Person in contact of the customer has no email address.'))
        return data

    def create(self, validated_data):
        instance = super().create(validated_data)
        if self.send_mail:
            
            document = self.getProjectDocument(instance.quotation)
            custom_send_mail(
                _('Your order has been received!'),
                settings.DEFAULT_FROM_EMAIL,
                [instance.quotation.project.request.person_in_contact.email],
                template_path='sales/project/mail/received.html',
                context={'the_company': TheCompany.objects.get(id=1), 'order_confirmation': instance,'document':document},
                document=document
            )
        return instance
    
    def getProjectDocument(self,quotation):
        """"""
        order_confirmation = quotation.confirmation
        project = quotation.project
        request = request = self.context.get("request")
        sub_total=0
        discount=0
        quotationParts=QuotationPart.objects.filter(quotation=quotation)
        for quotationPart  in quotationParts:
            sub_total+=quotationPart.get_total_price_1()
            #Total discaount as percent
            discount+=quotationPart.discount
        vat_total=round((sub_total / 100) * float(quotation.vat), 2)
        discount_total=round((sub_total / 100) * float(discount), 2)
        net_total=sub_total+vat_total-discount_total
        response = render_to_pdf("sales/project/pdf/order_confirmation.html", {
            'project': project,
            'quotation':quotation,
            'responsible':project.responsible,
            'quotationParts':quotationParts,
            'order_confirmation': order_confirmation,
            'company': TheCompany.objects.get(id=1),
            'bankAccounts':BankAccount.objects.all(),
            'date':timezone.localtime(timezone.now()).date(),
            'time':timezone.localtime(timezone.now()).time(),
            'subTotal':sub_total,
            'vatTotal':vat_total,
            'discount':discount,
            'discountTotal':discount_total,
            'netTotal':net_total,
        })
        filename = f"{project.no}({project.id})_{order_confirmation.no}({order_confirmation.pk}).pdf"
        content = f"attachment; filename={filename}" if request.GET.get("download") else f"inline; filename={filename}"
        response['Content-Disposition'] = content

        defaults = {'file': File(file=BytesIO(response.content),name=filename), 'project' : project}          
        instance, created = ProjectDocument.objects.get_or_create(project=project,
        file_stage='order confirmation', file_type='pdf', defaults=defaults)
        if created is False:
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)   
            instance.file = File(file=BytesIO(response.content),name=filename)
            instance.save()
                
        return instance
class ReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reason
        fields = "__all__"
class OrderNotConfirmationCreateSerializer(serializers.ModelSerializer):
    # send_mail = serializers.BooleanField(allow_null=True, required=False)
    REASON_CHOICES = (
        ('HP', _('High Price')),
        ('LQ', _('Low Quality')),
        ('DO', _('Delayed Order')),
        ('NN', _('No Need')),
        ('PO', _('Pending Order')),
    )
    
    try:
        reason_choices = serializers.MultipleChoiceField(write_only=True ,choices=Reason.objects.all())
    except:
        pass
    class Meta:
        model = OrderNotConfirmation
        exclude = ["created_at", "updated_at","no"]

    def validate(self, data):
        quotation = data.get('quotation', getattr(self.instance, 'quotation', None))
        if quotation.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if quotation.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if quotation.project.is_confirmed():
            raise serializers.ValidationError(_("You can't use not confirmation on this project, it is confirmed."))
        return data
    

class OrderConfirmationDetailSerializer(serializers.ModelSerializer):
    quotation = QuotationListSerializer(read_only=True)

    class Meta:
        model = OrderConfirmation
        exclude = ["created_at", "updated_at"]


class OrderConfirmationListSerializer(serializers.ModelSerializer):
    quotation = QuotationListSerializer(read_only=True)

    class Meta:
        model = OrderConfirmation
        fields = ["pk", "quotation"]


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        project = data.get('project', getattr(self.instance, 'project', None))
        order_confirmation = data.get('order_confirmation', getattr(self.instance, 'order_confirmation', None))
        inquiry = data.get('inquiry', getattr(self.instance, 'inquiry', None))

        if project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if project.is_claim_continue():
            raise serializers.ValidationError( _("You can't modify this project due to it claimed."))
        if project != order_confirmation.quotation.project:
            raise serializers.ValidationError(
                {"quotation": _("Select a valid choice. That choice is not one of the available choices.")})
        if project != inquiry.project:
            raise serializers.ValidationError(
                {"inquiry": _("Select a valid choice. That choice is not one of the available choices.")})
        if data.get('purchase_order_date'):
            error_message =  _("You can't add a purchase_order date before project date")
            if project.project_date > data.get('purchase_order_date'):       
                raise serializers.ValidationError(error_message)
            else:
                pass
        else:
            pass
        return data


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    order_confirmation = OrderConfirmationListSerializer(read_only=True)
    inquiry = InquiryListSerializer(read_only=True)
    creator = UserListSerializer(read_only=True)
    currency = CurrencyListSerializer(read_only=True)
    str = serializers.CharField(source='__str__')

    class Meta:
        model = PurchaseOrder
        exclude = ["created_at", "updated_at"]


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    order_confirmation = OrderConfirmationListSerializer(read_only=True)
    inquiry = InquiryListSerializer(read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ["id", "project", "no", "order_confirmation", "inquiry"]


class PurchaseOrderPartCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderPart
        exclude = ["created_at", "updated_at"]
        extra_kwargs = {
            'purchase_order': {'allow_null': True}
        }

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        quotation_part = data.get('quotation_part', getattr(self.instance, 'quotation_part', None))
        if hasattr(quotation_part.quotation, "confirmation"):
            try:
                purchase_order = PurchaseOrder.objects.get(
                    project=quotation_part.quotation.project,
                    order_confirmation=quotation_part.quotation.confirmation,
                    inquiry=quotation_part.inquiry_part.inquiry
                )
                print("found")
            except PurchaseOrder.DoesNotExist:
                purchase_order = PurchaseOrder.objects.create(
                    creator=self.context['request'].user,
                    project=quotation_part.quotation.project,
                    order_confirmation=quotation_part.quotation.confirmation,
                    inquiry=quotation_part.inquiry_part.inquiry,
                    currency=quotation_part.quotation.currency
                )
                print("created")
            data['purchase_order'] = purchase_order
        return data

    def validate(self, data):
        quotation_part = data.get('quotation_part', getattr(self.instance, 'quotation_part', None))
        purchase_order = data.get('purchase_order', getattr(self.instance, 'purchase_order', None))

        if purchase_order.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        
        if purchase_order.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        
        if not hasattr(quotation_part.quotation, "confirmation"):
            raise serializers.ValidationError(
                {"quotation": _("You can't add a part from an unconfirmed quotation.")})
        
        if purchase_order.project.is_claim_continue():
            raise serializers.ValidationError(
                {"quotation": _("You can't modify this project due to it claimed.")})    
            
        if quotation_part.inquiry_part.inquiry != purchase_order.inquiry:
            raise serializers.ValidationError(
                {"quotation_part": _("Select a valid choice. That choice is not one of the available choices.")})
        return data


class QuotationPartField(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        self.pk_field = kwargs.pop('pk_field', None)
        super().__init__(**kwargs)

    def display_value(self, instance):
        return instance


class PurchaseOrderPartListCreateSerializer(serializers.Serializer):
    quotation_part = QuotationPartField(queryset=QuotationPart.objects.all(), many=True)

    class Meta:
        fields = ['quotation_part', 'purchase_order', 'order_type']

    def validate(self, data):
        validation_errors = {'quotation_part': []}
        for quotation_part in data.get('quotation_part'):
            if quotation_part.quotation.project.is_closed:
                raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))

            if quotation_part.quotation.project.is_claim_continue():
                raise serializers.ValidationError( _("You can't modify this project due to it claimed."))
            
            if quotation_part and not hasattr(quotation_part.quotation, "confirmation"):
                validation_errors['quotation_part'].append(
                    _("The quotation of the '%(supplier)s / %(part_code)s / %(part)s' didn't confirmed yet." % {
                        'supplier': quotation_part.inquiry_part.inquiry.supplier.name,
                        'part_code': quotation_part.inquiry_part.request_part.part.code,
                        'part': quotation_part.inquiry_part.request_part.part.name,
                    }))
            if hasattr(quotation_part, 'purchased'):
                validation_errors['quotation_part'].append(
                    _("'%(supplier)s / %(part_code)s / %(part)s' is used already in a purchase order." % {
                        'supplier': quotation_part.inquiry_part.inquiry.supplier.name,
                        'part_code': quotation_part.inquiry_part.request_part.part.code,
                        'part': quotation_part.inquiry_part.request_part.part.name,
                    }))
        if validation_errors['quotation_part']:
            raise serializers.ValidationError(validation_errors)

        return data

    def create(self, validated_data):
        quotation_parts = []
        for quotation_part in validated_data.get('quotation_part'):
            try:
                purchase_order = PurchaseOrder.objects.get(
                    project=quotation_part.quotation.project,
                    order_confirmation=quotation_part.quotation.confirmation,
                    inquiry=quotation_part.inquiry_part.inquiry
                )
                print("found")
                quotation_parts.append(PurchaseOrderPart(purchase_order=purchase_order, quotation_part=quotation_part))
            except PurchaseOrder.DoesNotExist:
                purchase_order = PurchaseOrder.objects.create(
                    creator=self.context['request'].user,
                    project=quotation_part.quotation.project,
                    order_confirmation=quotation_part.quotation.confirmation,
                    inquiry=quotation_part.inquiry_part.inquiry,
                    currency=quotation_part.quotation.currency
                )
                print("created")
                quotation_parts.append(PurchaseOrderPart(purchase_order=purchase_order, quotation_part=quotation_part))

        return [{'quotation_part': part.quotation_part.id, 'purchase_order': part.purchase_order.id,
                 'order_type': part.order_type} for part in PurchaseOrderPart.objects.bulk_create(quotation_parts)]


class PurchaseOrderPartDetailSerializer(serializers.ModelSerializer):
    purchase_order = PurchaseOrderListSerializer(read_only=True)
    quotation_part = QuotationPartListSerializer(read_only=True)
    order_type = serializers.CharField(source='get_order_type_display')
    str = serializers.CharField(source='__str__')

    class Meta:
        model = PurchaseOrderPart
        exclude = ["created_at", "updated_at"]


class PurchaseOrderPartListSerializer(serializers.ModelSerializer):
    purchase_order = PurchaseOrderListSerializer(read_only=True)
    quotation_part = QuotationPartListSerializer(read_only=True)
    order_type = serializers.SerializerMethodField()
    unit_price = serializers.SerializerMethodField()
    total_price_3 = serializers.SerializerMethodField()
    str = serializers.CharField(source='__str__')
    
    def get_unit_price(self, obj):
        return obj.get_currency_unit_price()
    
    def get_total_price_3(self, obj):
        return obj.get_total_price_3()
    
    def get_order_type(self, obj):
        return {'name': obj.get_order_type_display(), 'value': obj.order_type}

    class Meta:
        model = PurchaseOrderPart
        fields = ["id", "purchase_order", "quotation_part", "order_type","unit_price", "total_price_3", "str"]


class DeliveryTransportationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTransportation
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        delivery = data.get('delivery', getattr(self.instance, 'delivery', None))

        if delivery.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if delivery.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if delivery.is_delivered:
            raise serializers.ValidationError(_("You can't modify the delivered delivery."))
        return data


class DeliveryTransportationDetailSerializer(serializers.ModelSerializer):
    currency = CurrencyListSerializer(read_only=True)
    total_charged_amount = serializers.CharField(source="get_total_charged_amount")

    class Meta:
        model = DeliveryTransportation
        exclude = ["created_at", "updated_at"]


class DeliveryTaxCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTax
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        delivery = data.get('delivery', getattr(self.instance, 'delivery', None))

        if delivery.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if delivery.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if delivery.is_delivered:
            raise serializers.ValidationError(_("You can't modify the delivered delivery."))

        return data


class DeliveryTaxDetailSerializer(serializers.ModelSerializer):
    currency = CurrencyListSerializer(read_only=True)
    total_charged_amount = serializers.CharField(source="get_total_charged_amount")

    class Meta:
        model = DeliveryTax
        exclude = ["created_at", "updated_at"]


class DeliveryInsuranceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryInsurance
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        delivery = data.get('delivery', getattr(self.instance, 'delivery', None))

        if delivery.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if delivery.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if delivery.is_delivered:
            raise serializers.ValidationError(_("You can't modify the delivered delivery."))

        return data


class DeliveryInsuranceDetailSerializer(serializers.ModelSerializer):
    currency = CurrencyListSerializer(read_only=True)
    total_charged_amount = serializers.CharField(source="get_total_charged_amount")

    class Meta:
        model = DeliveryInsurance
        exclude = ["created_at", "updated_at"]


class DeliveryCustomsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCustoms
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        delivery = data.get('delivery', getattr(self.instance, 'delivery', None))

        if delivery.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if delivery.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if delivery.is_delivered:
            raise serializers.ValidationError(_("You can't modify the delivered delivery."))

        return data


class DeliveryCustomsDetailSerializer(serializers.ModelSerializer):
    currency = CurrencyListSerializer(read_only=True)
    total_charged_amount = serializers.CharField(source="get_total_charged_amount")

    class Meta:
        model = DeliveryCustoms
        exclude = ["created_at", "updated_at"]


class DeliveryPackingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPacking
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        delivery = data.get('delivery', getattr(self.instance, 'delivery', None))

        if delivery.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if delivery.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if delivery.is_delivered:
            raise serializers.ValidationError(_("You can't modify the delivered delivery."))

        return data


class DeliveryPackingDetailSerializer(serializers.ModelSerializer):
    currency = CurrencyListSerializer(read_only=True)
    total_charged_amount = serializers.CharField(source="get_total_charged_amount")

    class Meta:
        model = DeliveryPacking
        exclude = ["created_at", "updated_at"]


class DeliveryCreateSerializer(serializers.ModelSerializer):
    send_mail = serializers.BooleanField(write_only=True, allow_null=True, required=False)

    def __init__(self, instance=None, data=empty, **kwargs):
        process_type_choices = {
            'STV': ['id', 'project', 'process_type', 'is_delivered', 'purchase_order', 'parts', 'shipping_company',
                    'tracking_no', 'port', 'agent', 'country', 'eta', 'waybill_no', 'dispatch_date', 'delivery_date',
                    'phone', 'fax_address', 'email', 'person_in_contact', 'weight', 'dimensions', 'send_mail'],
            'STC': ['id', 'project', 'process_type', 'is_delivered', 'purchase_order', 'parts', 'shipping_company',
                    'tracking_no', 'customer_location', 'waybill_no', 'dispatch_date', 'delivery_date', 'phone',
                    'fax_address', 'email', 'person_in_contact', 'weight', 'dimensions', 'send_mail'],
            'WTV': ['id', 'project', 'process_type', 'is_delivered', 'purchase_order', 'parts', 'shipping_company',
                    'tracking_no', 'port', 'agent', 'country', 'eta', 'waybill_no', 'dispatch_date', 'delivery_date',
                    'phone', 'fax_address', 'email', 'person_in_contact', 'weight', 'dimensions', 'send_mail'],
            'WTC': ['id', 'project', 'process_type', 'is_delivered', 'purchase_order', 'parts', 'shipping_company',
                    'tracking_no', 'customer_location', 'waybill_no', 'dispatch_date', 'delivery_date', 'phone',
                    'fax_address', 'email', 'person_in_contact', 'weight', 'dimensions', 'send_mail'],
            'STW': ['id', 'project', 'process_type', 'is_delivered', 'purchase_order', 'parts', 'shipping_company',
                    'tracking_no', 'waybill_no', 'dispatch_date', 'delivery_date', 'weight', 'dimensions', 'send_mail']
        }
        if instance:
            process_type = instance.process_type
        elif data is not empty:
            process_type = data.get('process_type', None)
        else:
            process_type = None
        if process_type in process_type_choices:
            fields = process_type_choices.get(process_type)
            exclude = None
            setattr(self.Meta, 'fields', fields)
            setattr(self.Meta, 'exclude', exclude)
        super().__init__(instance, data, **kwargs)

    def validate(self, data):
        self.send_mail = data.pop('send_mail', False)  # used for mailing when updating
        project = data.get('project', getattr(self.instance, 'project', None))
        purchase_order = data.get('purchase_order', getattr(self.instance, 'purchase_order', None))
        parts = data.get('parts', getattr(self.instance, 'parts', PurchaseOrderPart.objects.none()).all())

        if project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))  
        if self.instance and self.instance.is_delivered:
            raise serializers.ValidationError(_("You can't modify the delivered delivery."))
        if self.instance and data.get('is_delivered', None) and not self.instance.is_finish(check_delivery=False):
            raise serializers.ValidationError({"is_delivered": _("You can't deliver a not completed delivery.")})
        if project != purchase_order.project:
            raise serializers.ValidationError(
                {"purchase_order": _("Select a valid choice. That choice is not one of the available choices.")})
        for part in parts:
            if part.purchase_order != purchase_order:
                raise serializers.ValidationError(
                    {"parts": _("Select a valid choice. That choice is not one of the available choices.")})
            if part.delivery.all().filter(~Q(**{'id': self.instance.id} if self.instance else {})):
                raise serializers.ValidationError(
                    {"parts": _("You can't add a part that already is in another delivery.")})
        try:
            validate_email(project.request.person_in_contact.email)
        except ValidationError as e:
            raise serializers.ValidationError(_('Person in contact of the customer has no email address.'))
        if data.get('delivery_date') and data.get('dispatch_date'):
            error_message =  _("You can't add a dispatch date or delivery date before project date")
            if project.project_date > data.get('delivery_date') or project.project_date > data.get('dispatch_date'):       
                raise serializers.ValidationError(error_message)
            else:
                pass
        return data

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if self.send_mail:
            custom_send_mail(
                _('Your order has been packed!'),
                settings.DEFAULT_FROM_EMAIL,
                [instance.project.request.person_in_contact.email],
                template_path='sales/project/mail/shipped.html',
                context={'the_company': TheCompany.objects.get(id=1), 'delivery': instance}
            )
        elif validated_data.get('is_delivered', False):
            custom_send_mail(
                _('Your order has been delivered!'),
                settings.DEFAULT_FROM_EMAIL,
                [instance.project.request.person_in_contact.email],
                template_path='sales/project/mail/delivered.html',
                context={'the_company': TheCompany.objects.get(id=1), 'delivery': instance}
            )
        return instance

    def create(self, validated_data):
        instance = super().create(validated_data)
        custom_send_mail(
            _('Your order has been packed!'),
            settings.DEFAULT_FROM_EMAIL,
            [instance.project.request.person_in_contact.email],
            template_path='sales/project/mail/shipped.html',
            context={'the_company': TheCompany.objects.get(id=1), 'delivery': instance}
        )
        return instance

    class Meta:
        model = Delivery
        exclude = ["created_at", "updated_at"]
        extra_kwargs = {
            'port': {'required': True, 'allow_blank': False, 'allow_null': False},
            'agent': {'required': True, 'allow_blank': False, 'allow_null': False},
            'country': {'required': True, 'allow_null': False},
            'eta': {'required': True, 'allow_blank': False, 'allow_null': False},
            'customer_location': {'required': True, 'allow_blank': False, 'allow_null': False},
            'dispatch_date': {'required': True, 'allow_null': False},
            'phone': {'required': True, 'allow_blank': False, 'allow_null': False},
            'email': {'required': True, 'allow_blank': False, 'allow_null': False},
            'person_in_contact': {'required': True, 'allow_blank': False, 'allow_null': False}
        }


class DeliveryField(serializers.PrimaryKeyRelatedField):
    def display_value(self, instance):
        return instance


class PurchaseOrderPartField(serializers.PrimaryKeyRelatedField):
    def display_value(self, instance):
        return instance


class DeliveryPartAddSerializer(serializers.Serializer):
    delivery = DeliveryField(queryset=Delivery.objects.all())
    purchase_order_part = PurchaseOrderPartField(queryset=PurchaseOrderPart.objects.all())

    def validate(self, data):
        if data['delivery'].project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if data['delivery'].project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        if data['delivery'].is_delivered:
            raise serializers.ValidationError(_("You can't modify the delivered delivery."))
        if data['purchase_order_part'].purchase_order != data['delivery'].purchase_order:
            raise serializers.ValidationError(
                {"purchase_order_part": _("Select a valid choice. That choice is not one of the available choices.")})
        if data['purchase_order_part'].delivery.filter(id=data['delivery'].id):
            raise serializers.ValidationError(
                {"purchase_order_part": _("This purchase order part already exists in the delivery.")})
        return data

    def create(self, validated_data):
        delivery = validated_data.get('delivery')
        purchase_order_part = validated_data.get('purchase_order_part')
        delivery.parts.add(purchase_order_part)

        return {'delivery': delivery, 'purchase_order_part': purchase_order_part}


class DeliveryListSerializer(serializers.ModelSerializer):    

    process_type = serializers.CharField(source='get_process_type_display')
    country = CountryListSerializer(read_only=True)

    class Meta:
        model = Delivery
        fields = ['id', 'project', 'process_type', 'purchase_order', 'shipping_company', 'tracking_no', 'port', 'agent',
                  'country', 'customer_location', 'eta', 'waybill_no', 'dispatch_date', 'delivery_date', 'phone',
                  'email', 'person_in_contact']


class DeliveryDetailSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    process_type = serializers.CharField(source='get_process_type_display')
    purchase_order = PurchaseOrderListSerializer(read_only=True)
    parts = PurchaseOrderPartListSerializer(read_only=True, many=True)
    country = CountryListSerializer(read_only=True)
    transportation = DeliveryTransportationDetailSerializer(read_only=True)
    tax = DeliveryTaxDetailSerializer(read_only=True)
    insurance = DeliveryInsuranceDetailSerializer(read_only=True)
    customs = DeliveryCustomsDetailSerializer(read_only=True)
    packing = DeliveryPackingDetailSerializer(read_only=True)
    str = serializers.CharField(source='__str__')

    class Meta:
        model = Delivery
        exclude = ["created_at", "updated_at"]


class ClaimReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimReason
        fields = "__all__"        
        
class ClaimResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimResult
        fields = "__all__"
        
class ClaimsFollowUpCreateSerializer(serializers.ModelSerializer):
    # send_mail = serializers.BooleanField(allow_null=True, required=False)
    try:
        claim_reason_choices = serializers.MultipleChoiceField(write_only=True, choices=ClaimReason.objects.all())
    except:
        pass
    class Meta:
        model = ClaimsFollowUp
        exclude = ["created_at", "updated_at","no",'claim_status','customer_happiness','claim_results','claim_notes']

    def validate(self, data):
        
        delivery = data.get('delivery', getattr(self.instance, 'delivery', None))
        print(delivery)
        if delivery.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        if delivery.project.is_claim_continue():
            raise serializers.ValidationError(_("You can't modify this project due to it claimed."))
        return data
    
class ClaimsFollowUpUpdateSerializer(serializers.ModelSerializer):
    try:
        claim_results = serializers.MultipleChoiceField(write_only=True, choices=ClaimResult.objects.all())
    except:
        pass
    class Meta:
        model = ClaimsFollowUp
        fields = ['claim_status','customer_happiness','claim_results','claim_notes']

    def validate(self, data):
        
        delivery = data.get('delivery', getattr(self.instance, 'delivery', None))
        print(delivery)
        if delivery.project.is_closed:
            raise serializers.ValidationError(_("You can't modify this project due to it has been closed."))
        
        return data
    
class ClaimsFollowUpDetailSerializer(serializers.ModelSerializer):
    claim_reason_choices = serializers.SerializerMethodField(read_only=True)

    
    def get_claim_reason_choices(self, obj):
        return ClaimReasonSerializer(obj.claim_reason_choices, many=True).data

    class Meta:
        model = ClaimsFollowUp
        exclude = ["created_at", "updated_at",'claim_status','customer_happiness','claim_results','claim_notes']

class ClaimsFollowUpListSerializer(serializers.ModelSerializer):
    delivery = DeliveryDetailSerializer(read_only=True)
    request = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(format="%d %b %Y %H:%m")
    updated_at = serializers.DateTimeField(format="%d %b %Y %H:%m")
    
    def get_request(self,obj):
        print(RequestListSerializer(obj.delivery.project.request).data)
        return RequestListSerializer(obj.delivery.project.request).data
    
    class Meta:
        model = ClaimsFollowUp
        fields = ["pk", "delivery","claim_status","created_at", "updated_at","request"]
