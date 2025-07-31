from card.models import Currency, Current
from account.models import SendInvoice, IncomingInvoice

from decimal import Decimal

def convert_currency(amount,oldCurrencyRate,newCurrencyRate):
    amount = round(amount,2)
    return float(round(Decimal(str(amount)) * (Decimal(str(oldCurrencyRate)) / Decimal(str(newCurrencyRate))),2))

def round_price(amount):
    # Para miktarını belirtilen formatta gösterme
    amountFixed = "{:,.2f}".format(round(amount,2))
    # Nokta ile virgülü değiştirme
    amountFixed = amountFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')

    return amountFixed

def total_customer_soa(sourceCompany):
    currentObjects = SendInvoice.objects.select_related("currency").filter(sourceCompany = sourceCompany)

    totals = {
        "USD": {"total": 0, "paid": 0},
        "EUR": {"total": 0, "paid": 0},
        "GBP": {"total": 0, "paid": 0},
        "QAR": {"total": 0, "paid": 0},
        "RUB": {"total": 0, "paid": 0},
        "JPY": {"total": 0, "paid": 0},
        "TRY": {"total": 0, "paid": 0}
    }
    
    for current in currentObjects:
        currency_code = current.currency.code
        if currency_code in totals:
            totals[currency_code]["total"] += current.totalPrice
            totals[currency_code]["paid"] += current.paidPrice

    external_data = [{
        "USD" : {"total" : round_price(totals["USD"]["total"]), "paid" : round_price(totals["USD"]["paid"]), "balance" : round_price((totals["USD"]["total"] - totals["USD"]["paid"]))},
        "EUR" : {"total" : round_price(totals["EUR"]["total"]), "paid" : round_price(totals["EUR"]["paid"]), "balance" : round_price((totals["EUR"]["total"] - totals["EUR"]["paid"]))},
        "GBP" : {"total" : round_price(totals["GBP"]["total"]), "paid" : round_price(totals["GBP"]["paid"]), "balance" : round_price((totals["GBP"]["total"] - totals["GBP"]["paid"]))},
        "QAR" : {"total" : round_price(totals["QAR"]["total"]), "paid" : round_price(totals["QAR"]["paid"]), "balance" : round_price((totals["QAR"]["total"] - totals["QAR"]["paid"]))},
        "RUB" : {"total" : round_price(totals["RUB"]["total"]), "paid" : round_price(totals["RUB"]["paid"]), "balance" : round_price((totals["RUB"]["total"] - totals["RUB"]["paid"]))},
        "JPY" : {"total" : round_price(totals["JPY"]["total"]), "paid" : round_price(totals["JPY"]["paid"]), "balance" : round_price((totals["JPY"]["total"] - totals["JPY"]["paid"]))},
        "TRY" : {"total" : round_price(totals["TRY"]["total"]), "paid" : round_price(totals["TRY"]["paid"]), "balance" : round_price((totals["TRY"]["total"] - totals["TRY"]["paid"]))}
    }]

    return external_data

def total_supplier_soa(sourceCompany):
    currentObjects = IncomingInvoice.objects.select_related("currency").filter(sourceCompany = sourceCompany)

    totals = {
        "USD": {"total": 0, "paid": 0},
        "EUR": {"total": 0, "paid": 0},
        "GBP": {"total": 0, "paid": 0},
        "QAR": {"total": 0, "paid": 0},
        "RUB": {"total": 0, "paid": 0},
        "JPY": {"total": 0, "paid": 0},
        "TRY": {"total": 0, "paid": 0}
    }
    
    for current in currentObjects:
        currency_code = current.currency.code
        if currency_code in totals:
            totals[currency_code]["total"] += current.totalPrice
            totals[currency_code]["paid"] += current.paidPrice

    external_data = [{
        "USD" : {"total" : round_price(totals["USD"]["total"]), "paid" : round_price(totals["USD"]["paid"]), "balance" : round_price((totals["USD"]["total"] - totals["USD"]["paid"]))},
        "EUR" : {"total" : round_price(totals["EUR"]["total"]), "paid" : round_price(totals["EUR"]["paid"]), "balance" : round_price((totals["EUR"]["total"] - totals["EUR"]["paid"]))},
        "GBP" : {"total" : round_price(totals["GBP"]["total"]), "paid" : round_price(totals["GBP"]["paid"]), "balance" : round_price((totals["GBP"]["total"] - totals["GBP"]["paid"]))},
        "QAR" : {"total" : round_price(totals["QAR"]["total"]), "paid" : round_price(totals["QAR"]["paid"]), "balance" : round_price((totals["QAR"]["total"] - totals["QAR"]["paid"]))},
        "RUB" : {"total" : round_price(totals["RUB"]["total"]), "paid" : round_price(totals["RUB"]["paid"]), "balance" : round_price((totals["RUB"]["total"] - totals["RUB"]["paid"]))},
        "JPY" : {"total" : round_price(totals["JPY"]["total"]), "paid" : round_price(totals["JPY"]["paid"]), "balance" : round_price((totals["JPY"]["total"] - totals["JPY"]["paid"]))},
        "TRY" : {"total" : round_price(totals["TRY"]["total"]), "paid" : round_price(totals["TRY"]["paid"]), "balance" : round_price((totals["TRY"]["total"] - totals["TRY"]["paid"]))}
    }]

    return external_data