from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet, Q, Prefetch, OuterRef
from django.http import JsonResponse
from django_filters import filters
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter, BaseFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend as DatatablesFilterBackendDT
from rest_framework_datatables.django_filters.filterset import DatatablesFilterSet
from rest_framework_datatables.django_filters.filters import GlobalFilter
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend, FilterSet, ChoiceFilter, CharFilter

from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet, EditorModelMixin
#from rest_framework_datatables_editor.filters import DatatablesFilterBackend
from rest_framework.viewsets import ModelViewSet

from django.db.models import F, Value
from django.db.models.functions import Concat

from datetime import datetime
from django.utils import timezone

from report.api.serializers import *
from sale.models import Project, Request, Inquiry, OrderConfirmation, Quotation, PurchaseOrder, OrderTracking
from card.models import Company
from account.models import SendInvoice,IncomingInvoice,Payment
from source.models import Bank as SourceBank

def setup_eager_loading(get_queryset):
    def decorator(self):
        queryset = get_queryset(self)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset

    return decorator

def bankProcess(bankNames, startDate, endDate, sourceCompany):
        paymentInBankUSDTotal = 0
        paymentInBankEURTotal = 0
        paymentInBankTRYTotal = 0
        paymentInBankRUBTotal = 0

        paymentInBanksUSD = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "USD", type = "in", sourceBank__bankName = bankNames[0], paymentDate__range=(startDate,endDate))
        paymentInBanksEUR = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "EUR", type = "in", sourceBank__bankName = bankNames[1], paymentDate__range=(startDate,endDate))
        paymentInBanksTRY = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "TRY", type = "in", sourceBank__bankName = bankNames[2], paymentDate__range=(startDate,endDate))
        paymentInBanksRUB = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "RUB", type = "in", sourceBank__bankName = bankNames[3], paymentDate__range=(startDate,endDate))
        
        for paymentInBankUSD in paymentInBanksUSD:
            print(paymentInBankUSD.paymentDate)
            paymentInBankUSDTotal = paymentInBankUSDTotal + paymentInBankUSD.amount
            
        for paymentInBankEUR in paymentInBanksEUR:
            paymentInBankEURTotal = paymentInBankEURTotal + paymentInBankEUR.amount
            
        for paymentInBankTRY in paymentInBanksTRY:
            paymentInBankTRYTotal = paymentInBankTRYTotal + paymentInBankTRY.amount
            
        for paymentInBankRUB in paymentInBanksRUB:
            paymentInBankRUBTotal = paymentInBankRUBTotal + paymentInBankRUB.amount
        
        # Para miktarını belirtilen formatta gösterme
        paymentInBankUSDTotalFixed = "{:,.2f}".format(round(paymentInBankUSDTotal,2))
        paymentInBankEURTotalFixed = "{:,.2f}".format(round(paymentInBankEURTotal,2))
        paymentInBankTRYTotalFixed = "{:,.2f}".format(round(paymentInBankTRYTotal,2))
        paymentInBankRUBTotalFixed = "{:,.2f}".format(round(paymentInBankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        paymentInBankUSDTotalFixed = paymentInBankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInBankEURTotalFixed = paymentInBankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInBankTRYTotalFixed = paymentInBankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInBankRUBTotalFixed = paymentInBankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        paymentOutBankUSDTotal = 0
        paymentOutBankEURTotal = 0
        paymentOutBankTRYTotal = 0
        paymentOutBankRUBTotal = 0
        
        paymentOutBanksUSD= Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "USD", type = "out", sourceBank__bankName = bankNames[0], paymentDate = datetime.today().date())
        paymentOutBanksEUR = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "EUR", type = "out", sourceBank__bankName = bankNames[1], paymentDate = datetime.today().date())
        paymentOutBanksTRY = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "TRY", type = "out", sourceBank__bankName = bankNames[2], paymentDate = datetime.today().date())
        paymentOutBanksRUB= Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "RUB", type = "out", sourceBank__bankName = bankNames[3], paymentDate = datetime.today().date())
        
        for paymentOutBankUSD in paymentOutBanksUSD:
            paymentOutBankUSDTotal = paymentOutBankUSDTotal + paymentOutBankUSD.amount
            
        for paymentOutBankEUR in paymentOutBanksEUR:
            paymentOutBankEURTotal = paymentOutBankEURTotal + paymentOutBankEUR.amount
            
        for paymentOutBankTRY in paymentOutBanksTRY:
            paymentOutBankTRYTotal = paymentOutBankTRYTotal + paymentOutBankTRY.amount
            
        for paymentOutBankRUB in paymentOutBanksRUB:
            paymentOutBankRUBTotal = paymentOutBankRUBTotal + paymentOutBankRUB.amount
        
        # Para miktarını belirtilen formatta gösterme
        paymentOutBankUSDTotalFixed = "{:,.2f}".format(round(paymentOutBankUSDTotal,2))
        paymentOutBankEURTotalFixed = "{:,.2f}".format(round(paymentOutBankEURTotal,2))
        paymentOutBankTRYTotalFixed = "{:,.2f}".format(round(paymentOutBankTRYTotal,2))
        paymentOutBankRUBTotalFixed = "{:,.2f}".format(round(paymentOutBankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        paymentOutBankUSDTotalFixed = paymentOutBankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentOutBankEURTotalFixed = paymentOutBankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentOutBankTRYTotalFixed = paymentOutBankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentOutBankRUBTotalFixed = paymentOutBankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        #balance
        balancePaymentBankUSDTotal = paymentInBankUSDTotal - paymentOutBankUSDTotal
        balancePaymentBankEURTotal = paymentInBankEURTotal - paymentOutBankEURTotal
        balancePaymentBankTRYTotal = paymentInBankTRYTotal - paymentOutBankTRYTotal
        balancePaymentBankRUBTotal = paymentInBankRUBTotal - paymentOutBankRUBTotal
        
        # Para miktarını belirtilen formatta gösterme
        balancePaymentBankUSDTotalFixed = "{:,.2f}".format(round(balancePaymentBankUSDTotal,2))
        balancePaymentBankEURTotalFixed = "{:,.2f}".format(round(balancePaymentBankEURTotal,2))
        balancePaymentBankTRYTotalFixed = "{:,.2f}".format(round(balancePaymentBankTRYTotal,2))
        balancePaymentBankRUBTotalFixed = "{:,.2f}".format(round(balancePaymentBankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        balancePaymentBankUSDTotalFixed = balancePaymentBankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balancePaymentBankEURTotalFixed = balancePaymentBankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balancePaymentBankTRYTotalFixed = balancePaymentBankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balancePaymentBankRUBTotalFixed = balancePaymentBankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        bankUSD = SourceBank.objects.select_related().filter(company = sourceCompany, currency__code = "USD", bankName = bankNames[0]).first()
        bankEUR = SourceBank.objects.select_related().filter(company = sourceCompany, currency__code = "EUR", bankName = bankNames[1]).first()
        bankTRY = SourceBank.objects.select_related().filter(company = sourceCompany, currency__code = "TRY", bankName = bankNames[2]).first()
        bankRUB = SourceBank.objects.select_related().filter(company = sourceCompany, currency__code = "RUB", bankName = bankNames[3]).first()
        
        if bankUSD:
            bankUSDTotal = bankUSD.balance
        else:
            bankUSDTotal = 0
            
        if bankEUR:
            bankEURTotal = bankEUR.balance
        else:
            bankEURTotal = 0
            
        if bankTRY:
            bankTRYTotal = bankTRY.balance
        else:
            bankTRYTotal = 0
            
        if bankRUB:
            bankRUBTotal = bankRUB.balance
        else:
            bankRUBTotal = 0
        
        # Para miktarını belirtilen formatta gösterme
        bankUSDTotalFixed = "{:,.2f}".format(round(bankUSDTotal,2))
        bankEURTotalFixed = "{:,.2f}".format(round(bankEURTotal,2))
        bankTRYTotalFixed = "{:,.2f}".format(round(bankTRYTotal,2))
        bankRUBTotalFixed = "{:,.2f}".format(round(bankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        bankUSDTotalFixed = bankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankEURTotalFixed = bankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankTRYTotalFixed = bankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankRUBTotalFixed = bankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')

        return Response([
            {
                'type': 'transferBalance',
                'usd': balancePaymentBankUSDTotalFixed,
                'eur': balancePaymentBankEURTotalFixed,
                'try': balancePaymentBankTRYTotalFixed,
                'rub': balancePaymentBankRUBTotalFixed
            },
            {
                'type': 'inAmount',
                'usd': paymentInBankUSDTotalFixed,
                'eur': paymentInBankEURTotalFixed,
                'try': paymentInBankTRYTotalFixed,
                'rub': paymentInBankRUBTotalFixed
            },
            {
                'type': 'outAmount',
                'usd': paymentOutBankUSDTotalFixed,
                'eur': paymentOutBankEURTotalFixed,
                'try': paymentOutBankTRYTotalFixed,
                'rub': paymentOutBankRUBTotalFixed
            },
            {
                'type': 'balance',
                'usd': bankUSDTotalFixed,
                'eur': bankEURTotalFixed,
                'try': bankTRYTotalFixed,
                'rub': bankRUBTotalFixed
            }
        ])

def orderProcess(startDate, endDate, sourceCompany):
        #order confirmation
        orderConfirmationUSDTotal = 0
        orderConfirmationEURTotal = 0
        orderConfirmationTRYTotal = 0
        orderConfirmationRUBTotal = 0
        orderConfirmationsUSD= OrderConfirmation.objects.select_related("quotation").filter(sourceCompany = sourceCompany, quotation__currency__code = "USD", orderConfirmationDate__range=(startDate,endDate))
        orderConfirmationsEUR = OrderConfirmation.objects.select_related("quotation").filter(sourceCompany = sourceCompany, quotation__currency__code = "EUR", orderConfirmationDate__range=(startDate,endDate))
        orderConfirmationsTRY = OrderConfirmation.objects.select_related("quotation").filter(sourceCompany = sourceCompany, quotation__currency__code = "TRY", orderConfirmationDate__range=(startDate,endDate))
        orderConfirmationsRUB= OrderConfirmation.objects.select_related("quotation").filter(sourceCompany = sourceCompany, quotation__currency__code = "RUB", orderConfirmationDate__range=(startDate,endDate))
        
        for orderConfirmationUSD in orderConfirmationsUSD:
            orderConfirmationUSDTotal = orderConfirmationUSDTotal + orderConfirmationUSD.quotation.totalSellingPrice
            
        for orderConfirmationEUR in orderConfirmationsEUR:
            orderConfirmationEURTotal = orderConfirmationEURTotal + orderConfirmationEUR.quotation.totalSellingPrice
            
        for orderConfirmationTRY in orderConfirmationsTRY:
            orderConfirmationTRYTotal = orderConfirmationTRYTotal + orderConfirmationTRY.quotation.totalSellingPrice
            
        for orderConfirmationRUB in orderConfirmationsRUB:
            orderConfirmationRUBTotal = orderConfirmationRUBTotal + orderConfirmationRUB.quotation.totalSellingPrice
        
        # Para miktarını belirtilen formatta gösterme
        orderConfirmationUSDTotalFixed = "{:,.2f}".format(round(orderConfirmationUSDTotal,2))
        orderConfirmationEURTotalFixed = "{:,.2f}".format(round(orderConfirmationEURTotal,2))
        orderConfirmationTRYTotalFixed = "{:,.2f}".format(round(orderConfirmationTRYTotal,2))
        orderConfirmationRUBTotalFixed = "{:,.2f}".format(round(orderConfirmationRUBTotal,2))
        # Nokta ile virgülü değiştirme
        orderConfirmationUSDTotalFixed = orderConfirmationUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        orderConfirmationEURTotalFixed = orderConfirmationEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        orderConfirmationTRYTotalFixed = orderConfirmationTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        orderConfirmationRUBTotalFixed = orderConfirmationRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                
        #purchase order
        purchaseOrderUSDTotal = 0
        purchaseOrderEURTotal = 0
        purchaseOrderTRYTotal = 0
        purchaseOrderRUBTotal = 0
        
        purchaseOrdersUSD= PurchaseOrder.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "USD", purchaseOrderDate__range=(startDate,endDate))
        purchaseOrdersEUR = PurchaseOrder.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "EUR", purchaseOrderDate__range=(startDate,endDate))
        purchaseOrdersTRY = PurchaseOrder.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "TRY", purchaseOrderDate__range=(startDate,endDate))
        purchaseOrdersRUB= PurchaseOrder.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "RUB", purchaseOrderDate__range=(startDate,endDate))
        
        for purchaseOrderUSD in purchaseOrdersUSD:
            purchaseOrderUSDTotal = purchaseOrderUSDTotal + purchaseOrderUSD.totalTotalPrice
            
        for purchaseOrderEUR in purchaseOrdersEUR:
            purchaseOrderEURTotal = purchaseOrderEURTotal + purchaseOrderEUR.totalTotalPrice
            
        for purchaseOrderTRY in purchaseOrdersTRY:
            purchaseOrderTRYTotal = purchaseOrderTRYTotal + purchaseOrderTRY.totalTotalPrice
            
        for purchaseOrderRUB in purchaseOrdersRUB:
            purchaseOrderRUBTotal = purchaseOrderRUBTotal + purchaseOrderRUB.totalTotalPrice
        
        # Para miktarını belirtilen formatta gösterme
        purchaseOrderUSDTotalFixed = "{:,.2f}".format(round(purchaseOrderUSDTotal,2))
        purchaseOrderEURTotalFixed = "{:,.2f}".format(round(purchaseOrderEURTotal,2))
        purchaseOrderTRYTotalFixed = "{:,.2f}".format(round(purchaseOrderTRYTotal,2))
        purchaseOrderRUBTotalFixed = "{:,.2f}".format(round(purchaseOrderRUBTotal,2))
        # Nokta ile virgülü değiştirme
        purchaseOrderUSDTotalFixed = purchaseOrderUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        purchaseOrderEURTotalFixed = purchaseOrderEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        purchaseOrderTRYTotalFixed = purchaseOrderTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        purchaseOrderRUBTotalFixed = purchaseOrderRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        #balance
        balanceUSDTotal = orderConfirmationUSDTotal - purchaseOrderUSDTotal
        balanceEURTotal = orderConfirmationEURTotal - purchaseOrderEURTotal
        balanceTRYTotal = orderConfirmationTRYTotal - purchaseOrderTRYTotal
        balanceRUBTotal = orderConfirmationRUBTotal - purchaseOrderRUBTotal
        
        # Para miktarını belirtilen formatta gösterme
        balanceUSDTotalFixed = "{:,.2f}".format(round(balanceUSDTotal,2))
        balanceEURTotalFixed = "{:,.2f}".format(round(balanceEURTotal,2))
        balanceTRYTotalFixed = "{:,.2f}".format(round(balanceTRYTotal,2))
        balanceRUBTotalFixed = "{:,.2f}".format(round(balanceRUBTotal,2))
        # Nokta ile virgülü değiştirme
        balanceUSDTotalFixed = balanceUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balanceEURTotalFixed = balanceEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balanceTRYTotalFixed = balanceTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balanceRUBTotalFixed = balanceRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')

        return Response([
            {
                'type': 'orderConfirmationAmount',
                'usd': orderConfirmationUSDTotalFixed,
                'eur': orderConfirmationEURTotalFixed,
                'try': orderConfirmationTRYTotalFixed,
                'rub': orderConfirmationRUBTotalFixed
            },
            {
                'type': 'purchaseOrderAmount',
                'usd': purchaseOrderUSDTotalFixed,
                'eur': purchaseOrderEURTotalFixed,
                'try': purchaseOrderTRYTotalFixed,
                'rub': purchaseOrderRUBTotalFixed
            },
            {
                'type': 'balanceAmount',
                'usd': balanceUSDTotalFixed,
                'eur': balanceEURTotalFixed,
                'try': balanceTRYTotalFixed,
                'rub': balanceRUBTotalFixed
            }
        ])

def sendInvoiceProcess(startDate, endDate, sourceCompany):
        #send invoice
        sendInvoiceUSDTotal = 0
        sendInvoiceEURTotal = 0
        sendInvoiceTRYTotal = 0
        sendInvoiceRUBTotal = 0
        
        sendInvoicesUSD= SendInvoice.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "USD", group = "order", sendInvoiceDate__range=(startDate,endDate))
        sendInvoicesEUR = SendInvoice.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "EUR", group = "order", sendInvoiceDate__range=(startDate,endDate))
        sendInvoicesTRY = SendInvoice.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "TRY", group = "order", sendInvoiceDate__range=(startDate,endDate))
        sendInvoicesRUB= SendInvoice.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "RUB", group = "order", sendInvoiceDate__range=(startDate,endDate))
        
        for sendInvoiceUSD in sendInvoicesUSD:
            sendInvoiceUSDTotal = sendInvoiceUSDTotal + sendInvoiceUSD.totalPrice
            
        for sendInvoiceEUR in sendInvoicesEUR:
            sendInvoiceEURTotal = sendInvoiceEURTotal + sendInvoiceEUR.totalPrice
            
        for sendInvoiceTRY in sendInvoicesTRY:
            sendInvoiceTRYTotal = sendInvoiceTRYTotal + sendInvoiceTRY.totalPrice
            
        for sendInvoiceRUB in sendInvoicesRUB:
            sendInvoiceRUBTotal = sendInvoiceRUBTotal + sendInvoiceRUB.totalPrice
        
        # Para miktarını belirtilen formatta gösterme
        sendInvoiceUSDTotalFixed = "{:,.2f}".format(round(sendInvoiceUSDTotal,2))
        sendInvoiceEURTotalFixed = "{:,.2f}".format(round(sendInvoiceEURTotal,2))
        sendInvoiceTRYTotalFixed = "{:,.2f}".format(round(sendInvoiceTRYTotal,2))
        sendInvoiceRUBTotalFixed = "{:,.2f}".format(round(sendInvoiceRUBTotal,2))
        # Nokta ile virgülü değiştirme
        sendInvoiceUSDTotalFixed = sendInvoiceUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        sendInvoiceEURTotalFixed = sendInvoiceEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        sendInvoiceTRYTotalFixed = sendInvoiceTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        sendInvoiceRUBTotalFixed = sendInvoiceRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')

        return Response([
            {
                'type': 'amount',
                'usd': sendInvoiceUSDTotalFixed,
                'eur': sendInvoiceEURTotalFixed,
                'try': sendInvoiceTRYTotalFixed,
                'rub': sendInvoiceRUBTotalFixed
            }
        ])

