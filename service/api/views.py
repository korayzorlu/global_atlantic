from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet, Q
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet, EditorModelMixin
from rest_framework.viewsets import ModelViewSet

from service.api.serializers import *
from service.models import Offer,Acceptance
from data.models import Part, ServiceCard, Expense

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

class AcceptanceList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = AcceptanceListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
                        'user': ['exact','in', 'isnull']
    }
    #filterset_class = QuotationGlobalFilter
    #search_fields = ['quotationNo', 'inquiry__theRequest__customer__name', 'inquiry__theRequest__vessel__name', 'person__name', 'sessionKey']
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["customer"]
    
        queryset = Acceptance.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["acceptanceNo","acceptanceDate","customer__name","status"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset

class AcceptanceEquipmentList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = AcceptanceEquipmentListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
                        'user': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["equipment","acceptance","equipment__maker","equipment__makerType"]
    
        queryset = Acceptance.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["acceptanceNo","acceptanceDate","customer__name","status"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset


class AcceptanceServiceCardList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    custom_related_fields = ["acceptance","acceptance__currency","serviceCard"]
    queryset = AcceptanceServiceCard.objects.select_related(*custom_related_fields).all()
    serializer_class = AcceptanceServiceCardListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'acceptance': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'serviceCard': ['exact', 'isnull'],
                        'extra': ['exact', 'isnull']
    }
    ordering_fields = '__all__'

class OfferList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = OfferListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
                        'user': ['exact','in', 'isnull'],
                        'code': ['exact','in', 'isnull'],
                        'confirmed': ['exact', 'in', 'isnull'],
                        'finished': ['exact', 'in', 'isnull']
    }
    #filterset_class = QuotationGlobalFilter
    #search_fields = ['quotationNo', 'inquiry__theRequest__customer__name', 'inquiry__theRequest__vessel__name', 'person__name', 'sessionKey']
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["customer","vessel","person","equipment__maker","equipment__makerType","currency"]
    
        queryset = Offer.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["offerNo","offerDate","customer__name","vessel__name","person__name","equipment__maker__name","equipment__makerType__type","status"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset


class OfferServiceCardList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    custom_related_fields = ["offer","offer__currency","serviceCard"]
    queryset = OfferServiceCard.objects.select_related(*custom_related_fields).all()
    serializer_class = OfferServiceCardListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'offer': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'serviceCard': ['exact', 'isnull'],
                        'extra': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
 
class OfferExpenseList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    queryset = OfferExpense.objects.all()
    serializer_class = OfferExpenseListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'offer': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'expense': ['exact', 'isnull'],
                        'extra': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_options(self):
        return "options", {
            "offer": [{'label': obj.offerNo, 'value': obj.pk} for obj in Offer.objects.all()],
            "expense": [{'label': obj.code, 'value': obj.pk} for obj in Expense.objects.all()]
        }
    
    class Meta:
        datatables_extra_json = ('get_options', )
        
class OfferPartList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """

    custom_related_fields = ["offer__currency","part"]
    
    queryset = OfferPart.objects.select_related(*custom_related_fields).all().order_by("id")
    serializer_class = OfferPartListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'offer': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'part': ['exact', 'isnull'],
                        'extra': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    #pagination_class = PageNumberPagination
        
class OfferNoteList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    custom_related_fields = ["user"]
    queryset = OfferNote.objects.select_related(*custom_related_fields).all()
    serializer_class = OfferNoteListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'user': ['exact', 'isnull'],
                        'offer__id': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
        
        
        
        
        