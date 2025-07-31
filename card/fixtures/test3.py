import os

import json
import pandas as pd

import requests
import xmltodict

# liste = list(range(100))



# for i in range(0, len(liste), 30):
#     items_to_print = liste[i:i+30]  # Her 30 öğeyi alın.
#     print(items_to_print)
    
# kalan_eleman_sayisi = len(liste) % 30
# son_dilim = liste[-kalan_eleman_sayisi:]
# print("Son Dilim:", son_dilim)



# liste = [{"a":True},{"a":False},{"a":True},{"a":True},{"a":True}]

# if all(liste):
#     print("hepsi doğru")


# dd = {"sendInvoices" : [], "incomingInvoices" : []}

# for i in range(5):
#     dd["sendInvoices"].append({"invoice" : "sdfsdg",
#                                "total" : 2424,
#                                "paid" : 6546})
    
# print(dd)
    


dd = requests.get("https://www.tcmb.gov.tr/kurlar/today.xml").content

ff = xmltodict.parse(dd)

usd = next((rate for rate in ff["Tarih_Date"]["Currency"] if rate['@Kod'] == 'USD'), None)


if usd:
    print("USD Döviz Kuru:", usd['ForexBuying'])
else:
    print("USD döviz kuru bulunamadı.")