def incomingInvoiceProcess(startDate, endDate, sourceCompany):
        #send invoice
        incomingInvoiceUSDTotal = 0
        incomingInvoiceEURTotal = 0
        incomingInvoiceTRYTotal = 0
        incomingInvoiceRUBTotal = 0
        
        incomingInvoicesUSD= IncomingInvoice.objects.select_related().filter(sourceCompany = sourceCompany,currency__code = "USD", incomingInvoiceDate__range=(startDate,endDate))
        incomingInvoicesEUR = IncomingInvoice.objects.select_related().filter(sourceCompany = sourceCompany,currency__code = "EUR", incomingInvoiceDate__range=(startDate,endDate))
        incomingInvoicesTRY = IncomingInvoice.objects.select_related().filter(sourceCompany = sourceCompany,currency__code = "TRY", incomingInvoiceDate__range=(startDate,endDate))
        incomingInvoicesRUB= IncomingInvoice.objects.select_related().filter(sourceCompany = sourceCompany,currency__code = "RUB", incomingInvoiceDate__range=(startDate,endDate))
        
        for incomingInvoiceUSD in incomingInvoicesUSD:
            incomingInvoiceUSDTotal = incomingInvoiceUSDTotal + incomingInvoiceUSD.totalPrice
            
        for incomingInvoiceEUR in incomingInvoicesEUR:
            incomingInvoiceEURTotal = incomingInvoiceEURTotal + incomingInvoiceEUR.totalPrice
            
        for incomingInvoiceTRY in incomingInvoicesTRY:
            incomingInvoiceTRYTotal = incomingInvoiceTRYTotal + incomingInvoiceTRY.totalPrice
            
        for incomingInvoiceRUB in incomingInvoicesRUB:
            incomingInvoiceRUBTotal = incomingInvoiceRUBTotal + incomingInvoiceRUB.totalPrice
        
        # Para miktarını belirtilen formatta gösterme
        incomingInvoiceUSDTotalFixed = "{:,.2f}".format(round(incomingInvoiceUSDTotal,2))
        incomingInvoiceEURTotalFixed = "{:,.2f}".format(round(incomingInvoiceEURTotal,2))
        incomingInvoiceTRYTotalFixed = "{:,.2f}".format(round(incomingInvoiceTRYTotal,2))
        incomingInvoiceRUBTotalFixed = "{:,.2f}".format(round(incomingInvoiceRUBTotal,2))
        # Nokta ile virgülü değiştirme
        incomingInvoiceUSDTotalFixed = incomingInvoiceUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        incomingInvoiceEURTotalFixed = incomingInvoiceEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        incomingInvoiceTRYTotalFixed = incomingInvoiceTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        incomingInvoiceRUBTotalFixed = incomingInvoiceRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')

        return Response([
            {
                'type': 'amount',
                'usd': incomingInvoiceUSDTotalFixed,
                'eur': incomingInvoiceEURTotalFixed,
                'try': incomingInvoiceTRYTotalFixed,
                'rub': incomingInvoiceRUBTotalFixed
            }
        ])

