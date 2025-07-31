from rest_framework import serializers
from django_filters import FilterSet, DateFilter
from rest_framework.utils import html, model_meta, representation
from django.utils.translation import gettext_lazy as _

from account.models import *
from card.models import Company, Current

from card.api.serializers import CurrencyListSerializer, CompanyListSerializer, VesselListSerializer, BillingListSerializer
from sale.api.serializers import ProjectListSerializer, RequestListSerializer, PurchaseOrderListSerializer, PurchaseOrderPartListSerializer, OrderConfirmationListSerializer, QuotationPartListSerializer,PurchaseOrder
from user.api.serializers import UserListSerializer
from service.api.serializers import OfferListSerializer, OfferServiceCardListSerializer, OfferExpenseListSerializer, OfferPartListSerializer
from data.api.serializers import ExpenseListSerializer, PartListSerializer,ServiceCardListSerializer
from source.api.serializers import CompanyListSerializer as SourceCompanyListSerializer

from decimal import Decimal

class IncomingInvoiceListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sellerId = serializers.SerializerMethodField()
    projectId = serializers.SerializerMethodField()
    projectNo = serializers.SerializerMethodField()
    purchaseOrderNo = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    incomingInvoiceNo = serializers.CharField()
    incomingInvoiceDate = serializers.DateField()
    paymentDate = serializers.DateField()
    discountPrice = serializers.FloatField()
    vatPrice = serializers.FloatField()
    netPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    paidPrice = serializers.FloatField()
    exchangeRate = serializers.FloatField()
    currency = serializers.SerializerMethodField()
    forexBuying = serializers.SerializerMethodField()
    group = serializers.CharField()
    
    def get_projectId(self, obj):
        return obj.project.id if obj.project else ''
    
    def get_sellerId(self, obj):
        return obj.seller.id if obj.seller else ''
    
    def get_projectNo(self, obj):
        if obj.group == "order":
            return obj.project.projectNo if obj.project else ''
        elif obj.group == "purchasing":
            return obj.purchasingProject.projectNo if obj.purchasingProject else ''
        else:
            return ""
        
    def get_purchaseOrderNo(self, obj):
        if obj.group == "order":
            return obj.purchaseOrder.purchaseOrderNo if obj.purchaseOrder else ''
        elif obj.group == "purchasing":
            return obj.purchasingPurchaseOrder.purchaseOrderNo if obj.purchasingPurchaseOrder else ''
        else:
            return ""
    
    def get_seller(self, obj):
        return obj.seller.name if obj.seller else ''
    
    def get_customer(self, obj):
        return obj.customerSource.name if obj.customerSource else ''
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''
    
    def get_forexBuying(self, obj):
        return obj.currency.forexBuying if obj.currency else ''


  
class IncomingInvoiceItemListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    invoiceId = serializers.SerializerMethodField()
    name = serializers.CharField()
    description = serializers.CharField()
    unit = serializers.CharField()
    currency = serializers.SerializerMethodField()
    quantity = serializers.FloatField()
    unitPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    
    def get_invoiceId(self, obj):
        return obj.invoice.id if obj.invoice else ''
    
    def get_currency(self, obj):
        return obj.invoice.currency.symbol if obj.invoice.currency else ''
    
    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance
    

class IncomingInvoiceExpenseListSerializer(serializers.ModelSerializer):
    invoice = IncomingInvoiceListSerializer()
    user = UserListSerializer()
    expense = ExpenseListSerializer()
    class Meta:
        model = IncomingInvoiceExpense
        fields = ["id", "user", "sessionKey", "id", "invoice", "expense", "name", "description", "quantity","unit", "unitPrice", "totalPrice", "vat", "vatPrice"]   

class IncomingInvoiceSupplierListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()  

    
class SendInvoiceListSerializer2(serializers.ModelSerializer):
    project = ProjectListSerializer()
    offer = OfferListSerializer()
    #orderConfirmation = OrderConfirmationListSerializer()
    seller = CompanyListSerializer()
    customer = CompanyListSerializer()
    vessel = VesselListSerializer()
    billing = BillingListSerializer()
    currency = CurrencyListSerializer()
    
    def to_internal_value(self, data):
        return SendInvoice.objects.get(pk=data['id'])
    
    class Meta:
        model = SendInvoice
        fields = ["id", "user", "code","group", "project", "offer", "seller", "customer","vessel", "billing", "sendInvoiceNo", "sendInvoiceNoSys", "sendInvoiceDate","paymentDate", "awb", "ready","payed", "currency", "created_date", "discountPrice", "vatPrice", "netPrice", "totalPrice", "paidPrice"]

class SendInvoiceListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    customerId = serializers.SerializerMethodField()
    projectId = serializers.SerializerMethodField()
    projectNo = serializers.SerializerMethodField()
    offerNo = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    vessel = serializers.SerializerMethodField()
    imo = serializers.SerializerMethodField()
    billing = serializers.SerializerMethodField()
    exchangeRate = serializers.FloatField()
    currency = serializers.SerializerMethodField()
    code = serializers.IntegerField()
    group = serializers.CharField()
    sendInvoiceNo = serializers.CharField()
    sendInvoiceNoSys = serializers.CharField()
    sendInvoiceDate = serializers.DateField()
    paymentDate = serializers.DateField()
    awb = serializers.CharField()
    ready = serializers.BooleanField()
    payed = serializers.BooleanField()
    created_date = serializers.DateTimeField()
    discountPrice = serializers.SerializerMethodField()
    vatPrice = serializers.FloatField()
    netPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    paidPrice = serializers.FloatField()
    
    def get_customerId(self, obj):
        return obj.customer.id if obj.customer else ''

    def get_projectId(self, obj):
        return obj.project.id if obj.project else ''
    
    def get_projectNo(self, obj):
        return obj.project.projectNo if obj.project else ''
    
    def get_customer(self, obj):
        return obj.customer.name if obj.customer else ''
    
    def get_vessel(self, obj):
        return obj.vessel.name if obj.vessel else ''
    
    def get_imo(self, obj):
        return obj.vessel.imo if obj.vessel else ''
    
    def get_billing(self, obj):
        return obj.billing.name if obj.billing else ''
    
    def get_offerNo(self, obj):
        return obj.offer.offerNo if obj.offer else ''
    
    def get_discountPrice(self, obj):
        return float(Decimal(str(obj.discountPrice)) + Decimal(str(obj.extraDiscountPrice)))
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''

class SendInvoiceCustomerListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()  

class SendInvoiceExpenseListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    invoiceId = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    unit = serializers.CharField()
    quantity = serializers.FloatField()
    unitPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    currency = serializers.SerializerMethodField()

    def get_invoiceId(self, obj):
        return obj.invoice.id if obj.invoice else ''
    
    def get_code(self, obj):
        return obj.expense.code if obj.expense else ''
    
    def get_name(self, obj):
        return obj.expense.name if obj.expense else ''
    
    def get_currency(self, obj):
        return obj.invoice.currency.symbol if obj.invoice.currency else ''
    
    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

class SendInvoiceItemListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    invoiceId = serializers.SerializerMethodField()
    name = serializers.CharField()
    description = serializers.CharField()
    remark = serializers.CharField()
    unit = serializers.CharField()
    currency = serializers.SerializerMethodField()
    sequency = serializers.IntegerField()
    quantity = serializers.FloatField()
    unitPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    trDescription = serializers.CharField(allow_blank=True)
    
    def get_invoiceId(self, obj):
        return obj.invoice.id if obj.invoice else ''
    
    def get_currency(self, obj):
        return obj.invoice.currency.symbol if obj.invoice.currency else ''
    
    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance
    
class SendInvoicePartListSerializer(serializers.ModelSerializer):
    invoice = SendInvoiceListSerializer()
    user = UserListSerializer()
    quotationPart = QuotationPartListSerializer()
    class Meta:
        model = SendInvoicePart
        fields = ["user", "sessionKey", "id", "invoice", "quotationPart", "quantity", "sequency", "unitPrice", "totalPrice", "vat", "vatPrice", "trDescription"]
        
class PaymentListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    customer = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    paymentNo = serializers.CharField()
    type = serializers.CharField()
    paymentDate = serializers.DateField()
    amount = serializers.FloatField()
    description = serializers.CharField()
    forexBuying = serializers.SerializerMethodField()
    invoices = serializers.SerializerMethodField()
    bank = serializers.SerializerMethodField()
    invoiceAmount = serializers.SerializerMethodField()
    
    def get_customer(self, obj):
        return obj.customer.name if obj.customer else ''
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''
    
    def get_forexBuying(self, obj):
        return obj.currency.forexBuying if obj.currency else ''
    
    def get_bank(self, obj):
        return obj.sourceBank.bankName if obj.sourceBank else ''
    
    def get_invoiceAmount(self, obj):
        invoices = obj.paymentinvoice_set.select_related().all()
        if invoices:
            return sum(invoice.amount for invoice in invoices)
        else:
            return 0
    
    def get_invoices(self, obj):
        sendInvoicesIds = []
        incomingInvoicesIds = []
        
        # paymentSendInvoices = obj.invoices["sendInvoices"]
        # for paymentSendInvoice in paymentSendInvoices:
        #     sendInvoicesIds.append(paymentSendInvoice["invoice"])
            
        # paymentIncomingInvoices = obj.invoices["incomingInvoices"]
        # for paymentIncomingInvoice in paymentIncomingInvoices:
        #     incomingInvoicesIds.append(paymentIncomingInvoice["invoice"])
            
        # sendInvoicesList = []
        # sendInvoices = SendInvoice.objects.select_related().filter(id__in = sendInvoicesIds).order_by("-id")
        # for sendInvoice in sendInvoices:
        #     sendInvoicesList.append(sendInvoice.sendInvoiceNo)
            
        # incomingInvoicesList = []
        # incomingInvoices = IncomingInvoice.objects.select_related().filter(id__in = incomingInvoicesIds).order_by("-id")
        # for incomingInvoice in incomingInvoices:
        #     incomingInvoicesList.append(incomingInvoice.incomingInvoiceNo)
        paymentInvoicesList = []
        paymentInvoices = obj.paymentinvoice_set.all().order_by("invoicePaymentDate")
        for paymentInvoice in paymentInvoices:
            if paymentInvoice.sendInvoice:
                if paymentInvoice.sendInvoice.sendInvoiceNo:
                    paymentInvoicesList.append(paymentInvoice.sendInvoice.sendInvoiceNo)
                else:
                    paymentInvoicesList.append("invoice")
            elif paymentInvoice.incomingInvoice:
                if paymentInvoice.incomingInvoice.incomingInvoiceNo:
                    paymentInvoicesList.append(paymentInvoice.incomingInvoice.incomingInvoiceNo)
                else:
                    paymentInvoicesList.append("invoice")

        return {
            "invoices": paymentInvoicesList
        }

class PaymentInvoiceListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    paymentId = serializers.SerializerMethodField()
    paymentCurrency = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    invoice = serializers.SerializerMethodField()
    invoiceDate = serializers.SerializerMethodField()
    invoicePaymentDate = serializers.SerializerMethodField()
    invoiceTotalPrice = serializers.SerializerMethodField()
    invoiceBalance = serializers.SerializerMethodField()
    invoiceCurrency = serializers.SerializerMethodField()
    type = serializers.CharField()
    amount = serializers.FloatField()
    invoiceCurrencyAmount = serializers.FloatField()
    created_date = serializers.DateTimeField(format="%d.%m.%Y", required=False, read_only=True)
    
    def get_paymentId(self, obj):
        return obj.payment.id if obj.payment else ''
    
    def get_project(self, obj):
        if obj.sendInvoice:
            if obj.sendInvoice.group == "order":
                return obj.sendInvoice.project.projectNo if obj.sendInvoice.project else ''
            elif obj.sendInvoice.group == "service":
                return obj.sendInvoice.offer.offerNo if obj.sendInvoice.offer else ''
            else:
                ""
        elif obj.incomingInvoice:
            if obj.incomingInvoice.group == "order":
                return obj.incomingInvoice.project.projectNo if obj.incomingInvoice.project else ''
            elif obj.incomingInvoice.group == "purchasing":
                return obj.incomingInvoice.purchasingProject.projectNo if obj.incomingInvoice.purchasingProject else ''
            else:
                ""
        else:
            ""

    def get_invoice(self, obj):
        if obj.sendInvoice:
            return obj.sendInvoice.sendInvoiceNo
        elif obj.incomingInvoice:
            return obj.incomingInvoice.incomingInvoiceNo
        else:
            return ""
    
    def get_invoiceDate(self, obj):
        if obj.sendInvoice:
            return obj.sendInvoice.sendInvoiceDate.strftime("%d.%m.%Y")
        elif obj.incomingInvoice:
            return obj.incomingInvoice.incomingInvoiceDate.strftime("%d.%m.%Y")
        else:
            return ""
    
    def get_invoicePaymentDate(self, obj):
        if obj.sendInvoice:
            return obj.sendInvoice.paymentDate.strftime("%d.%m.%Y")
        elif obj.incomingInvoice:
            return obj.incomingInvoice.paymentDate.strftime("%d.%m.%Y")
        else:
            return ""
        
    def get_invoiceTotalPrice(self, obj):
        if obj.sendInvoice:
            return obj.sendInvoice.totalPrice
        elif obj.incomingInvoice:
            return obj.incomingInvoice.totalPrice
        else:
            return ""
        
    def get_invoiceBalance(self, obj):
        if obj.sendInvoice:
            return obj.sendInvoice.totalPrice - obj.sendInvoice.paidPrice
        elif obj.incomingInvoice:
            return obj.incomingInvoice.totalPrice - obj.incomingInvoice.paidPrice
        else:
            return ""
    
    def get_invoiceCurrency(self, obj):
        if obj.sendInvoice:
            return obj.sendInvoice.currency.code
        elif obj.incomingInvoice:
            return obj.incomingInvoice.currency.code
        else:
            return ""
        
    def get_paymentCurrency(self, obj):
        return obj.payment.currency.code if obj.payment.currency else ''

        

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance
    
    
class InvoiceForPaymentListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    companyId = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    invoiceNo = serializers.SerializerMethodField()
    invoiceDate = serializers.SerializerMethodField()
    paymentDate = serializers.DateField()
    totalPrice = serializers.FloatField()
    paidPrice = serializers.FloatField()
    exchangeRate = serializers.FloatField()
    currency = serializers.SerializerMethodField()
    group = serializers.CharField()

    def get_companyId(self, obj):
        if isinstance(obj, SendInvoice):
            return obj.customer.id if obj.seller else ''
        elif isinstance(obj, IncomingInvoice):
            return obj.seller.id if obj.seller else ''
    
    def get_project(self, obj):
        if isinstance(obj, SendInvoice):
            if obj.group == "order":
                return obj.project.projectNo if obj.project else ''
            elif obj.group == "service":
                return obj.offer.offerNo if obj.offer else ''
        elif isinstance(obj, IncomingInvoice):
            if obj.group == "order":
                return obj.project.projectNo if obj.project else ''
            elif obj.group == "purchasing":
                return obj.purchasingProject.projectNo if obj.purchasingProject else ''
    
    def get_invoiceNo(self, obj):
        if isinstance(obj, SendInvoice):
            return obj.sendInvoiceNo
        elif isinstance(obj, IncomingInvoice):
            return obj.incomingInvoiceNo
        
    def get_invoiceDate(self, obj):
        if isinstance(obj, SendInvoice):
            return obj.sendInvoiceDate.strftime("%d.%m.%Y")
        elif isinstance(obj, IncomingInvoice):
            return obj.incomingInvoiceDate.strftime("%d.%m.%Y")
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''   


        
class ProformaInvoiceListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    projectId = serializers.SerializerMethodField()
    projectNo = serializers.SerializerMethodField()
    offerNo = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    vessel = serializers.SerializerMethodField()
    billing = serializers.SerializerMethodField()
    exchangeRate = serializers.FloatField()
    currency = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    code = serializers.IntegerField()
    group = serializers.CharField()
    proformaInvoiceNo = serializers.CharField()
    proformaInvoiceDate = serializers.DateField()
    paymentDate = serializers.DateField()
    awb = serializers.CharField()
    ready = serializers.BooleanField()
    payed = serializers.BooleanField()
    created_date = serializers.DateTimeField()
    discountPrice = serializers.FloatField()
    vatPrice = serializers.FloatField()
    netPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    paidPrice = serializers.FloatField()
    
    def get_projectId(self, obj):
        return obj.project.id if obj.project else ''
    
    def get_projectNo(self, obj):
        return obj.project.projectNo if obj.project else ''
    
    def get_customer(self, obj):
        return obj.customer.name if obj.customer else ''
    
    def get_vessel(self, obj):
        return obj.vessel.name if obj.vessel else ''
    
    def get_billing(self, obj):
        return obj.billing.name if obj.billing else ''
    
    def get_offerNo(self, obj):
        return obj.offer.offerNo if obj.offer else ''
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''
        
class ProformaInvoiceItemListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    invoiceId = serializers.SerializerMethodField()
    name = serializers.CharField()
    description = serializers.CharField()
    unit = serializers.CharField()
    currency = serializers.SerializerMethodField()
    sequency = serializers.IntegerField()
    quantity = serializers.FloatField()
    unitPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    trDescription = serializers.CharField(allow_blank=True)
    
    def get_invoiceId(self, obj):
        return obj.invoice.id if obj.invoice else ''
    
    def get_currency(self, obj):
        return obj.invoice.currency.symbol if obj.invoice.currency else ''
    
    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance
 
     
class ProformaInvoicePartListSerializer(serializers.ModelSerializer):
    invoice = ProformaInvoiceListSerializer()
    user = UserListSerializer()
    quotationPart = QuotationPartListSerializer()
    class Meta:
        model = ProformaInvoicePart
        fields = ["user", "sessionKey", "id", "invoice", "quotationPart", "quantity", "sequency", "unitPrice", "totalPrice", "vat", "vatPrice"]

class ProformaInvoicePartListSerializer2(serializers.ModelSerializer):
    invoice = SendInvoiceListSerializer(read_only = True)
    sessionKey = serializers.CharField()
    id = serializers.IntegerField()
    partNo = serializers.CharField()
    sessidescriptiononKey = serializers.CharField()
    unit = serializers.CharField()
    quantity = serializers.FloatField()
    sequency = serializers.IntegerField()
    unitPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    vat = serializers.FloatField()
    vatPrice = serializers.FloatField()
    
    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

class ProformaInvoiceExpenseListSerializer(serializers.ModelSerializer):
    invoice = ProformaInvoiceListSerializer()
    user = UserListSerializer()
    expense = ExpenseListSerializer()
    class Meta:
        model = ProformaInvoiceExpense
        fields = ["id", "user", "sessionKey", "id", "invoice", "expense", "name", "description", "quantity","unit", "unitPrice", "totalPrice", "vat", "vatPrice"]
        
class CommericalInvoiceListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    projectId = serializers.SerializerMethodField()
    projectNo = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    vessel = serializers.SerializerMethodField()
    billing = serializers.SerializerMethodField()
    exchangeRate = serializers.FloatField()
    currency = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    code = serializers.IntegerField()
    group = serializers.CharField()
    commericalInvoiceNo = serializers.CharField()
    commericalInvoiceDate = serializers.DateField()
    paymentDate = serializers.DateField()
    transport = serializers.CharField()
    created_date = serializers.DateTimeField()
    discountPrice = serializers.FloatField()
    vatPrice = serializers.FloatField()
    netPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    
    def get_projectId(self, obj):
        return obj.project.id if obj.project else ''
    
    def get_projectNo(self, obj):
        return obj.project.projectNo if obj.project else ''
    
    def get_seller(self, obj):
        return obj.seller.name if obj.seller else ''
    
    def get_customer(self, obj):
        return obj.customer.name if obj.customer else ''
    
    def get_vessel(self, obj):
        return obj.vessel.name if obj.vessel else ''
    
    def get_billing(self, obj):
        return obj.billing.name if obj.billing else ''
    
    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''

class CommericalInvoiceExpenseListSerializer(serializers.ModelSerializer):
    invoice = CommericalInvoiceListSerializer()
    user = UserListSerializer()
    expense = ExpenseListSerializer()
    class Meta:
        model = CommericalInvoiceExpense
        fields = ["id", "user", "sessionKey", "id", "invoice", "expense", "name", "description", "quantity","unit", "unitPrice", "totalPrice", "vat", "vatPrice"]   

class CommericalInvoiceItemListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    invoiceId = serializers.SerializerMethodField()
    name = serializers.CharField()
    description = serializers.CharField()
    unit = serializers.CharField()
    currency = serializers.SerializerMethodField()
    sequency = serializers.IntegerField()
    quantity = serializers.FloatField()
    unitPrice = serializers.FloatField()
    totalPrice = serializers.FloatField()
    trDescription = serializers.CharField(allow_blank=True)
    
    def get_invoiceId(self, obj):
        return obj.invoice.id if obj.invoice else ''
    
    def get_currency(self, obj):
        return obj.invoice.currency.symbol if obj.invoice.currency else ''
    
    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

class ProcessStatusListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    company = serializers.SerializerMethodField()
    vessel = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    purchaseOrders = serializers.SerializerMethodField()
    orderConfirmation = serializers.SerializerMethodField()
    orderConfirmationDate = serializers.SerializerMethodField()
    orderConfirmationId = serializers.SerializerMethodField()
    offerId = serializers.SerializerMethodField()
    equipment = serializers.SerializerMethodField()
    maker = serializers.SerializerMethodField()
    makerType = serializers.SerializerMethodField()
    processStatusNo = serializers.CharField()
    projectNo = serializers.SerializerMethodField()
    projectDate = serializers.SerializerMethodField()
    type = serializers.CharField(source='get_type_display')
    processStatusDate = serializers.DateField()
    created_date = serializers.DateTimeField(format="%d.%m.%Y", required=False, read_only=True)
    
    def get_company(self, obj):
        if obj.type == "order":
            return obj.project.order_tracking.first().theRequest.customer.name if obj.project.order_tracking.first().theRequest.customer else ""
        elif obj.type == "service":
            return obj.offer.customer.name if obj.offer.customer else ""
        elif obj.type == "purchasing":
            return obj.purchasingProject.sourceCompany.name if obj.purchasingProject.sourceCompany else ""
    
    def get_vessel(self, obj):
        if obj.type == "order":
            return obj.project.order_tracking.first().theRequest.vessel.name if obj.project.order_tracking.first().theRequest.vessel else ""
        elif obj.type == "service":
            return obj.offer.vessel.name if obj.offer.vessel else ""
        elif obj.type == "purchasing":
            return ""
        
    def get_status(self, obj):
        if obj.type == "order":
            return obj.project.order_tracking.first().purchaseOrders.first().orderConfirmation.get_status_display() if obj.project.order_tracking.first().purchaseOrders.first().orderConfirmation else ""
        elif obj.type == "service":
            if obj.offer:
                if obj.offer.status == "active":
                    return obj.offer.get_status_display()
                elif obj.offer.status == "finished":
                    if obj.offer.sendInvoiced == True:
                        return "Invoiced"
                    else:
                        return "Invoicing"
        elif obj.type == "purchasing":
            return "Invoiced" if obj.purchasingProject.invoiced else "Invoicing"
        
    def get_items(self, obj):
        if obj.type == "order":
            return obj.project.order_tracking.first().items if obj.project.order_tracking.first() else ""
        elif obj.type == "service":
            return ""
        elif obj.type == "purchasing":
            return ""
        
    def get_projectNo(self, obj):
        if obj.type == "order":
            return obj.project.projectNo if obj.project else ""
        elif obj.type == "service":
            return obj.offer.offerNo if obj.offer else ""
        elif obj.type == "purchasing":
            return obj.purchasingProject.projectNo if obj.purchasingProject else ""
        
    def get_projectDate(self, obj):
        if obj.type == "order":
            return obj.project.order_tracking.first().theRequest.requestDate.strftime("%d.%m.%Y") if obj.project.order_tracking.first().theRequest else ""
        elif obj.type == "service":
            return obj.offer.offerDate.strftime("%d.%m.%Y") if obj.offer else ""
        elif obj.type == "purchasing":
            return obj.purchasingProject.projectDate.strftime("%d.%m.%Y") if obj.purchasingProject else ""
        
    def get_purchaseOrders(self, obj):
        if obj.type == "order":
            purchaseOrders = obj.project.order_tracking.first().purchaseOrders.all()  # ManyToManyField'dan tüm ilişkili nesneleri al
            items_list = []
            for item in purchaseOrders:
                items_list.append({
                    "id": item.id,
                    "purchaseOrder": item.purchaseOrderNo,
                })
            return items_list
        elif obj.type == "service":
            return []
        elif obj.type == "purchasing":
            purchaseOrders = obj.purchasingProject.purchasing_purchase_order.all()  # ManyToManyField'dan tüm ilişkili nesneleri al
            items_list = []
            for item in purchaseOrders:
                items_list.append({
                    "id": item.id,
                    "purchaseOrder": item.purchaseOrderNo,
                })
            return items_list
        
    def get_orderConfirmation(self, obj):
        if obj.type == "order":
            return obj.project.order_tracking.first().purchaseOrders.first().orderConfirmation.orderConfirmationNo if obj.project.order_tracking.first().purchaseOrders.first().orderConfirmation else ""
        elif obj.type == "service":
            return ""
        elif obj.type == "purchasing":
            return ""
        
    def get_orderConfirmationDate(self, obj):
        if obj.type == "order":
            return obj.project.order_tracking.first().purchaseOrders.first().orderConfirmation.orderConfirmationDate if obj.project.order_tracking.first().purchaseOrders.first().orderConfirmation else ""
        elif obj.type == "service":
            return ""
        elif obj.type == "purchasing":
            return ""
        
    def get_orderConfirmationId(self, obj):
        if obj.type == "order":
            return obj.project.order_tracking.first().purchaseOrders.first().orderConfirmation.id if obj.project.order_tracking.first().purchaseOrders.first().orderConfirmation else ""
        elif obj.type == "service":
            return ""
        elif obj.type == "purchasing":
            return ""
        
    def get_offerId(self, obj):
        if obj.type == "order":
            return ""
        elif obj.type == "service":
            return obj.offer.id if obj.offer else ""
        elif obj.type == "purchasing":
            return ""
        
    def get_equipment(self, obj):
        if obj.type == "order":
            return ""
        elif obj.type == "service":
            if obj.offer.equipment:
                if obj.offer.equipment.maker:
                    if obj.offer.equipment.makerType:
                        if obj.offer.equipment.version:
                            return str(obj.offer.equipment.maker.name) + " " + str(obj.offer.equipment.makerType.type) + " " + str(obj.offer.equipment.category) + " " + str(obj.offer.equipment.serialNo) + " " + str(obj.offer.equipment.cyl) + " " + str(obj.offer.equipment.version)
                        else:
                            return str(obj.offer.equipment.maker.name) + " " + str(obj.offer.equipment.makerType.type) + " " + str(obj.offer.equipment.category) + " " + str(obj.offer.equipment.serialNo) + " " + str(obj.offer.equipment.cyl)
                    else:
                        return str(obj.offer.equipment.maker.name) + " " + str(obj.offer.equipment.category) + " " + str(obj.offer.equipment.serialNo) + " " + str(obj.offer.equipment.cyl) + " " + str(obj.offer.equipment.version)
                else:
                    return str(obj.offer.equipment.category) + " " + str(obj.offer.equipment.serialNo) + " " + str(obj.offer.equipment.cyl) + " " + str(obj.offer.equipment.version)
            else:
                return ""
        elif obj.type == "purchasing":
            return ""
        
    def get_maker(self, obj):
        if obj.type == "order":
            return obj.project.order_tracking.first().theRequest.maker.name if obj.project.order_tracking.first().theRequest.maker else ""
        elif obj.type == "service":
            if obj.offer.equipment:
                if obj.offer.equipment.maker:
                    return obj.offer.equipment.maker.name
                else:
                    return ""
            else:
                return ""
        elif obj.type == "purchasing":
            return ""
        
    def get_makerType(self, obj):
        if obj.type == "order":
            return obj.project.order_tracking.first().theRequest.makerType.type if obj.project.order_tracking.first().theRequest.makerType else ""
        elif obj.type == "service":
            if obj.offer.equipment:
                if obj.offer.equipment.makerType:
                    return obj.offer.equipment.makerType.type
                else:
                    return ""
            else:
                return ""
        elif obj.type == "purchasing":
            return ""
        
        


