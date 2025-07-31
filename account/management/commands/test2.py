# Get the samples from http://www.adobe.com/go/pdftoolsapi_python_sample
# Run the sample:
# python src/extractpdf/extract_txt_table_info_from_pdf.py

import logging
import os.path
import pandas as pd

from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions, TableStructureType
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_renditions_element_type import ExtractRenditionsElementType
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation



# logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# try:
#     #get base path.
#     base_path = os.path.join(os.getcwd(), "media")
#     print(base_path)
#     #Initial setup, create credentials instance.
#     credentials = Credentials.service_principal_credentials_builder().with_client_id('4032e8bd6a0741b1b996b9065c4ac574').with_client_secret('p8e-TeQVhJ6I1S6yHqeH5dvmnbTQAU7VQSNQ').build()

#     #Create an ExecutionContext using credentials and create a new operation instance.
#     execution_context = ExecutionContext.create(credentials)
#     extract_pdf_operation = ExtractPDFOperation.create_new()

#     #Set operation input from a source file.
#     source = FileRef.create_from_local_file(base_path + "/sale/quotation/documents/ESQ-024-00000040.pdf")
#     extract_pdf_operation.set_input(source)

#     #Build ExtractPDF options and set them into the operation
#     extract_pdf_options: ExtractPDFOptions = ExtractPDFOptions.builder() \
#           .with_table_structure_format(TableStructureType.CSV) \
#           .build()
#     extract_pdf_operation.set_options(extract_pdf_options)

#     #Execute the operation.
#     result: FileRef = extract_pdf_operation.execute(execution_context)

#     #Save the result to the specified location.
#     result.save_as(base_path + "/ExtractTextTableWithTableRendition.zip")
# except (ServiceApiException, ServiceUsageException, SdkException):
#     logging.exception("Exception encountered while executing operation")


base_path = os.path.join(os.getcwd(), "media")

data = {
    'İsim': ['Ahmet', 'Mehmet', 'Ayşe', 'Fatma'],
    'Yaş': [25, 30, 22, 19],
    'Şehir': ['İstanbul', 'Ankara', 'İzmir', 'Bursa']
}

# Verileri pandas DataFrame'e dönüştür
df = pd.DataFrame(data)

# DataFrame'i Excel dosyasına dönüştür
excel_dosyasi_adi = base_path + "/ornek_dosya.xlsx"
df.to_excel(excel_dosyasi_adi, index=False)