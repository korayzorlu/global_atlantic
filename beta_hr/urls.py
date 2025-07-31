from django.urls import path, include

from .views import *

app_name = "beta_hr"

urlpatterns = [
    # path('the_company/', TheCompanyDetailView.as_view(), name="beta_the_company_detail"),
    # path('the_company_edit/', TheCompanyEditView.as_view(), name="beta_the_company_edit"),
    # path('the_company/bank_account_delete/<int:bank_account_id>', BankAccountDeleteView.as_view(),
    #      name="beta_bank_account_delete"),

    # path('user_add/', UserAddView.as_view(), name="beta_user_add"),
    # path('user/<int:user_id>', UserDetailView.as_view(), name="beta_user_detail"),
    # path('user_edit/<int:user_id>', UserEditView.as_view(), name="beta_user_edit"),
    # path('user_delete/<int:user_id>', UserDeleteView.as_view(), name="beta_user_delete"),
    # path('user_data/', UserDataView.as_view(), name="beta_user_data"),
    
    # path('user/certification/<int:profile_id>', CertificationAddView.as_view(),name="certificatiob_add"),

    # path('employee_type_add/', EmployeeTypeAddView.as_view(), name="beta_employee_type_add"),
    # path('employee_type/<int:employee_type_id>', EmployeeTypeDetailView.as_view(), name="beta_employee_type_detail"),
    # path('employee_type_edit/<int:employee_type_id>', EmployeeTypeEditView.as_view(), name="beta_employee_type_edit"),
    # path('employee_type_delete/<int:employee_type_id>', EmployeeTypeDeleteView.as_view(), name="beta_employee_type_delete"),
    # path('employee_type_data/', EmployeeTypeDataView.as_view(), name="beta_employee_type_data"),

    # path('team_add/', TeamAddView.as_view(), name="beta_team_add"),
    # path('team/<int:team_id>', TeamDetailView.as_view(), name="beta_team_detail"),
    # path('team_edit/<int:team_id>', TeamEditView.as_view(), name="beta_team_edit"),
    # path('team_delete/<int:team_id>', TeamDeleteView.as_view(), name="beta_team_delete"),
    # path('team_data/', TeamDataView.as_view(), name="beta_team_data"),

    # path('department_add/', DepartmentAddView.as_view(), name="beta_department_add"),
    # path('department/<int:department_id>', DepartmentDetailView.as_view(), name="beta_department_detail"),
    # path('department_edit/<int:department_id>', DepartmentEditView.as_view(), name="beta_department_edit"),
    # path('department_delete/<int:department_id>', DepartmentDeleteView.as_view(), name="beta_department_delete"),
    # path('department_data/', DepartmentDataView.as_view(), name="beta_department_data"),

    # path('record/<int:record_id>', RecordDetailView.as_view(), name="beta_record_detail"),
    # path('record_data/', RecordDataView.as_view(), name="beta_record_data"),

    # path('title_add/', TitleAddView.as_view(), name="beta_title_add"),
    # path('title/<int:title_id>', TitleDetailView.as_view(), name="beta_title_detail"),
    # path('title_edit/<int:title_id>', TitleEditView.as_view(), name="beta_title_edit"),
    # path('title_delete/<int:title_id>', TitleDeleteView.as_view(), name="beta_title_delete"),
    # path('title_data/', TitleDataView.as_view(), name="beta_title_data"),

    # path('document_add/', DocumentAddView.as_view(), name="beta_document_add"),
    # path('document/<int:document_id>', DocumentDetailView.as_view(), name="beta_document_detail"),
    # path('document_edit/<int:document_id>', DocumentEditView.as_view(), name="beta_document_edit"),
    # path('document_delete/<int:document_id>', DocumentDeleteView.as_view(), name="beta_document_delete"),
    # path('document_data/', DocumentDataView.as_view(), name="beta_document_data"),


    path('api/', include("beta_hr.api.urls")),
]
