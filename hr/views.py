from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from urllib.parse import urlparse

from django.contrib import messages

# Create your views here.
from django.views import View

from hr.forms import UserCreateForm, ProfileAddForm, UserEditForm, EmployeeTypeAddForm, TeamAddForm, DepartmentAddForm, \
    TheCompanyForm, BankAccountAddForm,CertifcationAddForm, DepartmentForm, TeamForm, UserForm, ProfileForm, UserUpdateForm, EducationForm, AdditionalPaymentForm
from hr.models import TheCompany, BankAccount
from user.models import EmployeeType, Profile, Team, Department, Record, Education, AdditionalPayment
from source.models import Company as SourceCompany

import random
import string



class EmployeeTypeDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'hr/employee_type/employee_type_data.html', context)

class RecordDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'admin/record/record_data.html', context)

class TheCompanyDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        the_company = get_object_or_404(TheCompany, pk=1)
        bank_account_add_form = BankAccountAddForm()
        context = {
            'the_company': the_company,
            'bank_account_add_form': bank_account_add_form
        }
        return render(request, 'admin/the_company/the_company_detail.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        the_company = get_object_or_404(TheCompany, pk=1)
        bank_account_add_form = BankAccountAddForm(request.POST)

        if bank_account_add_form.is_valid():
            bank_account = bank_account_add_form.save(commit=False)
            bank_account.sourceCompany = request.user.profile.sourceCompany
            bank_account.the_company = the_company
            bank_account.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:the_company_detail")
        else:
            context = {
                'the_company': the_company,
                'bank_account_add_form': bank_account_add_form,
            }
            return render(request, 'admin/the_company/the_company_detail.html', context)


class BankAccountDeleteView(LoginRequiredMixin, View):
    def post(self, request, bank_account_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        bank_account = get_object_or_404(BankAccount, pk=bank_account_id)
        bank_account.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("hr:the_company_detail")


class TheCompanyEditView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        the_company = get_object_or_404(TheCompany, pk=1)
        the_company_edit_form = TheCompanyForm(instance=the_company)
        context = {
            'the_company_edit_form': the_company_edit_form,
        }
        return render(request, 'admin/the_company/the_company_edit.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        the_company = get_object_or_404(TheCompany, pk=1)
        the_company_edit_form = TheCompanyForm(request.POST, request.FILES, instance=the_company)

        if the_company_edit_form.is_valid():
            the_company = the_company_edit_form.save(commit=False)
            the_company.updated_by = request.user
            the_company.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:the_company_detail")
        else:
            context = {
                'the_company_edit_form': the_company_edit_form,
            }
            return render(request, 'admin/the_company/the_company_edit.html', context)

class UserDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Employees")
        elementTag = "user"
        elementTagSub = "userPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'hr/user/users.html', context)

class UserAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add User")
        elementTag = "user"
        elementTagSub = "userPart"
        elementTagId = "new"
        
        educations = Education.objects.filter(user = request.user, educationProfile__isnull=True)
        for education in educations:
            education.delete()
        
        userForm = UserForm(request.POST or None, request.FILES or None)
        profileForm = ProfileForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "userForm" : userForm,
                "profileForm" : profileForm
        }
        return render(request, 'hr/user/user_add.html', context)
    
    def post(self, request, *args, **kwargs):
        userForm = UserForm(request.POST or None, request.FILES or None)
        profileForm = ProfileForm(request.POST or None, request.FILES or None)
        if userForm.is_valid() and profileForm.is_valid():
            username = userForm.cleaned_data.get("username")
            first_name = userForm.cleaned_data.get("first_name")
            last_name = userForm.cleaned_data.get("last_name")
            email = userForm.cleaned_data.get("email")
            password = userForm.cleaned_data.get("password")

            user = User(username = username, first_name = first_name, last_name = last_name, email = email)
            user.set_password(password)
            user.save()
            
            profile = profileForm.save(commit = False)
            profile.sourceCompany = request.user.profile.sourceCompany
            profile.user = user
            profile.save()
            
            print(profile.department.name)
            if profile.department.name == "Sales":
                user.groups.add(Group.objects.get(name="sales"))
            
            
            
            return HttpResponse(status=204)
        else:
            context = {
                    "userForm" : userForm,
                    "profileForm" : profileForm
            }
            print(userForm.errors)
            print(profileForm.errors)
            return render(request, 'hr/user/user_add.html', context)

# class UserAddView(LoginRequiredMixin, View):
#     def get(self, request, *args, **kwargs):
#         user_create_form = UserCreateForm()
#         profile_add_form = ProfileAddForm()
#         context = {
#             'user_create_form': user_create_form,
#             'profile_add_form': profile_add_form
#         }
#         return render(request, 'hr/user/user_add.html', context)

#     def post(self, request, *args, **kwargs):
#         next_url = request.POST.get('next', request.GET.get('next'))
#         default_password = "Micho.2021"  # this may be random in the future and it will send to the email
#         user_create_form = UserCreateForm(request.POST, default_password=default_password)
#         profile_add_form = ProfileAddForm(request.POST, request.FILES)
#         if user_create_form.is_valid() and profile_add_form.is_valid():
#             with transaction.atomic():
#                 user = user_create_form.save()
#                 for key, value in profile_add_form.cleaned_data.items():
#                     setattr(user.profile, key, value)
#                 user.profile.save()

#             # adding to manytomany objects
#             user.team.set(user_create_form.cleaned_data.get('team', []))

#             # if auto generated password applied send mail to user / in the future
#             if user_create_form.set_default_password:
#                 # print("auto-generated")
#                 pass

#             if next_url:
#                 # if next url exist
#                 return HttpResponseRedirect(next_url)
#             else:
#                 # to prevent refresh that sends post data again.
#                 return redirect("hr:user_detail", user.pk)
#         else:
#             context = {
#                 'user_create_form': user_create_form,
#                 'profile_add_form': profile_add_form
#             }
#             return render(request, 'hr/user/user_add.html', context)

class UserUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("User Detail")
        elementTag = "user"
        elementTagSub = "userPart"
        elementTagId = id
        
        users = User.objects.filter()
        profiles = Profile.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        user = get_object_or_404(User, id = id)
        profile = get_object_or_404(Profile, user = user)
        userForm = UserForm(request.POST or None, request.FILES or None, instance = user)
        profileForm = ProfileForm(request.POST or None, request.FILES or None, instance = profile)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "userForm" : userForm,
                "users" : users,
                "user" : user,
                "profileForm" : profileForm,
                "profiles" : profiles,
                "profile" : profile
        }
        return render(request, 'hr/user/user_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        users = User.objects.filter()
        user = get_object_or_404(User, id = id)
        emails = User.objects.filter(email = user.email)
        profile = get_object_or_404(Profile, user = user)
        sourceCompany = profile.sourceCompany
        userForm = UserUpdateForm(request.POST, request.FILES or None, instance = user)
        profileForm = ProfileForm(request.POST or None, request.FILES or None, instance = profile)
        if userForm.is_valid() and profileForm.is_valid():
            username = userForm.cleaned_data.get("username")
            first_name = userForm.cleaned_data.get("first_name")
            last_name = userForm.cleaned_data.get("last_name")
            email = userForm.cleaned_data.get("email")
            
            currentUsername = user.username
            currentEmail = user.email
            
            for a in users:
                if str(a) == username and str(a) != currentUsername:
                    messages.info(request, "Already registered with this username!")

            for a in emails:
                if str(a.email) == email and str(a.email) != currentEmail:
                    messages.info(request, "Already registered with this email address!")

            
            user = userForm.save(commit = False)
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            
            profile = profileForm.save(commit = False)
            profile.user = user
            profile.nondisclosureAgreement = request.FILES.get("nondisclosureAgreementUploadName")
            profile.employmentContract = request.FILES.get("employmentContractUploadName")
            profile.cv = request.FILES.get("cvUploadName")
            profile.identityCard = request.FILES.get("identityCardUploadName")
            profile.drivingLicenceCard = request.FILES.get("drivingLicenceCardUploadName")
            profile.sourceCompany = sourceCompany
            profile.save()
            
            return HttpResponse(status=204)
        else:
            print(userForm.errors)
            print(profileForm.errors)
            context = {
                    "userForm" : userForm,
                    "profileForm" : profileForm
            }
            return render(request, 'hr/user/user_detail.html', context)

class UserCVPdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("CV PDF")
        
        elementTag = "user"
        elementTagSub = "userPart"
        elementTagId = str(id) + "-cv-pdf"
        
        user = get_object_or_404(User, id = id)
        profile = get_object_or_404(Profile, user = user)
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #inquiryPdf(inquiry)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "user" : user,
                "profile" : profile,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'hr/user/pdf/cv_pdf.html', context)
    
class UserNDAPdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("NDA PDF")
        
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'hr/user/pdf/check_pin.html', context)
    
    def post(self, request, id, *args, **kwargs):
        tag = _("NDA PDF")
        
        elementTag = "user"
        elementTagSub = "userPart"
        elementTagId = str(id) + "-nda-pdf"
        
        user = get_object_or_404(User, id = id)
        profile = get_object_or_404(Profile, user = user)
        
        print(request.POST.get("userDocumentPin"))
        
        if request.POST.get("userDocumentPin") == "786723":
            characters = string.ascii_letters + string.digits
            version = ''.join(random.choice(characters) for _ in range(10))
            
            #inquiryPdf(inquiry)
            
            context = {
                    "tag": tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "elementTagId" : elementTagId,
                    "user" : user,
                    "profile" : profile,
                    "version" : version
            }
            
            #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
            refererPath = urlparse(request.META.get("HTTP_REFERER")).path
            if str(refererPath) == "b''":
                return redirect("/user/")

            return render(request, 'hr/user/pdf/nda_pdf.html', context)
        else:
            return render(request, 'hr/user/pdf/check_pin.html', context)
    
