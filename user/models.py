import datetime
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timesince import timesince
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth import get_user_model

from django.utils import timezone

from user.utils import resize_image
from user.validators import ExtensionValidator

from administration.models import AccessAuthorization as AccessAuth
from administration.models import DataAuthorization as DataAuth

def cv_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.pk is None:
        return 'hr/user/temp/{0}/{1}'.format(instance.pk, "cv.pdf")
    else:
        return 'hr/user/{0}/documents/{1}'.format(instance.pk, "cv.pdf")

def nondisclosureAgreement_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.pk is None:
        return 'hr/user/temp/{0}/{1}'.format(instance.pk, "non-disclosure-agreement.pdf")
    else:
        return 'hr/user/{0}/documents/{1}'.format(instance.pk, "non-disclosure-agreement.pdf")

def contract_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    if instance.pk is None:
        return 'documents/user/temp/{0}/{1}'.format(instance.pk, filename)
    else:
        return 'documents/user/{0}/contract/{1}'.format(instance.pk, filename)

def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="unknown")[0]

class Notification(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="user_notification_source_company")
    message = models.CharField(max_length=100)
    
    def __str__(self):
        return self.message


class Team(models.Model):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="user_team_source_company")
    name = models.CharField(_("Name"), max_length=140, null=True, unique=True)
    about = models.TextField(_("About"), blank=True, null=True)
    members = models.ManyToManyField(User, related_name="team", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Department(models.Model):
    """
    Describes department info
    """
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="user_department_source_company")
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
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="employee_type_source_company")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True, related_name="employee_types")
    name = models.CharField(_("Name"), max_length=140, null=True, unique=True)
    about = models.TextField(_("About"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def get_objects_by_name(name):
        return EmployeeType.objects.filter(name__icontains=name.lower())
    
class Position(MPTTModel):
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="user_position_source_company")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True, related_name="positions")
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    POSITION_LEVELS = (
        ('1', _('1')),
        ('2', _('2')),
        ('3', _('3')),
        ('4', _('4')),
        ('5', _('5')),
    )
    position_level= models.CharField(max_length=50, choices=POSITION_LEVELS, null=True, blank=True)
    name = models.CharField(_("Name"), max_length=140, null=True, blank=True)
    about = models.TextField(_("About"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return str(self.name)


class AccessAuthorization(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="access_authorization_user")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    
    name = models.CharField(_("Name"), max_length=140, null=True, unique=True)
    code = models.CharField(_("Code"), max_length=140, null=True, unique=True)
    about = models.TextField(_("About"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"
    
class DataAuthorization(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="data_authorization_user")
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    
    name = models.CharField(_("Name"), max_length=140, null=True, unique=True)
    code = models.CharField(_("Code"), max_length=140, null=True, unique=True)
    about = models.TextField(_("About"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"

class Profile(models.Model):
    """
    This model represents the profile info of Internal Personals.
    """
    THEME_CHOICES = (('dark', _('Dark')), ('light', _('Light')))
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, blank=True)
    #user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(_("Image"), upload_to='images/profiles/', null=True, blank=True,
                              help_text=_("Please upload a square image, otherwise center will be cropped."))
    
    registrationNo = models.CharField(_("Registration Number"), max_length=50, blank=True, null=True)
    identificationNo = models.CharField(_("Identification Number"), max_length=50, blank=True, null=True)
    
    GENDERS = (
        ('female', _('Female')),
        ('male', _('Male')),
        ('other', _('Other')),
    )
    
    gender= models.CharField(max_length=50, choices=GENDERS, null=True, blank=True)
    birthday = models.DateField(_("Birthday"), blank=True, null=True)
    
    motherName = models.CharField(_("Mother Name"), max_length=50, blank=True, null=True)
    fatherName = models.CharField(_("Father Name"), max_length=50, blank=True, null=True)
    
    drivingLicence = models.CharField(_("Driving Licence"), max_length=50, blank=True, null=True)
    
    MILITARY_STATUSES = (
        ('postponed', _('Postponed')),
        ('completed', _('Completed')),
    )
    
    militaryStatus= models.CharField(max_length=50, choices=MILITARY_STATUSES, null=True, blank=True)
    militaryPostponedDate = models.DateField(_("Military Postponed Date"), blank=True, null=True)
    
    phone = models.CharField(_("Phone Number"), max_length=50, blank=True, null=True)
    address = models.TextField(_("Address"), blank=True, null=True)
    note = models.TextField(_("Note"), blank=True, null=True)
    
    criminalRegistrationNo = models.CharField(_("Criminal Registration Number"), max_length=50, blank=True, null=True)
    socialSecurityNo = models.CharField(_("Social Security Number"), max_length=50, blank=True, null=True)
    startDate = models.DateField(_("Date of start"), blank=True, null=True)
    socialSecuirtyStartDate = models.DateField(_("Date of social security start"), blank=True, null=True)
    professionCode = models.CharField(_("Profession Code"), max_length=50, blank=True, null=True)
    
    RETIREMENT_STATUSES = (
        ('not_retired', _('Not Retired')),
        ('retired', _('Retired')),
    )
    
    retirementStatus= models.CharField(max_length=50, choices=RETIREMENT_STATUSES, null=True, blank=True, default="not_retired")
    
    company = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="user_company", default=1)

    # twitter = models.URLField(blank=True, null=True)
    # facebook = models.URLField(blank=True, null=True)
    # instagram = models.URLField(blank=True, null=True)
    
    EDUCATION_LEVELS = (
        ('none', _('None')),
        ('primary_school', _('Primary School')),
        ('secondary_school', _('Secondary School')),
        ('high_school', _('High School')),
        ('college', _('College')),
        ('bachelors_degree', _("Bachelor's Degree")),
        ('masters_degree', _("Master's Degree")),
        ('phd', _("Ph.D.")),
    )
    education_level= models.CharField(max_length=50, choices=EDUCATION_LEVELS, default="none", blank=True)
    salary = models.FloatField(_("Salary"), default = 0, blank = True, null = True)
    salaryCurrency = models.ForeignKey("card.currency", on_delete=models.SET_DEFAULT, related_name = "salary_currency", default = 102, blank = True, null = True)
    iban = models.CharField(_("IBAN"), max_length=26, blank=True, null=True)
    
    degree = models.CharField(_("Degree"), max_length=100, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True, related_name="members")
    positionType = models.ForeignKey(Position, on_delete=models.SET_NULL, blank=True, null=True,related_name="positions")
    #employeeType = models.ForeignKey(EmployeeType, on_delete=models.SET_NULL, blank=True, null=True,related_name="members")
    position = models.CharField(_("Position"), max_length=140, blank=True, null=True)

    language = models.CharField(_("Language"), max_length=50, choices = settings.LANGUAGES, blank=True, default="tr")
    theme = models.CharField(_("Theme"), max_length=25, default='light', choices=THEME_CHOICES, blank=True, null=True)
    cardColor = models.CharField(_("Card Color"), max_length=25, default='#003865', blank=True, null=True)
    #bonus_right = models.BooleanField(_("Bonus Right"), default=False)
    cv = models.FileField(_("CV / Resume"), upload_to = cv_directory_path, null=True, blank=True,
                                 validators=[ExtensionValidator(['pdf', 'doc', 'docx'])])
    nondisclosureAgreement = models.FileField(_("Non-disclosure Agreement"), null=True, blank=True,
                                               upload_to = nondisclosureAgreement_directory_path,
                                               validators=[ExtensionValidator(['pdf', 'doc', 'docx'])])
    employmentContract = models.FileField(_("Employment Contract"), null=True, blank=True,
                                           upload_to = cv_directory_path,
                                            validators=[ExtensionValidator(['pdf', 'doc', 'docx'])])
    identityCard = models.FileField(_("Identity Card"), null=True, blank=True,
                                           upload_to = cv_directory_path,
                                            validators=[ExtensionValidator(['pdf', 'doc', 'docx'])])
    drivingLicenceCard = models.FileField(_("Driving Licence Card"), null=True, blank=True,
                                           upload_to = cv_directory_path,
                                            validators=[ExtensionValidator(['pdf', 'doc', 'docx'])])
    graduationDocument = models.FileField(_("Graduation Document"), null=True, blank=True,
                                           upload_to = cv_directory_path,
                                            validators=[ExtensionValidator(['pdf', 'doc', 'docx'])])
    # ssiStatementOfEmployment = models.FileField(_("SSI Statement of Employment"), null=True, blank=True,
    #                                                upload_to = contract_directory_path,
    #                                                validators=[ExtensionValidator(['pdf', 'doc', 'docx'])])
    
    sourceCompanyList = models.ManyToManyField('source.Company',related_name='source_company_list', blank = True)
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="source_company")
    
    accessAuthorization = models.ManyToManyField(AccessAuthorization,related_name='access_authorization', blank = True)
    dataAuthorization = models.ManyToManyField(DataAuthorization,related_name='data_authorization', blank = True)
    
    accessAuth = models.ManyToManyField(AccessAuth,related_name='access_auth', blank = True)
    dataAuth = models.ManyToManyField(DataAuth,related_name='data_auth', blank = True)
    
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



class Education(models.Model):
    """
    Stores the currency info
    """
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="user_education_source_company")
    educationProfile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank = True, null = True, related_name = "education_profile")
    user = models.ForeignKey("auth.User", on_delete=models.DO_NOTHING)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    school = models.CharField(_("School"), max_length=140, blank = True, null = True)
    department = models.CharField(_("Department"), max_length=140, blank = True, null = True)
    EDUCATION_STATUSES = (
        ('ongoing', _('Ongoing')),
        ('graduated', _('Graduated')),
    )
    education_status= models.CharField(max_length=50, choices=EDUCATION_STATUSES, default="graduated", blank=True)
    startDate = models.DateField(_("Start Date"), default = timezone.now, blank = True)
    finishDate = models.DateField(_("Finish Date"), default = timezone.now, blank = True)

    def __str__(self):
        return str(self.school)

    class Meta:
        ordering = ['school']
        
