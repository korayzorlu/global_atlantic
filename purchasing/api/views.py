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

from purchasing.api.serializers import *
from card.models import Company

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

class ProjectList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = ProjectListSerializer
    filterset_fields = {
                        'user__id': ['exact','in', 'isnull'],
                        'sessionKey': ['exact','in', 'isnull'],
                        'id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["supplier"]
    
        queryset = Project.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["user__first_name", "user__last_name", "stage", "identificationCode", "yearCode", "code","projectNo",
                             "projectDate", "supplier__name","supplierRef"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
        # if query is not None:
        #     queryset = queryset.filter(
        #         Q(customer__name__icontains=query)
        #     )

class ProjectItemList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["project"]
    
    queryset = ProjectItem.objects.select_related(*custom_related_fields).filter()
    serializer_class = ProjectItemListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'project': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'part': ['exact', 'isnull'],
                        'serviceCard': ['exact', 'isnull'],
                        'expense': ['exact', 'isnull']
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

        custom_related_fields = ["project","project__user","supplier","currency"]
    
        queryset = Inquiry.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["project__projectNo","inquiryNo","inquiryDate","supplier_name","project__user__first_name","project__user__last_name",
                             "project__stage","supplierRef"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
class InquiryItemList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["inquiry__currency","projectItem"]
    
    queryset = InquiryItem.objects.select_related(*custom_related_fields).filter().order_by("sequency")
    serializer_class = InquiryItemListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'inquiry': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'projectItem': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    #pagination_class = PageNumberPagination

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
                        'inquiry__id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","project__user","inquiry__supplier","currency"]
    
        queryset = PurchaseOrder.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["project__projectNo","purchaseOrderNo","purchaseOrderDate","inquiry__supplierRef","inquiry__supplier__name",
                             "totalTotalPrice","currency__code","project__user__first_name","project__user__last_name","project__stage"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
class PurchaseOrderItemList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["purchaseOrder__currency","inquiryItem"]
    
    queryset = PurchaseOrderItem.objects.select_related(*custom_related_fields).filter().order_by("sequency")
    serializer_class = PurchaseOrderItemListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'purchaseOrder': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'inquiryItem': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    #pagination_class = PageNumberPagination