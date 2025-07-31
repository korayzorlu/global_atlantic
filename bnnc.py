import requests
import datetime
import pandas as pd

import os


# Binance API'si üzerinden 15 dakikalık periyot verilerini almak için fonksiyon
def get_15m_ohlcv(symbol):
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        'symbol': symbol,  # Örneğin BTCUSDT
        'interval': '15m',  # 15 dakikalık periyot
        'limit': 1000  # Maksimum veri sayısı
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

# MA25 ve MA99 hesaplamak için fonksiyon
def calculate_ma(data, ma_periods=[25, 99]):
    # Pandas DataFrame oluşturma
    df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    
    # Kapanış fiyatlarını al
    df['close'] = pd.to_numeric(df['close'])
    
    # MA25 ve MA99 hesaplama
    for period in ma_periods:
        df[f"MA{period}"] = df['close'].rolling(window=period).mean()
    
    return df

# Verileri alıp MA25 ve MA99 hesaplamak
def get_24h_ohlcv(symbol):
    data = get_15m_ohlcv(symbol)
    if data:
        df = calculate_ma(data)
        # Excel'e kaydetmek için df'yi döndürme
        return df
    else:
        print("Veri alınamadı.")
        return None

# Verileri alıp Excel'e kaydetmek
def save_to_excel(symbol, filename="binance_data.xlsx"):
    df = get_24h_ohlcv(symbol)
    if df is not None:
        # Excel dosyasına yazma
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Veriler {filename} dosyasına kaydedildi.")
    else:
        print("Veriler kaydedilemedi.")


if __name__ == "__main__":
    symbol = "DOGEUSDT"  # İlgili coin çifti
    save_to_excel(symbol)
