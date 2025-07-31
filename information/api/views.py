from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend

from information.api.serializers import *
from information.models import Contact, Company, City, Country, Vessel
from information.scrapers import get_vessel_info


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
    custom_related_fields = ["company_group", "country", "city"]
    queryset = Company.objects.select_related(*custom_related_fields).all()
    serializer_class = CompanyListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class CompanyCustomerList(QueryListAPIView):
    """
    Returns all companies those are customer
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["company_group", "country", "city"]
    queryset = Company.objects.select_related(*custom_related_fields).filter(
        company_type__in=["Customer", "Customer & Supplier"])
    serializer_class = CompanyListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class CompanySupplierList(QueryListAPIView):
    """
    Returns all companies those are supplier
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["company_group", "country", "city"]
    queryset = Company.objects.select_related(*custom_related_fields).filter(
        company_type__in=["Supplier", "Customer & Supplier"])
    serializer_class = CompanyListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class ContactList(QueryListAPIView):
    """
    Returns all contacts
    Use GET parameters to filter queryset
    """
    queryset = Contact.objects.prefetch_related("company").all()
    serializer_class = ContactListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class VesselList(QueryListAPIView):
    """
    Returns all contacts
    Use GET parameters to filter queryset
    """
    custom_related_fields = ["manager_company", "owner_company"]
    queryset = Vessel.objects.select_related(*custom_related_fields).all()
    serializer_class = VesselListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class CompanyAPI(generics.RetrieveDestroyAPIView):
    """
    Returns or deletes the company
    """
    custom_related_fields = ["company_group", "country", "city", "customer_representative", "key_account"]
    queryset = Company.objects.select_related(*custom_related_fields).all()
    serializer_class = CompanyDetailSerializer


class ContactAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the contact
    """
    queryset = Contact.objects.prefetch_related("company").all()
    serializer_class = ContactDetailSerializer


class VesselAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the vessel
    """
    queryset = Vessel.objects.prefetch_related("person_in_contacts").all()
    serializer_class = VesselDetailSerializer


class VesselDataFromOuter(APIView):
    """
    Retrieve vessel data from outer sources (only vesselfinder.com for now)
    """

    def get(self, request, imo):
        try:
            data = get_vessel_info(imo)
            return JsonResponse(data, safe=False)
        except TimeoutError as te:
            return JsonResponse({"detail": str(te)}, status=504)
        except TypeError as te:
            return JsonResponse({"detail": str(te)}, status=400)
        except ValueError as ve:
            return JsonResponse({"detail": str(ve)}, status=404)
