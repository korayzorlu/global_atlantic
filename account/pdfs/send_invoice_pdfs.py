from django.conf import settings

from django.template.loader import render_to_string
from weasyprint import HTML

from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import os
from itertools import chain

from ..models import SendInvoice,SendInvoiceExpense,SendInvoiceItem

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

def sendInvoicePdf(sourceCompanyId, invoiceId, base_url,elementTag):
    data = {
        "block":f"message-container-{elementTag}-{invoiceId}",
        "icon":"",
        "message":"Updating pdf...",
        "stage" : "loading",
        "buttons": f"tabPane-{elementTag}-{invoiceId} .modal-header .tableTopButtons"
    }
        
    sendAlert(data,"form")
    
    sourceCompany = SourceCompany.objects.filter(id = sourceCompanyId).first()
    sendInvoice = SendInvoice.objects.select_related("customer","vessel","billing","theRequest","theRequest__maker","theRequest__makerType","orderConfirmation","offer").filter(id = invoiceId).first()
    theRequest = sendInvoice.theRequest
    orderTracking = sendInvoice.theRequest.order_tracking_request.select_related().filter().first() if sendInvoice.theRequest else None
    delivery = orderTracking.delivery_set.select_related().first() if orderTracking else None
    orderConfirmation = sendInvoice.orderConfirmation
    offer = sendInvoice.offer

    path = os.path.join(os.getcwd(), "media", "docs", str(sourceCompanyId), "account", "send_invoice", "documents")
    fileName = f"{sendInvoice.sendInvoiceNoSys}.pdf"

    logo = f"/media/source/companies/{str(sourceCompanyId)}/{str(sourceCompany.documentLogo.name.split('/')[-1])}"
    
    #####company info#####
    if sendInvoice.vessel:
        vesselName = f"{sendInvoice.vessel.get_type_display()} {sendInvoice.vessel.name} - IMO No: {sendInvoice.vessel.imo}"
    else:
        vesselName = ""
    
    companyName = sendInvoice.customer.name if sendInvoice.customer else ""
    companyAddress = get_address(sendInvoice.customer) if sendInvoice.customer else ""

    if sendInvoice.billing:
        billingName = sendInvoice.billing.name
        billingAddress = get_address(sendInvoice.billing)
    else:
        billingName = companyName
        billingAddress = companyAddress

    if delivery:
        deliveryAddress = delivery.address if delivery.address else ""
    else:
        deliveryAddress = ""
    #####company info-end#####

    #####project info#####
    if sendInvoice.group == "order":
        projectNo = theRequest.requestNo if theRequest else ""
        orderDate = orderConfirmation.orderConfirmationDate.strftime("%d.%m.%Y") if orderConfirmation else ""
        deliveryType = orderConfirmation.quotation.delivery if orderConfirmation else ""
        deliveryNo = delivery.trackingNo if delivery else ""
        maker = theRequest.maker if theRequest else ""
        makerType = theRequest.makerType if theRequest else ""
        customerRef = theRequest.customerRef if theRequest else ""
        payment = orderConfirmation.quotation.payment if orderConfirmation else ""
    elif sendInvoice.group == "service":
        projectNo = offer.offerNo if offer else ""
        orderDate = offer.offerDate.strftime("%d.%m.%Y") if offer else ""
        deliveryType = offer.deliveryMethod if offer else ""
        deliveryNo = ""
        if offer:
            maker = offer.equipment.maker if offer.equipment else ""
            makerType = offer.equipment.makerType if offer.equipment else ""
        else:
            maker = ""
            makerType = ""
        customerRef = offer.customerRef if offer else ""
        payment = offer.paymentType if offer else ""

    projectData = {
        "projectNo" : projectNo if projectNo else "",
        "orderDate" : orderDate if orderDate else "",
        "deliveryType" : deliveryType if deliveryType else "",
        "deliveryNo" : deliveryNo if deliveryNo else "",
        "maker" : maker if maker else "",
        "makerType" : makerType if makerType else "",
        "customerRef" : customerRef if customerRef else "",
        "payment" : payment if payment else ""
    }
   
    #####project info-end#####

    #####items#####
    items = sendInvoice.sendinvoiceitem_set.select_related().all().order_by("sequency")
    expenses = sendInvoice.sendinvoiceexpense_set.select_related("expense").all().order_by("id")
    
    items = list(chain(items,expenses))
    itemsData = []

    seq = 1
    for key, item in enumerate(items):
        if isinstance(item, SendInvoiceItem):
            name = item.name
            description = item.description if item.description else ""
            trDescription = f"- {item.trDescription}" if item.trDescription else ""
        elif isinstance(item, SendInvoiceExpense):
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

    invoiceDate = sendInvoice.sendInvoiceDate.strftime("%d.%m.%Y")
    invoiceNo = sendInvoice.sendInvoiceNo if sendInvoice.sendInvoiceNo else ""
    invoiceCareOf = f"c/o {sendInvoice.careOf}" if sendInvoice.careOf else ""
    invoiceCurrency = sendInvoice.currency.code if sendInvoice.currency else ""
    invoiceOnly = sendInvoice.only if sendInvoice.only else ""
           
    if sendInvoice.vat == 0:
        invoiceVatText = "KDV / VAT"
    else:
        if sendInvoice.vat.is_integer():
            invoiceVatText = "KDV " + str(int(sendInvoice.vat)) + "% / VAT " + str(int(sendInvoice.vat)) + "%"
        else:
            invoiceVatText = "KDV " + str(sendInvoice.vat) + "% / VAT " + str(sendInvoice.vat) + "%"

    invoiceNetPrice = round_price(sendInvoice.netPrice)
    invoiceDiscountPrice = round_price(sendInvoice.discountPrice + sendInvoice.extraDiscountPrice)
    invoiceVatPrice = round_price(sendInvoice.vatPrice)
    invoiceTotalPrice = round_price(sendInvoice.totalPrice)

    context = {
        "sourceCompany" : sourceCompany,
        "logo" : logo,
        "items": items,
        "isBanks" : isBanks,
        "halkBanks" : halkBanks,
        "vakifBanks" : vakifBanks,
        "invoiceDate" : invoiceDate,
        "invoiceNo" : invoiceNo,
        "invoiceCareOf" : invoiceCareOf,
        "invoiceCurrency" : invoiceCurrency,
        "invoiceOnly" : invoiceOnly,
        "invoiceVatText" : invoiceVatText,
        "invoiceNetPrice" : invoiceNetPrice,
        "invoiceDiscountPrice" : invoiceDiscountPrice,
        "invoiceVatPrice" : invoiceVatPrice,
        "invoiceTotalPrice" : invoiceTotalPrice,
        "vesselName" : vesselName,
        "billingName" : billingName,
        "billingAddress" : billingAddress,
        "deliveryAddress" : deliveryAddress,
        "projectData" : projectData
    }

    # HTML içeriğini oluştur
    html_content = render_to_string("account/send_invoice/send_invoice_pdf_maker.html", context)

    # Kaydedilecek dosya yolu
    os.makedirs(path, exist_ok=True)  # Klasör yoksa oluştur
    file_path = os.path.join(path, fileName)

    # PDF'yi kaydet
    HTML(string=html_content,base_url=base_url).write_pdf(file_path,presentational_hints=True)

    data = {
            "block":f"message-container-{elementTag}-{invoiceId}",
            "icon":"circle-check",
            "message":"Updated successfully",
            "stage" : "completed",
            "buttons": f"tabPane-{elementTag}-{invoiceId} .modal-header .tableTopButtons"
    }
            
    sendAlert(data,"form")
