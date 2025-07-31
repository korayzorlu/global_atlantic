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

from note.api.serializers import *

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

from note.models import Note

class NoteList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    custom_related_fields = ["user"]
    queryset = Note.objects.select_related(*custom_related_fields).all()
    serializer_class = NoteListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'user': ['exact', 'isnull']
    }
    ordering_fields = '__all__'