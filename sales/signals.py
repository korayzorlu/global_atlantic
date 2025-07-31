import time

from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver

from sales.models import ClaimsFollowUp, OrderNotConfirmation, Project, RequestPart, Inquiry, InquiryPart, Quotation, Request, QuotationPart, PurchaseOrder, \
    OrderConfirmation, PurchaseOrderPart, Delivery, DeliveryTransportation, DeliveryTax, DeliveryInsurance, \
    DeliveryCustoms, DeliveryPacking


@receiver(pre_save, sender=Project)
def define_project_no(sender, instance, **kwargs):
    year = int(time.strftime("%y"))
    if instance._state.adding:
        last_project = Project.objects.filter(no__regex=f'^ESP-{year:03}-[0-9]{{8}}$').order_by('-no').first()
        if last_project:
            last_no = int(last_project.no.split('-')[2])
            instance.no = f'ESP-{year:03}-{last_no + 1:08}'
        else:
            instance.no = f'ESP-{year:03}-{1:08}'
    else:
        pass


@receiver(pre_save, sender=Request)
def define_request_no(sender, instance, **kwargs):
    year = int(time.strftime("%y"))
    if instance._state.adding or not instance.no:
        last_request = Request.objects.filter(no__regex=f'^ESR-{year:03}-[0-9]{{8}}$').order_by('-no').first()
        if last_request:
            last_no = int(last_request.no.split('-')[2])
            instance.no = f'ESR-{year:03}-{last_no + 1:08}'
        else:
            instance.no = f'ESR-{year:03}-{1:08}'
    else:
        pass


@receiver(pre_save, sender=RequestPart)
def define_request_part_order_no(sender, instance, **kwargs):
    if instance._state.adding:
        last_request_part = RequestPart.objects.filter(request=instance.request).order_by('-order_no').first()
        if last_request_part:
            instance.order_no = last_request_part.order_no + 1
        else:
            instance.order_no = 1
    else:
        pass


@receiver(pre_save, sender=Inquiry)
def define_inquiry_no(sender, instance, **kwargs):
    year = int(time.strftime("%y"))
    if instance._state.adding:
        last_inquiry = Inquiry.objects.filter(no__regex=f'^ESI-{year:03}-[0-9]{{8}}$').order_by('-no').first()
        if last_inquiry:
            last_no = int(last_inquiry.no.split('-')[2])
            instance.no = f'ESI-{year:03}-{last_no + 1:08}'
        else:
            instance.no = f'ESI-{year:03}-{1:08}'
    else:
        pass


@receiver(pre_save, sender=InquiryPart)
def define_inquiry_part_order_no(sender, instance, **kwargs):
    if instance._state.adding:
        last_inquiry_part = InquiryPart.objects.filter(inquiry=instance.inquiry).order_by('-order_no').first()
        if last_inquiry_part:
            instance.order_no = last_inquiry_part.order_no + 1
        else:
            instance.order_no = 1
    else:
        pass


@receiver(pre_save, sender=Quotation)
def define_quotation_no(sender, instance, **kwargs):
    year = int(time.strftime("%y"))
    if instance._state.adding:
        last_quotation = Quotation.objects.filter(no__regex=f'^ESQ-{year:03}-[0-9]{{8}}$').order_by('-no').first()
        if last_quotation:
            last_no = int(last_quotation.no.split('-')[2])
            instance.no = f'ESQ-{year:03}-{last_no + 1:08}'
        else:
            instance.no = f'ESQ-{year:03}-{1:08}'
    else:
        pass


@receiver(pre_save, sender=PurchaseOrder)
def define_purchase_order_no(sender, instance, **kwargs):
    year = int(time.strftime("%y"))
    if instance._state.adding:
        last_purchase = PurchaseOrder.objects.filter(no__regex=f'^ESP-{year:03}-[0-9]{{8}}$').order_by('-no').first()
        if last_purchase:
            last_no = int(last_purchase.no.split('-')[2])
            instance.no = f'ESP-{year:03}-{last_no + 1:08}'
        else:
            instance.no = f'ESP-{year:03}-{1:08}'
    else:
        pass


@receiver(pre_save, sender=Delivery)
def define_delivery_no(sender, instance, **kwargs):
    year = int(time.strftime("%y"))
    if instance._state.adding:
        last_delivery = Delivery.objects.filter(no__regex=f'^ESD-{year:03}-[0-9]{{8}}$').order_by('-no').first()
        if last_delivery:
            last_no = int(last_delivery.no.split('-')[2])
            instance.no = f'ESD-{year:03}-{last_no + 1:08}'
        else:
            instance.no = f'ESD-{year:03}-{1:08}'
    else:
        pass