#####SOA#####
class SOAListSerializer(serializers.ModelSerializer):
    
    
    
    class Meta:
        model = Company
        fields = ["id", "name"]
 

#####SOA COMPANY DETAIL#####       
class SOAIncomingInvoiceListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    project = ProjectListSerializer()
    customer = CompanyListSerializer()
    currency = CurrencyListSerializer()
    date = serializers.DateTimeField(source = "created_date", format="%d.%m.%Y %H:%M:%S")
    datetime = serializers.DateTimeField(source = "created_date", format="%Y%m%d%H%M%S")
    price = serializers.FloatField(source = "totalPrice")
    group = serializers.CharField()
    incomingInvoiceNo = serializers.CharField()
    
class SOASendInvoiceListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    project = ProjectListSerializer()
    offer = OfferListSerializer()
    customer = CompanyListSerializer()
    currency = CurrencyListSerializer()
    date = serializers.DateTimeField(source = "created_date", format="%d.%m.%Y %H:%M:%S")
    datetime = serializers.DateTimeField(source = "created_date", format="%Y%m%d%H%M%S")
    price = serializers.FloatField(source = "totalPrice")
    group = serializers.CharField()
    sendInvoiceNo = serializers.CharField()
    
class SOAPaymentListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    project = []
    customer = CompanyListSerializer()
    currency = CurrencyListSerializer()
    paymentType = serializers.CharField(source = "type")
    date = serializers.DateField(source = "paymentDate", format="%d.%m.%Y")
    datetime = serializers.DateTimeField(source = "created_date", format="%Y%m%d%H%M%S")
    price = serializers.FloatField(source = "amount")
    

