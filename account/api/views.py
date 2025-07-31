from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet, Q, Prefetch, JSONField
from django.http import JsonResponse
from django.views.generic.list import MultipleObjectMixin
import django_filters
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend
#from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend as DFDatatablesFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound

from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet, EditorModelMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
# from django_filters import FilterSet, ChoiceFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, ChoiceFilter, CharFilter, MultipleChoiceFilter
from drf_multiple_model.views import ObjectMultipleModelAPIView, FlatMultipleModelAPIView
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination

from itertools import chain
from django.utils.translation import gettext_lazy as _
from collections import OrderedDict


from account.api.serializers import *
from account.models import Process, CommericalInvoice
from sale.models import PurchaseOrderPart, QuotationPart, OrderTracking, PurchaseOrder
from sale.api.serializers import OrderTrackingListSerializer
from service.models import Offer,OfferServiceCard, OfferExpense, OfferPart
from service.api.serializers import OfferListSerializer,EnginePartListSerializer
from card.api.serializers import VesselListSerializer, PersonListSerializer
from purchasing.models import PurchaseOrder as PurchasingPurchaseOrder
from purchasing.api.serializers import PurchaseOrderListSerializer as PurchasingPurchaseOrderListSerializer

class QueryListAPIView(generics.ListAPIView):
    def get_queryset(self):
        if self.request.GET.get('format', None) == 'datatables':
            self.filter_backends = (OrderingFilter, DatatablesFilterBackend, DjangoFilterBackend, SearchFilter)
            return super().get_queryset()
        queryset = self.queryset
        # check the start index is integer
        try:
            start = self.request.GET.get('start')
            start = int(start) if start else None
        # else make it None
        except ValueError:
            start = None

        # check the end index is integer
        try:
            end = self.request.GET.get('end')
            end = int(end) if end else None
        # else make it None
        except ValueError:
            end = None

        # skip filters and sorting if they are not exists in the model to ensure security
        accepted_filters = {}
        # loop fields of the model
        for field in queryset.model._meta.get_fields():
            # if field exists in request, accept it
            if field.name in dict(self.request.GET):
                accepted_filters[field.name] = dict(self.request.GET)[field.name]
            # if field exists in sorting parameter's value, accept it

        filters = {}

        for key, value in accepted_filters.items():
            if any(val in value for val in EMPTY_VALUES):
                if queryset.model._meta.get_field(key).null:
                    filters[key + '__isnull'] = True
                else:
                    filters[key + '__exact'] = ''
            else:
                filters[key + '__in'] = value
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all().filter(**filters)[start:end]
        return queryset

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            elif self.request.GET.get('format', None) == 'datatables':
                self._paginator = self.pagination_class()
            else:
                self._paginator = None
        return self._paginator
    
class IncomingInvoiceList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = IncomingInvoiceListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
                        'seller': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","seller","customerSource","currency"]

        type = self.kwargs.get('type', None)

        if type == "soa":
            queryset = IncomingInvoice.objects.select_related(*custom_related_fields).filter(
                sourceCompany = self.request.user.profile.sourceCompany
            ).order_by("seller__name")
        else:
            queryset = IncomingInvoice.objects.select_related(*custom_related_fields).filter(
                sourceCompany = self.request.user.profile.sourceCompany
            ).order_by("-incomingInvoiceDate")

        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["project__projectNo","seller__name","customerSource__name","incomingInvoiceDate","incomingInvoiceNo","paymentDate","netPrice",
                             "discountPrice","vatPrice","totalPrice","exchangeRate","currency__code"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
    @action(detail=False, methods=['get'], url_path='type_(?P<type>[^/.]+)')
    def filter_by_type(self, request, type=None):
        """
        Custom action to filter by type.
        """

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class IncomingInvoicePartList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["invoice","invoice__currency"]
    
    queryset = IncomingInvoiceItem.objects.select_related(*custom_related_fields).all()
    serializer_class = IncomingInvoiceItemListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'invoice': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'purchaseOrderPart': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    
    # def get_options(self):
    #     return "options", {
    #         "invoice": [{'label': obj.incomingInvoiceNo, 'value': obj.pk} for obj in IncomingInvoice.objects.all()],
    #         "purchaseOrderPart": [{'label': obj.inquiryPart.requestPart.part.partNo, 'value': obj.pk} for obj in PurchaseOrderPart.objects.all()]
    #     }
    
    # class Meta:
    #     datatables_extra_json = ('get_options', )

class IncomingInvoiceExpenseList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = []
    
    queryset = IncomingInvoiceExpense.objects.select_related(*custom_related_fields).all()
    serializer_class = IncomingInvoiceExpenseListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'invoice': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'name': ['exact', 'isnull']
    }
    ordering_fields = '__all__'

