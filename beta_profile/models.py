import datetime
from decimal import Decimal
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timesince import timesince
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator 

from beta_profile.utils import resize_image
from beta_profile.validators import ExtensionValidator


class Team(models.Model):
    name = models.CharField(_("Name"), max_length=140, null=True, unique=True)
    about = models.TextField(_("About"), blank=True, null=True)
    members = models.ManyToManyField(User, related_name="beta_team", blank=True)
    lead = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="teams",  null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Department(models.Model):
    """
    Describes department info
    """
    name = models.CharField(_("Name"), max_length=140, null=True, unique=True)
    about = models.TextField(_("About"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def get_objects_by_name(name):
        return Department.objects.filter(name__icontains=name.lower())


class EmployeeType(models.Model):
    name = models.CharField(_("Name"), max_length=140, null=True, unique=True)
    about = models.TextField(_("About"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def get_objects_by_name(name):
        return EmployeeType.objects.filter(name__icontains=name.lower())

class Title(models.Model):
    name = models.CharField(_("Name"), max_length=140, null=True, unique=True)
    about = models.TextField(_("About"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def get_objects_by_name(name):
        return Title.objects.filter(name__icontains=name.lower())

class Profile(models.Model):
    """
    This model represents the profile info of Internal Personals.
    """
    THEME_CHOICES = (('dark', _('Dark')), ('light', _('Light')))
    GENDER_CHOICES = (('m', _('Male')),('f', _('Female'))) 
    MARIAL_STATUS_CHOICES = (('m', _('Married')),('s', _('Single'))) 
    COMPULSORY_MILITARY_SERVICE_STATUS_CHOICES = (('e', _('Exempt')), ('c', _('Completed')), ('dl', _('Delayed for less than 2 years')), ('dm', _('Delayed for more than 2 years')))

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="beta_profile")
    image = models.ImageField(_("Image"), upload_to='images/profiles/',
                              help_text=_("Please upload a square image, otherwise center will be cropped."),  null=True, blank=False)
    birthday = models.DateField(_("Birthday"),  null=True, blank=False)
    birthplace = models.CharField(_("Birth Place"), max_length=120,  null=True, blank=False)
    phone_number = models.CharField(_("Phone Number"), max_length=50,  null=True, blank=False)
    home_number = models.CharField(_("Home Number"), max_length=50,  null=True, blank=False)
    address = models.TextField(_("Address"),  null=True, blank=False)
    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,  null=True, blank=False)
    marial_status = models.CharField(max_length=1, choices=MARIAL_STATUS_CHOICES,  null=True, blank=False)
    compulsory_military_service_status = models.CharField(max_length=2, choices=COMPULSORY_MILITARY_SERVICE_STATUS_CHOICES, blank=True, null=True)

    degree = models.CharField(_("Degree"), max_length=100,  null=True, blank=False)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=False, related_name="beta_members")
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.SET_NULL, null=True, blank=False,
                                      related_name="beta_members")
    title = models.ForeignKey(Title, on_delete=models.SET_NULL, null=True, blank=False,
                                      related_name="beta_members")

    total_annual_leave = models.PositiveIntegerField(_("Total Annual Leave"), null=True, blank=False, validators=[MinValueValidator(0)])
    remaining_annual_leave = models.PositiveIntegerField(_("Remaining Annual Leave"), null=True, blank=False, validators=[MinValueValidator(0)])

    salary = models.DecimalField(_("Salary"), max_digits=8, decimal_places=3, null=True, blank=False,
                                 validators=[MinValueValidator(Decimal('0.0'))])
    bonus_right = models.BooleanField(_("Bonus Right"), default=False)

    bonus_rate = models.DecimalField(_("Bonus Rate %"), max_digits=6, decimal_places=3, blank=True, null=True,
                                 validators=[MinValueValidator(Decimal('0.0'))])
    bonus_info = models.TextField(_("Bonus Information"), null=True, blank=False)  

    language = models.CharField(_("Language"), max_length=50, choices=settings.LANGUAGES, default='Turkish')
    theme = models.CharField(_("Theme"), max_length=25, default='dark', choices=THEME_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__image = self.image

    def __str__(self):
        return f"{self.user} | {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        """
        Crop image before sending to Amazon, thanks to:
        https://blog.soards.me/posts/resize-image-on-save-in-django-before-sending-to-amazon-s3/
        https://bhch.github.io/posts/2018/12/django-how-to-editmanipulate-uploaded-images-on-the-fly-before-saving/
        """
        # check if the image field is changed
        if self.image and self.image != self.__image:
            self.image = resize_image(self.image, 512, 512)
        super().save(*args, **kwargs)

    @staticmethod
    def get_read_only_fields():
        return ['degree', 'position', 'birthday']

    def get_count_of_used_annual_leave(self):
        return (self.total_annual_leave - self.remaining_annual_leave)


class Currency(models.Model):
    base = models.CharField(_("Base"), max_length=50, blank=True, null=True)
    name = models.CharField(_("Name"), max_length=50, blank=True, null=True)
    rate = models.DecimalField(_('Rate'), max_digits=30, decimal_places=10, default=1.0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @staticmethod
    def get_last_currency_update_time():
        ordered_currencies = Currency.objects.all().order_by('-updated_at').first()
        if ordered_currencies:
            return ordered_currencies.updated_at
        else:
            return datetime.datetime(1, 1, 1, tzinfo=datetime.timezone.utc)

    @staticmethod
    def get_currencies(base="EUR"):
        updated_at = Currency.get_last_currency_update_time()
        # create a last updated info text if objects exists
        if updated_at:
            info = _(f"Updated {timesince(updated_at, depth=1)} ago")
        else:
            info = ''
        data = {
            "success": False,
            "base": base,
            "info": info,
            "rates": {}
        }
        # get base currency object
        base_obj = Currency.objects.filter(name=base).first()
        if base_obj:
            # get all currency objects
            currencies = Currency.objects.all()
            if currencies.exists():
                for currency in currencies:
                    # if base and currency is not the same
                    if currency.name != base:
                        # calculate the new rate due to new base
                        data["rates"][currency.name] = round(base_obj.rate / currency.rate, 2)
                    else:
                        continue
            else:
                return data
            data["success"] = True
            return data
        else:
            return data

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ("name",)


# this model was provided by Novuhub project, minor changes applied over
class Record(models.Model):
    """
    Basic log record describing all user interaction with the UI.
    Will be propagated by a middleware.
    This will be one BIG DB table!
    """

    session_id = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="beta_records")
    username = models.CharField(max_length=150, null=True)
    path = models.TextField(null=True)
    query_string = models.TextField(null=True, blank=True)
    method = models.CharField(max_length=7)
    secure = models.BooleanField(default=False)
    ajax = models.BooleanField(default=False)
    meta = models.TextField(null=True, blank=True)
    address = models.GenericIPAddressField(null=True, blank=True)
    response_code = models.CharField(max_length=3)
    response_content = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def get_timesince(self):
        return timesince(self.created_at)

    class Meta:
        verbose_name_plural = "Records"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.username} - {self.created_at}"


class Certification(models.Model):
    """
    this model provide keep Certification properties
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name="beta_certifications")    
    name = models.CharField(_("Certificate Name"), max_length=255)
    issued_by = models.CharField(_("Issued By"), max_length=255)
    issued_date = models.DateField(_("Issued Date"))
    expired_date = models.DateField(_("Expired Date"), null=True, blank=True)
    file = models.FileField(_("CV / Resume"), upload_to='documents/hr/certification',
                                validators=[ExtensionValidator(['pdf', 'png'])])

    def __str__(self):
        return f"{self.name}"

    def get_filename(self):
        return os.path.basename(str(self.file))



class Education(models.Model):

    EDUCATION_LEVEL_CHOICES = (
        ("ps", _("Primary School")),
        ("ss", _("Secondary School")),
        ("hh", _("High School")),   
        ("hhd", _("High School (Distance Education)")),   
        ("adeg", _("Associate Degree")),
        ("adegd", _("Associate Degree (Distance Education)")),
        ("deg", _("Degree")),
        ("degd", _("Degree (Distance Education)")),
        ("mdeg", _("Master Degree")),
        ("doc", _("Doctorate")),      
    )

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="educations")    
    name = models.CharField(_("Institution Name"), max_length=255)
    education_level = models.CharField(_("Education Level"), max_length=5, choices=EDUCATION_LEVEL_CHOICES)
    major = models.CharField(_("Major Branch"), max_length=255, default="Compulsory Education")
    diploma = models.FileField(_("Diploma"), upload_to='documents/hr/diploma',
                                validators=[ExtensionValidator(['pdf'])], null=True, blank=True)
    is_completed = models.BooleanField(default=True)  

    def __str__(self):
        return f"{self.name}"

    def get_filename(self):
        return os.path.basename(str(self.diploma)) 


class Fixture(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="fixtures")    
    name = models.CharField(_("Fixture Name"), max_length=255)
    brand = models.CharField(_("Brand"), max_length=255)
    model = models.CharField(_("Model"), max_length=255)
    serial_number = models.CharField(_("Serial Number"), max_length=255)
    current_situtation = models.TextField(_("Current Situtation"), null=True, blank=True)

class Document(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="documents")    
    title = models.CharField(_("Document Title"), max_length=255)
    file = models.FileField(_("Document"), blank=False, null=False, upload_to='documents/hr/user_document' ,validators=[ExtensionValidator(['pdf'])])
    
    class Meta:
        unique_together = ('profile', 'title',)

    def __str__(self):
        return f"{self.profile.user}'s {self.title} file"

class Leave(models.Model):

    LEAVE_TYPE_CHOICES = (
        ("vacation", _("Vacation")),
        ("sick", _("Sick")),
        ("holiday", _("Holiday")),
        ("unpaid", _("Unpaid Leave")),
        ("other", _("Other")),
    )

    MONTH_CHOICES =(
        ("January",_("January")),("February",_("February")),("March",_("March")),("April",_("April")),("May",_("May")),("June",_("June")),("July",_("July")),("August",_("August")),("September",_("September")),("October",_("October")),("November",_("November")),("December",_("december"))

    )
    STATUS_CHOICES = (
       ("Accepted",_("Accepted")),("Pending",_("Pending")),("Canceled",_("Canceled"))
    )

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="leaves")
    leave_type = models.CharField(_("Leave Type"), max_length=8, default='other', choices=LEAVE_TYPE_CHOICES)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank = True)
    reason = models.CharField(max_length=200)
   
    status = models.CharField(max_length=10, choices= STATUS_CHOICES, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.profile.user.first_name} {self.profile.user.last_name} / {self.leave_type} / {self.start_date}-{self.end_date}"

    def get_start_date_day(self):
        return self.start_date.day

    def get_start_date_month(self):
        return self.start_date.month
    
    def get_start_date_year(self):
        return self.start_date.year

    def get_end_date_day(self):
        return self.end_date.day

    def get_end_date_month(self):
        return self.end_date.month
    
    def get_end_date_year(self):
        return self.end_date.year

