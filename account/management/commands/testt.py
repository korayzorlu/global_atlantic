from collections import Counter

def max_pairs_with_sum(lst):
    # Elemanların frekanslarını hesapla
    freq = Counter(lst)
    
    max_pairs = 0
    
    # Tüm olası çiftlerin toplamlarını kontrol et
    for i in freq:
        for j in freq:
            if i <= j:
                if i == j:
                    # Aynı elemandan iki tane kullanıyorsak (örneğin, 2 + 2)
                    max_pairs += freq[i] // 2
                else:
                    # Farklı iki eleman kullanıyorsak
                    pairs = min(freq[i], freq[j])
                    max_pairs += pairs
                    # Kullanılan çiftleri çıkart
                    freq[i] -= pairs
                    freq[j] -= pairs
    
    return max_pairs

# Verilen liste
lst = [122, 22, 14, 16, 22, 22, 45, 22, 13]

# Fonksiyonu çağır ve sonucu al
result = max_pairs_with_sum(lst)
print(result)