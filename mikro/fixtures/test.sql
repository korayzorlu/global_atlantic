SELECT TOP (1000) [cha_create_date]
      ,[cha_lastup_date]
      ,[cha_tarihi]
      ,[cha_belge_no]
      ,[cha_belge_tarih]
      ,[cha_aciklama]
      ,[cha_miktari]
      ,[cha_meblag]
      ,[cha_aratoplam]
  FROM [MikroDB_V16_ESMS].[dbo].[CARI_HESAP_HAREKETLERI]

  ORDER BY [cha_lastup_date] DESC