from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from django.core.signals import request_finished

from .models import Part, PartUnique

from sale.models import RequestPart, InquiryPart, QuotationPart, PurchaseOrderPart
from account.models import SendInvoicePart, ProformaInvoicePart, IncomingInvoicePart
from service.models import OfferPart

import inspect
            
@receiver(pre_save, sender=Part)
def update_part(sender, instance, **kwargs):
    if sender.objects.filter(id=instance.id).exists():

        senderPart = sender.objects.get(id=instance.id)

        if getattr(senderPart, "techncialSpecification") != getattr(instance, "techncialSpecification"):
            if not instance.techncialSpecification:
                matchedPartSender = Part.objects.select_related().filter(sourceCompany = senderPart.sourceCompany,techncialSpecification = senderPart.techncialSpecification).exclude(id = senderPart.id).order_by("-partUniqueCode").first()
                if matchedPartSender:
                    startPartUniqueCodeValue = 1
                    startPartUniqueValue = 101
                    
                    lastPartUnique = PartUnique.objects.select_related().filter(sourceCompany = senderPart.sourceCompany).order_by('-code').first()
                    
                    if lastPartUnique:  
                        newPartUnique = PartUnique.objects.create(sourceCompany = senderPart.sourceCompany,code = int(lastPartUnique.code) + 1)
                        newPartUnique.save()
                    else:
                        newPartUnique = PartUnique.objects.create(sourceCompany = senderPart.sourceCompany,code = int(startPartUniqueValue))
                        newPartUnique.save()
                    
                    instance.partUnique = newPartUnique
                    instance.partUniqueCode = int(startPartUniqueCodeValue)
            else:
                matchedPartT = Part.objects.select_related("partUnique").filter(sourceCompany = senderPart.sourceCompany,techncialSpecification = instance.techncialSpecification).exclude(id = instance.id).order_by("-partUniqueCode").first()
                if matchedPartT:
                    instance.partUnique = matchedPartT.partUnique
                    instance.partUniqueCode = int(matchedPartT.partUniqueCode) + 1
                else:
                    matchedPartSender = Part.objects.select_related().filter(sourceCompany = senderPart.sourceCompany,techncialSpecification = senderPart.techncialSpecification).exclude(id = senderPart.id).order_by("-partUniqueCode").first()
                    if matchedPartSender:
                        startPartUniqueCodeValue = 1
                        startPartUniqueValue = 101
                        
                        lastPartUnique = PartUnique.objects.select_related().filter(sourceCompany = senderPart.sourceCompany).order_by('-id').order_by('-code').first()
                        
                        if lastPartUnique:  
                            newPartUnique = PartUnique.objects.create(sourceCompany = senderPart.sourceCompany,code = int(lastPartUnique.code) + 1)
                            newPartUnique.save()
                        else:
                            newPartUnique = PartUnique.objects.create(sourceCompany = senderPart.sourceCompany,code = int(startPartUniqueValue))
                            newPartUnique.save()
                        
                        instance.partUnique = newPartUnique
                        instance.partUniqueCode = int(startPartUniqueCodeValue)
                        
                        if senderPart.techncialSpecification:
                            matchedPartIns = Part.objects.select_related().filter(sourceCompany = senderPart.sourceCompany,techncialSpecification = senderPart.techncialSpecification).order_by("partUniqueCode")
                            print(matchedPartIns)
                            for index, matchedPartIn in enumerate(matchedPartIns):
                                matchedPartIn.partUniqueCode = index + 1
                                
                            matchedPartIns.update()
                            
                        
            

            