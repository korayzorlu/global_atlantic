import random
import time

# Güncellenmiş para birimleri
currency_codes = ["USD", "EUR", "GBP", "QAR", "RUB", "JPY", "TRY"]

# Örnek veri setini oluşturma (güncellenmiş para birimleri ile)
def generate_test_data_with_multiple_currencies(size):
    return [
        {
            "debt": random.randint(1, 1000),
            "credit": random.randint(1, 1000),
            "currency": {
                "code": random.choice(currency_codes)
            }
        }
        for _ in range(size)
    ]

# Normal döngü ile toplam hesaplama
def normal_loop(currents):
    totals = {
        "USD": {"debt": 0, "credit": 0},
        "EUR": {"debt": 0, "credit": 0},
        "GBP": {"debt": 0, "credit": 0},
        "QAR": {"debt": 0, "credit": 0},
        "RUB": {"debt": 0, "credit": 0},
        "JPY": {"debt": 0, "credit": 0},
        "TRY": {"debt": 0, "credit": 0}
    }
    for current in currents:
        currency_code = current["currency"]["code"]
        if currency_code in totals:
            totals[currency_code]["debt"] += current["debt"]
            totals[currency_code]["credit"] += current["credit"]
    return totals

def list_comprehension(currents):
    totals = {
        "USD": {"debt": sum(current["debt"] for current in currents if current["currency"]["code"] == "USD"),
                "credit": sum(current["credit"] for current in currents if current["currency"]["code"] == "USD")},
        "EUR": {"debt": sum(current["debt"] for current in currents if current["currency"]["code"] == "EUR"),
                "credit": sum(current["credit"] for current in currents if current["currency"]["code"] == "EUR")},
        "GBP": {"debt": sum(current["debt"] for current in currents if current["currency"]["code"] == "GBP"),
                "credit": sum(current["credit"] for current in currents if current["currency"]["code"] == "GBP")},
        "QAR": {"debt": sum(current["debt"] for current in currents if current["currency"]["code"] == "QAR"),
                "credit": sum(current["credit"] for current in currents if current["currency"]["code"] == "QAR")},
        "RUB": {"debt": sum(current["debt"] for current in currents if current["currency"]["code"] == "RUB"),
                "credit": sum(current["credit"] for current in currents if current["currency"]["code"] == "RUB")},
        "JPY": {"debt": sum(current["debt"] for current in currents if current["currency"]["code"] == "JPY"),
                "credit": sum(current["credit"] for current in currents if current["currency"]["code"] == "JPY")},
        "TRY": {"debt": sum(current["debt"] for current in currents if current["currency"]["code"] == "TRY"),
                "credit": sum(current["credit"] for current in currents if current["currency"]["code"] == "TRY")}
    }
    return totals

# Test fonksiyonu (güncellenmiş veri seti ile)
def test_methods_with_multiple_currencies(size):
    currents = generate_test_data_with_multiple_currencies(size)
    
    # Normal döngü süresini ölçme
    start_time = time.time()
    normal_result = normal_loop(currents)
    normal_duration = time.time() - start_time

    # List comprehension süresini ölçme
    start_time = time.time()
    comprehension_result = list_comprehension(currents)
    comprehension_duration = time.time() - start_time

    return normal_duration, comprehension_duration, normal_result, comprehension_result

# İlk test (1000 veri)
test_1000_updated = test_methods_with_multiple_currencies(10000)

# İkinci test (10000 veri)
test_10000_updated = test_methods_with_multiple_currencies(100000)

print(f"1000 veri: {test_1000_updated}")
print("--------")
print(f"10000 veri: {test_10000_updated}")






# currentss = {
#             "currentsUSDDebtTotal" : sum(current.debt for current in currents if current.currency.code == "USD"),
#             "currentsUSDCreditTotal" : sum(current.credit for current in currents if current.currency.code == "USD"),
#             "currentsUSDBalanceTotal" : sum((current.debt - current.credit) for current in currents if current.currency.code == "USD"),
            
#             "currentsEURDebtTotal" : sum(current.debt for current in currents if current.currency.code == "EUR"),
#             "currentsEURCreditTotal" : sum(current.credit for current in currents if current.currency.code == "EUR"),
#             "currentsEURBalanceTotal" : sum((current.debt - current.credit) for current in currents if current.currency.code == "EUR"),
            
