import os
import uuid

from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

# Create your models here.
from information.models import Company
from parts.validators import ExtensionValidator


class MakerCategory(models.Model):
    name = models.CharField(_("Category Name"), max_length=140)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class Maker(models.Model):
    name = models.CharField(_("Maker Name"), max_length=140, unique=True)
    category = models.ManyToManyField(MakerCategory)
    website = models.URLField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    def get_fields(self):
        ignore = ('id', 'created_at', 'updated_at')
        result = []
        for field in self._meta.fields:
            if field.name not in ignore:
                if self._meta.get_field(field.name).__class__.__name__ == "BooleanField":
                    value = True if getattr(self, field.name) else "False"
                elif field.choices:
                    value = getattr(self, f"get_{field.name}_display")()
                else:
                    value = getattr(self, field.name)
                result.append((field.verbose_name.title(), value if value else ''))
        return result


class MakerDocument(models.Model):
    maker = models.ForeignKey(Maker, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(_("Document"), upload_to='documents/makers/',
                            validators=[ExtensionValidator(['pdf', 'doc', 'docx'])])
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.maker.name} -> {os.path.basename(str(self.file))}"

    def get_filename(self):
        return os.path.basename(str(self.file))


class MakerTypeCategory(models.Model):
    name = models.CharField(_("Category Name"), max_length=140)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class MakerType(models.Model):
    maker = models.ForeignKey(Maker, on_delete=models.CASCADE, related_name="maker_types")
    name = models.CharField(_("Maker Type Name"), max_length=140)
    category = models.ManyToManyField(MakerTypeCategory)
    type = models.CharField(_("Type"), max_length=140)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.type}"


class MakerTypeDocument(models.Model):
    maker_type = models.ForeignKey(MakerType, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(_("Document"), upload_to='documents/maker_types/',
                            validators=[ExtensionValidator(['pdf', 'doc', 'docx'])])
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.maker_type.type} -> {os.path.basename(str(self.file))}"

    def get_filename(self):
        return os.path.basename(str(self.file))


class Manufacturer(models.Model):
    supplier_info = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True,
                                      verbose_name=_("Supplier"), related_name="manufacturer_info",
                                      limit_choices_to=Q(company_type__contains="Supplier"))
    maker_info = models.ForeignKey(Maker, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("Maker"),
                                   related_name="manufacturer_info")
    name = models.CharField(_("Manufacturer Name"), max_length=140, unique=True)
    maker = models.ManyToManyField(Maker, verbose_name=_("Maker (Compatible)"), related_name="manufacturers")
    category = models.ManyToManyField(MakerCategory, verbose_name=_("Category"), related_name="manufacturers")
    website = models.URLField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"


class PartUnit(models.Model):
    name = models.CharField(_("Unit Name"), max_length=140, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"


class PartCategory(models.Model):
    name = models.CharField(_("Category Name"), max_length=140, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Part(models.Model):
    name = models.CharField(_("Part Name"), max_length=140)
    unit = models.ForeignKey(PartUnit, on_delete=models.SET_NULL, null=True, verbose_name=_("Unit"),
                             related_name="parts")
    description = models.TextField(_("Description"), null=True)
    category = models.ForeignKey(PartCategory, on_delete=models.SET_NULL, null=True, verbose_name=_("Category"),
                                 related_name="parts")
    code = models.CharField(_("Part Code"), max_length=140, unique=True)
    dimensions = models.CharField(_("Dimensions"), max_length=140, blank=True)
    material = models.CharField(_("Material"), max_length=140, blank=True)

    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name} -> {self.code}"


class PartImage(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(_("Image"), upload_to='images/parts/')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.part.name} -> {os.path.basename(str(self.image))}"

    def get_filename(self):
        return os.path.basename(str(self.image))


class PartDocument(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(_("Document"), upload_to='documents/parts/',
                            validators=[ExtensionValidator(['pdf', 'doc', 'docx'])])
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.part.name} -> {os.path.basename(str(self.file))}"

    def get_filename(self):
        return os.path.basename(str(self.file))


class PartManufacturer(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="manufacturers")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    code = models.CharField(_("Manufacturer Code"), max_length=140)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.part.name} -> {self.manufacturer.name} -> {self.code}"

    class Meta:
        unique_together = ('part', 'code')


class PartCompatibility(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="compatibilities")
    maker = models.ForeignKey(Maker, on_delete=models.CASCADE)
    maker_type = models.ForeignKey(MakerType, on_delete=models.CASCADE)
    code = models.CharField(_("Maker Part Code"), max_length=140)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.part.name} -> {self.maker.name} -> {self.maker_type.type} -> {self.code}"

    class Meta:
        unique_together = ('part', 'code')


class PartSupplier(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="suppliers")
    supplier = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, verbose_name=_("Supplier"),
                                 limit_choices_to=Q(company_type__contains="Supplier"))
    code = models.CharField(_("Supplier Code"), max_length=140)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.part.name} -> {self.supplier.name} -> {self.code}"

    class Meta:
        unique_together = ('part', 'code')


class RelatedSet(models.Model):
    name = models.CharField(_("Related Set Name"), max_length=140)
    code = models.CharField(_("Related Set Code"), max_length=140, unique=True,
                            validators=[
                                RegexValidator(r'ES-SET-\d+', message=_("You should use this format: ES-SET-X"))])
    parts = models.ManyToManyField(Part, verbose_name=_("Parts"), related_name="sets")
    description = models.TextField(_("Description"), null=True)

    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name} -> {self.code}"


class RelatedSetImage(models.Model):
    related_set = models.ForeignKey(RelatedSet, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(_("Image"), upload_to='images/related_sets/')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.related_set.name} -> {os.path.basename(str(self.image))}"

    def get_filename(self):
        return os.path.basename(str(self.image))


class RelatedSetDocument(models.Model):
    related_set = models.ForeignKey(RelatedSet, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(_("Document"), upload_to='documents/related_sets/',
                            validators=[ExtensionValidator(['pdf', 'doc', 'docx'])])
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.related_set.name} -> {os.path.basename(str(self.file))}"

    def get_filename(self):
        return os.path.basename(str(self.file))