def paymentProcess(type, startDate, endDate, sourceCompany):
        #payment in
        paymentUSDTotal = 0
        paymentEURTotal = 0
        paymentTRYTotal = 0
        paymentRUBTotal = 0
        
        paymentsUSD= Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "USD", type = type, paymentDate__range=(startDate,endDate))
        paymentsEUR = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "EUR", type = type, paymentDate__range=(startDate,endDate))
        paymentsTRY = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "TRY", type = type, paymentDate__range=(startDate,endDate))
        paymentsRUB= Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "RUB", type = type, paymentDate__range=(startDate,endDate))
        
        for paymentUSD in paymentsUSD:
            paymentUSDTotal = paymentUSDTotal + paymentUSD.amount
            
        for paymentEUR in paymentsEUR:
            paymentEURTotal = paymentEURTotal + paymentEUR.amount
            
        for paymentTRY in paymentsTRY:
            paymentTRYTotal = paymentTRYTotal + paymentTRY.amount
            
        for paymentRUB in paymentsRUB:
            paymentRUBTotal = paymentRUBTotal + paymentRUB.amount
        
        # Para miktarını belirtilen formatta gösterme
        paymentUSDTotalFixed = "{:,.2f}".format(round(paymentUSDTotal,2))
        paymentEURTotalFixed = "{:,.2f}".format(round(paymentEURTotal,2))
        paymentTRYTotalFixed = "{:,.2f}".format(round(paymentTRYTotal,2))
        paymentRUBTotalFixed = "{:,.2f}".format(round(paymentRUBTotal,2))
        # Nokta ile virgülü değiştirme
        paymentUSDTotalFixed = paymentUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentEURTotalFixed = paymentEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentTRYTotalFixed = paymentTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentRUBTotalFixed = paymentRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')

        return Response([
            {
                'type': 'amount',
                'usd': paymentUSDTotalFixed,
                'eur': paymentEURTotalFixed,
                'try': paymentTRYTotalFixed,
                'rub': paymentRUBTotalFixed
            }
        ])
        


