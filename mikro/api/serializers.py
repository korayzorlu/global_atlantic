from rest_framework import serializers
from django_filters import FilterSet, DateFilter
from rest_framework.utils import html, model_meta, representation
from django.utils.translation import gettext_lazy as _

from account.models import *

class KullanicilarListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    
class StokBirimleriListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    unit = serializers.CharField()

class KurIsimleriListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    kurAdi = serializers.CharField()

class CariHesaplarListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    kod = serializers.CharField()
    unvan1 = serializers.CharField()
    unvan2 = serializers.CharField()
    vDaireAdi = serializers.CharField()
    vDaireNo = serializers.CharField()
    ulke = serializers.CharField()
    doviz = serializers.CharField()
    doviz1 = serializers.CharField()
    doviz2 = serializers.CharField()
    
class CariHesapAdresleriListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    kod = serializers.CharField()
    mahalle = serializers.CharField()
    cadde = serializers.CharField()
    sokak = serializers.CharField()
    postaKodu = serializers.CharField()
    ilce = serializers.CharField()
    il = serializers.CharField()
    ulke = serializers.CharField()
    
class CariHesapHareketleriListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tarih = serializers.DateTimeField(format="%d.%m.%Y %H:%M:%S")
    kod = serializers.CharField()
    cari = serializers.CharField()
    evrakTip = serializers.CharField()
    belgeNo = serializers.CharField()
    doviz = serializers.CharField()
    meblag = serializers.FloatField()
    araToplam = serializers.FloatField()
    iskonto = serializers.FloatField()
    vergi = serializers.FloatField()
    kur = serializers.FloatField()
    
class StoklarListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    kod = serializers.CharField()
    isim = serializers.CharField()
    yabanci_isim = serializers.CharField()
    kisa_ismi = serializers.CharField()
    birim1_ad = serializers.CharField()