from django.conf import settings

from django.template.loader import render_to_string
from weasyprint import HTML

from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import os
from itertools import chain

from ..models import IncomingInvoice,IncomingInvoiceExpense,IncomingInvoiceItem

from source.models import Bank as SourceBank
from source.models import Company as SourceCompany

from ..utils.pdf_utils import *
from ..utils.account_utils import *

def sendAlert(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "send_alert",
            "message": message,
            "location" : location
        }
    )

def incomingInvoicePdf(sourceCompanyId, invoiceId, base_url,elementTag):
    data = {
        "block":f"message-container-{elementTag}-{invoiceId}",
        "icon":"",
        "message":"Updating pdf...",
        "stage" : "loading",
        "buttons": f"tabPane-{elementTag}-{invoiceId} .modal-header .tableTopButtons"
    }
        
    sendAlert(data,"form")

    sourceCompany = SourceCompany.objects.filter(id = sourceCompanyId).first()
    invoice = IncomingInvoice.objects.select_related("customer","seller","customerSource").filter(id = invoiceId).first()

    path = os.path.join(os.getcwd(), "media", "docs", str(sourceCompanyId), "account", "incoming_invoice", "documents")
    fileName = f"{invoice.id}.pdf"

    logo = f"/media/source/companies/{str(sourceCompanyId)}/{str(sourceCompany.documentLogo.name.split('/')[-1])}"
    
    #####company info#####
    companyName = invoice.customer.name if invoice.customer else ""
    companyAddress = get_address(invoice.seller) if invoice.customer else ""

    billingName = companyName
    billingAddress = companyAddress

    #####company info-end#####


    #####items#####
    items = invoice.incominginvoiceitem_set.select_related().all().order_by("sequency")
    expenses = invoice.incominginvoiceexpense_set.select_related("expense").all().order_by("id")
    
    items = list(chain(items,expenses))
    itemsData = []

    seq = 1
    for key, item in enumerate(items):
        if isinstance(item, IncomingInvoiceItem):
            name = item.name
            description = item.description if item.description else ""
            trDescription = f"- {item.trDescription}" if item.trDescription else ""
        elif isinstance(item, IncomingInvoiceExpense):
            name = item.expense.code
            description = item.expense.name if item.expense.name else ""
            trDescription = ""

        itemsData.append({
            "sequency" : seq,
            "name" : f"{name}",
            "description" : f"{description} {trDescription}",
            "quantity" : item.quantity,
            "unit" : item.unit,
            "unitPrice" : item.unitPrice,
            "totalPrice" : item.totalPrice
        })

        seq += 1
    
    items = itemsData
    #####items-end#####

    ##### bank list #####
    filterList = ["USD","EUR","TRY"]
    isBanks = SourceBank.objects.select_related("currency").filter(
        (Q(company = sourceCompany, bankName__icontains='İŞ BANKASI') | Q(company = sourceCompany, bankName__icontains='TÜRKİYE İŞ BANKASI')) &
        Q(currency__code__in = filterList)
    )
    halkBanks = SourceBank.objects.select_related("currency").filter(
        (Q(company = sourceCompany, bankName__icontains='HALKBANK') | Q(company = sourceCompany, bankName__icontains='TÜRKİYE HALK BANKASI')) &
        Q(currency__code__in = filterList)
    )
    vakifBanks = SourceBank.objects.select_related("currency").filter(
        (Q(company = sourceCompany, bankName__icontains='VAKIFBANK') | Q(company = sourceCompany, bankName__icontains='TÜRKİYE VAKIFLAR BANKASI')) &
        Q(currency__code__in = filterList)
    )
    ##### bank list-end #####

    invoiceDate = invoice.incomingInvoiceDate.strftime("%d.%m.%Y")
    invoiceNo = invoice.incomingInvoiceNo if invoice.incomingInvoiceNo else ""
    invoiceCurrency = invoice.currency.code if invoice.currency else ""
    invoiceOnly = ""
           
    if invoice.vat == 0:
        invoiceVatText = "KDV / VAT"
    else:
        if invoice.vat.is_integer():
            invoiceVatText = "KDV " + str(int(invoice.vat)) + "% / VAT " + str(int(invoice.vat)) + "%"
        else:
            invoiceVatText = "KDV " + str(invoice.vat) + "% / VAT " + str(invoice.vat) + "%"

    invoiceNetPrice = round_price(invoice.netPrice)
    invoiceDiscountPrice = round_price(invoice.discountPrice)
    invoiceVatPrice = round_price(invoice.vatPrice)
    invoiceTotalPrice = round_price(invoice.totalPrice)

    context = {
        "sourceCompany" : sourceCompany,
        "logo" : logo,
        "items": items,
        "isBanks" : isBanks,
        "halkBanks" : halkBanks,
        "vakifBanks" : vakifBanks,
        "invoiceDate" : invoiceDate,
        "invoiceNo" : invoiceNo,
        "invoiceCurrency" : invoiceCurrency,
        "invoiceOnly" : invoiceOnly,
        "invoiceVatText" : invoiceVatText,
        "invoiceNetPrice" : invoiceNetPrice,
        "invoiceDiscountPrice" : invoiceDiscountPrice,
        "invoiceVatPrice" : invoiceVatPrice,
        "invoiceTotalPrice" : invoiceTotalPrice,
        "billingName" : billingName,
        "billingAddress" : billingAddress
    }

    html_content = render_to_string("account/incoming_invoice/incoming_invoice_pdf_maker.html", context)

    os.makedirs(path, exist_ok=True)  # Klasör yoksa oluştur
    file_path = os.path.join(path, fileName)

    HTML(string=html_content,base_url=base_url).write_pdf(file_path,presentational_hints=True)

    data = {
            "block":f"message-container-{elementTag}-{invoiceId}",
            "icon":"circle-check",
            "message":"Updated successfully",
            "stage" : "completed",
            "buttons": f"tabPane-{elementTag}-{invoiceId} .modal-header .tableTopButtons"
    }
            
    sendAlert(data,"form")