class IncomingInvoiceSupplierList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = IncomingInvoiceSupplierListSerializer
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []

        queryset = Company.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        
        incomingInvoiceSellers = []
        incomingInvoices = IncomingInvoice.objects.select_related("seller").filter(seller__in = queryset)
        for incomingInvoice in incomingInvoices:
            incomingInvoiceSellers.append(incomingInvoice.seller.id)
        queryset=queryset.filter(id__in = incomingInvoiceSellers)
                
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset

class SendInvoiceList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = SendInvoiceListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
                        'customer': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'

    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","customer","vessel","billing","offer","currency"]

        type = self.kwargs.get('type', None)

        if type == "soa":
            queryset = SendInvoice.objects.select_related(*custom_related_fields).filter(
                sourceCompany = self.request.user.profile.sourceCompany
            ).order_by("customer__name")
        else:
            queryset = SendInvoice.objects.select_related(*custom_related_fields).filter(
                sourceCompany = self.request.user.profile.sourceCompany
            ).order_by("-sendInvoiceDate")

        #queryset = SendInvoice.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-sendInvoiceDate")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["project__projectNo","offer__offerNo","group","customer__name","vessel__name","vessel__imo","billing__name",
                             "sendInvoiceDate","sendInvoiceNo","paymentDate","netPrice","discountPrice","vatPrice","totalPrice","currency__code",
                             "payed","ready"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
    @action(detail=False, methods=['get'], url_path='type_(?P<type>[^/.]+)')
    def filter_by_type(self, request, type=None):
        """
        Custom action to filter by type.
        """

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class SendInvoiceCustomerList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = SendInvoiceCustomerListSerializer
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []

        queryset = Company.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        
        sendInvoiceCustomers = []
        sendInvoices = SendInvoice.objects.select_related("customer").filter(customer__in = queryset)
        for sendInvoice in sendInvoices:
            sendInvoiceCustomers.append(sendInvoice.customer.id)
        queryset=queryset.filter(id__in = sendInvoiceCustomers)
                
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
class SendInvoiceItemList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["invoice","invoice__currency"]
    
    queryset = SendInvoiceItem.objects.select_related(*custom_related_fields).all()
    serializer_class = SendInvoiceItemListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'invoice': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'part': ['exact', 'isnull'],
                        'serviceCard': ['exact', 'isnull']
    }
    ordering_fields = '__all__'

class SendInvoiceExpenseList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["invoice","expense","invoice__currency"]
    
    queryset = SendInvoiceExpense.objects.select_related(*custom_related_fields).all()
    serializer_class = SendInvoiceExpenseListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'invoice': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'expense': ['exact', 'isnull']
    }
    ordering_fields = '__all__'

class SendInvoicePartList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = []
    
    queryset = SendInvoicePart.objects.select_related(*custom_related_fields).all()
    serializer_class = SendInvoicePartListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'invoice': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'quotationPart': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    
    # def get_options(self):
    #     return "options", {
    #         "invoice": [{'label': obj.sendInvoiceNo, 'value': obj.pk} for obj in SendInvoice.objects.all()],
    #         "quotationPart": [{'label': obj.inquiryPart.requestPart.part.partNo, 'value': obj.pk} for obj in QuotationPart.objects.all()]
    #     }
    
    # class Meta:
    #     datatables_extra_json = ('get_options', )
        
    
