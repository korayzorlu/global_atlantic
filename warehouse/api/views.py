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

from warehouse.api.serializers import *

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

class WarehouseList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = WarehouseListSerializer
    filterset_fields = {
                        'user__id': ['exact','in', 'isnull'],
                        'id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["country","city"]
    
        queryset = Warehouse.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["country__international_formal_name", "city__name", "code", "name", "address", "phone1"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
        # if query is not None:
        #     queryset = queryset.filter(
        #         Q(customer__name__icontains=query)
        #     )

class PartItemGroupList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = ItemGroupListSerializer
    filterset_fields = {
                        'user__id': ['exact','in', 'isnull'],
                        'id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["part","part__maker","part__type","part__partUnique"]
    
        queryset = ItemGroup.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("part__maker__name","part__type__type","name","-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name", "category", "unit", "quantity","part__maker__name","part__type__type","part__partUniqueCode",
                             "part__partUnique__code"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
        # if query is not None:
        #     queryset = queryset.filter(
        #         Q(customer__name__icontains=query)
        #     )
   
class PartItemList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = ItemListSerializer
    filterset_fields = {
                        'user__id': ['exact','in', 'isnull'],
                        'id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["warehouse","part","part__maker","part__type","part__partUnique","incomingInvoiceItem__invoice"]
    
        queryset = Item.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("part__maker__name","part__type__type","name","-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["itemNo", "name", "category", "unit", "quantity","part__maker__name","part__type__type","part__partUniqueCode",
                             "part__partUnique__code","warehouse__name","incomingInvoiceItem__invoice__invoiceNo"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
        # if query is not None:
        #     queryset = queryset.filter(
        #         Q(customer__name__icontains=query)
        #     )

class DispatchList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = DispatchListSerializer
    filterset_fields = {
                        'user__id': ['exact','in', 'isnull'],
                        'id': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["project","theRequest"]
    
        queryset = Dispatch.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["dispatchNo", "project__projectNo", "theRequest__requestNo"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
        # if query is not None:
        #     queryset = queryset.filter(
        #         Q(customer__name__icontains=query)
        #     )