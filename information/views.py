from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.views import View

from information.forms import CompanyAddForm, ContactAddForm, VesselAddForm
from information.helpers import get_image_file_by_url
from information.models import Company, Contact, Vessel


class CustomerDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'information/customer/customer_data.html', context)


class SupplierDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'information/supplier/supplier_data.html', context)


class VesselDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'information/vessel/vessel_data.html', context)


class ContactDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'information/contact/contact_person_data.html', context)


class CompanyAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        default_company_type = request.POST.get('company_type', request.GET.get('company_type'))
        company_add_form = CompanyAddForm(initial={'company_type': default_company_type})
        context = {
            'company_add_form': company_add_form,
        }
        return render(request, 'information/company/company_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        company_add_form = CompanyAddForm(request.POST)
        if company_add_form.is_valid():
            company = company_add_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("information:company_detail", company.id)
        else:
            context = {
                'company_add_form': company_add_form,
            }
            return render(request, 'information/company/company_add.html', context)


class CompanyDetailView(LoginRequiredMixin, View):
    def get(self, request, company_id, *args, **kwargs):
        company = get_object_or_404(Company, pk=company_id)
        context = {
            'company': company
        }
        return render(request, 'information/company/company_detail.html', context)


class CompanyEditView(LoginRequiredMixin, View):
    def get(self, request, company_id, *args, **kwargs):
        company = get_object_or_404(Company, pk=company_id)
        company_edit_form = CompanyAddForm(instance=company)
        context = {
            'company_edit_form': company_edit_form,
        }
        return render(request, 'information/company/company_edit.html', context)

    def post(self, request, company_id, *args, **kwargs):
        company = get_object_or_404(Company, pk=company_id)
        company_edit_form = CompanyAddForm(request.POST, instance=company)
        if company_edit_form.is_valid():
            company = company_edit_form.save()
            # to prevent refresh that sends post data again.
            return redirect("information:company_detail", company.id)
        else:
            context = {
                'company_edit_form': company_edit_form,
            }
            return render(request, 'information/company/company_edit.html', context)


class CompanyDeleteView(LoginRequiredMixin, View):
    def get(self, request, company_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        company = get_object_or_404(Company, pk=company_id)
        company.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("dashboard")


class ContactAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        default_company = request.POST.get('company', request.GET.get('company'))
        contact_add_form = ContactAddForm(initial={'company': default_company})
        context = {
            'contact_add_form': contact_add_form,
        }
        return render(request, 'information/contact/contact_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        contact_add_form = ContactAddForm(request.POST)
        if contact_add_form.is_valid():
            contact = contact_add_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("information:contact_detail", contact.id)
        else:
            context = {
                'contact_add_form': contact_add_form,
            }
            return render(request, 'information/contact/contact_add.html', context)


class ContactEditView(LoginRequiredMixin, View):
    def get(self, request, contact_id, *args, **kwargs):
        contact = get_object_or_404(Contact, pk=contact_id)
        contact_edit_form = ContactAddForm(instance=contact)
        context = {
            'contact_edit_form': contact_edit_form,
        }
        return render(request, 'information/contact/contact_edit.html', context)

    def post(self, request, contact_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        contact = get_object_or_404(Contact, pk=contact_id)
        contact_edit_form = ContactAddForm(request.POST, instance=contact)
        if contact_edit_form.is_valid():
            contact = contact_edit_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("information:contact_detail", contact.id)
        else:
            context = {
                'contact_edit_form': contact_edit_form,
            }
            return render(request, 'information/contact/contact_edit.html', context)


class ContactDetailView(LoginRequiredMixin, View):
    def get(self, request, contact_id, *args, **kwargs):
        contact = get_object_or_404(Contact, pk=contact_id)
        context = {
            'contact': contact,
        }
        return render(request, 'information/contact/contact_detail.html', context)


class ContactDeleteView(LoginRequiredMixin, View):
    """
    Deletes contact permanently
    """

    def get(self, request, contact_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        contact = get_object_or_404(Contact, pk=contact_id)
        contact.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("information:contact_person_data")


class ContactRemoveView(LoginRequiredMixin, View):
    """
    Removes contact from that company (removes company from contact's company list)
    Contact protected
    """

    def get(self, request, contact_id, company_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        contact = get_object_or_404(Contact, pk=contact_id)
        company = get_object_or_404(Company, pk=company_id)
        if get_object_or_404(contact.company, pk=company.pk):
            contact.company.remove(company)
        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("information:company_detail", company.id)


class VesselAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        default_manager_company = request.POST.get('manager_company', request.GET.get('manager_company'))
        default_owner_company = request.POST.get('owner_company', request.GET.get('owner_company'))
        initial = {'manager_company': default_manager_company, 'owner_company': default_owner_company}
        vessel_add_form = VesselAddForm(initial=initial)
        context = {
            'vessel_add_form': vessel_add_form,
        }
        return render(request, 'information/vessel/vessel_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        flag_url = request.POST.get("flag_url")
        vessel_add_form = VesselAddForm(request.POST)
        if vessel_add_form.is_valid():
            vessel = vessel_add_form.save(commit=False)
            if flag_url:
                vessel.flag = get_image_file_by_url(flag_url)
            vessel.save()
            # https://stackoverflow.com/a/50384606/14506165
            vessel_add_form.save_m2m()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("information:vessel_detail", vessel.id)
        else:
            context = {
                'vessel_add_form': vessel_add_form,
            }
            return render(request, 'information/vessel/vessel_add.html', context)


class VesselEditView(LoginRequiredMixin, View):
    def get(self, request, vessel_id, *args, **kwargs):
        vessel = get_object_or_404(Vessel, pk=vessel_id, status="available")
        vessel_edit_form = VesselAddForm(instance=vessel)
        context = {
            'vessel_edit_form': vessel_edit_form,
        }
        return render(request, 'information/vessel/vessel_edit.html', context)

    def post(self, request, vessel_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        posted_flag_url = request.POST.get("flag_url")
        posted_flag_name = request.POST.get("flag_name")
        vessel = get_object_or_404(Vessel, pk=vessel_id, status="available")
        flag_name = vessel.flag_name
        vessel_edit_form = VesselAddForm(request.POST, instance=vessel)
        if vessel_edit_form.is_valid():
            vessel = vessel_edit_form.save(commit=False)
            if (flag_name != posted_flag_name and posted_flag_url) or (not vessel.flag and posted_flag_url):
                vessel.flag = get_image_file_by_url(posted_flag_url)
            vessel.save()
            # https://stackoverflow.com/a/50384606/14506165
            vessel_edit_form.save_m2m()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("information:vessel_detail", vessel.id)
        else:
            context = {
                'vessel_edit_form': vessel_edit_form,
            }
            return render(request, 'information/vessel/vessel_edit.html', context)


class VesselDetailView(LoginRequiredMixin, View):
    def get(self, request, vessel_id, *args, **kwargs):
        vessel = get_object_or_404(Vessel, pk=vessel_id)
        vessel.all_changes()
        context = {
            'vessel': vessel,
        }
        return render(request, 'information/vessel/vessel_detail.html', context)


class VesselDeleteView(LoginRequiredMixin, View):
    """
    Deletes vessel permanently
    """

    def get(self, request, vessel_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        vessel = get_object_or_404(Vessel, pk=vessel_id)
        vessel.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("information:vessel_data")


class VesselRemoveView(LoginRequiredMixin, View):
    """
    Removes vessel (make available to false)
    Vessel protected
    """

    def get(self, request, vessel_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        vessel = get_object_or_404(Vessel, pk=vessel_id, status="available")
        vessel.status = "not_available"
        vessel.save()
        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("information:vessel_data")
        