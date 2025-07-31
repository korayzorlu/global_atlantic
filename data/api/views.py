from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet, Q
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework.pagination import PageNumberPagination

from django.contrib.auth.models import User

from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django_filters import filters

from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet, EditorModelMixin
from rest_framework.viewsets import ModelViewSet

from data.api.serializers import *
from data.models import Maker


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

class MakerList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all countries
    Use GET parameters to filter queryset
    """
    
    serializer_class = MakerListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend,SearchFilter]
    filterset_fields = {
                        'name': ['exact','in', 'isnull']
    }
    search_fields = ['partNo']
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = Maker.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
class MakerTypeList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    serializer_class = MakerTypeListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'maker': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'note': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["maker"]
    
        queryset = MakerType.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("type")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["type", "maker__name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
class PartUniqueList(QueryListAPIView):
    """
    Returns all countries
    Use GET parameters to filter queryset
    """
    
    serializer_class = PartUniqueListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend,SearchFilter]
    filterset_fields = {
                        'code': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = PartUnique.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("code")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["code"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset

class PartList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """

    serializer_class = PartListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend,SearchFilter]
    filterset_fields = {
                        'partNo': ['exact','in', 'isnull'],
                        'partUnique': ['exact','in', 'isnull'],
                        'maker': ['exact','in', 'isnull'],
                        'type': ['exact', 'in', 'isnull'],
                        'techncialSpecification': ['exact', 'isnull']
    }
    search_fields = ['partNo']
    ordering_fields = '__all__'
    #pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["maker","type","partUnique","sourceCompany"]
    
        queryset = Part.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("-pk")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["partUnique__code","maker__name","type__type","group","partNo","description","techncialSpecification","crossRef","ourRef","drawingNr",
                             "manufacturer","unit"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
class PartMakerList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = PartMakerListSerializer
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

        queryset = Maker.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        
        partMakers = []
        parts = Part.objects.select_related("maker").filter(maker__in = queryset)
        for part in parts:
            #print(type(part)._meta.model_name)
            partMakers.append(part.maker.id)
        queryset=queryset.filter(id__in = partMakers)

                
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset

class PartTypeFilter(FilterSet):
    maker = filters.BaseInFilter(field_name='maker__id', lookup_expr='in')

    class Meta:
        model = MakerType
        fields = {
            'id': ['exact', 'in', 'isnull'],
            'maker': ['exact', 'in', 'isnull'],
        }

class PartTypeList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    serializer_class = PartTypeListSerializer
    # filterset_fields = {
    #                     'id': ['exact','in', 'isnull'],
    #                     'maker': ['exact','in', 'isnull'],
    # }
    filterset_class = PartTypeFilter
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []

        queryset = MakerType.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).exclude(type = "").order_by("maker__name")
        
        partTypes = []
        parts = Part.objects.select_related("type").filter(type__in = queryset)
        for part in parts:
            #print(type(part)._meta.model_name)
            partTypes.append(part.type.id)
        queryset=queryset.filter(id__in = partTypes)

                
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query.strip()})
            
            queryset = queryset.filter(q_objects)
        return queryset

class PartForTechnicalSpecificationList(QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    serializer_class = PartForTechnicalSpecificationListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'techncialSpecification': ['exact', 'isnull']
    }
    search_fields = ['techncialSpecification']
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = Part.objects.filter(sourceCompany = self.request.user.profile.sourceCompany).exclude(Q(techncialSpecification__isnull = True) | Q(techncialSpecification = ""))
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = []
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset

class ServiceCardList(QueryListAPIView):
    """
    Returns all countries
    Use GET parameters to filter queryset
    """
    
    serializer_class = ServiceCardListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'id': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = ServiceCard.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name","code","about","group"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
class ExpenseList(QueryListAPIView):
    """
    Returns all countries
    Use GET parameters to filter queryset
    """
    
    serializer_class = ExpenseListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'id': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = Expense.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name","code","description","group"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
    
# Add formlarına uyarlama
class MakerTypeAddList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    serializer_class = MakerTypeAddListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'maker': ['exact','in', 'isnull'],
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'note': ['exact', 'isnull']
    }
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = ["maker"]
    
        queryset = MakerType.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("type")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["type","maker__name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset