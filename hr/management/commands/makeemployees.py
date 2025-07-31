from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from user.models import Profile, Team, Department, Position
from source.models import Company

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None
        
    def handle(self, *args, **options):
        data = pd.read_excel("./excelfile/employees-data.xlsx")
        df = pd.DataFrame(data)
        
        for i in range(len(df["Kişi sicil no"])):
            if df["Firma Bilgisi"][i] == "ESMS":
                position = Position.objects.filter(name = df["Firmadaki Pozisyonu"][i]).first()
                if position:
                    
                    userr = User.objects.filter(username = df["Kullanıcı Adı"][i]).first()
                    
                    if userr:
                        profile = Profile.objects.get(user = userr)
                        profile.delete()
                        userr.delete()
                        
                    newUser = User.objects.create(
                        username = df["Kullanıcı Adı"][i],
                        first_name = df["Ad"][i],
                        last_name = df["Soyad"][i]
                    )
                    newUser.set_password(df["Pass"][i])
                    newUser.save()
                    
                    if df["Cinsiyet"][i] == "E":
                        gender = "male"
                    elif df["Cinsiyet"][i] == "K":
                        gender = "female"
                    
                    birthday = df["Doğum Tarihi"][i]
                    birthday = birthday.date()
                    
                    if pd.isnull(df["Adres"][i]):
                        address = ""
                    else:
                        address = df["Adres"][i]
                        
                    if pd.isnull(df["Anne Adı"][i]):
                        motherName = ""
                    else:
                        motherName = df["Anne Adı"][i]
                        
                    if pd.isnull(df["Baba Adı"][i]):
                        fatherName = ""
                    else:
                        fatherName = df["Baba Adı"][i]
                        
                    if pd.isnull(df["Ehliyet"][i]):
                        drivingLicence = ""
                    else:
                        drivingLicence = df["Ehliyet"][i]
                        
                    if pd.isnull(df["Askerlik"][i]):
                        militaryStatus = None
                    else:
                        militaryStatus = df["Askerlik"][i]
                        
                    if pd.isnull(df["Askerlik Tecil Tarih"][i]):
                        militaryPostponedDate = None
                    else:
                        militaryPostponedDate = df["Askerlik Tecil Tarih"][i]
                        militaryPostponedDate = militaryPostponedDate.date()
                        
                    if pd.isnull(df["Sgk Sicil No"][i]):
                        socialSecurityNo = ""
                    else:
                        socialSecurityNo = df["Sgk Sicil No"][i]
                        
                    if pd.isnull(df["İşe Başlama Tarihi"][i]):
                        startDate = None
                    else:
                        startDate = df["İşe Başlama Tarihi"][i]
                        startDate = startDate.date()
                        
                    if pd.isnull(df["Meslek Kodu"][i]):
                        professionCode = ""
                    else:
                        professionCode = df["Meslek Kodu"][i]
                        
                    company = Company.objects.get(code = "ESMS")
                    
                    positionType = Position.objects.get(name = df["Firmadaki Pozisyonu"][i])
                    
                    if pd.isnull(df["Eğitim Durumu"][i]):
                        educationLevel = "none"
                    else:
                        educationLevel = df["Eğitim Durumu"][i]
                    
                    profile = Profile.objects.get(user = newUser)
                    profile.registrationNo = df["Kişi sicil no"][i]
                    profile.identificationNo = df["TC"][i]
                    profile.gender = gender
                    profile.birthday = birthday
                    profile.address = address
                    profile.motherName = motherName
                    profile.fatherName = fatherName
                    profile.drivingLicence = drivingLicence
                    profile.militaryStatus = militaryStatus
                    profile.militaryPostponedDate = militaryPostponedDate
                    profile.socialSecurityNo = socialSecurityNo
                    profile.startDate = startDate
                    profile.professionCode = professionCode
                    profile.company = company
                    profile.positionType = positionType
                    profile.education_level = educationLevel
                    
                    profile.save()
                

                
                