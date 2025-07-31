from django.urls import path, include

from .views import *

app_name = "hr"

urlpatterns = [
    path('the_company/', TheCompanyDetailView.as_view(), name="the_company_detail"),
    path('the_company_edit/', TheCompanyEditView.as_view(), name="the_company_edit"),
    path('the_company/bank_account_delete/<int:bank_account_id>', BankAccountDeleteView.as_view(),
         name="bank_account_delete"),

    path('user_data/', UserDataView.as_view(), name="user_data"),
    path('user_add/', UserAddView.as_view(), name="user_add"),
    path('user_update/<int:id>/', UserUpdateView.as_view(), name = "user_update"),
    path('user_delete/<str:list>', UserDeleteView.as_view(), name="user_delete"),
    path('user_cv_pdf/<int:id>/', UserCVPdfView.as_view(), name = "user_cv_pdf"),
    path('user_nda_pdf/<int:id>/', UserNDAPdfView.as_view(), name = "user_nda_pdf"),
    
    path('user_edit/<int:user_id>', UserEditView.as_view(), name="user_edit"),
    path('user/<int:user_id>', UserDetailView.as_view(), name="user_detail"),
    path('user/certification/<int:profile_id>', CertificationAddView.as_view(),name="certificatiob_add"),

    path('employee_type_add/', EmployeeTypeAddView.as_view(), name="employee_type_add"),
    path('employee_type/<int:employee_type_id>', EmployeeTypeDetailView.as_view(), name="employee_type_detail"),
    path('employee_type_edit/<int:employee_type_id>', EmployeeTypeEditView.as_view(), name="employee_type_edit"),
    path('employee_type_delete/<int:employee_type_id>', EmployeeTypeDeleteView.as_view(), name="employee_type_delete"),
    path('employee_type_data/', EmployeeTypeDataView.as_view(), name="employee_type_data"),

    path('team_add/', TeamAddView.as_view(), name="team_add"),
    path('team/<int:team_id>', TeamDetailView.as_view(), name="team_detail"),
    path('team_update/<int:id>/', TeamUpdateView.as_view(), name = "team_update"),
    path('team_edit/<int:team_id>', TeamEditView.as_view(), name="team_edit"),
    path('team_delete/<str:list>', TeamDeleteView.as_view(), name="team_delete"),
    path('team_data/', TeamDataView.as_view(), name="team_data"),

    path('department_add/', DepartmentAddView.as_view(), name="department_add"),
    path('department/<int:department_id>', DepartmentDetailView.as_view(), name="department_detail"),
    path('department_update/<int:id>/', DepartmentUpdateView.as_view(), name = "department_update"),
    path('department_edit/<int:department_id>', DepartmentEditView.as_view(), name="department_edit"),
    path('department_delete/<str:list>', DepartmentDeleteView.as_view(), name="department_delete"),
    path('department_data/', DepartmentDataView.as_view(), name="department_data"),
    
    path('education_add_in_user/', EducationAddView.as_view(), name = "education_add_in_user"),
    path('education_add_in_detail/u_<int:id>/', EducationInDetailAddView.as_view(), name = "education_add_in_detail"),
    path('education_delete/<str:list>', EducationDeleteView.as_view(), name = "education_delete"),
    
    path('additional_payment_add_in_detail/u_<int:id>/', AdditionalPaymentInDetailAddView.as_view(), name = "additional_payment_add_in_detail"),
    
    path('organization_chart_data/', OrganizationChartDataView.as_view(), name="organization_chart_data"),

    path('record/<int:record_id>', RecordDetailView.as_view(), name="record_detail"),
    path('record_data/', RecordDataView.as_view(), name="record_data"),

    path('api/', include("hr.api.urls")),
]