#             "currentsGBPDebtTotal" : sum(current.debt for current in currents if current.currency.code == "GBP"),
#             "currentsGBPCreditTotal" : sum(current.credit for current in currents if current.currency.code == "GBP"),
#             "currentsGBPBalanceTotal" : sum((current.debt - current.credit) for current in currents if current.currency.code == "GBP"),
            
#             "currentsQARDebtTotal" : sum(current.debt for current in currents if current.currency.code == "QAR"),
#             "currentsQARCreditTotal" : sum(current.credit for current in currents if current.currency.code == "QAR"),
#             "currentsQARBalanceTotal" : sum((current.debt - current.credit) for current in currents if current.currency.code == "QAR"),
            
#             "currentsRUBDebtTotal" : sum(current.debt for current in currents if current.currency.code == "RUB"),
#             "currentsRUBCreditTotal" : sum(current.credit for current in currents if current.currency.code == "RUB"),
#             "currentsRUBBalanceTotal" : sum((current.debt - current.credit) for current in currents if current.currency.code == "RUB"),
            
#             "currentsJPYDebtTotal" : sum(current.debt for current in currents if current.currency.code == "JPY"),
#             "currentsJPYCreditTotal" : sum(current.credit for current in currents if current.currency.code == "JPY"),
#             "currentsJPYBalanceTotal" : sum((current.debt - current.credit) for current in currents if current.currency.code == "JPY"),
            
#             "currentsTRYDebtTotal" : sum(current.debt for current in currents if current.currency.code == "TRY"),
#             "currentsTRYCreditTotal" : sum(current.credit for current in currents if current.currency.code == "TRY"),
#             "currentsTRYBalanceTotal" : sum((current.debt - current.credit) for current in currents if current.currency.code == "TRY")
#         }













        # #current-usd
        # currentsUSD = currents.filter(currency = 106)
        # currentsUSDDebtTotal = 0
        # currentsUSDCreditTotal = 0
        # currentsUSDBalanceTotal = 0
        # for currentUSD in currentsUSD:
        #     currentsUSDDebtTotal = currentsUSDDebtTotal + currentUSD.debt
        #     currentsUSDCreditTotal = currentsUSDCreditTotal + currentUSD.credit
        # currentsUSDBalanceTotal = currentsUSDDebtTotal - currentsUSDCreditTotal
        
        # # Para miktarını belirtilen formatta gösterme
        # currentsUSDDebtTotal = "{:,.2f}".format(round(currentsUSDDebtTotal,2))
        # currentsUSDCreditTotal = "{:,.2f}".format(round(currentsUSDCreditTotal,2))
        # currentsUSDBalanceTotal = "{:,.2f}".format(round(currentsUSDBalanceTotal,2))
        # # Nokta ile virgülü değiştirme
        # currentsUSDDebtTotal = currentsUSDDebtTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        # currentsUSDCreditTotal = currentsUSDCreditTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        # currentsUSDBalanceTotal = currentsUSDBalanceTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        # #current-eur
        # currentsEUR = currents.filter(currency = 33)
        # currentsEURDebtTotal = 0
        # currentsEURCreditTotal = 0
        # for currentEUR in currentsEUR:
        #     currentsEURDebtTotal = currentsEURDebtTotal + currentEUR.debt
        #     currentsEURCreditTotal = currentsEURCreditTotal + currentEUR.credit
        # currentsEURBalanceTotal = currentsEURDebtTotal - currentsEURCreditTotal
        
        # # Para miktarını belirtilen formatta gösterme
        # currentsEURDebtTotal = "{:,.2f}".format(round(currentsEURDebtTotal,2))
        # currentsEURCreditTotal = "{:,.2f}".format(round(currentsEURCreditTotal,2))
        # currentsEURBalanceTotal = "{:,.2f}".format(round(currentsEURBalanceTotal,2))
        # # Nokta ile virgülü değiştirme
        # currentsEURDebtTotal = currentsEURDebtTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        # currentsEURCreditTotal = currentsEURCreditTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        # currentsEURBalanceTotal = currentsEURBalanceTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        # #current-gbp
        # currentsGBP = currents.filter(currency = 105)
        # currentsGBPDebtTotal = 0
        # currentsGBPCreditTotal = 0
        # for currentGBP in currentsGBP:
        #     currentsGBPDebtTotal = currentsGBPDebtTotal + currentGBP.debt
        #     currentsGBPCreditTotal = currentsGBPCreditTotal + currentGBP.credit
        # currentsGBPBalanceTotal = currentsGBPDebtTotal - currentsGBPCreditTotal