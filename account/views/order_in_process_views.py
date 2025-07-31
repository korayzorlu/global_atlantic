from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
# Create your views here.
from django.views import View
from django.contrib import messages
from django.core import serializers
from urllib.parse import urlparse

from sale.models import OrderTracking

class OrderInProcessDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Process Status")
        elementTag = "orderInProcessA"
        elementTagSub = "quotationPartOICA"
        
        """
        orderTracking = OrderTracking.objects.filter()
        offer = Offer.objects.filter()
        
        combined_queryset = list(chain(orderTracking, offer))
        
        orderInProcessAJSON = {"data":[]}
        
        for object in combined_queryset:
            if object.__class__.__name__ == "OrderTracking":
                if object.purchaseOrders.all()[0].inquiry.theRequest.customer:
                    customer = object.purchaseOrders.all()[0].inquiry.theRequest.customer.name
                else:
                    customer = ""
                    
                if object.purchaseOrders.all()[0].inquiry.theRequest.vessel:
                    vessel = object.purchaseOrders.all()[0].inquiry.theRequest.vessel.name
                else:
                    vessel = ""
                    
                if object.purchaseOrders.all()[0].orderConfirmation:
                    status = object.purchaseOrders.all()[0].orderConfirmation.status
                else:
                    status = ""
                
                collections = Collection.objects.filter(orderTracking = object)
                
                if collections[0].agent:
                    agent = collections[0].agent.name
                else:
                    agent = ""
                    
                if object.purchaseOrders.all()[0].inquiry.theRequest.maker:
                    maker = object.purchaseOrders.all()[0].inquiry.theRequest.maker.name
                else:
                    maker = ""
                    
                if object.purchaseOrders.all()[0].inquiry.theRequest.makerType:
                    makerType = object.purchaseOrders.all()[0].inquiry.theRequest.makerType.name
                else:
                    makerType = ""
                    
                poList = []
                
                for po in object.purchaseOrders.all():
                    poList.append(po.id)
                    
                if object.purchaseOrders.all()[0].inquiry.supplier:
                    supplier = object.purchaseOrders.all()[0].inquiry.supplier.name
                else:
                    supplier = ""
                    
                if collections[0].port:
                    port = collections[0].port
                else:
                    port = ""
                    
                orderInProcessAJSON["data"].append({
                    "id" : object.id,
                    "no" : object.project.projectNo,
                    "created_date" : object.created_date.date().isoformat(),
                    "customer" : customer,
                    "vessel" : vessel,
                    "status" : status,
                    "agent" : agent,
                    "maker" : maker,
                    "makerType" : makerType,
                    "poList" : poList,
                    "supplier" : supplier,
                    "port" : port,
                    "type" : "sale"
                    
                })
            elif object.__class__.__name__ == "Offer":
                if object.status != "offer":
                    orderInProcessAJSON["data"].append({
                        "id" : object.id,
                        "no" : object.offerNo,
                        "created_date" : object.created_date.date().isoformat(),
                        "customer" : object.customer.name,
                        "vessel" : object.vessel.name,
                        "status" : object.status,
                        "agent" : "",
                        "maker" : "",
                        "makerType" : "",
                        "poList" : [],
                        "supplier" : "",
                        "port" : "",
                        "type" : "service"
                        
                    })
        
        orderInProcessAJSON = json.dumps(orderInProcessAJSON)
        
        with open(os.path.join(os.getcwd(), "media", "orderInProcessA.json"), "w") as f:
            f.write(orderInProcessAJSON)
        """
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/order_in_processes.html', context)
    
class OrderInProcessUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Order In Process Detail")
        elementTag = "orderInProcessA"
        elementTagSub = "quotationPartOICA"
        elementTagId = id

        orderTracking = get_object_or_404(OrderTracking, id = id)
        
        purchaseOrders = orderTracking.purchaseOrders.filter(sourceCompany = request.user.profile.sourceCompany)
        collections = orderTracking.collection_set.select_related("purchaseOrder")
        print(purchaseOrders[0].orderConfirmation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "orderTracking" : orderTracking,
                "purchaseOrders" : purchaseOrders,
                "collections" : collections,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/order_in_process_detail.html', context)
    