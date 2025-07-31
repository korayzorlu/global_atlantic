from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet, ForeignObjectRel
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework_datatables.filters import DatatablesFilterBackend

from parts.api.serializers import *
from parts.models import Maker, MakerType


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
            if isinstance(field, ForeignObjectRel):
                for n in field.related_model._meta.get_fields():
                    related_field = f"{field.name}__{n.name}"
                    if related_field in dict(self.request.GET):
                        accepted_filters[related_field] = dict(self.request.GET)[related_field]
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


class MakerList(QueryListAPIView):
    """
    Returns all makers
    Use GET parameters to filter queryset
    """
    queryset = Maker.objects.prefetch_related("category", "documents", "maker_types").all()
    serializer_class = MakerListDetailSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class MakerTypeList(QueryListAPIView):
    """
    Returns all maker types
    Use GET parameters to filter queryset
    """
    queryset = MakerType.objects.select_related("maker").prefetch_related("category", "documents").all()
    serializer_class = MakerTypeListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class MakerAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the maker
    """
    queryset = Maker.objects.all()
    serializer_class = MakerDetailSerializer


class MakerTypeAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the maker type
    """
    queryset = MakerType.objects.all()
    serializer_class = MakerTypeDetailSerializer


class MakerDocumentAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the maker document
    """
    queryset = MakerDocument.objects.all()
    serializer_class = MakerDocumentDetailSerializer


class MakerTypeDocumentAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the maker type document
    """
    queryset = MakerTypeDocument.objects.all()
    serializer_class = MakerTypeDocumentDetailSerializer


class ManufacturerList(QueryListAPIView):
    """
    Returns all manufacturers
    Use GET parameters to filter queryset
    """
    select_related = ["supplier_info", "maker_info"]
    prefetch_related = ["category", "maker"]
    queryset = Manufacturer.objects.select_related(*select_related).prefetch_related(*prefetch_related).all()
    serializer_class = ManufacturerListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class ManufacturerAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the manufacturer
    """
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerDetailSerializer


class PartList(QueryListAPIView):
    """
    Returns all parts
    Use GET parameters to filter queryset
    """
    select_related = ["unit", "category"]
    prefetch_related = ["compatibilities", "suppliers", "manufacturers"]
    queryset = Part.objects.select_related(*select_related).prefetch_related(*prefetch_related).all()
    serializer_class = PartListSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = '__all__'
    search_fields = ['name', 'code']


class PartAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the part
    """
    queryset = Part.objects.all()
    serializer_class = PartDetailSerializer


class PartCompatibilityAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the part compatibility
    """
    queryset = PartCompatibility.objects.all()
    serializer_class = PartCompatibilityDetailSerializer


class PartSupplierAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the part supplier
    """
    queryset = PartSupplier.objects.all()
    serializer_class = PartSupplierDetailSerializer


class PartManufacturerAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the part manufacturer
    """
    queryset = PartManufacturer.objects.all()
    serializer_class = PartManufacturerDetailSerializer


class PartImageAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the part image
    """
    queryset = PartImage.objects.all()
    serializer_class = PartImageDetailSerializer


class PartDocumentAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the part document
    """
    queryset = PartDocument.objects.all()
    serializer_class = PartDocumentDetailSerializer


class RelatedSetList(QueryListAPIView):
    """
    Returns all related sets
    Use GET parameters to filter queryset
    """
    select_related = []
    prefetch_related = ["parts"]
    queryset = RelatedSet.objects.select_related(*select_related).prefetch_related(*prefetch_related).all()
    serializer_class = RelatedSetListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class RelatedSetAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the related set
    """
    queryset = RelatedSet.objects.all()
    serializer_class = RelatedSetDetailSerializer


class RelatedSetImageAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the related set image
    """
    queryset = RelatedSetImage.objects.all()
    serializer_class = RelatedSetImageDetailSerializer


class RelatedSetDocumentAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, updates or deletes the related set document
    """
    queryset = RelatedSetDocument.objects.all()
    serializer_class = RelatedSetDocumentDetailSerializer
