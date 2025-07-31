from django.contrib.auth.views import LogoutView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.urls import path, include

from .views import *

urlpatterns = [
    # path('', DashboardView.as_view(), name="beta_dashboard"),
    # path('landing/', LandingPageView.as_view(), name="beta_landing_page"),
    # path('user/profile/', ProfileView.as_view(), name="beta_profile_page"),
    # path('logout/', LogoutView.as_view(), name="beta_logout"),
    # path('password_reset/', CustomPasswordResetView.as_view(), name='beta_password_reset'),
    # path('password_reset_done/', PasswordResetDoneView.as_view(), name='beta_password_reset_done'),
    # path('password_reset_confirm/<slug:uidb64>/<slug:token>', PasswordResetConfirmView.as_view(),
    #      name='beta_password_reset_confirm'),
    # path('password_reset_complete/', PasswordResetCompleteView.as_view(), name='beta_password_reset_complete'),

    path('api/', include("beta_profile.api.urls")),
]
