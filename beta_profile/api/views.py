from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework_datatables.filters import DatatablesFilterBackend

from beta_profile.api.serializers import *


class QueryListAPIView(generics.ListAPIView):
    def get_queryset(self):
        if self.request.GET.get('format', None) == 'datatables':
            self.filter_backends = (OrderingFilter, DatatablesFilterBackend)
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
    queryset = Department.objects.all()
    serializer_class = DepartmentListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class TeamList(QueryListAPIView):
    """
    Returns all teams
    Use GET parameters to filter queryset
    """

    queryset = Team.objects.prefetch_related("members").all()
    serializer_class = TeamListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class EmployeeTypeList(QueryListAPIView):
    """
    Returns all employee types
    Use GET parameters to filter queryset
    """
    queryset = EmployeeType.objects.all()
    serializer_class = EmployeeTypeListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class UserList(QueryListAPIView):
    """
    Returns all users
    Use GET parameters to filter queryset
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


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

class LeaveListAPIView(generics.ListAPIView):
    """
    Returns all leaves
    Use GET parameters to filter queryset
    """
    queryset = Leave.objects.all()
    serializer_class = LeaveListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'

class LeaveCreateAPIView(generics.CreateAPIView):
    """
    Creates a leave
    """
    queryset = Leave.objects.all()
    serializer_class = LeaveCreateSerializer


class LeaveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the leave
    """
    queryset = Leave.objects.all()
    serializer_class = LeaveCreateSerializer

    def destroy(self, request, *args, **kwargs):
        # instance = self.get_object()
        return super().destroy(request, *args, **kwargs)

class TitleListAPIView(generics.ListAPIView):
    """
    Returns all titles
    Use GET parameters to filter queryset
    """
    queryset = Title.objects.all()
    serializer_class = TitleListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'

class TitleUpdateAPIView(generics.RetrieveDestroyAPIView):
    """
    Returns, delete or update the title
    """
    queryset = Title.objects.all()
    serializer_class = TitleListSerializer

class DocumentListAPIView(generics.ListAPIView):
    """
    Returns all documents
    Use GET parameters to filter queryset
    """
    queryset = Document.objects.all()
    serializer_class = DocumentListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'

class DocumentCreateAPIView(generics.CreateAPIView):
    """
    Creates a document
    """
    queryset = Document.objects.all()
    serializer_class = DocumentCreateSerializer

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.beta_profile)

class DocumentUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the document
    """
    queryset = Document.objects.all()
    serializer_class = DocumentCreateSerializer
    
    def perform_update(self, serializer):
        instance = self.get_object()
        serializer.save(profile=instance.profile)

    def destroy(self, request, *args, **kwargs):
        # instance = self.get_object()
        return super().destroy(request, *args, **kwargs)