class FinancialReportOrderList(APIView):
    def get(self, request):
        if request.GET.get("startdate") == "":
            startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        else:
            startDate = datetime.strptime(request.GET.get("startdate"), "%d/%m/%Y").date()
            
        if request.GET.get("enddate") == "":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("enddate"), "%d/%m/%Y").date()
        #startDate = datetime.today().date()
        #endDate = datetime.today().date()
        
        return orderProcess(startDate, endDate, self.request.user.profile.sourceCompany)
        
class FinancialReportOrderYearList(APIView):
    def get(self, request):
        startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        endDate = datetime.today().date()
        
        return orderProcess(startDate, endDate, self.request.user.profile.sourceCompany)
        
class FinancialReportSendInvoiceList(APIView):
    def get(self, request):
        if request.GET.get("startdate") == "":
            startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        else:
            startDate = datetime.strptime(request.GET.get("startdate"), "%d/%m/%Y").date()
            
        if request.GET.get("enddate") == "":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("enddate"), "%d/%m/%Y").date()
        
        return sendInvoiceProcess(startDate, endDate, self.request.user.profile.sourceCompany)

class FinancialReportIncomingInvoiceList(APIView):
    def get(self, request):
        if request.GET.get("startdate") == "":
            startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        else:
            startDate = datetime.strptime(request.GET.get("startdate"), "%d/%m/%Y").date()
            
        if request.GET.get("enddate") == "":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("enddate"), "%d/%m/%Y").date()
        
        return incomingInvoiceProcess(startDate, endDate, self.request.user.profile.sourceCompany)