class UserDocumentDeleteView(LoginRequiredMixin, View):
    """
    Deletes user permanently
    """

    def get(self, request, list, *args, **kwargs):
        tag = _("Delete User")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        return render(request, 'hr/user/user_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:   
            user = get_object_or_404(User, id = int(id))
            user.delete()
        return HttpResponse(status=204)

class UserEditView(LoginRequiredMixin, View):
    def get(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, pk=user_id)
        # initials for custom fields
        initial = {
            'team': user.team.values_list('pk', flat=True),
        }
        user_edit_form = UserEditForm(instance=user, initial=initial)
        print(user.profile)
        profile_edit_form = ProfileAddForm(instance=user.profile)
        context = {
            'user_edit_form': user_edit_form,
            'profile_edit_form': profile_edit_form
        }
        return render(request, 'hr/user/user_edit.html', context)

    def post(self, request, user_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        user = get_object_or_404(User, pk=user_id)
        user_edit_form = UserEditForm(request.POST, instance=user)
        profile_edit_form = ProfileAddForm(request.POST, request.FILES, instance=user.profile)
        if user_edit_form.is_valid() and profile_edit_form.is_valid():
            user = user_edit_form.save()
            profile_edit_form.save()
            user.team.set(user_edit_form.cleaned_data.get('team', []))
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:user_detail", user.id)
        else:
            context = {
                'user': user,
                'user_edit_form': user_edit_form,
                'profile_edit_form': profile_edit_form
            }
            return render(request, 'hr/user/user_edit.html', context)


class UserDetailView(LoginRequiredMixin, View):
    def get(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, pk=user_id)
        certification_add_form = CertifcationAddForm()

        context = {
            'user': user,
            'certification_add_form':certification_add_form
        }
        return render(request, 'hr/user/user_detail.html', context)


class UserDeleteView(LoginRequiredMixin, View):
    """
    Deletes user permanently
    """

    def get(self, request, list, *args, **kwargs):
        tag = _("Delete User")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        return render(request, 'hr/user/user_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:   
            user = get_object_or_404(User, id = int(id))
            user.delete()
        return HttpResponse(status=204)


class EmployeeTypeAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        employee_type_add_form = EmployeeTypeAddForm()
        context = {
            'employee_type_add_form': employee_type_add_form,
        }
        return render(request, 'hr/employee_type/employee_type_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        employee_type_add_form = EmployeeTypeAddForm(request.POST)
        if employee_type_add_form.is_valid():
            employee_type = employee_type_add_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:employee_type_detail", employee_type.id)
        else:
            context = {
                'employee_type_add_form': employee_type_add_form,
            }
            return render(request, 'hr/employee_type/employee_type_add.html', context)


class EmployeeTypeDetailView(LoginRequiredMixin, View):
    def get(self, request, employee_type_id, *args, **kwargs):
        employee_type = get_object_or_404(EmployeeType, pk=employee_type_id)
        context = {
            'employee_type': employee_type,
        }
        return render(request, 'hr/employee_type/employee_type_detail.html', context)


class EmployeeTypeEditView(LoginRequiredMixin, View):
    def get(self, request, employee_type_id, *args, **kwargs):
        employee_type = get_object_or_404(EmployeeType, pk=employee_type_id)
        employee_type_edit_form = EmployeeTypeAddForm(instance=employee_type)
        context = {
            'employee_type_edit_form': employee_type_edit_form,
        }
        return render(request, 'hr/employee_type/employee_type_edit.html', context)

    def post(self, request, employee_type_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        employee_type = get_object_or_404(EmployeeType, pk=employee_type_id)
        employee_type_edit_form = EmployeeTypeAddForm(request.POST, instance=employee_type)
        if employee_type_edit_form.is_valid():
            employee_type = employee_type_edit_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:employee_type_detail", employee_type.id)
        else:
            context = {
                'employee_type_edit_form': employee_type_edit_form,
            }
            return render(request, 'hr/employee_type/employee_type_edit.html', context)


class EmployeeTypeDeleteView(LoginRequiredMixin, View):
    """
    Deletes employee type permanently
    """

    def get(self, request, employee_type_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        employee_type = get_object_or_404(EmployeeType, pk=employee_type_id)
        employee_type.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("hr:employee_type_data")

class TeamDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Teams")
        elementTag = "team"
        elementTagSub = "teamPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'hr/team/teams.html', context)

class TeamAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Team")
        elementTag = "team"
        elementTagSub = "teamtPart"
        elementTagId = "new"
        
        form = TeamForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form
        }
        return render(request, 'hr/team/team_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = TeamForm(request.POST, request.FILES or None)
        if form.is_valid():
            team = form.save()
            team.sourceCompany = request.user.profile.sourceCompany
            team.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            print(form.errors)
            return render(request, 'hr/team/team_add.html', context)

class TeamUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Team Detail")
        elementTag = "team"
        elementTagSub = "teamPart"
        elementTagId = id
        
        teams = Team.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        team = get_object_or_404(Team, id = id)
        form = TeamForm(request.POST or None, request.FILES or None, instance = team)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "teams" : teams,
                "team" : team
        }
        return render(request, 'hr/team/team_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        team = get_object_or_404(Team, id = id)
        sourceCompany = team.sourceCompany
        form = TeamForm(request.POST, request.FILES or None, instance = team)
        if form.is_valid():
            team = form.save(commit = False)
            team.sourceCompany = sourceCompany
            team.save()
            
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'hr/team/team_detail.html', context)

class TeamDetailView(LoginRequiredMixin, View):
    def get(self, request, team_id, *args, **kwargs):
        team = get_object_or_404(Team, pk=team_id)
        context = {
            'team': team,
        }
        return render(request, 'hr/team/team_detail.html', context)


class TeamEditView(LoginRequiredMixin, View):
    def get(self, request, team_id, *args, **kwargs):
        team = get_object_or_404(Team, pk=team_id)
        team_edit_form = TeamAddForm(instance=team)
        context = {
            'team_edit_form': team_edit_form,
        }
        return render(request, 'hr/team/team_edit.html', context)

    def post(self, request, team_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        team = get_object_or_404(Team, pk=team_id)
        team_edit_form = TeamAddForm(request.POST, instance=team)
        if team_edit_form.is_valid():
            team = team_edit_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:team_detail", team.id)
        else:
            context = {
                'team_edit_form': team_edit_form,
            }
            return render(request, 'hr/team/team_edit.html', context)


class TeamDeleteView(LoginRequiredMixin, View):
    """
    Deletes team permanently
    """

    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Team")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        return render(request, 'hr/team/team_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:   
            team = get_object_or_404(Team, id = int(id))
            team.delete()
        return HttpResponse(status=204)

class DepartmentDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Departments")
        elementTag = "department"
        elementTagSub = "departmentPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'hr/department/departments.html', context)

class DepartmentAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Department")
        elementTag = "department"
        elementTagSub = "departmentPart"
        elementTagId = "new"
        
        form = DepartmentForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form
        }
        return render(request, 'hr/department/department_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = DepartmentForm(request.POST, request.FILES or None)
        if form.is_valid():
            department = form.save(commit = False)
            department.sourceCompany = request.user.profile.sourceCompany
            department.save()
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=404)
        
class DepartmentUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Department Detail")
        elementTag = "department"
        elementTagSub = "departmentPart"
        elementTagId = id
        
        departments = Department.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        department = get_object_or_404(Department, id = id)
        form = DepartmentForm(request.POST or None, request.FILES or None, instance = department)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "departments" : departments,
                "department" : department
        }
        return render(request, 'hr/department/department_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        department = get_object_or_404(Department, id = id)
        sourceCompany = department.sourceCompany
        form = DepartmentForm(request.POST, request.FILES or None, instance = department)
        if form.is_valid():
            department = form.save(commit = False)
            department.sourceCompany = sourceCompany
            department.save()
            
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'hr/department/department_detail.html', context)


class DepartmentDetailView(LoginRequiredMixin, View):
    def get(self, request, department_id, *args, **kwargs):
        department = get_object_or_404(Department, pk=department_id)
        context = {
            'department': department,
        }
        return render(request, 'hr/department/department_detail.html', context)


class DepartmentEditView(LoginRequiredMixin, View):
    def get(self, request, department_id, *args, **kwargs):
        department = get_object_or_404(Department, pk=department_id)
        department_edit_form = DepartmentAddForm(instance=department)
        context = {
            'department_edit_form': department_edit_form,
        }
        return render(request, 'hr/department/department_edit.html', context)

    def post(self, request, department_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        department = get_object_or_404(Department, pk=department_id)
        department_edit_form = DepartmentAddForm(request.POST, instance=department)
        if department_edit_form.is_valid():
            department = department_edit_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:department_detail", department.id)
        else:
            context = {
                'department_edit_form': department_edit_form,
            }
            return render(request, 'hr/department/department_edit.html', context)


class DepartmentDeleteView(LoginRequiredMixin, View):
    """
    Deletes department permanently
    """

    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Department")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        return render(request, 'hr/department/department_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:   
            department = get_object_or_404(Department, id = int(id))
            department.delete()
        return HttpResponse(status=204)

class OrganizationChartDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Organization Chart")
        elementTag = "organizationChart"
        elementTagSub = "organizationChartPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'hr/organization_chart/organization_chart.html', context)

class EducationAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Education")
        elementTagSub = "userEducation"
        
        form = EducationForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "form" : form
        }
        return render(request, 'hr/user/education_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = EducationForm(request.POST, request.FILES or None)
        if form.is_valid():
            education = form.save(commit = False)
            education.sourceCompany = request.user.profile.sourceCompany
            education.user = request.user
            education.sessionKey = request.session.session_key
            education.save()
            return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=404)

class EducationInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Education")
        elementTag = "education"
        elementTagSub = "educationPart"
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        profileId = refererPath.replace("/hr/user_update/","").replace("/","")
        profile = get_object_or_404(Profile, pk = id)
        
        form = EducationForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "profile" : profile,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'hr/user/education_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        profileId = refererPath.replace("/hr/user_update/","").replace("/","")
        
        profile = Profile.objects.get(pk = id)
        educations = Education.objects.filter(sourceCompany = request.user.profile.sourceCompany,educationProfile = profile)
        
        form = EducationForm(request.POST, request.FILES or None)
        if form.is_valid():
            education = form.save(commit = False)
            education.sourceCompany = request.user.profile.sourceCompany
            
            education.user = request.user
            education.educationProfile = profile
            education.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form,
                    "profileId" : profileId
            }
            return render(request, 'hr/user/education_add_in_detail.html', context)

class EducationDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Education")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'hr/user/education_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            education = get_object_or_404(Education, id = int(id))
            education.delete()
        return HttpResponse(status=204)

class AdditionalPaymentInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Additional Payment")
        elementTag = "additionalPayemnt"
        elementTagSub = "additionalPayemntPart"
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        profileId = refererPath.replace("/hr/user_update/","").replace("/","")
        profile = get_object_or_404(Profile, pk = id)
        
        form = AdditionalPaymentForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "profile" : profile,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'hr/user/additional_payment_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        profileId = refererPath.replace("/hr/user_update/","").replace("/","")
        
        profile = Profile.objects.get(pk = id)
        additionalPayments = AdditionalPayment.objects.filter(sourceCompany = request.user.profile.sourceCompany,additionalPaymentProfile = profile)
        
        form = AdditionalPaymentForm(request.POST, request.FILES or None)
        if form.is_valid():
            additionalPayment = form.save(commit = False)
            additionalPayment.sourceCompany = request.user.profile.sourceCompany
            
            additionalPayment.user = request.user
            additionalPayment.additionalPaymentProfile = profile
            additionalPayment.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form,
                    "profileId" : profileId
            }
            return render(request, 'hr/user/additional_payment_add_in_detail.html', context)

class RecordDetailView(LoginRequiredMixin, View):
    def get(self, request, record_id, *args, **kwargs):
        record = get_object_or_404(Record, pk=record_id)
        context = {
            'record': record,
        }
        return render(request, 'hr/record/record_detail.html', context)
    
    
class CertificationAddView(LoginRequiredMixin, View):
    # def get(self, request, *args, **kwargs):
    #     certification_add_form = CertifcationAddForm()
        
    #     context = {
    #         'certification_add_form': certification_add_form
    #     }
    #     return render(request, 'hr/user/user_add.html', context)

    def post(self, request, profile_id, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=profile_id)
        certification_add_form = CertifcationAddForm(request.POST,request.FILES)
        if certification_add_form.is_valid():
            certification = certification_add_form.save(commit=False)
            certification.profile = profile
            certification.save()           
            return redirect("hr:user_detail", profile.id)
        else:
            context = {
                'certification_add_form': certification_add_form,
            }
            return render(request, 'hr/user/user_detail.html', context)
