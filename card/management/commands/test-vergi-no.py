import requests
import json

def curl(url, data):
    # HTTP POST isteği gönder
    response = requests.post(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    # İstek sonucunu döndür
    return response.text

def token():
    postdata = {
        'assoscmd': 'cfsession',
        'rtype': 'json',
        'fskey': 'intvrg.fix.session',
        'fuserid': 'INTVRG_FIX'
    }
    
    url = 'https://ivd.gib.gov.tr/tvd_server/assos-login'
    data = curl(url, postdata)
    
    return data

def vkn_verification():
    vkn = '41419169230'  # vergi kimlik numarası
    vd = '034245'    # vergi dairesi kodu
    il = '034'       # il kodu
    token_response = json.loads(token())  # token'ı al ve JSON olarak çöz

    # Token'ı kontrol et
    if 'token' not in token_response:
        print("Token alınamadı:", token_response)
        return

    jp = json.dumps({
        "dogrulama": {
            "vkn1": vkn,
            "tckn1": "",  # Eğer şahıs şirketiyseniz vkn1'i boş bırakıp tckn1'i doldurunuz.
            "iller": il,
            "vergidaireleri": vd
        }
    })

    postdata = {
        'cmd': 'vergiNoIslemleri_vergiNumarasiSorgulama',
        'callid': 'ff81dd010b12d-8',
        'pageName': 'R_INTVRG_INTVD_VERGINO_DOGRULAMA',
        'token': token_response['token'],
        'jp': jp
    }

    data = curl('https://ivd.gib.gov.tr/tvd_server/dispatch', postdata)
    print(data)

# Fonksiyonu çağır
vkn_verification()