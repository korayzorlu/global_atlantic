from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend

from django_filters.rest_framework import DjangoFilterBackend
from drf_multiple_model.views import ObjectMultipleModelAPIView, FlatMultipleModelAPIView

from library.api.serializers import *

from sale.api.serializers import *
from sale.models import Project, Request, Inquiry



#from sale.models import Project, Request, Inquiry, OrderConfirmation, Quotation, PurchaseOrder, OrderTracking

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
    
    
class SaleDocumentsList(FlatMultipleModelAPIView, QueryListAPIView):
    querylist = [
        {'queryset':Request.objects.all(),'serializer_class':RequestListSerializer,'filter_backends':[OrderingFilter,DjangoFilterBackend],'filterset_fields':{'project': ['exact','in', 'isnull']},'ordering_fields':'__all__'},
        {'queryset':Inquiry.objects.all(),'serializer_class':InquiryListSerializer,'filter_backends':[OrderingFilter,DjangoFilterBackend],'filterset_fields':{'project': ['exact','in', 'isnull']},'ordering_fields':'__all__'}
    ]
    filterset_fields = {'project': ['exact','in', 'isnull']}
