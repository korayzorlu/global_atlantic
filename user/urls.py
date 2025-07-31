from django.contrib.auth.views import LogoutView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.urls import path, include

from .views import *

app_name = "user"

urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard"),
    path('landing/', LandingPageView.as_view(), name="landing_page"),
    path('user/profile/', ProfileView.as_view(), name="profile_page"),
    path('profile/<str:username>/', UserProfileView.as_view(), name="user_profile"),
    path('source_company_update/', SourceCompanyUpdateView.as_view(), name="source_company_update"),
    path('light_theme_update/', LightThemeUpdateView.as_view(), name="light_theme_update"),
    path('dark_theme_update/', DarkThemeUpdateView.as_view(), name="dark_theme_update"),
    path('card_color_update/', CardColorUpdateView.as_view(), name="card_color_update"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<slug:uidb64>/<slug:token>', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password_reset_complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    path('access_authorization_data/', AccessAuthorizationDataView.as_view(), name="access_authorization_data"),
    path('access_authorization_add/', AccessAuthorizationAddView.as_view(), name = "access_authorization_add"),
    path('access_authorization_update/<int:id>/', AccessAuthorizationUpdateView.as_view(), name = "access_authorization_update"),
    path('access_authorization_delete/<str:list>/', AccessAuthorizationDeleteView.as_view(), name = "access_authorization_delete"),
    
    path('data_authorization_data/', DataAuthorizationDataView.as_view(), name="data_authorization_data"),
    path('data_authorization_add/', DataAuthorizationAddView.as_view(), name = "data_authorization_add"),
    path('data_authorization_update/<int:id>/', DataAuthorizationUpdateView.as_view(), name = "data_authorization_update"),
    path('data_authorization_delete/<str:list>/', DataAuthorizationDeleteView.as_view(), name = "data_authorization_delete"),
    
    path('user_authorization_data/', UserAuthorizationDataView.as_view(), name="user_authorization_data"),
    path('user_authorization_update/<int:id>/', UserAuthorizationUpdateView.as_view(), name = "user_authorization_update"),

    path('api/', include("user.api.urls")),
]