class FinancialReportPaymentInList(APIView):
    def get(self, request):
        type = "in"
        if request.GET.get("startdate") == "":
            startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        else:
            startDate = datetime.strptime(request.GET.get("startdate"), "%d/%m/%Y").date()
            
        if request.GET.get("enddate") == "":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("enddate"), "%d/%m/%Y").date()
        
        return paymentProcess(type, startDate, endDate, self.request.user.profile.sourceCompany)

class FinancialReportPaymentOutList(APIView):
    def get(self, request):
        type = "out"
        if request.GET.get("startdate") == "":
            startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        else:
            startDate = datetime.strptime(request.GET.get("startdate"), "%d/%m/%Y").date()
            
        if request.GET.get("enddate") == "":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("enddate"), "%d/%m/%Y").date()
        
        return paymentProcess(type, startDate, endDate, self.request.user.profile.sourceCompany)

class FinancialReportBankHalkbankList(APIView):
    def get(self, request):
        bankNames = ["HALKBANK USD","HALKBANK EUR","HALKBANK TL","HALKBANK RUB"]
        if request.GET.get("startdate") == "":
            startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        else:
            startDate = datetime.strptime(request.GET.get("startdate"), "%d/%m/%Y").date()
            
        if request.GET.get("enddate") == "":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("enddate"), "%d/%m/%Y").date()
        
        return bankProcess(bankNames, startDate, endDate, self.request.user.profile.sourceCompany)

