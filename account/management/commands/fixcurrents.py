from django.core.management.base import BaseCommand, CommandError
from sale.models import QuotationPart,Quotation
from account.models import ProformaInvoicePart, SendInvoicePart, ProformaInvoice, SendInvoice,Payment, IncomingInvoice, Process

from card.models import Current,Company, Currency
from source.models import Bank

import pandas as pd
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None

    def add_arguments(self, parser):
        parser.add_argument('company', type=int, help='Company Id')

    def handle(self, *args, **kwargs):
        app = kwargs['company']
        
        if app == 0:
            companiess = Company.objects.select_related().filter()
        else:
            companiess = Company.objects.select_related().filter(id = app)
            
        currentss = Current.objects.select_related().filter()
        bankss = Bank.objects.select_related().filter()
        sendInvoicess = SendInvoice.objects.select_related().filter()
        incomingInvoicess = IncomingInvoice.objects.select_related().filter()
            
        #carileri sıfırlar
        for current in currentss:
            current.debt = 0
            current.credit = 0
            current.save()
        
        #bankaları sıfırlar
        for bank in bankss:
            bank.balance = 0
            bank.save()
            
        #invoice paid sıfırlar
        for sendInvoice in sendInvoicess:
            sendInvoice.paidPrice = 0
            sendInvoice.payed = False
            sendInvoice.save()
        #invoice paid sıfırlar
        for incomingInvoice in incomingInvoicess:
            incomingInvoice.paidPrice = 0
            incomingInvoice.payed = False
            incomingInvoice.save()

        #send invoice düzeltmesi
        for company in companiess:
            #company debtleri sıfırlar
            company.debt = 0
            company.save()
            
            theCompanyCurrencies = []
            sendInvoices = SendInvoice.objects.select_related("currency").filter(customer = company)
            incomingInvoices = IncomingInvoice.objects.select_related("currency").filter(seller = company)
            
            for sendInvoice in sendInvoices:
                theCompanyCurrencies.append(sendInvoice.currency)
                
            for incomingInvoice in incomingInvoices:
                theCompanyCurrencies.append(incomingInvoice.currency)
            
            theCompanyCurrencies = list(set(theCompanyCurrencies))
            
            overPaidJSON = {}
            
            for currency in theCompanyCurrencies:
                sendInvoices = SendInvoice.objects.select_related().filter(customer = company, currency = currency)
                incomingInvoices = IncomingInvoice.objects.select_related().filter(seller = company, currency = currency)
                
                print("para birimi: " + str(currency.code))
                for sendInvoice in sendInvoices:
                    print("send invoice para birimleri: " + str(sendInvoice.currency.code))
                for incomingInvoice in incomingInvoices:
                    print("incoming invoice para birimleri: " + str(incomingInvoice.currency.code))
                    
                sendInvoiceTotal = 0
                incomingInvoiceTotal = 0
                
                if sendInvoices:
                    for sendInvoice in sendInvoices:
                        sendInvoiceTotal = sendInvoiceTotal + sendInvoice.totalPrice
                
                if incomingInvoices:
                    for incomingInvoice in incomingInvoices:
                        incomingInvoiceTotal = incomingInvoiceTotal + incomingInvoice.totalPrice
                    
                invoiceTotal = sendInvoiceTotal - incomingInvoiceTotal
                
                current = Current.objects.filter(company = company, currency = currency).first()
                print("current: " + str(current))
                if current:
                    current.debt = invoiceTotal
                    current.save()
                else:
                    current = Current.objects.create(
                        company = company,
                        currency = currency
                    )
                    current.save()
                    current.debt = invoiceTotal
                    current.save()
                    
                company.debt = invoiceTotal
                company.save()
                
                if sendInvoices:
                    for sendInvoice in sendInvoices:
                        process = Process.objects.select_related().filter(company = company, sendInvoice = sendInvoice).first()
                        
                        if process:
                            process.amount = sendInvoice.totalPrice
                            process.save()
                        else:
                            if sendInvoice.user:
                                user = sendInvoice.user
                            else:
                                user = None
                                
                            process = Process.objects.create(
                                user = sendInvoice.user,
                                company = company,
                                sendInvoice = sendInvoice,
                                companyName = company.name,
                                sourceNo = sendInvoice.sendInvoiceNo,
                                type = "send_invoice",
                                amount = sendInvoice.totalPrice,
                                currency = currency,
                                processDateTime = sendInvoice.created_date
                            )
                            process.save()
                            
                            identificationCode = "PRC"
                            yearCode = int(str(datetime.today().date().year)[-2:])
                            startCodeValue = 1
                            
                            lastProcess = Process.objects.filter(yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                            
                            if lastProcess:
                                lastCode = lastProcess.code
                            else:
                                lastCode = startCodeValue - 1
                            
                            code = int(lastCode) + 1
                            process.code = code
                            
                            process.yearCode = yearCode
                            
                            processNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
                            process.processNo = processNo
                            
                            process.save()
                            
                if incomingInvoices:
                    for incomingInvoice in incomingInvoices:
                        process = Process.objects.select_related().filter(company = company, incomingInvoice = incomingInvoice).first()
                        
                        if process:
                            process.amount = incomingInvoice.totalPrice
                            process.save()
                        else:
                            if incomingInvoice.user:
                                user = incomingInvoice.user
                            else:
                                user = None
                                
                            process = Process.objects.create(
                                user = user,
                                company = company,
                                incomingInvoice = incomingInvoice,
                                companyName = company.name,
                                sourceNo = incomingInvoice.incomingInvoiceNo,
                                type = "incoming_invoice",
                                amount = incomingInvoice.totalPrice,
                                currency = currency,
                                processDateTime = incomingInvoice.created_date
                            )
                            process.save()
                            
                            identificationCode = "PRC"
                            yearCode = int(str(datetime.today().date().year)[-2:])
                            startCodeValue = 1
                            
                            lastProcess = Process.objects.filter(yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                            
                            if lastProcess:
                                lastCode = lastProcess.code
                            else:
                                lastCode = startCodeValue - 1
                            
                            code = int(lastCode) + 1
                            process.code = code
                            
                            process.yearCode = yearCode
                            
                            processNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
                            process.processNo = processNo
                            
                            process.save()

                payments = Payment.objects.select_related().filter(customer = company, currency = currency)
                
                if payments:
                    extraPaidTotal = 0
                    for payment in payments:
                        if payment.type == "in":
                            print("payment in: " + str(payment))
                            if payment.sourceBank:
                                sourceBank = payment.sourceBank
                                sourceBank.balance = float(sourceBank.balance) + float(payment.amount)
                                sourceBank.save()
                                
                            invoiceJSON = payment.invoices
                            invoices = invoiceJSON["sendInvoices"]
                            if len(invoices) > 0:
                                current = Current.objects.filter(company = company, currency = currency).first()
                                
                                if current:
                                    current.credit = current.credit + payment.amount
                                    current.save()
                                else:
                                    current = Current.objects.create(
                                        company = company,
                                        currency = currency
                                    )
                                    current.save()
                                    current.credit = current.credit + payment.amount
                                    current.save()
                                    
                                company.debt = company.debt - payment.amount
                                company.save()
                                
                                paidPrice = payment.amount
                                paidAmount = 0
                                
                                for invoice in invoices:
                                    if paidPrice > 0:
                                        theSendInvoice = SendInvoice.objects.filter(id = int(invoice["invoice"])).first()
                                        print("payment send invoice: " + str(theSendInvoice.sendInvoiceNoSys))
                                        paidAmount = paidPrice
                                        paidPrice = float(paidPrice) - float((theSendInvoice.totalPrice - theSendInvoice.paidPrice))
                                        if paidPrice >= 0:
                                            theSendInvoice.paidPrice = theSendInvoice.totalPrice
                                            theSendInvoice.payed = True
                                        else:
                                            theSendInvoice.paidPrice = theSendInvoice.paidPrice + paidAmount
                                            theSendInvoice.save()
                                            break
                                        theSendInvoice.save()
                                
                                #burada ekstra ödenen tutarları toplar
                                if paidPrice > 0:
                                    extraPaidTotal = extraPaidTotal + paidPrice
                                    
                            else:
                                current = Current.objects.filter(company = company, currency = currency).first()
                                
                                if current:
                                    current.credit = current.credit + payment.amount
                                    current.save()
                                else:
                                    current = Current.objects.create(
                                        company = company,
                                        currency = currency
                                    )
                                    current.save()
                                    current.credit = current.credit + payment.amount
                                    current.save()
                                
                            process = Process.objects.filter(company = company, payment = payment).first()
                            
                            if process:
                                process.amount = payment.amount
                                process.save()
                            else:
                                if sendInvoice.user:
                                    user = sendInvoice.user
                                else:
                                    user = None
                                process = Process.objects.create(
                                    user = user,
                                    company = company,
                                    payment = payment,
                                    companyName = company.name,
                                    sourceNo = payment.paymentNo,
                                    type = "payment_in",
                                    amount = payment.amount,
                                    currency = currency,
                                    processDateTime = payment.created_date
                                )
                                process.save()
                                
                                identificationCode = "PRC"
                                yearCode = int(str(datetime.today().date().year)[-2:])
                                startCodeValue = 1
                                
                                lastProcess = Process.objects.filter(yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                                
                                if lastProcess:
                                    lastCode = lastProcess.code
                                else:
                                    lastCode = startCodeValue - 1
                                
                                code = int(lastCode) + 1
                                process.code = code
                                
                                process.yearCode = yearCode
                                
                                processNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
                                process.processNo = processNo
                                
                                process.save()

                        elif payment.type == "out":
                            print("payment out: " + str(payment))
                            if payment.sourceBank:
                                sourceBank = payment.sourceBank
                                sourceBank.balance = float(sourceBank.balance) - float(payment.amount)
                                sourceBank.save()
                            invoiceJSON = payment.invoices
                            invoices = invoiceJSON["incomingInvoices"]
                            
                            if len(invoices) > 0:
                                current = Current.objects.filter(company = company, currency = currency).first()
                                
                                if current:
                                    current.credit = current.credit - payment.amount
                                    current.save()
                                else:
                                    current = Current.objects.create(
                                        company = company,
                                        currency = currency
                                    )
                                    current.save()
                                    current.credit = current.credit - payment.amount
                                    current.save()
                                    
                                company.debt = company.debt + payment.amount
                                company.save()
                                
                                paidPrice = payment.amount
                                paidAmount = 0
                                
                                for invoice in invoices:
                                    theIncomingInvoice = IncomingInvoice.objects.filter(id = int(invoice["invoice"])).first()
                                    paidAmount = paidPrice
                                    paidPrice = float(paidPrice) - float(theIncomingInvoice.totalPrice)
                                    if paidPrice >= 0:
                                        theIncomingInvoice.paidPrice = theIncomingInvoice.totalPrice
                                        theIncomingInvoice.payed = True
                                    else:
                                        theIncomingInvoice.paidPrice = theIncomingInvoice.paidPrice + paidAmount
                                        theIncomingInvoice.save()
                                        break
                                    theIncomingInvoice.save()
                            else:
                                current = Current.objects.filter(company = company, currency = currency).first()
                                
                                if current:
                                    current.credit = current.credit - payment.amount
                                    current.save()
                                else:
                                    current = Current.objects.create(
                                        company = company,
                                        currency = currency
                                    )
                                    current.save()
                                    current.credit = current.credit - payment.amount
                                    current.save()
                                    
                            process = Process.objects.filter(company = company, payment = payment).first()
                            
                            if process:
                                process.amount = payment.amount
                                process.save()
                            else:
                                if sendInvoice.user:
                                    user = sendInvoice.user
                                else:
                                    user = None
                                process = Process.objects.create(
                                    user = user,
                                    company = company,
                                    payment = payment,
                                    companyName = company.name,
                                    sourceNo = payment.paymentNo,
                                    type = "payment_out",
                                    amount = payment.amount,
                                    currency = currency,
                                    processDateTime = payment.created_date
                                )
                                process.save()
                                
                                identificationCode = "PRC"
                                yearCode = int(str(datetime.today().date().year)[-2:])
                                startCodeValue = 1
                                
                                lastProcess = Process.objects.filter(yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                                
                                if lastProcess:
                                    lastCode = lastProcess.code
                                else:
                                    lastCode = startCodeValue - 1
                                
                                code = int(lastCode) + 1
                                process.code = code
                                
                                process.yearCode = yearCode
                                
                                processNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
                                process.processNo = processNo
                                
                                process.save()
                                
                    overPaidJSON[currency.code] = extraPaidTotal
                    
                print("\n") 
            
            print(f"ödemelerden artan tutar: {overPaidJSON}")
            company.overPaid = overPaidJSON
            company.save()
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                                  
        #send invoice düzeltmesi
        # for sendInvoice in sendInvoices:
        #     sendInvoicess = SendInvoice.objects.filter(customer = sendInvoice.customer, currency = sendInvoice.currency)
        #     incomingInvoicess = IncomingInvoice.objects.filter(seller = sendInvoice.customer, currency = sendInvoice.currency)
        #     sendInvoiceTotal = 0
        #     for sendInvoicee in sendInvoicess:
        #         sendInvoiceTotal = sendInvoiceTotal + sendInvoicee.totalPrice
        #     incomingInvoiceTotal = 0
        #     for incomingInvoicee in incomingInvoicess:
        #         incomingInvoiceTotal = incomingInvoiceTotal + incomingInvoicee.totalPrice

        #     invoiceTotal = sendInvoiceTotal- incomingInvoiceTotal
                
        #     current = Current.objects.filter(company = sendInvoice.customer, currency = sendInvoice.currency).first()
        #     if current:
        #         current.debt = invoiceTotal
        #         current.save()
        #     else:
        #         current = Current.objects.create(
        #             company = sendInvoice.customer,
        #             currency = sendInvoice.currency
        #         )
        #         current.save()
        #         current.debt = invoiceTotal
        #         current.save()
            
        #     sendInvoice.customer.debt = invoiceTotal
        #     sendInvoice.customer.save()
            
        #     process = Process.objects.filter(company = sendInvoice.customer, sendInvoice = sendInvoice).first()
        #     if process:
        #         process.amount = sendInvoice.totalPrice
        #         process.save()
        #     else:
        #         process = Process.objects.create(
        #             user = sendInvoice.user,
        #             company = sendInvoice.customer,
        #             sendInvoice = sendInvoice,
        #             companyName = sendInvoice.customer.name,
        #             sourceNo = sendInvoice.sendInvoiceNo,
        #             type = "send_invoice",
        #             amount = sendInvoice.totalPrice,
        #             currency = sendInvoice.currency,
        #             processDateTime = sendInvoice.created_date
        #         )
        #         process.save()
                
        #         identificationCode = "PRC"
        #         yearCode = int(str(datetime.today().date().year)[-2:])
        #         startCodeValue = 1
                
        #         lastProcess = Process.objects.filter(yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                
        #         if lastProcess:
        #             lastCode = lastProcess.code
        #         else:
        #             lastCode = startCodeValue - 1
                
        #         code = int(lastCode) + 1
        #         process.code = code
                
        #         process.yearCode = yearCode
                
        #         processNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        #         process.processNo = processNo
                
        #         process.save()
        
        # #incoming invoice düzeltmesi
        # for incomingInvoice in incomingInvoices:
        #     sendInvoicess = SendInvoice.objects.filter(customer = incomingInvoice.seller, currency = incomingInvoice.currency)
        #     incomingInvoicess = IncomingInvoice.objects.filter(seller = incomingInvoice.seller, currency = incomingInvoice.currency)
        #     sendInvoiceTotal = 0
        #     for sendInvoicee in sendInvoicess:
        #         sendInvoiceTotal = sendInvoiceTotal + sendInvoicee.totalPrice
        #     incomingInvoiceTotal = 0
        #     for incomingInvoicee in incomingInvoicess:
        #         incomingInvoiceTotal = incomingInvoiceTotal + incomingInvoicee.totalPrice
    
        #     invoiceTotal = sendInvoiceTotal - incomingInvoiceTotal
                
        #     current = Current.objects.filter(company = incomingInvoice.seller, currency = incomingInvoice.currency).first()
        #     if current:
        #         current.debt = invoiceTotal
        #         current.save()
        #     else:
        #         current = Current.objects.create(
        #             company = incomingInvoice.seller,
        #             currency = incomingInvoice.currency
        #         )
        #         current.save()
        #         current.debt = invoiceTotal
        #         current.save()
            
        #     incomingInvoice.seller.debt = invoiceTotal
        #     incomingInvoice.seller.save()
        #     process = Process.objects.filter(company = incomingInvoice.seller, incomingInvoice = incomingInvoice).first()
        #     if process:
        #         process.amount = incomingInvoice.totalPrice
        #         process.save()
        #     else:
        #         process = Process.objects.create(
        #             user = incomingInvoice.user,
        #             company = incomingInvoice.seller,
        #             incomingInvoice = incomingInvoice,
        #             companyName = incomingInvoice.seller.name,
        #             sourceNo = incomingInvoice.incomingInvoiceNo,
        #             type = "incoming_invoice",
        #             amount = incomingInvoice.totalPrice,
        #             currency = incomingInvoice.currency,
        #             processDateTime = sendInvoice.created_date
        #         )
        #         process.save()
                
        #         identificationCode = "PRC"
        #         yearCode = int(str(datetime.today().date().year)[-2:])
        #         startCodeValue = 1
                
        #         lastProcess = Process.objects.filter(yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                
        #         if lastProcess:
        #             lastCode = lastProcess.code
        #         else:
        #             lastCode = startCodeValue - 1
                
        #         code = int(lastCode) + 1
        #         process.code = code
                
        #         process.yearCode = yearCode
                
        #         processNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        #         process.processNo = processNo
                
        #         process.save()
        
        # #payment düzeltmesi
        # for index, payment in enumerate(paymentss):
        #     if payment.type == "in":
        #         print(str(index + 1) + " / " + str(len(paymentss)))
        #         print(payment.sourceBank)
        #         if payment.sourceBank:
        #             sourceBank = payment.sourceBank
        #             sourceBank.balance = float(sourceBank.balance) + float(payment.amount)
        #             sourceBank.save()
        #         invoiceJSON = payment.invoices
        #         invoices = invoiceJSON["sendInvoices"]
        #         if len(invoices) > 0:
        #             current = Current.objects.filter(company = payment.customer, currency = payment.currency).first()
        #             if current:
        #                 current.credit = current.credit + payment.amount
        #                 current.save()
        #             else:
        #                 current = Current.objects.create(
        #                     company = payment.customer,
        #                     currency = payment.currency
        #                 )
        #                 current.save()
        #                 current.credit = current.credit + payment.amount
        #                 current.save()
                    
        #             payment.customer.debt = payment.customer.debt - payment.amount
        #             payment.customer.save()
        #         else:
        #             current = Current.objects.filter(company = payment.customer, currency = payment.currency).first()
        #             if current:
        #                 current.credit = current.credit + payment.amount
        #                 current.save()
        #             else:
        #                 current = Current.objects.create(
        #                     company = payment.customer,
        #                     currency = payment.currency
        #                 )
        #                 current.save()
        #                 current.credit = current.credit + payment.amount
        #                 current.save()
                        
        #         process = Process.objects.filter(company = payment.customer, payment = payment).first()
        #         if process:
        #             process.amount = payment.amount
        #             process.save()
        #         else:
        #             process = Process.objects.create(
        #                 user = payment.user,
        #                 company = payment.customer,
        #                 payment = payment,
        #                 companyName = payment.customer.name,
        #                 sourceNo = payment.paymentNo,
        #                 type = "payment_in",
        #                 amount = payment.amount,
        #                 currency = payment.currency,
        #                 processDateTime = sendInvoicee.created_date
        #             )
        #             process.save()
                    
        #             identificationCode = "PRC"
        #             yearCode = int(str(datetime.today().date().year)[-2:])
        #             startCodeValue = 1
                    
        #             lastProcess = Process.objects.filter(yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                    
        #             if lastProcess:
        #                 lastCode = lastProcess.code
        #             else:
        #                 lastCode = startCodeValue - 1
                    
        #             code = int(lastCode) + 1
        #             process.code = code
                    
        #             process.yearCode = yearCode
                    
        #             processNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        #             process.processNo = processNo
                    
        #             process.save()
                        
        #     elif payment.type == "out":
        #         if payment.sourceBank:
        #             sourceBank = payment.sourceBank
        #             sourceBank.balance = float(sourceBank.balance) - float(payment.amount)
        #             sourceBank.save()
        #         invoiceJSON = payment.invoices
        #         invoices = invoiceJSON["incomingInvoices"]
        #         if len(invoices) > 0:
        #             current = Current.objects.filter(company = payment.customer, currency = payment.currency).first()
        #             if current:
        #                 current.credit = current.credit - payment.amount
        #                 current.save()
        #             else:
        #                 current = Current.objects.create(
        #                     company = payment.customer,
        #                     currency = payment.currency
        #                 )
        #                 current.save()
        #                 current.credit = current.credit - payment.amount
        #                 current.save()
                    
        #             payment.customer.debt = payment.customer.debt + payment.amount
        #             payment.customer.save()
        #         else:
        #             current = Current.objects.filter(company = payment.customer, currency = payment.currency).first()
        #             if current:
        #                 current.credit = current.credit - payment.amount
        #                 current.save()
        #             else:
        #                 current = Current.objects.create(
        #                     company = payment.customer,
        #                     currency = payment.currency
        #                 )
        #                 current.save()
        #                 current.credit = current.credit - payment.amount
        #                 current.save()
                        
        #         process = Process.objects.filter(company = payment.customer, payment = payment).first()
        #         if process:
        #             process.amount = payment.amount
        #             process.save()
        #         else:
        #             process = Process.objects.create(
        #                 user = payment.user,
        #                 company = payment.customer,
        #                 payment = payment,
        #                 companyName = payment.customer.name,
        #                 sourceNo = payment.paymentNo,
        #                 type = "payment_out",
        #                 amount = payment.amount,
        #                 currency = payment.currency,
        #                 processDateTime = sendInvoicee.created_date
        #             )
        #             process.save()
                    
        #             identificationCode = "PRC"
        #             yearCode = int(str(datetime.today().date().year)[-2:])
        #             startCodeValue = 1
                    
        #             lastProcess = Process.objects.filter(yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                    
        #             if lastProcess:
        #                 lastCode = lastProcess.code
        #             else:
        #                 lastCode = startCodeValue - 1
                    
        #             code = int(lastCode) + 1
        #             process.code = code
                    
        #             process.yearCode = yearCode
                    
        #             processNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        #             process.processNo = processNo
                    
        #             process.save()
                