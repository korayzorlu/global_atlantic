from django.urls import path, include

from . import views
from .views import *

app_name = "mikro"

urlpatterns = [
    path('kullanicilar_data/', KullanicilarDataView.as_view(), name="kullanicilar_data"),
    path('stok_birimleri_data/', StokBirimleriDataView.as_view(), name="stok_birimleri_data"),
    path('kur_isimleri_data/', KurIsimleriDataView.as_view(), name="kur_isimleri_data"),
    path('cari_hesaplar_data/', CariHesaplarDataView.as_view(), name="cari_hesaplar_data"),
    path('cari_hesaplar_update/<str:cariKod>/', CariHesaplarUpdateView.as_view(), name = "cari_hesaplar_update"),
    path('cari_hesap_adresleri_data/', CariHesapAdresleriDataView.as_view(), name="cari_hesap_adresleri_data"),
    path('cari_hesap_hareketleri_data/', CariHesapHareketleriDataView.as_view(), name="cari_hesap_hareketleri_data"),
    path('stoklar_data/', StoklarDataView.as_view(), name="stoklar_data"),
    
    path('api/', include("mikro.api.urls")),
]