class FinancialReportBankVakifbankList(APIView):
    def get(self, request):
        bankNames = ["VAKIFBANK USD","VAKIFBANK EUR","VAKIFBANK TL","VAKIFBANK RUB"]
        if request.GET.get("startdate") == "":
            startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        else:
            startDate = datetime.strptime(request.GET.get("startdate"), "%d/%m/%Y").date()
            
        if request.GET.get("enddate") == "":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("enddate"), "%d/%m/%Y").date()
        
        return bankProcess(bankNames, startDate, endDate, self.request.user.profile.sourceCompany)

class FinancialReportBankIsbankList(APIView):
    def get(self, request):
        bankNames = ["İŞ BANKASI USD","İŞ BANKASI EUR","İŞ BANKASI TL","İŞ BANKASI RUB"]
        if request.GET.get("startdate") == "":
            startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        else:
            startDate = datetime.strptime(request.GET.get("startdate"), "%d/%m/%Y").date()
            
        if request.GET.get("enddate") == "":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("enddate"), "%d/%m/%Y").date()
        
        return bankProcess(bankNames, startDate, endDate, self.request.user.profile.sourceCompany)

class FinancialReportBankAlbarakaturkList(APIView):
    def get(self, request):
        bankNames = ["ALBARAKA TÜRK KATILIM BANKASI A.Ş.","ALBARAKA TÜRK KATILIM BANKASI A.Ş.","ALBARAKA TÜRK KATILIM BANKASI A.Ş.","ALBARAKA TÜRK KATILIM BANKASI A.Ş."]
        if request.GET.get("startdate") == "":
            startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        else:
            startDate = datetime.strptime(request.GET.get("startdate"), "%d/%m/%Y").date()
            
        if request.GET.get("enddate") == "":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("enddate"), "%d/%m/%Y").date()
        
        return bankProcess(bankNames, startDate, endDate, self.request.user.profile.sourceCompany)

