import icu

def locale_upper(text, locale_str):
    # UnicodeString ile metni büyük harfe çeviriyoruz
    locale = icu.Locale(locale_str)
    ustring = icu.UnicodeString(text)
    return ustring.toUpper(locale)

def locale_lower(text, locale_str):
    # UnicodeString ile metni küçük harfe çeviriyoruz
    locale = icu.Locale(locale_str)
    ustring = icu.UnicodeString(text)
    return ustring.toLower(locale)

text = "İzmir"
newText = locale_lower(text, 'tr_TR')

if isinstance(newText, icu.UnicodeString):
    newText = str(newText)
print(newText)
print(newText[1:])

