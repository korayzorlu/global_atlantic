from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction

# Create your views here.
from django.views import View

from beta_hr.forms import DocumentAddForm, TitleAddForm, UserCreateForm, ProfileAddForm, UserEditForm, EmployeeTypeAddForm, TeamAddForm, DepartmentAddForm, \
    TheCompanyForm, BankAccountAddForm,CertifcationAddForm
from beta_hr.models import TheCompany, BankAccount
from beta_profile.models import Document, EmployeeType, Profile, Team, Department, Record, Title


class UserDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'hr/user/user_data.html', context)


class EmployeeTypeDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'hr/employee_type/employee_type_data.html', context)


class TeamDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'hr/team/team_data.html', context)


class DepartmentDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'hr/department/department_data.html', context)


class RecordDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'admin/record/record_data.html', context)

class TitleDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'hr/title/title_data.html', context)

class DocumentDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'hr/document/document_data.html', context)

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


class UserAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_create_form = UserCreateForm()
        profile_add_form = ProfileAddForm()
        context = {
            'user_create_form': user_create_form,
            'profile_add_form': profile_add_form
        }
        return render(request, 'hr/user/user_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        default_password = "Micho.2021"  # this may be random in the future and it will send to the email
        user_create_form = UserCreateForm(request.POST, default_password=default_password)
        profile_add_form = ProfileAddForm(request.POST, request.FILES)
        if user_create_form.is_valid() and profile_add_form.is_valid():
            with transaction.atomic():
                user = user_create_form.save()
                for key, value in profile_add_form.cleaned_data.items():
                    setattr(user.beta_profile, key, value)
                user.beta_profile.save()

            # adding to manytomany objects
            user.team.set(user_create_form.cleaned_data.get('team', []))

            # if auto generated password applied send mail to user / in the future
            if user_create_form.set_default_password:
                # print("auto-generated")
                pass

            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:user_detail", user.pk)
        else:
            context = {
                'user_create_form': user_create_form,
                'profile_add_form': profile_add_form
            }
            return render(request, 'hr/user/user_add.html', context)


class UserEditView(LoginRequiredMixin, View):
    def get(self, request, user_id, *args, **kwargs):
        user = get_object_or_404(User, pk=user_id)
        # initials for custom fields
        initial = {
            'team': user.team.values_list('pk', flat=True),
        }
        user_edit_form = UserEditForm(instance=user, initial=initial)
        profile_edit_form = ProfileAddForm(instance=user.beta_profile)
        context = {
            'user_edit_form': user_edit_form,
            'profile_edit_form': profile_edit_form
        }
        return render(request, 'hr/user/user_edit.html', context)

    def post(self, request, user_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        user = get_object_or_404(User, pk=user_id)
        user_edit_form = UserEditForm(request.POST, instance=user)
        profile_edit_form = ProfileAddForm(request.POST, request.FILES, instance=user.beta_profile)
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

    def get(self, request, user_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        user = get_object_or_404(User, pk=user_id)
        if user == request.user:
            logout(request)
        user.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("hr:user_data")


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


class TeamAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        team_add_form = TeamAddForm()
        context = {
            'team_add_form': team_add_form,
        }
        return render(request, 'hr/team/team_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        team_add_form = TeamAddForm(request.POST)
        if team_add_form.is_valid():
            team = team_add_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:team_detail", team.id)
        else:
            context = {
                'team_add_form': team_add_form,
            }
            return render(request, 'hr/team/team_add.html', context)


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

    def get(self, request, team_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        team = get_object_or_404(Team, pk=team_id)
        team.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("hr:team_data")


class DepartmentAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        department_add_form = DepartmentAddForm()
        context = {
            'department_add_form': department_add_form,
        }
        return render(request, 'hr/department/department_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        department_add_form = DepartmentAddForm(request.POST)
        if department_add_form.is_valid():
            department = department_add_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:department_detail", department.id)
        else:
            context = {
                'department_add_form': department_add_form,
            }
            return render(request, 'hr/department/department_add.html', context)


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

    def get(self, request, department_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        department = get_object_or_404(Department, pk=department_id)
        department.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("hr:department_data")


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

class TitleAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        title_add_form = TitleAddForm()
        context = {
            'title_add_form': title_add_form,
        }
        return render(request, 'hr/title/title_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        title_add_form = TitleAddForm(request.POST)
        if title_add_form.is_valid():
            title = title_add_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:title_detail", title.id)
        else:
            context = {
                'title_add_form': title_add_form,
            }
            return render(request, 'hr/title/title_add.html', context)


class TitleDetailView(LoginRequiredMixin, View):
    def get(self, request, title_id, *args, **kwargs):
        title = get_object_or_404(Title, pk=title_id)
        context = {
            'title': title,
        }
        return render(request, 'hr/title/title_detail.html', context)


class TitleEditView(LoginRequiredMixin, View):
    def get(self, request, title_id, *args, **kwargs):
        title = get_object_or_404(Title, pk=title_id)
        title_edit_form = TitleAddForm(instance=title)
        context = {
            'title_edit_form': title_edit_form,
        }
        return render(request, 'hr/title/title_edit.html', context)

    def post(self, request, title_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        title = get_object_or_404(Title, pk=title_id)
        title_edit_form = TitleAddForm(request.POST, instance=title)
        if title_edit_form.is_valid():
            title = title_edit_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:title_detail", title.id)
        else:
            context = {
                'title_edit_form': title_edit_form,
            }
            return render(request, 'hr/title/title_edit.html', context)


class TitleDeleteView(LoginRequiredMixin, View):
    """
    Deletes title permanently
    """

    def get(self, request, title_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        title = get_object_or_404(Title, pk=title_id)
        title.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("hr:title_data")

class DocumentAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        document_add_form = DocumentAddForm()
        context = {
            'document_add_form': document_add_form,
        }
        return render(request, 'hr/document/document_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        document_add_form = DocumentAddForm(request.POST)
        if document_add_form.is_valid():
            document = document_add_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:document_detail", document.id)
        else:
            context = {
                'document_add_form': document_add_form,
            }
            return render(request, 'hr/document/document_add.html', context)


class DocumentDetailView(LoginRequiredMixin, View):
    def get(self, request, document_id, *args, **kwargs):
        document = get_object_or_404(Document, pk=document_id)
        context = {
            'document': document,
        }
        return render(request, 'hr/document/document_detail.html', context)


class DocumentEditView(LoginRequiredMixin, View):
    def get(self, request, document_id, *args, **kwargs):
        document = get_object_or_404(Document, pk=document_id)
        document_edit_form = DocumentAddForm(instance=document)
        context = {
            'document_edit_form': document_edit_form,
        }
        return render(request, 'hr/document/document_edit.html', context)

    def post(self, request, document_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        document = get_object_or_404(Document, pk=document_id)
        document_edit_form = DocumentAddForm(request.POST, instance=document)
        if document_edit_form.is_valid():
            document = document_edit_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("hr:document_detail", document.id)
        else:
            context = {
                'document_edit_form': document_edit_form,
            }
            return render(request, 'hr/document/document_edit.html', context)


class DocumentDeleteView(LoginRequiredMixin, View):
    """
    Deletes document permanently
    """

    def get(self, request, document_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        document = get_object_or_404(Document, pk=document_id)
        document.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("hr:document_data")