class AdditionalPayment(models.Model):
    """
    Stores the currency info
    """
    sourceCompany = models.ForeignKey('source.Company', on_delete=models.SET_NULL, blank=True, null=True, related_name="user_additional_source_company")
    additionalPaymentProfile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank = True, null = True, related_name = "additional_payment_profile")
    user = models.ForeignKey("auth.User", on_delete=models.DO_NOTHING)
    sessionKey = models.CharField(_("Session Key"), max_length=140, blank = True, null = True)
    amount = models.FloatField(_("Amount"), default = 0, blank = True, null = True)
    currency = models.ForeignKey("card.currency", on_delete=models.SET_DEFAULT, related_name = "additional_payment_currency", default = 102, blank = True, null = True)
    PAYMENT_TYPES = (
        ('bonus', _('Bonus')),
        ('expense', _('Expense')),
        ('overtime', _('Overtime')),
    )
    payment_type= models.CharField(max_length=50, choices=PAYMENT_TYPES, default="graduated", blank=True)
    additionalPaymentDate = models.DateField(_("Date"), default = timezone.now, blank = True)

    def __str__(self):
        return str(self.additionalPaymentProfile)

    class Meta:
        ordering = ['additionalPaymentProfile']

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
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="records")
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
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name="certifications")    
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