class FinancialReportBankEmlakkatilimList(APIView):
    def get(self, request):
        bankNames = ["TÜRKİYE EMLAK KATILIM BANKASI A.Ş.","TÜRKİYE EMLAK KATILIM BANKASI A.Ş.","TÜRKİYE EMLAK KATILIM BANKASI A.Ş.","TÜRKİYE EMLAK KATILIM BANKASI A.Ş."]
        if request.GET.get("startdate") == "":
            startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        else:
            startDate = datetime.strptime(request.GET.get("startdate"), "%d/%m/%Y").date()
            
        if request.GET.get("enddate") == "":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("enddate"), "%d/%m/%Y").date()
        
        return bankProcess(bankNames, startDate, endDate, self.request.user.profile.sourceCompany)

class FinancialReportBankVakifkatilimList(APIView):
    def get(self, request):
        bankNames = ["VAKIF KATILIM BANKASI A.Ş.","VAKIF KATILIM BANKASI A.Ş.","VAKIF KATILIM BANKASI A.Ş.","VAKIF KATILIM BANKASI A.Ş."]
        if request.GET.get("startdate") == "":
            startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        else:
            startDate = datetime.strptime(request.GET.get("startdate"), "%d/%m/%Y").date()
            
        if request.GET.get("enddate") == "":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("enddate"), "%d/%m/%Y").date()
        
        return bankProcess(bankNames, startDate, endDate, self.request.user.profile.sourceCompany)

