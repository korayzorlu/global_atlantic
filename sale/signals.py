from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import F 
from django.db import transaction

from django.core.signals import request_finished
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import InquiryPart, QuotationPart, Inquiry, Quotation, Request, RequestPart,PurchaseOrderPart
from card.models import Currency

from .pdfs.quotation_pdfs import *
from .pdfs.inquiry_pdfs import *

from .tasks import *

import inspect

import sys

def updateDetail(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "update_detail",
            "message": message,
            "location" : location
        }
    )



@receiver(pre_save, sender=RequestPart)
def update_total_price_or_unit_price_request(sender, instance, **kwargs):
    if sender.objects.filter(id=instance.id).exists():

        senderRequestPart = sender.objects.filter(id=instance.id).first()
        
        if getattr(senderRequestPart, "sequency") != getattr(instance, "sequency"):
            
            with transaction.atomic():
                theRequest = instance.theRequest
                new_sequency = instance.sequency
                if senderRequestPart.sequency < new_sequency:
                    RequestPart.objects.filter(
                        sourceCompany = senderRequestPart.sourceCompany,
                        theRequest=theRequest,
                        sequency__gt=senderRequestPart.sequency,
                        sequency__lte=new_sequency
                    ).exclude(pk=instance.pk).update(sequency=F('sequency') - 1)
                else:
                    RequestPart.objects.filter(
                        sourceCompany = senderRequestPart.sourceCompany,
                        theRequest=theRequest,
                        sequency__lt=senderRequestPart.sequency,
                        sequency__gte=new_sequency
                    ).exclude(pk=instance.pk).update(sequency=F('sequency') + 1)
                
     
      
@receiver(pre_save, sender=Quotation)
def update_quotation(sender, instance, **kwargs):
    if sender.objects.filter(id=instance.id).exists():

        senderQuotation = sender.objects.get(id=instance.id)

        if getattr(senderQuotation, "currency") != getattr(instance, "currency"):
            print("sender: " + senderQuotation.currency.code)
            print("instance: " + instance.currency.code)
            
            senderCurrency = Currency.objects.get(code = senderQuotation.currency.code)
            instanceCurrency = Currency.objects.get(code = instance.currency.code)
            
            quotationParts = QuotationPart.objects.filter(sourceCompany = senderQuotation.sourceCompany,quotation = senderQuotation)
            quotationExtras = QuotationExtra.objects.filter(sourceCompany = senderQuotation.sourceCompany,quotation = senderQuotation)
            
            for quotationPart in quotationParts:
                # if instanceCurrency.code == "JPY":
                #     quotationPart.unitPrice3 = (quotationPart.unitPrice3 * senderCurrency.forexBuying) / (instanceCurrency.forexBuying / 100)
                # elif senderCurrency.code == "JPY":
                #     quotationPart.unitPrice3 = (quotationPart.unitPrice3 * (senderCurrency.forexBuying / 100)) / instanceCurrency.forexBuying
                # else:
                quotationPart.unitPrice1 = (quotationPart.unitPrice1 * senderCurrency.forexBuying) / instanceCurrency.forexBuying
                quotationPart.save()
            
            for quotationExtra in quotationExtras:
                quotationExtra.unitPrice = (quotationExtra.unitPrice * senderCurrency.forexBuying) / instanceCurrency.forexBuying
                quotationExtra.save()

