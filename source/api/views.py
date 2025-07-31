from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet, EditorModelMixin
from rest_framework.viewsets import ModelViewSet

import django_filters
from django.db.models import Q
from django_filters import CharFilter

from source.api.serializers import *
from source.models import Company

class QueryListAPIView(generics.ListAPIView):
    def get_queryset(self):
        if self.request.GET.get('format', None) == 'datatables':
            self.filter_backends = (OrderingFilter, DatatablesFilterBackend, DjangoFilterBackend)
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

class PersonFilter(django_filters.FilterSet):
    company = CharFilter(field_name='company', lookup_expr='exact',method='include_null')

    def include_null(self, queryset, name, value):
        return queryset.filter(Q(**{f'{name}__isnull': True}) | Q(**{name: value}))


class CompanyList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all companies
    Use GET parameters to filter queryset
    """
    custom_related_fields = []
    
    queryset = Company.objects.select_related(*custom_related_fields).all()
    serializer_class = CompanyListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'name': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'


    
class BankList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    serializer_class = BankListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'bankName': ['exact', 'isnull']
    }
    search_fields = []
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["currency"]
    
        queryset = Bank.objects.select_related(*custom_related_fields).filter(company = self.request.user.profile.sourceCompany).order_by("bankName")
        query = self.request.query_params.get('search[value]', None)
        
        if query:
            search_fields = ["bankName","currency__code"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            print(q_objects)
            queryset = queryset.filter(q_objects)
        return queryset