####SOA FULL HISTORY####
class ProcessListSerializer2(serializers.ModelSerializer):
    company = CompanyListSerializer()
    incomingInvoice = serializers.PrimaryKeyRelatedField(read_only=True)
    sendInvoice = serializers.PrimaryKeyRelatedField(read_only=True)
    payment = serializers.PrimaryKeyRelatedField(read_only=True)
    currency = CurrencyListSerializer()
    processDateTime = serializers.DateTimeField(format="%d.%m.%Y %H:%M:%S")
    created_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M:%S")
    class Meta:
        model = Process
        fields = ["id", "user", "company", "incomingInvoice", "sendInvoice", "payment", "currency", "companyName", "sourceNo","processNo", "type", "processDateTime", "created_date", "amount", "description"]
        

class ProcessListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    company = serializers.SerializerMethodField()
    companyId = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    #incomingInvoice = IncomingInvoiceListSerializer()
    #sendInvoice = SendInvoiceListSerializer()
    #payment = PaymentListSerializer()
    # incomingInvoice = serializers.PrimaryKeyRelatedField(read_only=True)
    # sendInvoice = serializers.PrimaryKeyRelatedField(read_only=True)
    # payment = serializers.PrimaryKeyRelatedField(read_only=True)
    currency = serializers.SerializerMethodField()
    exchangeRate = serializers.SerializerMethodField()
    sourceNo = serializers.CharField()
    type = serializers.CharField()
    processDateTime = serializers.DateTimeField(format="%d.%m.%Y %H:%M:%S")
    amount = serializers.FloatField()
    
    def get_company(self, obj):
        return obj.company.name if obj.company else ''
    
    def get_companyId(self, obj):
        return obj.company.id if obj.company else ''
    
    def get_project(self, obj):
        if obj.incomingInvoice:
            if obj.incomingInvoice.project:
                return obj.incomingInvoice.project.projectNo
            elif obj.incomingInvoice.purchasingProject:
                return obj.incomingInvoice.purchasingProject.projectNo
            else:
                ""
        elif obj.sendInvoice:
            if obj.sendInvoice.project:
                return obj.sendInvoice.project.projectNo
            elif obj.sendInvoice.offer:
                return obj.sendInvoice.offer.offerNo
            else:
                ""
        else:
            ""

    def get_currency(self, obj):
        return obj.currency.code if obj.currency else ''
    
    def get_exchangeRate(self, obj):
        return obj.currency.forexBuying if obj.currency else ''
    
    def get_type(self,obj):
        return obj.get_type_display()
    
class CurrentTotalListSerializer(serializers.Serializer):
    USD = serializers.JSONField()
    EUR = serializers.JSONField()
    GBP = serializers.JSONField()
    QAR = serializers.JSONField()
    RUB = serializers.JSONField()
    JPY = serializers.JSONField()
    TRY = serializers.JSONField()

class SendInvoiceTotalListSerializer(serializers.Serializer):
    USD = serializers.JSONField()
    EUR = serializers.JSONField()
    GBP = serializers.JSONField()
    QAR = serializers.JSONField()
    RUB = serializers.JSONField()
    JPY = serializers.JSONField()
    TRY = serializers.JSONField()

class IncomingInvoiceTotalListSerializer(serializers.Serializer):
    USD = serializers.JSONField()
    EUR = serializers.JSONField()
    GBP = serializers.JSONField()
    QAR = serializers.JSONField()
    RUB = serializers.JSONField()
    JPY = serializers.JSONField()
    TRY = serializers.JSONField()


