from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet, Q
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework_datatables.filters import DatatablesFilterBackend
import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django_filters import CharFilter

from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet, EditorModelMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from user.api.serializers import *

from user.models import AccessAuthorization,DataAuthorization

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


class DepartmentList(QueryListAPIView):
    """
    Returns all departments
    Use GET parameters to filter queryset
    """
    
    serializer_class = DepartmentListSerializer
    filterset_fields = {
                        'name': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = Department.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset

class PositionList(QueryListAPIView):
    """
    Returns all departments
    Use GET parameters to filter queryset
    """
    
    serializer_class = PositionListSerializer
    filterset_fields = {
                        'name': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = Position.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset

class TeamList(QueryListAPIView):
    """
    Returns all teams
    Use GET parameters to filter queryset
    """
    
    serializer_class = TeamListSerializer
    filterset_fields = {
                        'name': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = Team.objects.select_related(*custom_related_fields).prefetch_related("members").filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset


class EmployeeTypeList(QueryListAPIView):
    """
    Returns all employee types
    Use GET parameters to filter queryset
    """
    
    serializer_class = EmployeeTypeListSerializer
    filterset_fields = {
                        'name': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = EmployeeType.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset


class UserList(QueryListAPIView):
    """
    Returns all users
    Use GET parameters to filter queryset
    """
    
    serializer_class = UserListSerializer
    filterset_fields = {
                        'name': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []

        queryset = User.objects.select_related(*custom_related_fields).filter(profile__sourceCompany = self.request.user.profile.sourceCompany).order_by("first_name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["username", "first_name", "last_name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
    


class RecordList(QueryListAPIView):
    """
    Returns all records
    Use GET parameters to filter queryset
    """
    queryset = Record.objects.all()
    serializer_class = RecordListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class CurrencyList(QueryListAPIView):
    """
    Returns all currencies
    Use GET parameters to filter queryset
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencyListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class DepartmentAPI(generics.RetrieveAPIView, generics.DestroyAPIView):
    """
    Returns or deletes the department
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentListSerializer


class TeamAPI(generics.RetrieveAPIView, generics.DestroyAPIView):
    """
    Returns or deletes the team
    """
    queryset = Team.objects.all()
    serializer_class = TeamListSerializer


class EmployeeTypeAPI(generics.RetrieveAPIView, generics.DestroyAPIView):
    """
    Returns or deletes the employee type
    """
    queryset = EmployeeType.objects.all()
    serializer_class = EmployeeTypeListSerializer


class UserAPI(generics.RetrieveAPIView, generics.DestroyAPIView):
    """
    Returns or deletes the user
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer


class ProfileThemeAPI(generics.RetrieveUpdateAPIView):
    """
    Returns or updates the theme value of the profile
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileThemeSerializer


class ProfileImageAPI(generics.RetrieveUpdateAPIView):
    """
    Returns or updates the image of the profile
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileImageSerializer

class ProfileList(QueryListAPIView):
    """
    Returns all users
    Use GET parameters to filter queryset
    """
    
    serializer_class = ProfileListSerializer
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
    
        queryset = Profile.objects.select_related(*custom_related_fields).filter(sourceCompany = self.request.user.profile.sourceCompany).order_by("user__first_name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["user__username", "user__first_name", "user__last_name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset


class EducationList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    queryset = Education.objects.all()
    serializer_class = EducationListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'educationProfile': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'
    
class AdditionalPaymentList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    queryset = AdditionalPayment.objects.all()
    serializer_class = AdditionalPaymentListSerializer
    #filterset_class = PersonFilter
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    filterset_fields = {
                        'user': ['exact', 'isnull'],
                        'sessionKey': ['exact', 'isnull'],
                        'additionalPaymentProfile': ['exact','in', 'isnull']
    }
    ordering_fields = '__all__'
    
class AccessAuthorizationList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """

    serializer_class = AccessAuthorizationListSerializer
    filterset_fields = {
                        'user': ['exact','in', 'isnull'],
                        'sessionKey': ['exact','in', 'isnull'],
                        'name': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = AccessAuthorization.objects.select_related(*custom_related_fields).all().order_by("name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name","code"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
class DataAuthorizationList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """

    serializer_class = DataAuthorizationListSerializer
    filterset_fields = {
                        'user': ['exact','in', 'isnull'],
                        'sessionKey': ['exact','in', 'isnull'],
                        'name': ['exact','in', 'isnull'],
    }
    filter_backends = [OrderingFilter,DjangoFilterBackend]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        custom_related_fields = []
    
        queryset = DataAuthorization.objects.select_related(*custom_related_fields).all().order_by("name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["name","code"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset
    
class UserAuthorizationList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """

    serializer_class = UserAuthorizationListSerializer
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
    
        queryset = Profile.objects.select_related(*custom_related_fields).all().order_by("user__first_name","user__last_name")
        query = self.request.query_params.get('search[value]', None)
        if query:
            search_fields = ["username","first_name","last_name"]
            
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": query})
            
            queryset = queryset.filter(q_objects)
        return queryset