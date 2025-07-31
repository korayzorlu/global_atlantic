from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet, Q, Prefetch, OuterRef
from django.http import JsonResponse
from django_filters import filters
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter, BaseFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend as DatatablesFilterBackendDT
from rest_framework_datatables.django_filters.filterset import DatatablesFilterSet
from rest_framework_datatables.django_filters.filters import GlobalFilter
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend, FilterSet, ChoiceFilter, CharFilter

from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet, EditorModelMixin
#from rest_framework_datatables_editor.filters import DatatablesFilterBackend
from rest_framework.viewsets import ModelViewSet

from django.db.models import F, Value
from django.db.models.functions import Concat

from datetime import datetime
from django.utils import timezone

from sale.api.serializers import *
from sale.models import Project, Request, Inquiry, OrderConfirmation, Quotation, PurchaseOrder, OrderTracking
from card.models import Company, Vessel
from account.models import SendInvoice,IncomingInvoice,Payment

def setup_eager_loading(get_queryset):
    def decorator(self):
        queryset = get_queryset(self)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset

    return decorator



class QueryListAPIView(generics.ListAPIView):
    def get_queryset(self):
        #print(self.request.query_params.get('columns[6][data]', None))
        #print(dict(self.request.GET))
        
        if self.request.GET.get('format', None) == 'datatables':
            self.filter_backends = (OrderingFilter, DatatablesFilterBackend, DjangoFilterBackend)
            
            return super().get_queryset()
        self.filter_backends = (OrderingFilter, DatatablesFilterBackend, DjangoFilterBackend)
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


    
class ProjectList(ModelViewSet, QueryListAPIView):
    """
    Returns all projects
    Use GET parameters to filter queryset
    """
    
    serializer_class = ProjectListSerializer
    filterset_fields = {
                        'user': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = Project.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-id")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = []
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
 
class RequestList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = RequestListSerializer
    filterset_fields = {
                        'project__user': ['exact','in', 'isnull'],
                        'sessionKey': ['exact','in', 'isnull'],
                        'project__id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","customer","vessel","maker","makerType"]
    
        queryset = Request.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        
        # 'exact' filter for stage
        stage = self.request.query_params.get('project__stage')
        if stage:
            queryset = queryset.filter(project__stage=stage)
            
        # 'in' filter for stage
        stages = self.request.query_params.get('project__stage__in')
        if stages:
            stages_list = stages.split(',')
            queryset = queryset.filter(project__stage__in=stages_list)
        
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["project__user__first_name", "project__user__last_name", "project__stage", "identificationCode", "yearCode", "code","requestNo",
                             "requestDate", "customer__name","person__name", "vessel__name", "requestDate", "customerRef", "maker__name", "makerType__type"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
        # if query is not None:
        #     queryset = queryset.filter(
        #         Q(customer__name__icontains=query)
        #     )
        

class RequestPartList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["theRequest","part"]
    
    queryset = RequestPart.objects.select_related(*custom_related_fields).all().order_by("sequency")
    serializer_class = RequestPartListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'theRequest': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'part': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    

    
class InquiryList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = InquiryListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
                        'user': ['exact','in', 'isnull'],
                        'sessionKey': ['exact','in', 'isnull'],
                        'project__id': ['exact','in', 'isnull'],
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","project__user","theRequest__customer","theRequest__vessel","theRequest__maker","theRequest__makerType","supplier","currency"]
    
        queryset = Inquiry.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["project__projectNo","inquiryNo","inquiryDate","theRequest__customer__name","theRequest__vessel__name","supplier__name",
                             "theRequest__maker__name","theRequest__makerType__type","project__user__first_name","project__user__last_name","project__stage",
                             "supplierRef"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset

class InquiryPartList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["inquiry__currency","requestPart__part"]
    
    queryset = InquiryPart.objects.select_related(*custom_related_fields).all().order_by("sequency")
    serializer_class = InquiryPartListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'inquiry': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'requestPart': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    #pagination_class = PageNumberPagination





class QuotationList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = QuotationListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
                        'user': ['exact','in', 'isnull'],
                        'sessionKey': ['exact','in', 'isnull'],
                        'project__id': ['exact','in', 'isnull'],
    }
    #filterset_class = QuotationGlobalFilter
    #search_fields = ['quotationNo', 'inquiry__theRequest__customer__name', 'inquiry__theRequest__vessel__name', 'person__name', 'sessionKey']
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","project__user","inquiry__theRequest","inquiry__theRequest__customer","inquiry__theRequest__vessel","currency",
                                 "inquiry__theRequest__maker","inquiry__theRequest__makerType"]
    
        queryset = Quotation.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["project__projectNo","quotationNo","quotationDate","inquiry__theRequest__customer__name","inquiry__theRequest__vessel__name",
                             "inquiry__theRequest__customerRef","soc","totalBuyingPrice","totalSellingPrice","currency__code","project__user__first_name",
                             "project__user__last_name","approval","project__stage","inquiry__theRequest__maker__name","inquiry__theRequest__makerType__type"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    

    
    # def get_queryset(self):
    #     # `customer_name` anotasyonu ile queryset'i özelleştir
    #     return Inquiry.objects.annotate(
    #         customer_name=Concat('theRequest__customer__name', Value(''))
    #     )

    # def get_queryset(self):
    #     custom_related_fields = []
    #     queryset = Quotation.objects.select_related(*custom_related_fields).all()
    #     custom_field_value = self.request.query_params.get('customer')
    #     if custom_field_value:
    #         queryset = queryset.filter(inquiry__theRequest__customer__name = custom_field_value)
    #     return queryset
    
class QuotationCustomerList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = QuotationCustomerListSerializer
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
        
        quotationCustomers = []
        quotations = Quotation.objects.select_related("inquiry__theRequest__customer").filter(inquiry__theRequest__customer__in = queryset)
        for quotation in quotations:
            quotationCustomers.append(quotation.inquiry.theRequest.customer.id)
        queryset=queryset.filter(id__in = quotationCustomers)

                
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    

    
class QuotationPartList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    custom_related_fields = ["quotation","quotation__currency","inquiryPart__requestPart","inquiryPart__requestPart__part","inquiryPart__inquiry__supplier"]
    queryset = QuotationPart.objects.select_related(*custom_related_fields).all()
    serializer_class = QuotationPartListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'quotation': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'inquiryPart': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    #pagination_class = PageNumberPagination
   
    

class QuotationExtraList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    queryset = QuotationExtra.objects.all()
    serializer_class = QuotationExtraListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'quotation': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'name': ['exact', 'isnull']
    }
    ordering_fields = '__all__'

class OrderConfirmationList(QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = OrderConfirmationListSerializer
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
                        'user': ['exact','in', 'isnull'],
                        'sessionKey': ['exact','in', 'isnull'],
                        'quotation__id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","project__user","quotation","quotation__inquiry__theRequest","quotation__inquiry__theRequest__customer","quotation__inquiry__theRequest__vessel",
                                 "quotation__inquiry__theRequest__maker","quotation__inquiry__theRequest__makerType","quotation__currency"]
    
        queryset = OrderConfirmation.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["project__projectNo","orderConfirmationNo","orderConfirmationDate","quotation__inquiry__theRequest__customerRef",
                             "quotation__inquiry__theRequest__customer__name","quotation__inquiry__theRequest__vessel__name",
                             "quotation__inquiry__theRequest__maker__name","quotation__inquiry__theRequest__makerType__type","quotation__totalSellingPrice",
                             "quotation__currency__code","project__user__first_name","project__user__last_name","project__stage"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset

class OrderConfirmationCustomerList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = OrderConfirmationCustomerListSerializer
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

        queryset = Company.objects.select_related(*custom_related_fields).all().order_by("name")
        
        orderConfirmationCustomers = []
        orderConfirmations = OrderConfirmation.objects.select_related("quotation__inquiry__theRequest__customer").filter(
            sourceCompany = self.request.user.profile.sourceCompany,
            quotation__inquiry__theRequest__customer__in = queryset
        )
        for orderConfirmation in orderConfirmations:
            orderConfirmationCustomers.append(orderConfirmation.quotation.inquiry.theRequest.customer.id)
        queryset=queryset.filter(id__in = orderConfirmationCustomers)

                
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
  
 
class OrderNotConfirmationList(QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = OrderNotConfirmationListSerializer
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = OrderNotConfirmation.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = []
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
class PurchaseOrderList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = PurchaseOrderListSerializer
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
                        'user': ['exact','in', 'isnull'],
                        'sessionKey': ['exact','in', 'isnull'],
                        'orderConfirmation__id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","project__user","inquiry__supplier","inquiry__theRequest__customer","inquiry__theRequest__vessel",
                                 "inquiry__theRequest__maker","inquiry__theRequest__makerType","currency"]
    
        queryset = PurchaseOrder.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["project__projectNo","purchaseOrderNo","purchaseOrderDate","inquiry__supplierRef","inquiry__supplier__name",
                             "inquiry__theRequest__customer__name","inquiry__theRequest__vessel__name","inquiry__theRequest__maker__name",
                             "inquiry__theRequest__makerType__type","totalTotalPrice","currency__code","project__user__first_name",
                             "project__user__last_name","project__stage"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
class PurchaseOrderSupplierList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = PurchaseOrderSupplierListSerializer
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

        queryset = Company.objects.select_related(*custom_related_fields).all().order_by("name")
        
        purchaseOrderSuppliers = []
        purchaseOrders = PurchaseOrder.objects.select_related("inquiry__supplier").filter(
            sourceCompany = self.request.user.profile.sourceCompany,
            inquiry__supplier__in = queryset
        )
        for purchaseOrder in purchaseOrders:
            #print(type(purchaseOrder)._meta.model_name)
            purchaseOrderSuppliers.append(purchaseOrder.inquiry.supplier.id)
        queryset=queryset.filter(id__in = purchaseOrderSuppliers)

                
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset

class PurchaseOrderCustomerList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = PurchaseOrderCustomerListSerializer
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

        queryset = Company.objects.select_related(*custom_related_fields).all().order_by("name")
        
        purchaseOrderCustomers = []
        purchaseOrders = PurchaseOrder.objects.select_related("inquiry__theRequest__customer").filter(
            sourceCompany = self.request.user.profile.sourceCompany,
            inquiry__theRequest__customer__in = queryset
        )
        for purchaseOrder in purchaseOrders:
            #print(type(purchaseOrder)._meta.model_name)
            purchaseOrderCustomers.append(purchaseOrder.inquiry.theRequest.customer.id)
        queryset=queryset.filter(id__in = purchaseOrderCustomers)

                
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset

class PurchaseOrderVesselList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = PurchaseOrderVesselListSerializer
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

        queryset = Vessel.objects.select_related(*custom_related_fields).all().order_by("name")
        
        purchaseOrderVessels = []
        purchaseOrders = PurchaseOrder.objects.select_related("inquiry__theRequest__vessel").filter(
            sourceCompany = self.request.user.profile.sourceCompany,
            inquiry__theRequest__vessel__in = queryset
        )
        for purchaseOrder in purchaseOrders:
            #print(type(purchaseOrder)._meta.model_name)
            purchaseOrderVessels.append(purchaseOrder.inquiry.theRequest.vessel.id)
        queryset=queryset.filter(id__in = purchaseOrderVessels)

                
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset

  
class PurchaseOrderPartList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["purchaseOrder","purchaseOrder__currency","inquiryPart__requestPart__part"]
    queryset = PurchaseOrderPart.objects.select_related(*custom_related_fields).all()
    serializer_class = PurchaseOrderPartListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'purchaseOrder': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    
    # def get_options(self):
    #     return "options", {
    #         "purchaseOrder": [{'label': obj.purchaseOrderNo, 'value': obj.pk} for obj in PurchaseOrder.objects.all()]
    #     }
    
    # class Meta:
    #     datatables_extra_json = ('get_options', )



class OrderTrackingList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = OrderTrackingListSerializer
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
                        'user': ['exact','in', 'isnull'],
                        'sessionKey': ['exact','in', 'isnull'],
                        'project__id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","project__user","theRequest__customer","theRequest__vessel","theRequest"]
        
        po_custom_related_fields = ["inquiry__theRequest__customer","inquiry__theRequest__vessel","inquiry__theRequest__maker","inquiry__theRequest__makerType",
                                    "orderConfirmation","currency"]
        purchaseOrderPrefetch = Prefetch('purchaseOrders', queryset=PurchaseOrder.objects.select_related(*po_custom_related_fields))
        
        queryset = OrderTracking.objects.select_related(*custom_related_fields).prefetch_related(purchaseOrderPrefetch).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["project__projectNo","theRequest__customer__name","theRequest__vessel__name","theRequest__customerRef",
                             "project__user__first_name","project__user__last_name","items","project__stage"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
class DispatchOrderList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = DispatchOrderListSerializer
    filterset_fields = {
                        'user__id': ['exact','in', 'isnull'],
                        'id': ['exact','in', 'isnull'],
                        'orderTracking__id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["orderTracking"]
    
        queryset = DispatchOrder.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["dispatchOrderNo"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
        # if query is not None:
        #     queryset = queryset.filter(
        #         Q(customer__name__icontains=query)
        #     )

class DispatchOrderPartList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["dispatchOrder","collectionPart__purchaseOrderPart__inquiryPart__requestPart__part"]
    queryset = DispatchOrderPart.objects.select_related(*custom_related_fields).all()
    serializer_class = DispatchOrderPartListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'dispatchOrder': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull']
    }
    ordering_fields = '__all__'