@receiver(pre_save, sender=OrderConfirmation)
def define_order_confirmation_no(sender, instance, **kwargs):
    year = int(time.strftime("%y"))
    if instance._state.adding or not instance.no:
        last_order_confirmation = OrderConfirmation.objects.filter(no__regex=f'^ESC-{year:03}-[0-9]{{8}}$').order_by(
            '-no').first()
        if last_order_confirmation:
            last_no = int(last_order_confirmation.no.split('-')[2])
            instance.no = f'ESC-{year:03}-{last_no + 1:08}'
        else:
            instance.no = f'ESC-{year:03}-{1:08}'
    else:
        pass
    
@receiver(pre_save, sender=OrderNotConfirmation)
def define_order_not_confirmation_no(sender, instance, **kwargs):
    year = int(time.strftime("%y"))
    if instance._state.adding or not instance.no:
        last_order_not_confirmation = OrderNotConfirmation.objects.filter(no__regex=f'^ESNC-{year:03}-[0-9]{{8}}$').order_by(
            '-no').first()
        if last_order_not_confirmation:
            last_no = int(last_order_not_confirmation.no.split('-')[2])
            instance.no = f'ESNC-{year:03}-{last_no + 1:08}'
        else:
            instance.no = f'ESNC-{year:03}-{1:08}'
    else:
        pass
    
@receiver(pre_save, sender=ClaimsFollowUp)
def define_claims_follow_up_no(sender, instance, **kwargs):
    year = int(time.strftime("%y"))
    if instance._state.adding or not instance.no:
        last_claims_follow_up = ClaimsFollowUp.objects.filter(no__regex=f'^ESCFU-{year:03}-[0-9]{{8}}$').order_by(
            '-no').first()
        if last_claims_follow_up:
            last_no = int(last_claims_follow_up.no.split('-')[2])
            instance.no = f'ESCFU-{year:03}-{last_no + 1:08}'
        else:
            instance.no = f'ESCFU-{year:03}-{1:08}'
    else:
        pass    


@receiver(post_save, sender=Delivery)
def create_delivery_inner_input_objects(sender, instance, created, **kwargs):
    if created:
        DeliveryTransportation.objects.create(delivery=instance)
        DeliveryTax.objects.create(delivery=instance)
        DeliveryInsurance.objects.create(delivery=instance)
        DeliveryCustoms.objects.create(delivery=instance)
        DeliveryPacking.objects.create(delivery=instance)
    else:
        pass


@receiver(post_delete, sender=Request)
def checkups_after_request_delete(sender, instance, using, **kwargs):
    if instance.project:
        print("stage updated by request delete signal")
        instance.project.update_stage()
        instance.project.save()


@receiver(post_delete, sender=RequestPart)
def checkups_after_request_part_delete(sender, instance, using, **kwargs):
    if instance.request.project:
        print("stage updated by request part delete signal")
        instance.request.project.update_stage()
        instance.request.project.save()


@receiver(post_delete, sender=Inquiry)
def checkups_after_inquiry_delete(sender, instance, using, **kwargs):
    if instance.project:
        print("stage updated by inquiry delete signal")
        instance.project.update_stage()
        instance.project.save()


@receiver(post_delete, sender=InquiryPart)
def checkups_after_inquiry_part_delete(sender, instance, using, **kwargs):
    if instance.inquiry.project:
        print("stage updated by inquiry part delete signal")
        instance.inquiry.project.update_stage()
        instance.inquiry.project.save()


@receiver(post_delete, sender=Quotation)
def checkups_after_quotation_delete(sender, instance, using, **kwargs):
    if instance.project:
        print("stage updated by quotation delete signal")
        instance.project.update_stage()
        instance.project.save()


@receiver(post_delete, sender=QuotationPart)
def checkups_after_quotation_part_delete(sender, instance, using, **kwargs):
    if hasattr(instance.quotation, "confirmation"):
        print("order confirmation deleted by quotation part delete signal")
        instance.quotation.confirmation.delete()
    if instance.quotation.project:
        print("stage updated by quotation part delete signal")
        instance.quotation.project.update_stage()
        instance.quotation.project.save()


@receiver(post_delete, sender=OrderConfirmation)
def checkups_after_order_confirmation_delete(sender, instance, using, **kwargs):
    if instance.quotation.project:
        print("stage updated by order confirmation delete signal")
        instance.quotation.project.update_stage()
        instance.quotation.project.save()


@receiver(post_delete, sender=PurchaseOrder)
def checkups_after_purchase_order_delete(sender, instance, using, **kwargs):
    if instance.project:
        print("stage updated by purchase order delete signal")
        instance.project.update_stage()
        instance.project.save()


@receiver(post_delete, sender=PurchaseOrderPart)
def checkups_after_purchase_order_part_delete(sender, instance, using, **kwargs):
    if instance.purchase_order.project:
        print("stage updated by purchase order part delete signal")
        instance.purchase_order.project.update_stage()
        instance.purchase_order.project.save()


@receiver(post_delete, sender=Delivery)
def checkups_after_delivery_delete(sender, instance, using, **kwargs):
    if instance.project:
        print("stage updated by delivery delete signal")
        instance.project.update_stage()
        instance.project.save()