@receiver(pre_save, sender=InquiryPart)
def update_total_price_or_unit_price_inquiry(sender, instance, **kwargs):
    if sender.objects.select_related("inquiry__currency").filter(id=instance.id).exists():

        senderInquiryPart = sender.objects.select_related("inquiry__currency").filter(id=instance.id).first()
        
        if getattr(senderInquiryPart, "sequency") != getattr(instance, "sequency"):
            
            with transaction.atomic():
                inquiry = instance.inquiry
                new_sequency = instance.sequency
                if senderInquiryPart.sequency < new_sequency:
                    InquiryPart.objects.select_related().filter(
                        sourceCompany = senderInquiryPart.sourceCompany,
                        inquiry=inquiry,
                        sequency__gt=senderInquiryPart.sequency,
                        sequency__lte=new_sequency
                    ).exclude(pk=instance.pk).update(sequency=F('sequency') - 1)
                else:
                    InquiryPart.objects.select_related().filter(
                        sourceCompany = senderInquiryPart.sourceCompany,
                        inquiry=inquiry,
                        sequency__lt=senderInquiryPart.sequency,
                        sequency__gte=new_sequency
                    ).exclude(pk=instance.pk).update(sequency=F('sequency') + 1)
        
        inquiryCurrency = senderInquiryPart.inquiry.currency
        
        quotationPart = senderInquiryPart.quotaiton_part_part.select_related("quotation__currency").first()
        
        if quotationPart:
            quotationCurrency = quotationPart.quotation.currency
        else:
            quotationPart = None
            
        if getattr(senderInquiryPart, "quantity") != getattr(instance, "quantity"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
                if quotationPart:
                    quotationPart.unitPrice1 = 0
            else:
                if quotationPart:
                    quotationPart.unitPrice1 = (instance.unitPrice * inquiryCurrency.forexBuying) / quotationCurrency.forexBuying
            
            if quotationPart:
                quotationPart.totalPrice1 = float(quotationPart.unitPrice1) * float(quotationPart.quantity)
                quotationPart.unitPrice2 = round(float(quotationPart.unitPrice1) * float(1 + (float(quotationPart.profit)/100)), 2)
                quotationPart.totalPrice2 = round(float(quotationPart.unitPrice2) * float(quotationPart.quantity), 2)
                quotationPart.unitPrice3 = round(float(quotationPart.unitPrice2) * float(1 - (float(quotationPart.discount)/100)), 2)
                quotationPart.totalPrice3 = round(float(quotationPart.unitPrice3) * float(quotationPart.quantity), 2)
            instance.totalPrice = float(instance.unitPrice) * float(instance.quantity)
            
        if getattr(senderInquiryPart, "unitPrice") != getattr(instance, "unitPrice"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
                if quotationPart:
                    quotationPart.unitPrice1 = 0
            else:
                if quotationPart:
                    quotationPart.unitPrice1 = (instance.unitPrice * inquiryCurrency.forexBuying) / quotationCurrency.forexBuying
                    
            if quotationPart:
                quotationPart.totalPrice1 = float(quotationPart.unitPrice1) * float(quotationPart.quantity)
            instance.totalPrice = float(instance.unitPrice) * float(instance.quantity)
            
        if getattr(senderInquiryPart, "totalPrice") != getattr(instance, "totalPrice"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
                instance.totalPrice = 0
                if quotationPart:
                    quotationPart.unitPrice1 = 0
                    quotationPart.totalPrice1 = 0
            else:
                if quotationPart:
                    quotationPart.unitPrice1 = (instance.unitPrice * inquiryCurrency.forexBuying) / quotationCurrency.forexBuying
                    quotationPart.totalPrice1 = float(quotationPart.unitPrice1) * float(quotationPart.quantity)
                    quotationPart.unitPrice2 = round(float(quotationPart.unitPrice1) * float(1 + (float(quotationPart.profit)/100)), 2)
                    quotationPart.totalPrice2 = round(float(quotationPart.unitPrice2) * float(quotationPart.quantity), 2)
                    quotationPart.unitPrice3 = round(float(quotationPart.unitPrice2) * float(1 - (float(quotationPart.discount)/100)), 2)
                    quotationPart.totalPrice3 = round(float(quotationPart.unitPrice3) * float(quotationPart.quantity), 2)
                instance.unitPrice = float(instance.totalPrice) / float(instance.quantity)
            if quotationPart:
                quotationPart.save()
        #print("bruası çalıştı")
        #inquiry total fiyatları günceller
        inquiry = instance.inquiry
        inquiryParts = inquiry.inquirypart_set.select_related().filter(sourceCompany = senderInquiryPart.sourceCompany,inquiry = instance.inquiry).exclude(id=instance.id)
        partsTotalTotalPrice = 0
        for inquiryPart in inquiryParts:
            partsTotalTotalPrice = partsTotalTotalPrice + (inquiryPart.unitPrice * inquiryPart.quantity)
        inquiry.totalTotalPrice = round(partsTotalTotalPrice + (instance.unitPrice * instance.quantity),2)
        inquiry.save()
        
        # Para miktarını belirtilen formatta gösterme
        totalTotalPriceFixed = "{:,.2f}".format(round(inquiry.totalTotalPrice,2))
        # Nokta ile virgülü değiştirme
        totalTotalPriceFixed = totalTotalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        totalPrices = {"inquiry":inquiry.id,
                        "totalTotalPrice":totalTotalPriceFixed,
                        "currency":inquiry.currency.symbol}
        
        updateDetail(totalPrices,"inquiry_update")
        inquiryPdfInTask.delay(inquiry.id,senderInquiryPart.sourceCompany.id)           

          
@receiver(pre_save, sender=QuotationPart)
def update_total_price_or_unit_price_quotation(sender, instance, **kwargs):

    # request = [
    #     frame_record[0].f_locals["request"]
    #     for frame_record in inspect.stack()
    #     if frame_record[3] == "get_response"
    # ][0]
    
    if sender.objects.select_related().filter(id=instance.id).exists():
        senderQuotationPart = sender.objects.select_related("inquiryPart").get(id=instance.id)
        
        if getattr(senderQuotationPart, "sequency") != getattr(instance, "sequency"):
            
            with transaction.atomic():
                quotation = instance.quotation
                new_sequency = instance.sequency
                if senderQuotationPart.sequency < new_sequency:
                    QuotationPart.objects.select_related().filter(
                        sourceCompany = senderQuotationPart.sourceCompany,
                        quotation=quotation,
                        sequency__gt=senderQuotationPart.sequency,
                        sequency__lte=new_sequency
                    ).exclude(pk=instance.pk).update(sequency=F('sequency') - 1)
                else:
                    QuotationPart.objects.select_related().filter(
                        sourceCompany = senderQuotationPart.sourceCompany,
                        quotation=quotation,
                        sequency__lt=senderQuotationPart.sequency,
                        sequency__gte=new_sequency
                    ).exclude(pk=instance.pk).update(sequency=F('sequency') + 1)
        
        instance.totalPrice1 = float(instance.unitPrice1) * float(instance.quantity)
        
        if getattr(senderQuotationPart, "quantity") != getattr(instance, "quantity"):
            if float(instance.quantity) == 0:
                instance.unitPrice1 = 0
            if float(senderQuotationPart.quantity) == 0:
                instance.unitPrice1 = senderQuotationPart.inquiryPart.unitPrice
            instance.unitPrice2 = round(float(instance.unitPrice1) * float(1 + (float(instance.profit)/100)), 2)
            instance.totalPrice2 = round(float(instance.unitPrice2) * float(instance.quantity), 2)
            instance.unitPrice3 = round(float(instance.unitPrice2) * float(1 - (float(instance.discount)/100)), 2)
            instance.totalPrice3 = round(float(instance.unitPrice3) * float(instance.quantity), 2)
            instance.inquiryPart.quantity = instance.quantity
            instance.inquiryPart.save()
            instance.inquiryPart.requestPart.quantity = instance.quantity
            instance.inquiryPart.requestPart.save()
        
        
        if getattr(senderQuotationPart, "profit") != getattr(instance, "profit"):
            instance.unitPrice2 = round(float(instance.unitPrice1) * float(1 + (float(instance.profit)/100)), 2)
            instance.totalPrice2 = round(float(instance.unitPrice2) * float(instance.quantity), 2)
            instance.unitPrice3 = round(float(instance.unitPrice2) * float(1 - (float(instance.discount)/100)), 2)
            instance.totalPrice3 = round(float(instance.unitPrice3) * float(instance.quantity), 2)
            
        elif getattr(senderQuotationPart, "unitPrice2") != getattr(instance, "unitPrice2"):
            if float(instance.unitPrice1) == 0:
                instance.profit = 0
            else:
                instance.profit = round(((float(instance.unitPrice2) / float(instance.unitPrice1)) - 1) * 100, 2)
            instance.totalPrice2 = round(float(instance.unitPrice2) * float(instance.quantity), 2)
            instance.unitPrice3 = round(float(instance.unitPrice2) * float(1 - (float(instance.discount)/100)), 2)
            instance.totalPrice3 = round(float(instance.unitPrice3) * float(instance.quantity), 2)
            
        elif getattr(senderQuotationPart, "totalPrice2") != getattr(instance, "totalPrice2"):
            if float(instance.quantity) == 0:
                instance.unitPrice2 = 0
            else:
                instance.unitPrice2 = round(float(instance.totalPrice2) / float(instance.quantity), 2)
            if float(instance.unitPrice1) == 0:
                instance.profit = 0
            else:
                instance.profit = round(((float(instance.unitPrice2) / float(instance.unitPrice1)) - 1) * 100, 2)
            instance.unitPrice3 = round(float(instance.unitPrice2) * float(1 - (float(instance.discount)/100)), 2)
            instance.totalPrice3 = round(float(instance.unitPrice3) * float(instance.quantity), 2)
        
        elif getattr(senderQuotationPart, "discount") != getattr(instance, "discount"):
            instance.unitPrice3 = round(float(instance.unitPrice2) * float(1 - (float(instance.discount)/100)), 2)
            instance.totalPrice3 = round(float(instance.unitPrice3) * float(instance.quantity), 2)
            
        elif getattr(senderQuotationPart, "unitPrice3") != getattr(instance, "unitPrice3"):
            if float(instance.unitPrice2) == 0:
                instance.discount = 0
            else:
                instance.discount = round(((float(instance.unitPrice3) / float(instance.unitPrice2)) - 1) * 100, 2)
            instance.totalPrice3 = round(float(instance.unitPrice3) * float(instance.quantity), 2)
            
        elif getattr(senderQuotationPart, "totalPrice3") != getattr(instance, "totalPrice3"):
            if float(instance.quantity) == 0:
                instance.unitPrice3 = 0
            else:
                instance.unitPrice3 = round(float(instance.totalPrice3) / float(instance.quantity), 2)
            if float(instance.unitPrice2) == 0:
                instance.discount= 0
            else:
                instance.discount = abs(round(((float(instance.unitPrice3) / float(instance.unitPrice2)) - 1) * 100, 2))
                
        #quotation total fiyatları günceller
        quotation = Quotation.objects.select_related().filter(id = instance.quotation.id).first()
        quotationParts = quotation.quotationpart_set.select_related().filter(sourceCompany = senderQuotationPart.sourceCompany,quotation = instance.quotation).exclude(id=instance.id)
        quotationExtras = quotation.quotationextra_set.select_related().filter(sourceCompany = senderQuotationPart.sourceCompany,quotation = instance.quotation)

        partsTotalBuyingPrice = 0
        partsTotalSellingPrice = 0
        for quotationPart in quotationParts:
            partsTotalBuyingPrice = partsTotalBuyingPrice + (quotationPart.unitPrice1 * quotationPart.quantity)
            partsTotalSellingPrice = partsTotalSellingPrice + (quotationPart.unitPrice3 * quotationPart.quantity)
        for quotationExtra in quotationExtras:
            partsTotalSellingPrice = partsTotalSellingPrice + (quotationExtra.unitPrice * quotationExtra.quantity)
        quotation.totalBuyingPrice = round(partsTotalBuyingPrice + (instance.unitPrice1 * instance.quantity),2)
        quotation.totalSellingPrice = round((partsTotalSellingPrice + (instance.unitPrice3 * instance.quantity)) - quotation.totalDiscountPrice,2)
        quotation.save()
        
        if quotation.totalSellingPrice == 0 or quotation.totalSellingPrice < 0 and quotation.totalBuyingPrice == 0:
            totalProfitPrice = 0
        else:
            totalProfitPrice = round(((quotation.totalSellingPrice / quotation.totalBuyingPrice) - 1) * 100,2)
        
        # Para miktarını belirtilen formatta gösterme
        totalBuyingPriceFixed = "{:,.2f}".format(quotation.totalBuyingPrice)
        totalGrossPriceFixed = "{:,.2f}".format(quotation.totalSellingPrice + quotation.totalDiscountPrice)
        totalDiscountPriceFixed = "{:,.2f}".format(quotation.totalDiscountPrice)
        totalSellingPriceFixed = "{:,.2f}".format(quotation.totalSellingPrice)
        totalProfitAmountPriceFixed = "{:,.2f}".format(round(quotation.totalSellingPrice - quotation.totalBuyingPrice,2))
        # Nokta ile virgülü değiştirme
        totalBuyingPriceFixed = totalBuyingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalGrossPriceFixed = totalGrossPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalDiscountPriceFixed = totalDiscountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalSellingPriceFixed = totalSellingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalProfitAmountPriceFixed = totalProfitAmountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        totalPrices = {"quotation":quotation.id,
                        "totalBuyingPrice":totalBuyingPriceFixed,
                        "totalGrossPrice":totalGrossPriceFixed,
                        "totalDiscountPrice":totalDiscountPriceFixed,
                        "totalSellingPrice":totalSellingPriceFixed,
                        "totalProfitAmountPrice":totalProfitAmountPriceFixed,
                        "totalProfitPrice":totalProfitPrice,
                        "currency":quotation.currency.symbol}
        
        updateDetail(totalPrices,"quotation_update")
        
        #####order confirmation tetiklemesi#####
        try:
            orderConfirmation = quotation.order_confirmation_quotation
            vatAmount = quotation.totalSellingPrice * (orderConfirmation.vat/100)
            
            if quotation.totalSellingPrice == 0 or quotation.totalSellingPrice < 0 and quotation.totalBuyingPrice == 0:
                totalProfitPrice = 0
            else:
                totalProfitPrice = round(((quotation.totalSellingPrice / quotation.totalBuyingPrice) - 1) * 100,2)
            
            # Para miktarını belirtilen formatta gösterme
            totalBuyingPriceFixed = "{:,.2f}".format(quotation.totalBuyingPrice)
            totalGrossPriceFixed = "{:,.2f}".format(quotation.totalSellingPrice + quotation.totalDiscountPrice)
            totalDiscountPriceFixed = "{:,.2f}".format(quotation.totalDiscountPrice)
            totalVatPriceFixed = "{:,.2f}".format(vatAmount)
            totalSellingPriceFixed = "{:,.2f}".format(quotation.totalSellingPrice + vatAmount)
            totalProfitAmountPriceFixed = "{:,.2f}".format(round(quotation.totalSellingPrice - quotation.totalBuyingPrice,2))
            # Nokta ile virgülü değiştirme
            totalBuyingPriceFixed = totalBuyingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalGrossPriceFixed = totalGrossPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalDiscountPriceFixed = totalDiscountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalVatPriceFixed = totalVatPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalSellingPriceFixed = totalSellingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalProfitAmountPriceFixed = totalProfitAmountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')

            totalPrices = {"orderConfirmation":orderConfirmation.id,
                                "totalBuyingPrice":totalBuyingPriceFixed,
                                "totalGrossPrice":totalGrossPriceFixed,
                                "totalDiscountPrice":totalDiscountPriceFixed,
                                "totalVatPrice":totalVatPriceFixed,
                                "totalSellingPrice":totalSellingPriceFixed,
                                "totalProfitAmountPrice":totalProfitAmountPriceFixed,
                                "totalProfitPrice":totalProfitPrice,
                                "currency":quotation.currency.symbol}
                
            updateDetail(totalPrices,"order_confirmation_update")
        except:
            pass
        #####order confirmation tetiklemesi-end#####
        
        quotationPdfInTask.delay(quotation.id,senderQuotationPart.sourceCompany.id)
        
@receiver(pre_save, sender=QuotationExtra)
def update_total_price_or_unit_price_quotation_extra(sender, instance, **kwargs):

    # request = [
    #     frame_record[0].f_locals["request"]
    #     for frame_record in inspect.stack()
    #     if frame_record[3] == "get_response"
    # ][0]
    
    if sender.objects.select_related().filter(id=instance.id).exists():
        senderQuotationExtra = sender.objects.select_related().get(id=instance.id)
        
        instance.totalPrice = float(instance.unitPrice) * float(instance.quantity)
        
        if getattr(senderQuotationExtra, "quantity") != getattr(instance, "quantity"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
            instance.totalPrice = round(float(instance.unitPrice) * float(instance.quantity), 2)
            
        elif getattr(senderQuotationExtra, "unitPrice") != getattr(instance, "unitPrice"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
            instance.totalPrice = round(float(instance.unitPrice) * float(instance.quantity), 2)
            
        elif getattr(senderQuotationExtra, "totalPrice") != getattr(instance, "totalPrice"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
                instance.totalPrice = 0
            else:
                instance.unitPrice = round(float(instance.totalPrice) / float(instance.quantity), 2)
                
        #quotation total fiyatları günceller
        quotation = Quotation.objects.select_related().filter(id = instance.quotation.id).first()
        quotationParts = quotation.quotationpart_set.select_related().filter(sourceCompany = senderQuotationExtra.sourceCompany,quotation = instance.quotation)
        quotationExtras = quotation.quotationextra_set.select_related().filter(sourceCompany = senderQuotationExtra.sourceCompany,quotation = instance.quotation).exclude(id=instance.id)

        partsTotalBuyingPrice = 0
        partsTotalSellingPrice = 0
        for quotationPart in quotationParts:
            partsTotalBuyingPrice = partsTotalBuyingPrice + (quotationPart.unitPrice1 * quotationPart.quantity)
            partsTotalSellingPrice = partsTotalSellingPrice + (quotationPart.unitPrice3 * quotationPart.quantity)
        for quotationExtra in quotationExtras:
            partsTotalSellingPrice = partsTotalSellingPrice + (quotationExtra.unitPrice * quotationExtra.quantity)
        quotation.totalSellingPrice = round((partsTotalSellingPrice + (instance.unitPrice * instance.quantity)) - quotation.totalDiscountPrice,2)
        quotation.save()
        
        if quotation.totalSellingPrice == 0 or quotation.totalSellingPrice < 0 and quotation.totalBuyingPrice == 0:
            totalProfitPrice = 0
        else:
            totalProfitPrice = round(((quotation.totalSellingPrice / quotation.totalBuyingPrice) - 1) * 100,2)
        
        # Para miktarını belirtilen formatta gösterme
        totalBuyingPriceFixed = "{:,.2f}".format(quotation.totalBuyingPrice)
        totalGrossPriceFixed = "{:,.2f}".format(quotation.totalSellingPrice + quotation.totalDiscountPrice)
        totalDiscountPriceFixed = "{:,.2f}".format(quotation.totalDiscountPrice)
        totalSellingPriceFixed = "{:,.2f}".format(quotation.totalSellingPrice)
        totalProfitAmountPriceFixed = "{:,.2f}".format(round(quotation.totalSellingPrice - quotation.totalBuyingPrice,2))
        # Nokta ile virgülü değiştirme
        totalBuyingPriceFixed = totalBuyingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalGrossPriceFixed = totalGrossPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalDiscountPriceFixed = totalDiscountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalSellingPriceFixed = totalSellingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalProfitAmountPriceFixed = totalProfitAmountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        totalPrices = {"quotation":quotation.id,
                        "totalBuyingPrice":totalBuyingPriceFixed,
                        "totalGrossPrice":totalGrossPriceFixed,
                        "totalDiscountPrice":totalDiscountPriceFixed,
                        "totalSellingPrice":totalSellingPriceFixed,
                        "totalProfitAmountPrice":totalProfitAmountPriceFixed,
                        "totalProfitPrice":totalProfitPrice,
                        "currency":quotation.currency.symbol}
        
        updateDetail(totalPrices,"quotation_update")
        
        #####order confirmation tetiklemesi#####
        try:
            orderConfirmation = quotation.order_confirmation_quotation
            vatAmount = quotation.totalSellingPrice * (orderConfirmation.vat/100)
            
            if quotation.totalSellingPrice == 0 or quotation.totalSellingPrice < 0 and quotation.totalBuyingPrice == 0:
                totalProfitPrice = 0
            else:
                totalProfitPrice = round(((quotation.totalSellingPrice / quotation.totalBuyingPrice) - 1) * 100,2)
            
            # Para miktarını belirtilen formatta gösterme
            totalBuyingPriceFixed = "{:,.2f}".format(quotation.totalBuyingPrice)
            totalGrossPriceFixed = "{:,.2f}".format(quotation.totalSellingPrice + quotation.totalDiscountPrice)
            totalDiscountPriceFixed = "{:,.2f}".format(quotation.totalDiscountPrice)
            totalVatPriceFixed = "{:,.2f}".format(vatAmount)
            totalSellingPriceFixed = "{:,.2f}".format(quotation.totalSellingPrice + vatAmount)
            totalProfitAmountPriceFixed = "{:,.2f}".format(round(quotation.totalSellingPrice - quotation.totalBuyingPrice,2))
            # Nokta ile virgülü değiştirme
            totalBuyingPriceFixed = totalBuyingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalGrossPriceFixed = totalGrossPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalDiscountPriceFixed = totalDiscountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalVatPriceFixed = totalVatPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalSellingPriceFixed = totalSellingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalProfitAmountPriceFixed = totalProfitAmountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')

            totalPrices = {"orderConfirmation":orderConfirmation.id,
                                "totalBuyingPrice":totalBuyingPriceFixed,
                                "totalGrossPrice":totalGrossPriceFixed,
                                "totalDiscountPrice":totalDiscountPriceFixed,
                                "totalVatPrice":totalVatPriceFixed,
                                "totalSellingPrice":totalSellingPriceFixed,
                                "totalProfitAmountPrice":totalProfitAmountPriceFixed,
                                "totalProfitPrice":totalProfitPrice,
                                "currency":quotation.currency.symbol}
                
            updateDetail(totalPrices,"order_confirmation_update")
        except:
            pass
        #####order confirmation tetiklemesi-end#####
        
        quotationPdfInTask.delay(quotation.id,senderQuotationExtra.sourceCompany.id)
    

@receiver(pre_save, sender=PurchaseOrderPart)
def update_total_price_or_unit_price_purchase_order(sender, instance, **kwargs):
    
    if sender.objects.filter(id=instance.id).exists():
        senderPurchaseOrderPart = sender.objects.select_related("purchaseOrder").get(id=instance.id)
        
        if getattr(senderPurchaseOrderPart, "sequency") != getattr(instance, "sequency"):
            
            with transaction.atomic():
                purchaseOrder = instance.purchaseOrder
                new_sequency = instance.sequency
                if senderPurchaseOrderPart.sequency < new_sequency:
                    PurchaseOrderPart.objects.filter(
                        sourceCompany = senderPurchaseOrderPart.sourceCompany,
                        purchaseOrder=purchaseOrder,
                        sequency__gt=senderPurchaseOrderPart.sequency,
                        sequency__lte=new_sequency
                    ).exclude(pk=instance.pk).update(sequency=F('sequency') - 1)
                else:
                    PurchaseOrderPart.objects.filter(
                        sourceCompany = senderPurchaseOrderPart.sourceCompany,
                        purchaseOrder=purchaseOrder,
                        sequency__lt=senderPurchaseOrderPart.sequency,
                        sequency__gte=new_sequency
                    ).exclude(pk=instance.pk).update(sequency=F('sequency') + 1)
        
        purchaseOrder =  senderPurchaseOrderPart.purchaseOrder       
        purchaseOrderPdfInTask.delay(purchaseOrder.id,senderPurchaseOrderPart.sourceCompany.id)
        
        
       
    
        
                