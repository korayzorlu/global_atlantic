"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    #path(str(os.getenv('SECRET_ADMIN_URL')) + '/admin/', admin.site.urls),
    path('very_secret_url/admin/', admin.site.urls),
    #path(str(os.getenv('SECRET_ADMIN_URL')) + '/admin/clearcache/', include('clearcache.urls')),
    path('very_secret_url/admin/clearcache/', include('clearcache.urls')),
    path('', include('user.urls')),
    #path('beta/', include('beta_profile.urls')),
    path('information/', include("information.urls")),
    path('sales/', include("parts.urls")),  # we show parts as sales in url to not confuse user
    path('sales/', include("sales.urls")),
    path('hr/', include("hr.urls")),
    path('beta_hr/', include("beta_hr.urls")),
    path('notification/', include("notifications.urls")),
    path('card/', include("card.urls")),
    path('data/', include("data.urls")),
    #path('user/', include("user.urls")),
    path('scan/', include("scan.urls")),
    path('sale/', include("sale.urls")),
    path('note/', include("note.urls")),
    path('account/', include("account.urls")),
    path('library/', include("library.urls")),
    path('source/', include("source.urls")),
    path('service/', include("service.urls")),
    path('event/', include("event.urls")),
    path('mikro/', include("mikro.urls")),
    path('chat/', include("chat.urls")),
    path("select2/", include("django_select2.urls")),
    path('report/', include("report.urls")),
    path('purchasing/', include("purchasing.urls")),
    path('administration/', include("administration.urls")),
    path('warehouse/', include("warehouse.urls")),
    # path("__debug__/", include("debug_toolbar.urls")),
    #path('maintenance/', UserDataView.as_view(), name="user_data"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
