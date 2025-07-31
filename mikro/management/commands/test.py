"""
Connects to a SQL database using pyodbc
"""

import os
import pyodbc

from decouple import config, Csv

SERVER = os.getenv("MIKRO_SERVER","")
DATABASE = "MikroDB_V16_ESMS_TEST"
USERNAME = os.getenv("MIKRO_USERNAME","")
PASSWORD = os.getenv("MIKRO_PASSWORD","")

# SERVER = 'localhost'
# DATABASE = 'michoapptestdb'
# USERNAME = 'sa'
# PASSWORD = 'Mamtiolen.11'
# TRUSTED_CONNECTION = "YES"

connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'

conn = pyodbc.connect(connectionString)

SQL_QUERY = f"""
DELETE FROM CARI_HESAP_ADRESLERI
WHERE adr_cari_kod = '120.02.2101';
"""

cursor = conn.cursor()
cursor.execute(SQL_QUERY)

conn.commit()