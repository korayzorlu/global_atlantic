

from django.contrib.auth.models import User
from django.db import close_old_connections
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.deprecation import MiddlewareMixin
from asgiref.sync import sync_to_async
import psycopg2.pool

from django.shortcuts import redirect, render
from django.urls import resolve
from urllib.parse import urlparse
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse

import os
import psutil
import socket
import logging
import requests

import threading
#import htmx

# Her thread için bir yerel kullanıcı değişkeni
_user = threading.local()

def get_current_user():
    return getattr(_user, 'user', None)

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.user = request.user  # Request'teki kullanıcıyı yakalıyoruz
        response = self.get_response(request)
        return response

_thread_locals = threading.local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

class CurrentRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response

class PostgreSQLConnectionMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            1,  # Minimum bağlantı sayısı
            300,  # Maksimum bağlantı sayısı
            database="michoappdb",
            user="micho",
            password="9527",
            host="localhost",
            port='5432',
        )

    def __call__(self, request):
        response = self.get_response(request)
        close_old_connections()  # Her istek sonrası bağlantıları temizle
        return response

    async def process_request(self, request):
        await self.process_request_async(request)

    @sync_to_async
    def process_request_async(self, request):
        if not isinstance(request.user, User):
            pass  # İlgili işlemleri buraya yazın
        

class TokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger = logging.getLogger("django")
        app_name = resolve(request.path_info).app_name
        
        if app_name == "admin":
            return self.get_response(request)
        
        if os.environ.get('MAINTENANCE_MODE') == "True":
            return render(request, 'maintenance_page.html')
        
        if app_name == "administration":
            ip = os.environ.get('IP')
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ipAddress = x_forwarded_for.split(',')[0]
            else:
                ipAddress = request.META.get('REMOTE_ADDR')
            logger.info(ipAddress)      
            if not ipAddress:
                return HttpResponseForbidden("IP not found.")

            if ipAddress != ip:
                return HttpResponseForbidden("Access denied.")
        
        return self.get_response(request)

class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url_name = resolve(request.path_info).url_name
        app_name = resolve(request.path_info).app_name

        # Anasayfa URL'ini hariç tut
        if url_name == 'dashboard' or url_name == 'landing_page' or "api" in str(url_name) or "index" in str(url_name):
            return self.get_response(request)
        
        if app_name == "admin":
            return self.get_response(request)
        
        if "/media/source/companies/" in request.path_info:
            return self.get_response(request)

        # if not request.META.get("HTTP_HX_REQUEST"):
        #     return redirect("/")
        
        if not request.user.is_authenticated and request.META.get("HTTP_HX_REQUEST"):
            response = HttpResponse()
            response['HX-Redirect'] = '/'  # HTMX yönlendirme başlığını ayarla
            return response
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if not request.META.get("HTTP_REFERER"):
            return redirect("/")
        # if str(refererPath) == "b''":
        #     return redirect("/")
        
        if 'HX-History-Restore-Request' in request.headers:
            pass
        
        request.session['session_restore'] = True

        response = self.get_response(request)
        return response
    