class FinancialReportBankZiraatkatilimList(APIView):
    def get(self, request):
        bankNames = ["ZİRAAT KATILIM BANKASI A.Ş.","ZİRAAT KATILIM BANKASI A.Ş.","ZİRAAT KATILIM BANKASI A.Ş.","ZİRAAT KATILIM BANKASI A.Ş."]
        if request.GET.get("startdate") == "":
            startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
        else:
            startDate = datetime.strptime(request.GET.get("startdate"), "%d/%m/%Y").date()
            
        if request.GET.get("enddate") == "":
            endDate = datetime.today().date()
        else:
            endDate = datetime.strptime(request.GET.get("enddate"), "%d/%m/%Y").date()
        
        return bankProcess(bankNames, startDate, endDate, self.request.user.profile.sourceCompany)


class FinancialReportBankTotalList(APIView):
    def get(self, request):
        banksUSD = SourceBank.objects.select_related().filter(company = self.request.user.profile.sourceCompany, currency__code = "USD")
        banksEUR = SourceBank.objects.select_related().filter(company = self.request.user.profile.sourceCompany, currency__code = "EUR")
        banksTRY = SourceBank.objects.select_related().filter(company = self.request.user.profile.sourceCompany, currency__code = "TRY")
        banksRUB = SourceBank.objects.select_related().filter(company = self.request.user.profile.sourceCompany, currency__code = "RUB")
        
        bankUSDTotal = 0
        bankEURTotal = 0
        bankTRYTotal = 0
        bankRUBTotal = 0
        
        for bankUSD in banksUSD:
            bankUSDTotal = bankUSDTotal + bankUSD.balance
        for bankEUR in banksEUR:
            bankEURTotal = bankEURTotal + bankEUR.balance
        for bankTRY in banksTRY:
            bankTRYTotal = bankTRYTotal + bankTRY.balance
        for bankRUB in banksRUB:
            bankRUBTotal = bankRUBTotal + bankRUB.balance
        
        # Para miktarını belirtilen formatta gösterme
        bankUSDTotalFixed = "{:,.2f}".format(round(bankUSDTotal,2))
        bankEURTotalFixed = "{:,.2f}".format(round(bankEURTotal,2))
        bankTRYTotalFixed = "{:,.2f}".format(round(bankTRYTotal,2))
        bankRUBTotalFixed = "{:,.2f}".format(round(bankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        bankUSDTotalFixed = bankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankEURTotalFixed = bankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankTRYTotalFixed = bankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankRUBTotalFixed = bankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        return Response([
            {
                'type': 'balance',
                'usd': bankUSDTotalFixed,
                'eur': bankEURTotalFixed,
                'try': bankTRYTotalFixed,
                'rub': bankRUBTotalFixed
            }
        ])

