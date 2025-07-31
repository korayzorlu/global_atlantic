from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
# Create your views here.
from django.views import View
from django.contrib import messages
from django.core import serializers
from urllib.parse import urlparse


import pandas as pd
import json

class VesselApiDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Vessel API")
        elementTag  ="vesselapi"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'scan/vessel_api.html', context)