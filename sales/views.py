import json, os
from django.http.response import Http404
from django.urls import resolve

from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from django.views import View

from hr.models import BankAccount, TheCompany
from sales.api.serializers import OrderConfirmationDetailSerializer
from sales.forms import ClaimsFollowUpResultForm, ClaimsFollowUpStartForm, ProjectRequestForm, ProjectInquiryForm, ProjectQuotationForm, DeliverySupplierToVesselForm, \
    DeliverySupplierToCustomerForm, DeliveryWarehouseToVesselForm, DeliveryWarehouseToCustomerForm, \
    DeliverySupplierToWarehouseForm, DeliveryTransportationForm, DeliveryTaxForm, DeliveryInsuranceForm, \
    DeliveryCustomsForm, DeliveryPackingForm, ProjectCreateRequestForm, ProjectPurchaseOrderForm, OrderConfirmationForm, OrderNotConfirmationForm, QuotationPartNoteForm
from sales.models import ClaimsFollowUp, OrderNotConfirmation, Project, Quotation, QuotationPart, Request, InquiryPart, PurchaseOrderPart,ClaimReason, RequestPart
from utilities.render_excel import render_to_excel
from utilities.render_pdf import render_to_pdf

from sales.models import ProjectDocument
from io import BytesIO
from django.core.files import File

class SalesDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'sales/process/sales_data.html', context)

class NotConfirmedQuotationView(LoginRequiredMixin, View):
    def get(self,request, *args, **kwargs):
        context={}
        return render(request,'sales/not_confirmed_quotation/not_confirmed_quotation_data.html',context)
class OrderStatusView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {'projects': Project.objects.all().exclude(quotation__notconfirmation__isnull=False)}
        return render(request, 'sales/order_status/order_status.html', context)


class ProjectCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        project_create_request_form = ProjectCreateRequestForm()
        context = {
            'project_create_request_form': project_create_request_form,
        }
        return render(request, 'sales/project/create.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        project_create_request_form = ProjectCreateRequestForm(request.POST)
        if project_create_request_form.is_valid():
            project = Project.objects.create(responsible=request.user, creator=request.user,
                                             project_date=project_create_request_form.cleaned_data.get("project_date"),
                                             project_deadline=project_create_request_form.cleaned_data.get(
                                                 "project_deadline"))
            project_request = project_create_request_form.save(commit=False)
            project_request.project = project
            project_request.creator = request.user
            project_request.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect('sales:project_request', project.id)
        else:
            context = {
                'project_create_request_form': project_create_request_form,
            }
            return render(request, 'sales/project/create.html', context)


class ProjectContinueView(LoginRequiredMixin, View):
    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        return redirect(f'sales:project_{project.stage}', project.id)

class NotConfirmedProjectContinueView(LoginRequiredMixin, View):
    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        return redirect(f'sales:notconfirmation_{project.stage}', project.id)
class ProjectRequestView(LoginRequiredMixin, View):
    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        current_url = resolve(request.path_info).url_name
        
        not_confirmed, not_confirmation_message  = project.is_not_confirmed()
        if current_url != 'notconfirmation_request':
            if not_confirmed:
                messages.error(request, not_confirmation_message)
                return redirect(f'sales:notconfirmation_request', project.id)
        
        allowed, stage, message = project.can_continue("request")
        if not allowed:
            messages.error(request, message)
            return redirect(f'sales:project_{stage}', project.id)
        elif message:
            messages.warning(request, message)
        if not hasattr(project, 'request'):
            Request.objects.create(project=project)
        project_request_form = ProjectRequestForm(instance=project.request)
        
        humanized_days = project.get_delta()    
        context = {
            'project_request_form': project_request_form,
            'next_stage': project.get_next_stage("request"),
            'project': project,
            'users': User.objects.all(),
            'humanized_days':humanized_days
        }
        
        
        if not_confirmed:
            not_confirmation = OrderNotConfirmation.objects.get(quotation__project=project) 
            if not_confirmation:
                context.update({"not_confirmed_quotation":not_confirmation.quotation})
        return render(request, 'sales/project/request.html', context)

    def post(self, request, project_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        project = get_object_or_404(Project, pk=project_id)
        allowed, stage, message = project.can_continue("request")

        if project.is_closed:
            messages.error(request, message)
            return redirect('sales:project_request', project.id)

        if not allowed:
            messages.error(request, message)
            return redirect(f'sales:project_{stage}', project.id)
        elif message:
            messages.warning(request, message)

        project_request_form = ProjectRequestForm(request.POST, instance=project.request)
        if project_request_form.is_valid():
            project_request_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect('sales:project_request', project.id)
        else:
            humanized_days = project.get_delta()    
            context = {
                'project_request_form': project_request_form,
                'next_stage': project.get_next_stage("request"),
                'project': project,
                'users': User.objects.all(),
                'humanized_days':humanized_days
            }
            return render(request, 'sales/project/request.html', context)


class ProjectRequestPDFView(LoginRequiredMixin, View):

    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        requestParts = RequestPart.objects.filter(request=project.request)
        response = render_to_pdf("sales/project/pdf/request.html", {
            'project': project,
            'request': project.request,
            'company': TheCompany.objects.get(id=1),
            'requestParts':requestParts,
            'date':timezone.localtime(timezone.now()).date(),
            'time':timezone.localtime(timezone.now()).time(),
        })
        filename = f"{project.no}({project.id})_{project.request.no}({project.request.pk}).pdf"
        content = f"attachment; filename={filename}" if request.GET.get("download") else f"inline; filename={filename}"
        response['Content-Disposition'] = content

        defaults = {'file': File(file=BytesIO(response.content),name=filename), 'project' : project}          
        instance, created = ProjectDocument.objects.get_or_create(project=project,
        file_stage='request', file_type='pdf', defaults=defaults)
        if created is False:
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)   
            instance.file = File(file=BytesIO(response.content),name=filename)
            instance.save()
                              
        return response


class ProjectRequestExcelView(LoginRequiredMixin, View):
    STYLES = {
        'header': {
            'bg_color': '#ECDCDF',
            'align': 'center',
            'border': 1,
            'border_color': '#A0A0A0'
        },
        'border': {
            'bg_color': '#FFFFFF',
            'border_color': '#A0A0A0'
        },
        'style_2': {
            'bg_color': '#F2F2F2',
            'align': 'center',
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': '#5D5D5D'
        }
        ,
        'style_3': {
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': 'red'
        },
        'style_4': {
            'border': 1,
            'border_color': '#A0A0A0',
        }
    }

    COLUMNS = {
        'Sr': STYLES['style_2'],
        'Part': STYLES['style_3'],
        'Description Of Goods': STYLES['style_4'],
        'Quantity': STYLES['style_3'],
        'Unit': STYLES['style_2']
    }

    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        project_request = project.request

        # if not project_request.is_finish():
        #     raise Http404('This stage is not finished yet.')

        response = render_to_excel(project_request.no, self.STYLES, self.COLUMNS, project_request.parts.all(),
                                   ['part__code', 'part__description', 'quantity', 'part__unit__name'], ['Quantity'])
        filename = f"{project.no}({project.id})_{project_request.no}({project_request.pk}).xlsx"
        response['Content-Disposition'] = f"attachment; filename={filename}"

        defaults = {'file': File(file=BytesIO(response.content),name=filename), 'project' : project}          
        instance, created = ProjectDocument.objects.get_or_create(project=project,
        file_stage='request', file_type='xlsx', defaults=defaults)
        if created is False:
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)   
            instance.file = File(file=BytesIO(response.content),name=filename)
            instance.save()
            
        return response


class ProjectInquiryView(LoginRequiredMixin, View):
    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        current_url = resolve(request.path_info).url_name

        
        not_confirmed, not_confirmation_message  = project.is_not_confirmed()
        if current_url != 'notconfirmation_inquiry':
            if not_confirmed:
                messages.error(request, not_confirmation_message)
                return redirect(f'sales:notconfirmation_inquiry', project.id)
        
        allowed, stage, message = project.can_continue("inquiry")
        if not allowed:
            messages.error(request, message)
            return redirect(f'sales:project_{stage}', project.id)
        elif message:
            messages.warning(request, message)

        project_inquiry_forms = [ProjectInquiryForm(instance=inquiry, auto_id=False) for inquiry in
                                 project.inquiry.all().order_by("created_at")]
        humanized_days = project.get_delta()
        context = {
            'project_inquiry_form_fresh': ProjectInquiryForm(auto_id=False),
            'project_inquiry_forms': project_inquiry_forms,
            'previous_stage': project.get_previous_stage("inquiry"),
            'next_stage': project.get_next_stage("inquiry"),
            'quality_choices': json.dumps({str(x): str(y) for x, y in InquiryPart.QUALITY_CHOICES}),
            'availability_choices': json.dumps({str(x): str(y) for x, y in InquiryPart.AVAILABILITY_CHOICES}),
            'project': project,
            'users': User.objects.all(),
            'humanized_days': humanized_days
        }
        if not_confirmed:
            not_confirmation = OrderNotConfirmation.objects.get(quotation__project=project) 
            if not_confirmation:
                context.update({"not_confirmed_quotation":not_confirmation.quotation})
                
        return render(request, 'sales/project/inquiry.html', context)


