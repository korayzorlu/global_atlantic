import os

import json


with open("/home/novu/projects/django/michoapp/michoapp/card/fixtures/currency-data.json", "r") as f:
    currencies = json.load(f)
    
print(currencies[0])

newCurrencies = []

for i in range(len(currencies)):
    newCurrencies.append({"model" : "card.currency",
                          "pk" : i + 1,
                          "fields" : {"flag" : currencies[i]["flag"],
                                      "country" : currencies[i]["country"],
                                      "currency" : currencies[i]["currency"],
                                      "code" : currencies[i]["code"],
                                      "symbol" : currencies[i]["symbol"]
                                      }
                          })
    
print(newCurrencies)

with open("/home/novu/projects/django/michoapp/michoapp/card/fixtures/currency.json", "w") as f:
    json.dump(newCurrencies, f)