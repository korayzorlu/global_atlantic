from django.urls import path, include
from rest_framework import routers

from user.api.views import *

router = routers.DefaultRouter()
router.register(r'educations', EducationList, "educations_api")
router.register(r'aditional_payments', AdditionalPaymentList, "aditional_payments_api")
router.register(r'access_authorizations', AccessAuthorizationList, "access_authorizations_api")
router.register(r'data_authorizations', DataAuthorizationList, "data_authorizations_api")
router.register(r'user_authorizations', UserAuthorizationList, "user_authorizations_api")

urlpatterns = [
    path('',include(router.urls)),
    path('users', UserList.as_view(), name="users_api"),
    path('user/<int:pk>', UserAPI.as_view(), name="user_api"),
    path('profiles', ProfileList.as_view(), name="profiles_api"),
    path('profile_theme/<int:pk>', ProfileThemeAPI.as_view(), name="profile_theme_api"),
    path('profile_image/<int:pk>', ProfileImageAPI.as_view(), name="profile_image_api"),
    path('teams', TeamList.as_view(), name="teams_api"),
    path('team/<int:pk>', TeamAPI.as_view(), name="team_api"),
    path('departments', DepartmentList.as_view(), name="departments_api"),
    path('department/<int:pk>', DepartmentAPI.as_view(), name="department_api"),
    path('positions', PositionList.as_view(), name="positions_api"),
    path('employee_types', EmployeeTypeList.as_view(), name="employee_types_api"),
    path('employee_type/<int:pk>', EmployeeTypeAPI.as_view(), name="employee_type_api"),
    path('records', RecordList.as_view(), name="records_api"),
    path('currencies', CurrencyList.as_view(), name="currencies_api"),
]
