from django.urls import path, include
from rest_framework import routers

from mikro.api.views import *

router = routers.DefaultRouter()
router.register(r'cari_hesap_hareketleri', CariHesapHareketleriList, "cari_hesap_hareketleri_api")

urlpatterns = [
    path('',include(router.urls)),
    path('kullanicilar', KullanicilarList.as_view(), name="kullanicilar_api"),
    path('stok_birimleri', StokBirimleriList.as_view(), name="stok_birimleri_api"),
    path('kur_isimleri', KurIsimleriList.as_view(), name="kur_isimleri_api"),
    path('cari_hesaplar', CariHesaplarList.as_view(), name="cari_hesaplar_api"),
    path('cari_hesap_adresleri', CariHesapAdresleriList.as_view(), name="cari_hesap_adresleri_api"),
    #path('cari_hesap_hareketleri', CariHesapHareketleriList.as_view(), name="cari_hesap_hareketleri_api"),
    path('stoklar', StoklarList.as_view(), name="stoklar_api"),
]