"""
Connects to a SQL database using pyodbc
"""

import pyodbc

from decouple import config, Csv

SERVER = config('MIKRO_SERVER', default = "")
DATABASE = "MikroDB_V16_ESMS_TEST"
USERNAME = config('MIKRO_USERNAME', default = "")
PASSWORD = config('MIKRO_PASSWORD', default = "")

# SERVER = 'localhost'
# DATABASE = 'michoapptestdb'
# USERNAME = 'sa'
# PASSWORD = 'Mamtiolen.11'
# TRUSTED_CONNECTION = "YES"

connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'

conn = pyodbc.connect(connectionString)

#####DÖKÜMANTASYON#####
text = """
SELECT yit_isim2 FROM YARDIMCI_ISIM_TABLOSU
WHERE yit_language = 'T' AND yit_tip_no = 0 AND yit_sub_id = 0;
"""
tabloListeleme = """
SELECT * FROM SYS.TABLES;
"""
tabloGoruntuleme = """
SELECT TOP 1000 * FROM CARI_HESAPLAR;
"""
tabloGoruntulemeDetay = """
SELECT cha_create_date,cha_kod,cha_evrak_tip
FROM CARI_HESAP_HAREKETLERI
ORDER BY cha_create_date DESC;
"""
databaseSutunListeleme = """
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'ADAY_CARI_HESAPLAR';
"""
#####DÖKÜMANTASYON-END#####

SQL_QUERY = tabloGoruntulemeDetay

cursor = conn.cursor()
cursor.execute(SQL_QUERY)

records = cursor.fetchall()
for r in records:
    row_to_list = [elem for elem in r]
    print(row_to_list)



#conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=159.146.53.102,4443;Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2')

# conn = pyodbc.connect('Driver={ ODBC Driver 18 for SQL Server };Server=VSRV2;Database=MikroV16xx;Trusted_Connection=yes;')

# [ODBC Driver 18 for SQL Server]
# Description=Microsoft ODBC Driver 18 for SQL Server
# Driver=/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.3.so.2.1
# UsageCount=1

