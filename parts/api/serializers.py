from rest_framework import serializers

from information.api.serializers import CompanyListSerializer
from parts.models import MakerType, Maker, MakerDocument, MakerTypeDocument, MakerCategory, MakerTypeCategory, \
    Manufacturer, PartUnit, PartCategory, Part, PartDocument, PartImage, PartManufacturer, PartSupplier, \
    PartCompatibility, RelatedSetImage, RelatedSetDocument, RelatedSet


class MakerTypeDocumentDetailSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source='get_filename')

    class Meta:
        model = MakerTypeDocument
        exclude = ["created_at", "updated_at"]


class MakerTypeDocumentListSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source='get_filename')

    class Meta:
        model = MakerTypeDocument
        fields = ["id", "filename", "file", "maker_type"]


class MakerTypeCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakerTypeCategory
        exclude = ["created_at", "updated_at"]


class MakerTypeCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakerTypeCategory
        fields = ["id", "name"]


class MakerTypeDetailSerializer(serializers.ModelSerializer):
    category = MakerTypeCategoryListSerializer(many=True)
    documents = MakerTypeDocumentListSerializer(many=True)

    class Meta:
        model = MakerType
        exclude = ["created_at", "updated_at"]


class MakerTypeListSerializer(serializers.ModelSerializer):
    category = MakerTypeCategoryListSerializer(many=True)

    class Meta:
        model = MakerType
        fields = ["id", "maker", "name", "type", "category"]


class MakerDocumentDetailSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source='get_filename')

    class Meta:
        model = MakerDocument
        exclude = ["created_at", "updated_at"]


class MakerDocumentListSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source='get_filename')

    class Meta:
        model = MakerDocument
        fields = ["id", "filename", "file", "maker"]


class MakerCategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakerCategory
        exclude = ["created_at", "updated_at"]


class MakerCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MakerCategory
        fields = ["id", "name"]


class MakerDetailSerializer(serializers.ModelSerializer):
    category = MakerCategoryListSerializer(many=True)
    documents = MakerDocumentListSerializer(many=True)
    maker_types = MakerTypeListSerializer(many=True)

    class Meta:
        model = Maker
        exclude = ["created_at", "updated_at"]


class MakerListDetailSerializer(serializers.ModelSerializer):
    """
    This one is made for users can search the datatable with category and types of the maker types
    """
    category = MakerCategoryListSerializer(many=True)
    maker_types = MakerTypeListSerializer(many=True)

    class Meta:
        model = Maker
        fields = ["id", "name", "website", "category", "maker_types"]


class MakerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maker
        fields = ["id", "name", "website"]


class ManufacturerListSerializer(serializers.ModelSerializer):
    maker = MakerListSerializer(many=True)
    category = MakerCategoryListSerializer(many=True)

    class Meta:
        model = Manufacturer
        fields = ["id", "name", "website", "maker", "category"]


class ManufacturerDetailSerializer(serializers.ModelSerializer):
    supplier_info = CompanyListSerializer()
    maker_info = MakerListSerializer()
    maker = MakerListSerializer(many=True)
    category = MakerCategoryListSerializer(many=True)

    class Meta:
        model = Manufacturer
        exclude = ["created_at", "updated_at"]


class PartUnitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartUnit
        fields = ["id", "name"]


class PartCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartCategory
        fields = ["id", "name"]


class PartDocumentDetailSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source='get_filename')

    class Meta:
        model = PartDocument
        exclude = ["created_at", "updated_at"]


class PartDocumentListSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source='get_filename')

    class Meta:
        model = PartDocument
        fields = ["id", "filename", "file"]


class PartImageDetailSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source='get_filename')

    class Meta:
        model = PartImage
        exclude = ["created_at", "updated_at"]


class PartManufacturerDetailSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerListSerializer()

    class Meta:
        model = PartManufacturer
        exclude = ["created_at", "updated_at"]


class PartManufacturerListSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerListSerializer()

    class Meta:
        model = PartManufacturer
        fields = ["id", "part", "manufacturer", "code"]


class PartSupplierDetailSerializer(serializers.ModelSerializer):
    supplier = CompanyListSerializer()

    class Meta:
        model = PartSupplier
        exclude = ["created_at", "updated_at"]


class PartSupplierListSerializer(serializers.ModelSerializer):
    supplier = CompanyListSerializer()

    class Meta:
        model = PartSupplier
        fields = ["id", "part", "supplier", "code"]


class PartCompatibilityDetailSerializer(serializers.ModelSerializer):
    maker = MakerListSerializer()
    maker_type = MakerTypeListSerializer()

    class Meta:
        model = PartCompatibility
        exclude = ["created_at", "updated_at"]


class PartCompatibilityListSerializer(serializers.ModelSerializer):
    maker = MakerListSerializer()
    maker_type = MakerTypeListSerializer()

    class Meta:
        model = PartCompatibility
        fields = ["id", "maker", "maker_type", "code"]


class PartDetailSerializer(serializers.ModelSerializer):
    unit = PartUnitListSerializer()
    category = PartCategoryListSerializer()
    images = PartImageDetailSerializer(many=True)
    documents = PartDocumentListSerializer(many=True)
    compatibilities = PartCompatibilityListSerializer(many=True)
    suppliers = PartSupplierListSerializer(many=True)
    manufacturers = PartManufacturerListSerializer(many=True)

    class Meta:
        model = Part
        exclude = ["created_at", "updated_at"]


class PartListSerializer(serializers.ModelSerializer):
    str = serializers.CharField(source='__str__')
    unit = PartUnitListSerializer()
    category = PartCategoryListSerializer()

    class Meta:
        model = Part
        fields = ["id", "name", "description", "dimensions", "material", "code", "unit", "category", "str"]


class RelatedSetDocumentDetailSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source='get_filename')

    class Meta:
        model = RelatedSetDocument
        exclude = ["created_at", "updated_at"]


class RelatedSetImageDetailSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(source='get_filename')

    class Meta:
        model = RelatedSetImage
        exclude = ["created_at", "updated_at"]


class RelatedSetDetailSerializer(serializers.ModelSerializer):
    parts = PartListSerializer(many=True)
    images = RelatedSetImageDetailSerializer(many=True)
    documents = RelatedSetDocumentDetailSerializer(many=True)

    class Meta:
        model = RelatedSet
        exclude = ["created_at", "updated_at"]


class RelatedSetListSerializer(serializers.ModelSerializer):
    str = serializers.CharField(source='__str__')
    parts = PartListSerializer(many=True)

    class Meta:
        model = RelatedSet
        fields = ["id", "name", "description", "code", "parts", "str"]
