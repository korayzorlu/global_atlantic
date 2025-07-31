from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

# from django_filters import FilterSet, ChoiceFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, ChoiceFilter, CharFilter, MultipleChoiceFilter
from drf_multiple_model.views import ObjectMultipleModelAPIView, FlatMultipleModelAPIView

from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet, EditorModelMixin
from rest_framework.viewsets import ModelViewSet

import django_filters
from django.db.models import Q
from django_filters import CharFilter
from django.utils import timezone

from unidecode import unidecode

from card.api.serializers import *
from card.models import Company


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


class CountryList(QueryListAPIView):
    """
    Returns all countries
    Use GET parameters to filter queryset
    """
    queryset = Country.objects.all()
    serializer_class = CountryListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'
    
class CityList(QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    queryset = City.objects.all()
    serializer_class = CityListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'
 
class CompanyList(QueryListAPIView):
    """
    Returns all companies
    Use GET parameters to filter queryset
    """

    serializer_class = CompanyListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend,SearchFilter]
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
                        'name': ['exact','in', 'isnull'],
                        'supplierCheck': ['exact','in', 'isnull'],
                        'sourceCompany': ['exact','in', 'isnull']
    }
    search_fields = ['name']
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        
        custom_related_fields = ["country","city"]
    
        queryset = Company.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        query = self.request.query_params.get('search[value]', None)
        
        if query:
            search_fields = ["name","lowerName","hesapKodu","role","country__international_formal_name","city__name","phone1","email","companyNo","vatOffice","vatNo"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            print(q_objects)
            queryset = queryset.filter(q_objects)
        return queryset

class CurrencyList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """

    serializer_class = CurrencyListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
                        'code': ['exact','in', 'isnull'],
                        'symbol': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = Currency.objects.select_related(*custom_related_fields).filter().order_by("sequency")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["code","symbol","rateDate"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset

class CurrentList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    serializer_class = CurrentListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
                        'company': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["company","currency"]
    
        queryset = Current.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["company__name","debt","credit","currency__code"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset

class PersonList(QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    serializer_class = PersonListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend,SearchFilter]
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
                        'company': ['exact','in', 'isnull'],
                        'vessel': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sourceCompany': ['exact','in', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'title': ['exact', 'isnull']
    }
    search_fields = []
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = Person.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        query = self.request.query_params.get('search[value]', None)
        
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            print(q_objects)
            queryset = queryset.filter(q_objects)
        return queryset
  
class VesselList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all companies
    Use GET parameters to filter queryset
    """
    serializer_class = VesselListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend,SearchFilter]
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
                        'name': ['exact','in', 'isnull'],
                        'company__id': ['exact','in', 'isnull'],
                        'sourceCompany': ['exact','in', 'isnull']
    }
    
    ordering_fields = '__all__'

    #pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["company","owner"]
    
        queryset = Vessel.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        query = self.request.query_params.get('search[value]', None)
        
        if query:
            search_fields = ["name","company__name","owner__name","imo","mmsi"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            print(q_objects)
            queryset = queryset.filter(q_objects)
        return queryset

class VesselHistoryList(generics.ListAPIView):
    serializer_class = VesselHistoryListSerializer
    queryset = []
    
    def list(self, request, id, *args, **kwargs):
        vessel = Vessel.objects.filter(id = id).first()
        
        historyRecords = []
        for history in vessel.history.all().order_by("history_date"):
            historyRecords.append({
                "vessel" : history.instance.id,
                "value" : history.company.name,
                "date" : history.history_date.astimezone(timezone.get_current_timezone()).strftime("%d.%m.%Y %H:%M:%S"),
                "status" : "Old"
            })
            
        uniqueHistory = []
        previousValue = None
        for history in historyRecords:
            if history["value"] != previousValue:
                uniqueHistory.append({
                    "vessel," : history["vessel"],
                    "value" : history["value"],
                    "date" : history["date"],
                    "status" : history["status"],
                })
                previousValue = history["value"]
        
        uniqueHistory[-1]["status"] = "Current"
        
        data_format = request.query_params.get('format', None)
        if data_format == 'datatables':
            filter_backends = (DatatablesFilterBackend)
            data = {
                "draw": int(self.request.GET.get('draw', 1)),  # Müşteri tarafından gönderilen çizim sayısı
                "recordsTotal": len(list(reversed(uniqueHistory))),  # Toplam kayıt sayısı
                "recordsFiltered": len(list(reversed(uniqueHistory))),  # Filtre sonrası kayıt sayısı
                "data": list(reversed(uniqueHistory))  # Gösterilecek veri
            }
            
            return Response(data)
        serializer = self.get_serializer(list(reversed(uniqueHistory)), many=True)
        return Response(serializer.data)
    
    
class EnginePartList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """

    custom_related_fields = ["vessel", "maker","makerType"]
    queryset = EnginePart.objects.select_related(*custom_related_fields).all().order_by("-id")
    serializer_class = EnginePartListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
                        'id': ['exact','in', 'isnull'],
                        'vessel': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'maker': ['exact', 'isnull'],
                        'makerType': ['exact', 'isnull']
    }
    ordering_fields = '__all__'

class BankList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    serializer_class = BankListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend,SearchFilter]
    filterset_fields = {
                        'company': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
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
    
        queryset = Bank.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("bankName")
        query = self.request.query_params.get('search[value]', None)
        
        if query:
            search_fields = ["bankName","currency__code"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            print(q_objects)
            queryset = queryset.filter(q_objects)
        return queryset
        
class OwnerList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    serializer_class = OwnerListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'vessel': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'ownerCompany': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["ownerCompany"]
    
        queryset = Owner.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("ownerCompany__name")
        query = self.request.query_params.get('search[value]', None)
        
        if query:
            search_fields = ["ownerCompany__name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            print(q_objects)
            queryset = queryset.filter(q_objects)
        return queryset
    
class BillingList2(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    queryset = Billing.objects.all()
    serializer_class = BillingListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'vessel__id': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'name': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    
class BillingInVesselList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    
    serializer_class = BillingInVesselListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'vessel': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["vessel"]
    
        queryset = Billing.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        query = self.request.query_params.get('search[value]', None)
        
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            print(q_objects)
            queryset = queryset.filter(q_objects)
        return queryset
    
    # def get_queryset(self):
    #     """
    #     Optionally restricts the returned requests to a given user,
    #     by filtering against a `username` query parameter in the URL.
    #     """

    #     custom_related_fields = ["vessel"]
    
    #     queryset = Billing.objects.select_related(*custom_related_fields).all().order_by("vessel__name","-pk")
    #     query = self.request.query_params.get('search[value]', None)
    #     if query:
    #         search_fields = ["vessel__name","name"]
            
    #         q_objects = Q()
    #         for field in search_fields:
    #             q_objects |= Q(**{f"{field}__icontains": query})
            
    #         queryset = queryset.filter(q_objects)
    #     return queryset

class BillingList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = BillingListSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
                        'vessel__id': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["vessel"]
    
        queryset = Billing.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("vessel__name","-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["vessel__name","name","hesapKodu","vatNo"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset