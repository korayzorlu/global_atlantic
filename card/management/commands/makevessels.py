from django.core.management.base import BaseCommand, CommandError
from card.models import Vessel, Company, Country, City, Currency, EnginePart
from data.models import Maker, MakerType

from django.contrib.auth.models import User

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        data = pd.read_excel("./excelfile/vessels-data.xlsx")
        df = pd.DataFrame(data)
        
        for i in range(len(df["Name"])):
            if not pd.isnull(df["OWNER SYSTEM"][i]):
                vessel = Vessel.objects.filter(name = df["Name"][i]).first()
                if not vessel:
                    company = Company.objects.filter(name = df["OWNER SYSTEM"][i]).first()
                    if not company:
                        if not pd.isnull(df["OWNER SYSTEM"][i]):
                            # identificationCode = "C"
                            # startCodeValue = 1
                            # lastCompany = Company.objects.filter().extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                            # if lastCompany:
                            #     lastCode = lastCompany.code
                            # else:
                            #     lastCode = startCodeValue - 1
                            # code = int(lastCode) + 1
                            # companyNo = str(identificationCode) + "-" + str(code).zfill(8)
                            
                            if pd.isnull(df["SYSTEM COUNTRY"][i]):
                                country = None
                            else:
                                country = Country.objects.get(iso3 = df["SYSTEM COUNTRY"][i])
                                
                            if pd.isnull(df["SYSTEM CITY"][i]):
                                city = None
                            else:
                                city = City.objects.filter(name = df["SYSTEM CITY"][i]).first()
                                if not city:
                                    city = None
                                    
                            if pd.isnull(df["SYSTEM ADRESS"][i]):
                                address = ""
                            else:
                                address = df["SYSTEM ADRESS"][i]
                                
                            if pd.isnull(df["VAT OFFICE"][i]):
                                vatOffice = ""
                            else:
                                vatOffice = df["VAT OFFICE"][i]
                                
                            if pd.isnull(df["VAT NO"][i]):
                                vatNo = ""
                            else:
                                vatNo = df["VAT NO"][i]
                                
                            if pd.isnull(df["PHN"][i]):
                                phone1 = ""
                            else:
                                phone1 = df["PHN"][i]
                                
                            if pd.isnull(df["FAX"][i]):
                                fax = ""
                            else:
                                fax = df["FAX"][i]
                                
                            if pd.isnull(df["E MAIL"][i]):
                                email = ""
                            else:
                                email = df["E MAIL"][i]
                                
                            # if pd.isnull(df["KEY ACCOUNT"][i]):
                            #     keyAccount = ""
                            # else:
                            #     keyAccount = User.objects.filter(name = df["KEY ACCOUNT"][i])
                            
                            if pd.isnull(df["CREDİT LİMİT"][i]):
                                creditLimit = 0
                            else:
                                creditLimit = df["CREDİT LİMİT"][i]
                                
                            if pd.isnull(df["CURR"][i]):
                                currency = None
                            else:
                                currency = Currency.objects.filter(code = df["CURR"][i]).first()
                                
                            if pd.isnull(df["CREDIT PERIOD"][i]):
                                creditPeriot = ""
                            else:
                                creditPeriot = df["CREDIT PERIOD"][i]
                            
                            company = Company.objects.create(
                                customerCheck = True,
                                name = df["OWNER SYSTEM"][i],
                                # code = code,
                                # companyNo = companyNo,
                                country = country,
                                city = city,
                                address = address,
                                vatOffice = vatOffice,
                                vatNo = vatNo,
                                phone1 = phone1,
                                fax = fax,
                                email = email,
                                creditLimit = creditLimit,
                                currency = currency,
                                creditPeriot = creditPeriot
                            )
                            company.save()
                    
                    if pd.isnull(df["Flag State"][i]):
                        flag = ""
                    else:
                        flag = df["Flag State"][i]
                        
                    if pd.isnull(df["Builder"][i]):
                        builder = ""
                    else:
                        builder = df["Builder"][i]
                        
                    if pd.isnull(df["Hull No"][i]):
                        hullNo = ""
                    else:
                        hullNo = df["Hull No"][i]
                        
                    if pd.isnull(df["IMO Number"][i]):
                        imo = ""
                    else:
                        imo = df["IMO Number"][i]
                        
                    if pd.isnull(df["MMSI"][i]):
                        mmsi = ""
                    else:
                        mmsi = df["MMSI"][i]
                        
                    if pd.isnull(df["Call Sign"][i]):
                        callSign = ""
                    else:
                        callSign = df["Call Sign"][i]
                        
                    if pd.isnull(df["TYPE 2"][i]):
                        vesselType = None
                    else:
                        vesselType = df["TYPE 2"][i]
                        
                    if pd.isnull(df["Built"][i]):
                        buildYear = ""
                    else:
                        buildYear = df["Built"][i]
                        
                    if pd.isnull(df["GT"][i]):
                        grosston = ""
                    else:
                        grosston = df["GT"][i]
                        
                    if pd.isnull(df["Dwt"][i]):
                        deadWeight = ""
                    else:
                        deadWeight = df["Dwt"][i]
                        
                    if pd.isnull(df["LOA (m)"][i]):
                        loa = ""
                    else:
                        loa = df["LOA (m)"][i]
                        
                    if pd.isnull(df["Beam Mld (m)"][i]):
                        beam = ""
                    else:
                        beam = df["Beam Mld (m)"][i]
                        
                    if pd.isnull(df["Draft (m)"][i]):
                        draught = ""
                    else:
                        draught = df["Draft (m)"][i]
                    
                    vessel = Vessel.objects.create(
                        name = df["Name"][i].upper(),
                        company = company,
                        owner = company,
                        flag = flag,
                        hallNo = hullNo,
                        imo = imo,
                        mmsi = mmsi,
                        callSign = callSign,
                        type = vesselType,
                        building = buildYear,
                        shipyard = builder,
                        grosston = grosston,
                        deadWeight = deadWeight,
                        loa = loa,
                        beam = beam,
                        draught = draught
                    )
                    vessel.save()
                    
                    if not pd.isnull(df["maker"][i]):
                        maker = Maker.objects.filter(name = df["maker"][i]).first()
                        if not maker:
                            maker = Maker.objects.create(
                                name = df["maker"][i]
                            )
                            maker.save()
                            
                        if not pd.isnull(df["TYPE"][i]):
                            type = MakerType.objects.filter(maker = maker, type = df["TYPE"][i]).first()
                            if not type:
                                type = MakerType.objects.create(
                                    maker = maker,
                                    type = df["TYPE"][i]
                                )
                                type.save()
                            
                        if pd.isnull(df["CYLINDER NO"][i]):
                            cyl = ""
                        else:
                            cyl = df["CYLINDER NO"][i]
                            
                        if pd.isnull(df["VERSION 1"][i]):
                            version1 = ""
                        else:
                            version1 = df["VERSION 1"][i]
                            
                        if pd.isnull(df["VERSION 2"][i]):
                            version2 = ""
                        else:
                            version2 = df["VERSION 2"][i]
                            
                        version = str(version1) + " " + str(version2)

                        enginePart = EnginePart.objects.create(
                            vessel = vessel,
                            maker = maker,
                            makerType = type,
                            cyl = cyl,
                            version = version
                        )
                        enginePart.save()