class ProjectInquiryPDFView(LoginRequiredMixin, View):
    def get(self, request, project_id, inquiry_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        project_inquiry = get_object_or_404(project.inquiry, pk=inquiry_id)

        allowed, stage, message = project.can_continue("inquiry")
        if not allowed:
            messages.error(request, message)
            return redirect(f'sales:project_{stage}', project.id)

        # if not project_inquiry.is_finish():
        #     raise Http404('This stage is not finished yet.')

        response = render_to_pdf("sales/project/pdf/inquiry.html", {
            'project': project,
            'inquiry': project_inquiry,
            'company': TheCompany.objects.get(id=1)
        })
        filename = f"{project.no}({project.id})_{project_inquiry.no}({project_inquiry.pk}).pdf"
        content = f"attachment; filename={filename}" if request.GET.get("download") else f"inline; filename={filename}"
        response['Content-Disposition'] = content
        
        defaults = {'file': File(file=BytesIO(response.content),name=filename), 'project' : project}          
        instance, created = ProjectDocument.objects.get_or_create(project=project,
        file_stage='inquiry', file_type='pdf', defaults=defaults)
        if created is False:
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)   
            instance.file = File(file=BytesIO(response.content),name=filename)
            instance.save()
                
        return response


class ProjectInquiryExcelView(LoginRequiredMixin, View):
    STYLES = {
        'header': {
            'bg_color': '#ECDCDF',
            'align': 'center',
            'border': 1,
            'border_color': '#A0A0A0'
        },
        'border': {
            'bg_color': '#FFFFFF',
            'border_color': '#A0A0A0'
        },
        'style_2': {
            'bg_color': '#F2F2F2',
            'align': 'center',
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': '#5D5D5D'
        }
        ,
        'style_3': {
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': 'red'
        },
        'style_4': {
            'border': 1,
            'border_color': '#A0A0A0',
        },
        'style_5': {
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': 'blue'
        },
        'style_6': {
            'bg_color': '#F2F2F2',
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': '#5D5D5D'
        }
    }

    COLUMNS = {
        'Sr': STYLES['style_2'],
        'Part': STYLES['style_3'],
        'Description Of Goods': STYLES['style_6'],
        'Quantity': STYLES['style_3'],
        'Unit': STYLES['style_2'],
        'Unit Price': STYLES['style_3'],
        'Total Price': STYLES['style_6'],
        'Availability': STYLES['style_5'],
        '<-Type': STYLES['style_5'],
    }

    def get(self, request, project_id, inquiry_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        project_inquiry = get_object_or_404(project.inquiry, pk=inquiry_id)

        allowed, stage, message = project.can_continue("inquiry")
        if not allowed:
            messages.error(request, message)
            return redirect(f'sales:project_{stage}', project.id)

        # if not project_inquiry.is_finish():
        #     raise Http404('This stage is not finished yet.')

        response = render_to_excel(project_inquiry.no, self.STYLES, self.COLUMNS, project_inquiry.parts.all(),
                                   ['request_part__part__code', 'request_part__part__description', 'quantity',
                                    'request_part__part__unit__name', 'unit_price', 'get_total_price',
                                    'availability_period', 'get_availability_display'],
                                   ['Total Price'])

        filename = f"{project.no}({project.id})_{project_inquiry.no}({project_inquiry.id}).xlsx"
        response['Content-Disposition'] = f"attachment; filename={filename}"
        
        defaults = {'file': File(file=BytesIO(response.content),name=filename), 'project' : project}          
        instance, created = ProjectDocument.objects.get_or_create(project=project,
        file_stage='inquiry', file_type='xlsx', defaults=defaults)
        if created is False:
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)   
            instance.file = File(file=BytesIO(response.content),name=filename)
            instance.save()
            
        return response