class PaymentList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = PaymentListSerializer
    filterset_fields = {
                        'sessionKey': ['exact','in', 'isnull'],
                        'customer__id': ['exact','in', 'isnull'],
                        'currency__code': ['exact','in', 'isnull'],
                        'paymentDate': ['exact','in', 'isnull'],
                        'user__id': ['exact','in', 'isnull'],
                        'id': ['exact','in', 'isnull'],
                        #'type': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["customer","currency"]
    
        queryset = Payment.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["customer__name","currency__code","paymentDate","type","paymentNo","amount","currency__forexBuying","description"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        
        # 'type' alanı için manuel filtre uygulaması
        type_param = self.request.query_params.get('type', None)
        if type_param:
            queryset = queryset.filter(type=type_param)

        type_in_param = self.request.query_params.get('type__in', None)
        if type_in_param:
            type_list = type_in_param.split(',')
            queryset = queryset.filter(type__in=type_list)
        
        type_isnull_param = self.request.query_params.get('type__isnull', None)
        if type_isnull_param:
            isnull_value = type_isnull_param.lower() in ['true', '1']
            queryset = queryset.filter(type__isnull=isnull_value)
        
        return queryset



class PaymentInvoiceList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """

    custom_related_fields = ["payment", "payment__currency","sendInvoice","incomingInvoice"]
    queryset = PaymentInvoice.objects.select_related(*custom_related_fields).all().order_by("invoicePaymentDate")
    serializer_class = PaymentInvoiceListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
                        'payment': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'

    
  

    



class InvoiceForPaymentList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = InvoiceForPaymentListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["currency"]

        type = self.kwargs.get('type', None)
        company = self.kwargs.get('company', None)
        
        if type == "in":
            queryset = SendInvoice.objects.select_related(*custom_related_fields).filter(
                sourceCompany = self.request.user.profile.sourceCompany,
                customer__id = int(company)
            ).order_by("paymentDate")
        elif type == "out":
            queryset = IncomingInvoice.objects.select_related(*custom_related_fields).filter(
                sourceCompany = self.request.user.profile.sourceCompany,
                seller__id = int(company)
            ).order_by("paymentDate")
        else:
            queryset = []

        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = []
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
    @action(detail=False, methods=['get'], url_path='type_(?P<type>[^/.]+)_company_(?P<company>[^/.]+)')
    def filter_by_type(self, request, type=None, company=None):
        """
        Custom action to filter by type.
        """

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
 

class ProcessStatusList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = ProcessStatusListSerializer
    filterset_fields = {
                        'user': ['exact','in', 'isnull'],
                        'processStatusDate': ['exact','in', 'isnull'],
                        #'type': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","offer","purchasingProject","purchasingProject__sourceCompany"]
        custom_prefetch_related_fields = ["project__order_tracking","purchasingProject__purchasing_purchase_order","offer__customer"]
    
        queryset = ProcessStatus.objects.select_related(*custom_related_fields).prefetch_related(*custom_prefetch_related_fields).filter(
            sourceCompany = self.request.user.profile.sourceCompany
        ).order_by("-created_date",)
        #order_by("-purchasingProject__projectDate","-offer__offerDate","-project__order_tracking__theRequest__requestDate",)
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["project__projectNo","offer__offerNo","purchasingProject__projectNo","project__order_tracking__theRequest__customer__name",
                             "offer__customer__name","purchasingProject__sourceCompany__name","project__order_tracking__theRequest__vessel__name",
                             "project__order_tracking__purchaseOrders__purchaseOrderNo","purchasingProject__purchasing_purchase_order__purchaseOrderNo"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        
        # 'type' alanı için manuel filtre uygulaması
        type_param = self.request.query_params.get('type', None)
        if type_param:
            queryset = queryset.filter(type=type_param)

        type_in_param = self.request.query_params.get('type__in', None)
        if type_in_param:
            type_list = type_in_param.split(',')
            queryset = queryset.filter(type__in=type_list)
        
        type_isnull_param = self.request.query_params.get('type__isnull', None)
        if type_isnull_param:
            isnull_value = type_isnull_param.lower() in ['true', '1']
            queryset = queryset.filter(type__isnull=isnull_value)
        
        return queryset

class OrderInProcessList(FlatMultipleModelAPIView,QueryListAPIView):
    permission_classes = ()
    pagination_class = None
    
    serializer_class = OrderTrackingListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_querylist(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        order_tracking_custom_related_fields = ["project","project__user","theRequest__customer","theRequest__vessel","theRequest__maker","theRequest__makerType","theRequest"]
        
        po_custom_related_fields = ["inquiry__theRequest__customer","inquiry__theRequest__vessel","inquiry__theRequest__maker","inquiry__theRequest__makerType",
                                    "orderConfirmation","currency"]
        purchaseOrderPrefetch = Prefetch('purchaseOrders', queryset=PurchaseOrder.objects.select_related(*po_custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany))

        offer_custom_related_fields = []
        
        purchasing_purchase_order_custom_related_fields = []
        
        querylist = [
            {'queryset':OrderTracking.objects.select_related(*order_tracking_custom_related_fields).prefetch_related(purchaseOrderPrefetch).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk"),'serializer_class':OrderTrackingListSerializer},
            {'queryset':Offer.objects.select_related(*offer_custom_related_fields).exclude(status = "offer").filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk"),'serializer_class':OfferListSerializer},
            {'queryset':PurchasingPurchaseOrder.objects.select_related(*purchasing_purchase_order_custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk"),'serializer_class':PurchasingPurchaseOrderListSerializer}
        ]
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields_order_tracking = ["theRequest__customer__name","theRequest__vessel__name","purchaseOrders__orderConfirmation__orderConfirmationNo",
                                            "theRequest__requestNo"]
            search_fields_offer = ["customer__name","offerNo"]
            
            search_fields_purchasing_purchase_order = ["inquiry__supplier__name","purchaseOrderNo"]
            
            q_objects_order_tracking = Q()
            for field in search_fields_order_tracking:
                q_objects_order_tracking |= Q(**{f"{field}__icontains": query})
            
            q_objects_offer = Q()
            for field in search_fields_offer:
                q_objects_offer |= Q(**{f"{field}__icontains": query})
                
            q_objects_purchasing_purchase_order = Q()
            for field in search_fields_purchasing_purchase_order:
                q_objects_purchasing_purchase_order |= Q(**{f"{field}__icontains": query})
            
            # OrderTracking queryset'i filtrele
            querylist[0]['queryset'] = querylist[0]['queryset'].filter(q_objects_order_tracking)
            
            # Offer queryset'i filtrele
            querylist[1]['queryset'] = querylist[1]['queryset'].filter(q_objects_offer)
            
            # Offer queryset'i filtrele
            querylist[1]['queryset'] = querylist[1]['queryset'].filter(q_objects_purchasing_purchase_order)
            
        return querylist


class SendInvoiceMultipleList(FlatMultipleModelAPIView,QueryListAPIView):
    permission_classes = ()
    pagination_class = None
    
    querylist = [
        {'queryset':SendInvoice.objects.filter().order_by("-code"),'serializer_class':SendInvoiceListSerializer,'filter_backends':[OrderingFilter, SearchFilter],'ordering_fields':'__all__'}
    ]
    serializer_class = SendInvoiceListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend, SearchFilter]
    filterset_fields = {
                        'code': ['exact','in', 'isnull']
    }
    ordering_fields = ["id", "code"]
    search_fields = ["customer__name"]
    
    # def get_queryset(self):
    #     queryset = super().get_queryset()

    #     # Arama filtresini uygula
    #     queryset = self.filter_queryset(queryset)

    #     return queryset
    
class ProformaInvoiceList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """

    serializer_class = ProformaInvoiceListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","customer","vessel","billing","offer","currency"]
    
        queryset = ProformaInvoice.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["project__projectNo","offer__offerNo","group","customer__name","vessel__name","billing__name","proformaInvoiceDate","proformaInvoiceNo","paymentDate",
                             "netPrice","discountPrice","vatPrice","totalPrice","currency__code","payed","ready"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset

class ProformaInvoiceItemList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["invoice","invoice__currency"]
    
    queryset = ProformaInvoiceItem.objects.select_related(*custom_related_fields).all()
    serializer_class = ProformaInvoiceItemListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'invoice': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'part': ['exact', 'isnull'],
                        'serviceCard': ['exact', 'isnull'],
                        'expense': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    
    
    
    # def get_options(self):
    #     return "options", {
    #         "invoice": [{'label': obj.sendInvoiceNo, 'value': obj.pk} for obj in SendInvoice.objects.all()],
    #         "quotationPart": [{'label': obj.inquiryPart.requestPart.part.partNo, 'value': obj.pk} for obj in QuotationPart.objects.all()]
    #     }
    
    # class Meta:
    #     datatables_extra_json = ('get_options', )


class ProformaInvoiceMultipleList(FlatMultipleModelAPIView,QueryListAPIView):
    permission_classes = ()
    pagination_class = None
    
    custom_related_fields = []
    
    querylist = [
        {'queryset':ProformaInvoice.objects.select_related(*custom_related_fields).all().order_by("-code"),'serializer_class':ProformaInvoiceListSerializer,'ordering_fields':'__all__'}
    ]
    serializer_class = ProformaInvoiceListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ordering_fields = ["id", "code"]
    
class ProformaInvoicePartList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = []

    queryset = ProformaInvoicePart.objects.select_related(*custom_related_fields).all()
    serializer_class = ProformaInvoicePartListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'invoice': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'quotationPart': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    pagination_class = PageNumberPagination
    
    # def get_options(self):
    #     return "options", {
    #         "invoice": [{'label': obj.proformaInvoiceNo, 'value': obj.pk} for obj in ProformaInvoice.objects.all()],
    #         "quotationPart": [{'label': obj.inquiryPart.requestPart.part.partNo, 'value': obj.pk} for obj in QuotationPart.objects.all()]
    #     }
    
    # class Meta:
    #     datatables_extra_json = ('get_options', )
        
class ProformaInvoiceExpenseList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = []

    queryset = ProformaInvoiceExpense.objects.select_related(*custom_related_fields).all()
    serializer_class = ProformaInvoiceExpenseListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'invoice': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'name': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    
class CommericalInvoiceList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = CommericalInvoiceListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","seller","customer","vessel","billing","currency"]
    
        queryset = CommericalInvoice.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["customer__name","seller__name","vessel__name","commericalInvoiceDate","commericalInvoiceNo","paymentDate","transport",
                             "netPrice","discountPrice","vatPrice","totalPrice","currency__code"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset

class CommericalInvoiceItemList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["invoice","invoice__currency"]
    
    queryset = CommericalInvoiceItem.objects.select_related(*custom_related_fields).all().order_by("quotationPart__sequency")
    serializer_class = CommericalInvoiceItemListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'invoice': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'part': ['exact', 'isnull'],
                        'expense': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    
    # def get_options(self):
    #     return "options", {
    #         "invoice": [{'label': obj.sendInvoiceNo, 'value': obj.pk} for obj in CommericalInvoice.objects.all()],
    #         "quotationPart": [{'label': obj.inquiryPart.requestPart.part.partNo, 'value': obj.pk} for obj in QuotationPart.objects.all()]
    #     }
    
    # class Meta:
    #     datatables_extra_json = ('get_options', )

class CommericalInvoiceExpenseList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = []
    
    queryset = CommericalInvoiceExpense.objects.select_related(*custom_related_fields).all()
    serializer_class = CommericalInvoiceExpenseListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'invoice': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'name': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
  
    
#####SOA#####

        
        
class SOAMultipleList(FlatMultipleModelAPIView,QueryListAPIView):
    permission_classes = ()
    pagination_class = None
    
    querylist = [
        {'queryset':IncomingInvoice.objects.filter().order_by("-created_date"),'serializer_class':SOAIncomingInvoiceListSerializer,'filter_backends':[OrderingFilter, SearchFilter],'ordering_fields':'__all__'},
        {'queryset':SendInvoice.objects.filter().order_by("-created_date"),'serializer_class':SOASendInvoiceListSerializer,'filter_backends':[OrderingFilter, SearchFilter],'ordering_fields':'__all__'},
        {'queryset':Payment.objects.filter().order_by("-created_date"),'serializer_class':SOAPaymentListSerializer,'filter_backends':[OrderingFilter, SearchFilter],'ordering_fields':'__all__'},
        
    ]
    serializer_class = SOAIncomingInvoiceListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
                        'created_date': ['exact','in', 'isnull'],
                        'customer': ['exact','in', 'isnull']
    }
    ordering_fields = ["id", "created_date"]
    sorting_field = "-datetime"


# class ProcessFilter(FilterSet):
    
#     type = ChoiceFilter(choices=Process.PROCESS_TYPES, null_label="Any")
#     class Meta:
#         model = Process
#         fields = {
#             'created_date': ['exact', 'in', 'isnull']
#         }

class ProcessFilter(django_filters.FilterSet):
    class Meta:
        model = Process
        fields = ['created_date', 'type', 'company__role']
        filter_overrides = {
            JSONField: {
                'filter_class': CharFilter,
            },
        }

class ProcessList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = ProcessListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    #filterset_class = ProcessFilter
    filterset_fields = {
            'created_date': ['exact', 'in', 'isnull'],
            'type': ['startswith', 'in', 'isnull'],
            #'company__role': ['startswith','in', 'isnull']
    }

    ordering_fields = '__all__'
    #@action(detail=False, methods=['get'], url_path='type_(?P<type>[^/.]+)')
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        
        custom_related_fields = ["company","sendInvoice","incomingInvoice","sendInvoice__project","incomingInvoice__project","currency"]

        type = self.kwargs.get('type', None)

        if type == "customer":
            queryset = Process.objects.select_related(*custom_related_fields).filter(
                Q(sourceCompany = self.request.user.profile.sourceCompany) &
                (Q(type = "send_invoice") | Q(type = "payment_in"))
            ).order_by("-processDateTime")
        elif type == "supplier":
            queryset = Process.objects.select_related(*custom_related_fields).filter(
                Q(sourceCompany = self.request.user.profile.sourceCompany) &
                (Q(type = "incoming_invoice") | Q(type = "payment_out"))
            ).order_by("-processDateTime")
        else:
            queryset = Process.objects.select_related(*custom_related_fields).filter(
                sourceCompany = self.request.user.profile.sourceCompany
            ).order_by("-processDateTime")

        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["company__name","type","amount","currency__code","sendInvoice__project__projectNo","incomingInvoice__project__proejctNo",
                             "payment__paymentNo"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
    @action(detail=False, methods=['get'], url_path='type_(?P<type>[^/.]+)')
    def filter_by_type(self, request, type=None):
        """
        Custom action to filter by type.
        """
        # custom_related_fields = ["company","currency"]
        # if type == "customer":
        #     queryset = self.get_queryset().select_related(*custom_related_fields).filter(Q(type = "send_invoice") | Q(type = "payment_in")).order_by("-processDateTime")
        # elif type == "supplier":
        #     queryset = self.get_queryset().select_related(*custom_related_fields).filter(Q(type = "incoming_invoice") | Q(type = "payment_out")).order_by("-processDateTime")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class CurrentTotalList(generics.ListAPIView):
    serializer_class = CurrentTotalListSerializer
    queryset = []

    def list(self, request, *args, **kwargs):
        currentObjects = Current.objects.select_related("currency").filter(sourceCompany = request.user.profile.sourceCompany)

        totals = {
            "USD": {"debt": 0, "credit": 0},
            "EUR": {"debt": 0, "credit": 0},
            "GBP": {"debt": 0, "credit": 0},
            "QAR": {"debt": 0, "credit": 0},
            "RUB": {"debt": 0, "credit": 0},
            "JPY": {"debt": 0, "credit": 0},
            "TRY": {"debt": 0, "credit": 0}
        }
        
        for current in currentObjects:
            currency_code = current.currency.code
            if currency_code in totals:
                totals[currency_code]["debt"] += current.debt
                totals[currency_code]["credit"] += current.credit

        external_data = [{
            "USD" : {"debt" : totals["USD"]["debt"], "credit" : totals["USD"]["credit"], "balance" : (totals["USD"]["debt"] - totals["USD"]["credit"])},
            "EUR" : {"debt" : totals["EUR"]["debt"], "credit" : totals["EUR"]["credit"], "balance" : (totals["EUR"]["debt"] - totals["EUR"]["credit"])},
            "GBP" : {"debt" : totals["GBP"]["debt"], "credit" : totals["GBP"]["credit"], "balance" : (totals["GBP"]["debt"] - totals["GBP"]["credit"])},
            "QAR" : {"debt" : totals["QAR"]["debt"], "credit" : totals["QAR"]["credit"], "balance" : (totals["QAR"]["debt"] - totals["QAR"]["credit"])},
            "RUB" : {"debt" : totals["RUB"]["debt"], "credit" : totals["RUB"]["credit"], "balance" : (totals["RUB"]["debt"] - totals["RUB"]["credit"])},
            "JPY" : {"debt" : totals["JPY"]["debt"], "credit" : totals["JPY"]["credit"], "balance" : (totals["JPY"]["debt"] - totals["JPY"]["credit"])},
            "TRY" : {"debt" : totals["TRY"]["debt"], "credit" : totals["TRY"]["credit"], "balance" : (totals["TRY"]["debt"] - totals["TRY"]["credit"])}
        }]

        data_format = request.query_params.get('format', None)
        
        if data_format == 'datatables':
            filter_backends = (DatatablesFilterBackend)
            data = {
                "draw": int(self.request.GET.get('draw', 1)),  # Müşteri tarafından gönderilen çizim sayısı
                "recordsTotal": len(external_data),  # Toplam kayıt sayısı
                "recordsFiltered": len(external_data),  # Filtre sonrası kayıt sayısı
                "data": external_data  # Gösterilecek veri
            }
            
            return Response(data)
        
        serializer = self.get_serializer(external_data, many=True)
        return Response(serializer.data)
    
class SendInvoiceTotalList(generics.ListAPIView):
    serializer_class = SendInvoiceTotalListSerializer
    queryset = []

    def list(self, request, *args, **kwargs):
        currentObjects = SendInvoice.objects.select_related("currency").filter(sourceCompany = request.user.profile.sourceCompany)

        totals = {
            "USD": {"total": 0, "paid": 0},
            "EUR": {"total": 0, "paid": 0},
            "GBP": {"total": 0, "paid": 0},
            "QAR": {"total": 0, "paid": 0},
            "RUB": {"total": 0, "paid": 0},
            "JPY": {"total": 0, "paid": 0},
            "TRY": {"total": 0, "paid": 0}
        }
        
        for current in currentObjects:
            currency_code = current.currency.code
            if currency_code in totals:
                totals[currency_code]["total"] += current.totalPrice
                totals[currency_code]["paid"] += current.paidPrice

        external_data = [{
            "USD" : {"total" : totals["USD"]["total"], "paid" : totals["USD"]["paid"], "balance" : (totals["USD"]["total"] - totals["USD"]["paid"])},
            "EUR" : {"total" : totals["EUR"]["total"], "paid" : totals["EUR"]["paid"], "balance" : (totals["EUR"]["total"] - totals["EUR"]["paid"])},
            "GBP" : {"total" : totals["GBP"]["total"], "paid" : totals["GBP"]["paid"], "balance" : (totals["GBP"]["total"] - totals["GBP"]["paid"])},
            "QAR" : {"total" : totals["QAR"]["total"], "paid" : totals["QAR"]["paid"], "balance" : (totals["QAR"]["total"] - totals["QAR"]["paid"])},
            "RUB" : {"total" : totals["RUB"]["total"], "paid" : totals["RUB"]["paid"], "balance" : (totals["RUB"]["total"] - totals["RUB"]["paid"])},
            "JPY" : {"total" : totals["JPY"]["total"], "paid" : totals["JPY"]["paid"], "balance" : (totals["JPY"]["total"] - totals["JPY"]["paid"])},
            "TRY" : {"total" : totals["TRY"]["total"], "paid" : totals["TRY"]["paid"], "balance" : (totals["TRY"]["total"] - totals["TRY"]["paid"])}
        }]

        data_format = request.query_params.get('format', None)
        
        if data_format == 'datatables':
            filter_backends = (DatatablesFilterBackend)
            data = {
                "draw": int(self.request.GET.get('draw', 1)),  # Müşteri tarafından gönderilen çizim sayısı
                "recordsTotal": len(external_data),  # Toplam kayıt sayısı
                "recordsFiltered": len(external_data),  # Filtre sonrası kayıt sayısı
                "data": external_data  # Gösterilecek veri
            }
            
            return Response(data)
        
        serializer = self.get_serializer(external_data, many=True)
        return Response(serializer.data)
    
class IncomingInvoiceTotalList(generics.ListAPIView):
    serializer_class = IncomingInvoiceTotalListSerializer
    queryset = []

    def list(self, request, *args, **kwargs):
        currentObjects = IncomingInvoice.objects.select_related("currency").filter(sourceCompany = request.user.profile.sourceCompany)

        totals = {
            "USD": {"total": 0, "paid": 0},
            "EUR": {"total": 0, "paid": 0},
            "GBP": {"total": 0, "paid": 0},
            "QAR": {"total": 0, "paid": 0},
            "RUB": {"total": 0, "paid": 0},
            "JPY": {"total": 0, "paid": 0},
            "TRY": {"total": 0, "paid": 0}
        }
        
        for current in currentObjects:
            currency_code = current.currency.code
            if currency_code in totals:
                totals[currency_code]["total"] += current.totalPrice
                totals[currency_code]["paid"] += current.paidPrice

        external_data = [{
            "USD" : {"total" : totals["USD"]["total"], "paid" : totals["USD"]["paid"], "balance" : (totals["USD"]["total"] - totals["USD"]["paid"])},
            "EUR" : {"total" : totals["EUR"]["total"], "paid" : totals["EUR"]["paid"], "balance" : (totals["EUR"]["total"] - totals["EUR"]["paid"])},
            "GBP" : {"total" : totals["GBP"]["total"], "paid" : totals["GBP"]["paid"], "balance" : (totals["GBP"]["total"] - totals["GBP"]["paid"])},
            "QAR" : {"total" : totals["QAR"]["total"], "paid" : totals["QAR"]["paid"], "balance" : (totals["QAR"]["total"] - totals["QAR"]["paid"])},
            "RUB" : {"total" : totals["RUB"]["total"], "paid" : totals["RUB"]["paid"], "balance" : (totals["RUB"]["total"] - totals["RUB"]["paid"])},
            "JPY" : {"total" : totals["JPY"]["total"], "paid" : totals["JPY"]["paid"], "balance" : (totals["JPY"]["total"] - totals["JPY"]["paid"])},
            "TRY" : {"total" : totals["TRY"]["total"], "paid" : totals["TRY"]["paid"], "balance" : (totals["TRY"]["total"] - totals["TRY"]["paid"])}
        }]

        data_format = request.query_params.get('format', None)
        
        if data_format == 'datatables':
            filter_backends = (DatatablesFilterBackend)
            data = {
                "draw": int(self.request.GET.get('draw', 1)),  # Müşteri tarafından gönderilen çizim sayısı
                "recordsTotal": len(external_data),  # Toplam kayıt sayısı
                "recordsFiltered": len(external_data),  # Filtre sonrası kayıt sayısı
                "data": external_data  # Gösterilecek veri
            }
            
            return Response(data)
        
        serializer = self.get_serializer(external_data, many=True)
        return Response(serializer.data)
    