class ProjectQuotationView(LoginRequiredMixin, View):
    def get(self, request, project_id, quotation_id = None, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        current_url = resolve(request.path_info).url_name
       
       
        not_confirmed, not_confirmation_message  = project.is_not_confirmed()
        if current_url != 'notconfirmation_quotation':
            if not_confirmed:
                messages.error(request, not_confirmation_message)
                return redirect(f'sales:notconfirmation_quotation', project.id)
         
        allowed, stage, message = project.can_continue("quotation")
        if not allowed:
            messages.error(request, message)
            return redirect(f'sales:project_{stage}', project.id)
        elif message:
            messages.warning(request, message)

        project_quotation_forms = [ProjectQuotationForm(instance=quotation, auto_id=False) for quotation in
                                   project.quotation.all().order_by("created_at")]
        humanized_days = project.get_delta()
        context = {
            'project_quotation_form_fresh': ProjectQuotationForm(auto_id=False),
            'project_quotation_forms': project_quotation_forms,
            'order_confirmation_form': OrderConfirmationForm(auto_id=False),
            'order_not_confirmation_form': OrderNotConfirmationForm(auto_id=False),
            'quotation_part_note_form': QuotationPartNoteForm(auto_id=False),
            'previous_stage': project.get_previous_stage("quotation"),
            'next_stage': project.get_next_stage("quotation"),
            'project': project,
            'users': User.objects.all(),
            'humanized_days':humanized_days
        }
        if not_confirmed:
            not_confirmation = OrderNotConfirmation.objects.get(quotation__project=project) 
            if not_confirmation:
                context.update({"not_confirmed_quotation":not_confirmation.quotation})
        
        if quotation_id:
            notified_quotation = get_object_or_404(Quotation, pk=quotation_id)
            context.update({"notified_quotation":notified_quotation})
        print(project_quotation_forms)
        return render(request, 'sales/project/quotation.html', context)


class ProjectQuotationPDFView(LoginRequiredMixin, View):
    def get(self, request, project_id, quotation_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        project_quotation = get_object_or_404(project.quotation, pk=quotation_id)
        company=TheCompany.objects.get(id=1)
        allowed, stage, message = project.can_continue("quotation")
        if not allowed:
            messages.error(request, message)
            return redirect(f'sales:project_{stage}', project.id)

        responsible=User.objects.get(username=project.responsible)
       
        quotationParts=QuotationPart.objects.filter(quotation=project_quotation)
        net_total=0
        for quotationPart  in quotationParts:
            net_total+=quotationPart.get_currency_total_price_1()
        # if not project_quotation.is_finish(check_confirmation=False):
        #     raise Http404('This stage is not finished yet.')
        response = render_to_pdf("sales/project/pdf/quotation.html", {
            'project': project,
            'responsible':responsible,
            'quotation': project_quotation,
            'quotationParts':quotationParts,
            'netTotal':round(net_total, 2),
            'company': company,
            'date':timezone.localtime(timezone.now()).date(),
            'time':timezone.localtime(timezone.now()).time(),
        })
        filename = f"{project.no}({project.id})_{project_quotation.no}({project_quotation.pk}).pdf"
        content = f"attachment; filename={filename}" if request.GET.get("download") else f"inline; filename={filename}"
        response['Content-Disposition'] = content
        
        defaults = {'file': File(file=BytesIO(response.content),name=filename), 'project' : project}          
        instance, created = ProjectDocument.objects.get_or_create(project=project,
        file_stage='quotation', file_type='pdf', defaults=defaults)
        if created is False:
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)   
            instance.file = File(file=BytesIO(response.content),name=filename)
            instance.save()
        
        return response


class ProjectQuotationExcelView(LoginRequiredMixin, View):
    STYLES = {
        'header': {
            'bg_color': '#ECDCDF',
            'align': 'center',
            'border': 1,
            'border_color': '#A0A0A0'
        },
        'border': {
            'bg_color': '#FFFFFF',
            'border_color': '#A0A0A0'
        },
        'default': {
            'border': 1,
            'border_color': '#A0A0A0'
        },
        'style_2': {
            'bg_color': '#F2F2F2',
            'align': 'center',
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': '#5D5D5D'
        },
        'style_3': {
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': 'red'
        },
        'style_4': {
            'border': 1,
            'border_color': '#A0A0A0',
        },
        'style_5': {
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': 'blue'
        },
        'style_6': {
            'bg_color': '#F2F2F2',
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': '#5D5D5D'
        },
        'style_7': {
            'bg_color': '#FEFFE0',
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': '#743D2E'
        }
    }

    COLUMNS = {
        'Sr': STYLES['style_2'],
        'Part': STYLES['style_3'],
        'Description Of Goods': STYLES['style_6'],
        'Quantity': STYLES['style_3'],
        'Unit': STYLES['style_2'],
        'Unit Price 1': STYLES['style_6'],
        'Total Price 1': STYLES['style_6'],
        '% Profit': STYLES['style_5'],
        'Unit Price 2': STYLES['style_6'],
        'Total Price 2': STYLES['style_6'],
        '% Discount': STYLES['style_3'],
        'Discount': STYLES['style_6'],
        'Unit Price 3': STYLES['style_7'],
        'Total Price 3': STYLES['style_7'],
        'Availability': STYLES['default'],
        '<-Type': STYLES['default'],
        'Quality': STYLES['default'],
    }

    def get(self, request, project_id, quotation_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        project_quotation = get_object_or_404(project.quotation, pk=quotation_id)

        allowed, stage, message = project.can_continue("quotation")
        if not allowed:
            messages.error(request, message)
            return redirect(f'sales:project_{stage}', project.id)

        # if not project_quotation.is_finish(check_confirmation=False):
        #     raise Http404('This stage is not finished yet.')

        response = render_to_excel(project_quotation.no, self.STYLES, self.COLUMNS, project_quotation.parts.all(),
                                   ['inquiry_part__request_part__part__code',
                                    'inquiry_part__request_part__part__description',
                                    'inquiry_part__quantity',
                                    'inquiry_part__request_part__part__unit__name',
                                    'get_currency_unit_price',
                                    'get_currency_total_price_1',
                                    'profit',
                                    'get_unit_price_2',
                                    'get_total_price_2',
                                    'discount',
                                    'get_total_discount_value',
                                    'get_unit_price_3',
                                    'get_total_price_3',
                                    'inquiry_part__availability_period',
                                    'inquiry_part__get_availability_display',
                                    'inquiry_part__get_quality_display'],
                                   ['Total Price 1', 'Total Price 2', 'Discount', 'Total Price 3'])

        filename = f"{project.no}({project.id})_{project_quotation.no}({project_quotation.id}).xlsx"
        response['Content-Disposition'] = f"attachment; filename={filename}"

        defaults = {'file': File(file=BytesIO(response.content),name=filename), 'project' : project}          
        instance, created = ProjectDocument.objects.get_or_create(project=project,
        file_stage='quotation', file_type='xlsx', defaults=defaults)
        if created is False:
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)   
            instance.file = File(file=BytesIO(response.content),name=filename)
            instance.save()
            
        return response


class ProjectOrderConfirmationPDFView(LoginRequiredMixin, View):
    def get(self, request, project_id, confirmation_pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        quotation = get_object_or_404(project.quotation, pk=confirmation_pk)

        # if not hasattr(quotation, 'confirmation'):
        #     raise Http404('This quotation has not confirmed yet.')
        try:
            order_confirmation = quotation.confirmation
        except:
            raise Http404("Confirmation not found")
        
        quotationParts=QuotationPart.objects.filter(quotation=quotation)
        responsible=User.objects.get(username=project.responsible)
        sub_total=0
        discount_total=0
        for quotationPart in quotationParts:
            
            sub_total+=quotationPart.get_total_price_2()
            discount_total+=quotationPart.get_total_discount_value()
        vat_total=round((sub_total / 100) * float(quotation.vat), 2)
        net_total=sub_total+vat_total-discount_total
        discount = round((discount_total/sub_total) * 100,2)
        response = render_to_pdf("sales/project/pdf/order_confirmation.html", {
            'project': project,
            'quotation':quotation,
            'responsible':responsible,
            'quotationParts':quotationParts,
            'order_confirmation': order_confirmation,
            'company': TheCompany.objects.get(id=1),
            'bankAccounts':BankAccount.objects.all(),
            'date':timezone.localtime(timezone.now()).date(),
            'time':timezone.localtime(timezone.now()).time(),
            'subTotal':round(sub_total, 2),
            'vatTotal':vat_total,
            'discount':discount,
            'discountTotal':discount_total,
            'netTotal':round(net_total, 2),
            
        })
        filename = f"{project.no}({project.id})_{order_confirmation.no}({order_confirmation.pk}).pdf"
        content = f"attachment; filename={filename}" if request.GET.get("download") else f"inline; filename={filename}"
        response['Content-Disposition'] = content

        defaults = {'file': File(file=BytesIO(response.content),name=filename), 'project' : project}          
        instance, created = ProjectDocument.objects.get_or_create(project=project,
        file_stage='order confirmation', file_type='pdf', defaults=defaults)
        if created is False:
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)   
            instance.file = File(file=BytesIO(response.content),name=filename)
            instance.save()
                
        return response


class ProjectOrderConfirmationExcelView(LoginRequiredMixin, View):
    STYLES = {
        'header': {
            'bg_color': '#ECDCDF',
            'align': 'center',
            'border': 1,
            'border_color': '#A0A0A0'
        },
        'border': {
            'bg_color': '#FFFFFF',
            'border_color': '#A0A0A0'
        },
        'default': {
            'border': 1,
            'border_color': '#A0A0A0'
        },
        'style_2': {
            'bg_color': '#F2F2F2',
            'align': 'center',
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': '#5D5D5D'
        },
        'style_3': {
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': 'red'
        },
        'style_4': {
            'border': 1,
            'border_color': '#A0A0A0',
        },
        'style_5': {
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': 'blue'
        },
        'style_6': {
            'bg_color': '#F2F2F2',
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': '#5D5D5D'
        },
        'style_7': {
            'bg_color': '#FEFFE0',
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': '#743D2E'
        }
    }

    COLUMNS = {
        'Sr': STYLES['style_2'],
        'Part': STYLES['style_6'],
        'Description Of Goods': STYLES['style_6'],
        'Quantity': STYLES['style_6'],
        'Unit': STYLES['style_2'],
        '% Profit': STYLES['style_6'],
        'Unit Price': STYLES['style_6'],
        'Sub Total': STYLES['style_6'],
        '% Discount': STYLES['style_6'],
        'Final Total Price': STYLES['style_6'],
        'Inquiry Number': STYLES['style_6'],
        '_Seller': STYLES['style_6']
    }

    def get(self, request, project_id, confirmation_pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        project_quotation = get_object_or_404(project.quotation, pk=confirmation_pk)

        # if not hasattr(project_quotation, 'confirmation'):
        #     raise Http404('This quotation has not confirmed yet.')

        try:
            order_confirmation = project_quotation.confirmation
        except:
            raise Http404("Confirmation not found")

        response = render_to_excel(order_confirmation.no, self.STYLES, self.COLUMNS,
                                   order_confirmation.quotation.parts.all(),
                                   ['inquiry_part__request_part__part__code',
                                    'inquiry_part__request_part__part__description',
                                    'inquiry_part__quantity',
                                    'inquiry_part__request_part__part__unit__name',
                                    'profit',
                                    'get_currency_unit_price',
                                    'get_total_price_2',
                                    'discount',
                                    'get_total_price_3',
                                    'inquiry_part__inquiry__no',
                                    'inquiry_part__inquiry__supplier__default_person_in_contact__get_full_name'],
                                   ['Sub Total', 'Final Total Price'])

        filename = f"{project.no}({project.id})_{order_confirmation.no}({order_confirmation.pk}).xlsx"
        response['Content-Disposition'] = f"attachment; filename={filename}"
        
        defaults = {'file': File(file=BytesIO(response.content),name=filename), 'project' : project}          
        instance, created = ProjectDocument.objects.get_or_create(project=project,
        file_stage='order confirmation', file_type='xlsx', defaults=defaults)
        if created is False:
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)   
            instance.file = File(file=BytesIO(response.content),name=filename)
            instance.save()
        
        return response


class ProjectPurchaseOrderView(LoginRequiredMixin, View):
    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        
        not_confirmed, not_confirmation_message  = project.is_not_confirmed()
        if not_confirmed:
            messages.error(request, not_confirmation_message)
            return redirect(f'sales:notconfirmation_quotation', project.id)
        
        allowed, stage, message = project.can_continue("purchase_order")
        if not allowed:
            messages.error(request, message)
            return redirect(f'sales:project_{stage}', project.id)
        elif message:
            messages.warning(request, message)

        quotation_based_project_purchase_order_forms = {}
        for purchase_order in project.purchase_order.all().order_by("created_at"):
            quotation = purchase_order.order_confirmation.quotation
            if quotation.no in quotation_based_project_purchase_order_forms:
                quotation_based_project_purchase_order_forms[quotation.no]['forms'].append(
                    ProjectPurchaseOrderForm(instance=purchase_order, auto_id=False))
            else:
                quotation_based_project_purchase_order_forms[quotation.no] = {
                    'id': quotation.id,
                    'forms': [ProjectPurchaseOrderForm(instance=purchase_order, auto_id=False)]
                }
        humanized_days = project.get_delta()
        context = {
            'quotation_based_project_purchase_order_forms': quotation_based_project_purchase_order_forms,
            'previous_stage': project.get_previous_stage("purchase_order"),
            'next_stage': project.get_next_stage("purchase_order"),
            'order_type_choices': json.dumps({str(x): str(y) for x, y in PurchaseOrderPart.ORDER_TYPE_CHOICES}),
            'project': project,
            'users': User.objects.all(),
            'humanized_days':humanized_days
        }
        return render(request, 'sales/project/purchase_order.html', context)


class ProjectPurchaseOrderPDFView(LoginRequiredMixin, View):
    def get(self, request, project_id, purchase_order_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        project_purchase_order = get_object_or_404(project.purchase_order, pk=purchase_order_id)
        purchase_order_parts=PurchaseOrderPart.objects.filter(purchase_order=purchase_order_id)
        responsible=User.objects.get(username=project.responsible)
        allowed, stage, message = project.can_continue("purchase_order")
        if not allowed:
            messages.error(request, message)
            return redirect(f'sales:project_{stage}', project.id)
        # if not project_purchase_order.is_finish():
        #     raise Http404('This stage is not finished yet.')
        sub_total =0
        discount_total = 0

        for purchase_order_part in purchase_order_parts:
            sub_total+=purchase_order_part.get_total_price_2()
            #Total discaount as price
            discount_total+=purchase_order_part.get_total_discount_value()
        
        net_total=sub_total-discount_total
        #Total discaount as percent
        discount = round((discount_total/sub_total) * 100,2)
        response = render_to_pdf("sales/project/pdf/purchase_order.html", {
            'project': project,
            'purchase_order': project_purchase_order,
            'responsible' :responsible,
            'purchaseOrderParts':purchase_order_parts,
            'company': TheCompany.objects.get(id=1),
            'date':timezone.localtime(timezone.now()).date(),
            'time':timezone.localtime(timezone.now()).time(),
            'subTotal':sub_total,
            'discount':discount,
            'discountTotal':discount_total,
            'netTotal':round(net_total, 2),
        })
        filename = f"{project.no}({project.id})_{project_purchase_order.no}({project_purchase_order.pk}).pdf"
        content = f"attachment; filename={filename}" if request.GET.get("download") else f"inline; filename={filename}"
        response['Content-Disposition'] = content
        
        defaults = {'file': File(file=BytesIO(response.content),name=filename), 'project' : project}          
        instance, created = ProjectDocument.objects.get_or_create(project=project,
        file_stage='purchase order', file_type='pdf', defaults=defaults)
        if created is False:
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)   
            instance.file = File(file=BytesIO(response.content),name=filename)
            instance.save()
                
        return response


class ProjectPurchaseOrderExcelView(LoginRequiredMixin, View):
    STYLES = {
        'header': {
            'bg_color': '#ECDCDF',
            'align': 'center',
            'border': 1,
            'border_color': '#A0A0A0'
        },
        'border': {
            'bg_color': '#FFFFFF',
            'border_color': '#A0A0A0'
        },
        'default': {
            'border': 1,
            'border_color': '#A0A0A0'
        },
        'style_2': {
            'bg_color': '#F2F2F2',
            'align': 'center',
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': '#5D5D5D'
        },
        'style_3': {
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': 'red'
        },
        'style_4': {
            'border': 1,
            'border_color': '#A0A0A0',
        },
        'style_5': {
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': 'blue'
        },
        'style_6': {
            'bg_color': '#F2F2F2',
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': '#5D5D5D'
        },
        'style_7': {
            'bg_color': '#FEFFE0',
            'border': 1,
            'border_color': '#A0A0A0',
            'font_color': '#743D2E'
        }
    }

    COLUMNS = {
        'Sr': STYLES['style_2'],
        'Part': STYLES['default'],
        'Description Of Goods': STYLES['style_6'],
        'Quantity': STYLES['default'],
        'Unit': STYLES['style_2'],
        'Unit Price': STYLES['default'],
        'Total Price': STYLES['style_6'],
        'Order Type': STYLES['default'],
        'Availability': STYLES['default'],
        '<-Type': STYLES['default'],
        'Quality': STYLES['default'],
    }

    def get(self, request, project_id, purchase_order_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        project_purchase_order = get_object_or_404(project.purchase_order, pk=purchase_order_id)

        allowed, stage, message = project.can_continue("purchase_order")
        if not allowed:
            messages.error(request, message)
            return redirect(f'sales:project_{stage}', project.id)

        # if not project_purchase_order.is_finish():
        #     raise Http404('This stage is not finished yet.')

        response = render_to_excel(project_purchase_order.no, self.STYLES, self.COLUMNS,
                                   project_purchase_order.parts.all(),
                                   ['quotation_part__inquiry_part__request_part__part__code',
                                    'quotation_part__inquiry_part__request_part__part__description',
                                    'quotation_part__inquiry_part__quantity',
                                    'quotation_part__inquiry_part__request_part__part__unit__name',
                                    'get_currency_unit_price',
                                    'get_total_price_3',
                                    'get_order_type_display',
                                    'quotation_part__inquiry_part__availability_period',
                                    'quotation_part__inquiry_part__get_availability_display',
                                    'quotation_part__inquiry_part__get_quality_display'],
                                   ['Total Price'])

        filename = f"{project.no}({project.id})_{project_purchase_order.no}({project_purchase_order.id}).xlsx"
        response['Content-Disposition'] = f"attachment; filename={filename}"
   
        defaults = {'file': File(file=BytesIO(response.content),name=filename), 'project' : project}          
        instance, created = ProjectDocument.objects.get_or_create(project=project,
        file_stage='purchase order', file_type='xlsx', defaults=defaults)
        if created is False:
            if os.path.exists(instance.file.path):
                os.remove(instance.file.path)   
            instance.file = File(file=BytesIO(response.content),name=filename)
            instance.save()
        
        return response


class ProjectDeliveryView(LoginRequiredMixin, View):
    def get(self, request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_id)
        
        not_confirmed, not_confirmation_message  = project.is_not_confirmed()
        if not_confirmed:
            messages.error(request, not_confirmation_message)
            return redirect(f'sales:notconfirmation_quotation', project.id)
        
        claim_continue = project.is_claim_continue()
        
        allowed, stage, message = project.can_continue("delivery")
        if not allowed:
            messages.error(request, message)
            return redirect(f'sales:project_{stage}', project.id)
        elif message:
            messages.warning(request, message)

        delivery_forms = {
            'STV': DeliverySupplierToVesselForm,
            'STC': DeliverySupplierToCustomerForm,
            'WTV': DeliveryWarehouseToVesselForm,
            'WTC': DeliveryWarehouseToCustomerForm,
            'STW': DeliverySupplierToWarehouseForm
        }

        delivery_charges_forms = {
            'transportation': DeliveryTransportationForm,
            'tax': DeliveryTaxForm,
            'insurance': DeliveryInsuranceForm,
            'customs': DeliveryCustomsForm,
            'packing': DeliveryPackingForm,
        }

        project_delivery_forms = [
            delivery_forms[delivery.process_type](instance=delivery, project=project, auto_id=False) for delivery
            in project.delivery.all().order_by("created_at")]
        humanized_days = project.get_delta()
        context = {
            'delivery_forms_fresh': {k: v(project=project, auto_id=False) for k, v in delivery_forms.items()},
            'delivery_charges_forms_fresh': {k: v(auto_id=False) for k, v in delivery_charges_forms.items()},
            'project_delivery_forms': project_delivery_forms,
            'previous_stage': project.get_previous_stage("delivery"),
            'next_stage': project.get_next_stage("delivery"),
            'project': project,
            'users': User.objects.all(),
            'humanized_days':humanized_days,
            'claims_follow_up_start_form': ClaimsFollowUpStartForm(auto_id=False),
            'claim_continue':claim_continue
        }
        return render(request, 'sales/project/delivery.html', context)

class ClaimsFollowUpView(LoginRequiredMixin, View):
    def get(self,request, *args, **kwargs):
        context={
            'claims_follow_up_start_form': ClaimsFollowUpStartForm(is_disable=True), 
            'claims_follow_up_result_form':ClaimsFollowUpResultForm
        }
        return render(request,'sales/claims_follow_up/claims_follow_up_data.html',context)

class ClaimsFollowUpDetailView(LoginRequiredMixin, View):
    def get(self,request,claim_id, *args, **kwargs):
        claim = get_object_or_404(ClaimsFollowUp, pk=claim_id)
        reason_choices=claim.claim_reason_choices.all()
        claim_results=claim.claim_results.all()
        project = claim.delivery.project 
        humanized_days = project.get_delta()
        context={
            'claim':claim,
            'reason_choices':reason_choices,
            'claim_results':claim_results,
            'claim_follow_up_result_form':ClaimsFollowUpResultForm,
            'project':project,
            'humanized_days':humanized_days
        }
        return render(request,"sales/claims_follow_up/claims_follow_up_detail.html",context)