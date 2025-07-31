from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet, ForeignObjectRel, ForeignKey
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import fields, generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework_datatables.filters import DatatablesFilterBackend, f_search_q

from sales.api.serializers import *

class CustomDatatablesFilterBackend(DatatablesFilterBackend):

    def get_q(self, datatables_query):
        q = Q()
        initial_q = Q()
        for f in datatables_query['fields']:
            if not f['searchable']:
                continue
            q |= f_search_q(f,
                            datatables_query['search_value'],
                            datatables_query['search_regex'])
            initial_q &= f_search_q(f,
                                    f.get('search_value'),
                                    f.get('search_regex', False))
        q &= initial_q
        return q


class QueryListAPIView(generics.ListAPIView):
    def get_queryset(self):
        if self.request.GET.get('format', None) == 'datatables':
            self.filter_backends = (OrderingFilter, CustomDatatablesFilterBackend)
            return super().get_queryset()
        queryset = self.queryset

        # skip filters and sorting if they are not exists in the model to ensure security
        accepted_filters = {}
        # loop fields of the model
        for field in queryset.model._meta.get_fields():
            # if field exists in request, accept it
            if field.name in dict(self.request.GET):
                accepted_filters[field.name] = dict(self.request.GET)[field.name]
            if isinstance(field, ForeignObjectRel) or isinstance(field, ForeignKey):
                for n in field.related_model._meta.get_fields():
                    related_field = f"{field.name}__{n.name}"
                    if related_field in dict(self.request.GET):
                        accepted_filters[related_field] = dict(self.request.GET)[related_field]
        filters = {}
        for key, value in accepted_filters.items():
            if any(val in value for val in EMPTY_VALUES):
                if queryset.model._meta.get_field(key).null:
                    filters[key + '__isnull'] = True
                else:
                    filters[key + '__exact'] = ''
            else:
                filters[key + '__in'] = value
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.filter(**filters)
        return queryset

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            elif self.request.GET.get('format', None) == 'datatables':
                self._paginator = self.pagination_class()
            else:
                self._paginator = None
        return self._paginator


class ProjectList(QueryListAPIView):
    """
    Returns all projects
    Use GET parameters to filter queryset
    """
    custom_related_fields = []
    queryset = Project.objects.select_related(*custom_related_fields).all().exclude(quotation__notconfirmation__isnull=False)
    serializer_class = ProjectProcessListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class ProjectCreateAPI(generics.CreateAPIView):
    """
    Creates a project
    """
    queryset = Project.objects.all()
    serializer_class = ProjectCreateSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, responsible=self.request.user)


class ProjectUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update a project
    """
    queryset = Project.objects.all()
    serializer_class = ProjectCreateSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_claim_continue():
            return Response({"project": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class ProjectDetailAPI(generics.RetrieveAPIView):
    """
    Returns the project
    """
    custom_related_fields = ["responsible", "creator"]
    queryset = Project.objects.select_related(*custom_related_fields).all()
    serializer_class = ProjectDetailSerializer

class ProjectDuplicateAPI(generics.CreateAPIView):
    """
    Creates a project
    """
    queryset = Project.objects.all()
    serializer_class = ProjectDuplicateSerializer
    
    def get_serializer_context(self):
        pk = self.kwargs['pk']   
        project = get_object_or_404(Project,id=pk)
        return {"project": project,'parts':list(project.request.parts.all())}
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, responsible=self.request.user)

class ProjectDocumentList(QueryListAPIView):
    """
    Returns, delete or update a project document
    """
    queryset = ProjectDocument.objects.all()
    serializer_class = ProjectDocumentListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class ProjectDocumentCreateAPI(generics.CreateAPIView):
    """
    Creates a project document
    """
    queryset = ProjectDocument.objects.all()
    serializer_class = ProjectDocumentCreateSerializer


class ProjectDocumentUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update a project document
    """
    queryset = ProjectDocument.objects.all()
    serializer_class = ProjectDocumentCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.project.is_closed:
            return Response({"file": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

class ProjecNotConfirmedtList(QueryListAPIView):
    """
    Returns all projects
    Use GET parameters to filter queryset
    """
    custom_related_fields = []
    queryset = Project.objects.select_related(*custom_related_fields).all().filter(quotation__notconfirmation__isnull=False)
    serializer_class = ProjectProcessListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'
       
class RequestList(QueryListAPIView):
    """
    Returns all requests
    Use GET parameters to filter queryset
    """
    custom_related_fields = ['project', 'customer', 'vessel', 'maker_type']
    queryset = Request.objects.select_related(*custom_related_fields).all()
    serializer_class = RequestListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class RequestCreateAPI(generics.CreateAPIView):
    """
    Creates a request
    """
    queryset = Request.objects.all()
    serializer_class = RequestCreateSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class RequestUpdateAPI(generics.RetrieveUpdateAPIView):
    """
    Returns, delete or update the request
    """
    queryset = Request.objects.all()
    serializer_class = RequestCreateSerializer


class RequestDetailAPI(generics.RetrieveAPIView):
    """
    Returns the request
    """
    custom_related_fields = ['project', 'customer', 'vessel', 'maker', 'maker_type', 'person_in_contact']
    queryset = Request.objects.select_related(*custom_related_fields).all()
    serializer_class = RequestDetailSerializer


class RequestPartList(QueryListAPIView):
    """
    Returns all request parts
    Use GET parameters to filter queryset
    """
    custom_related_fields = ['request', 'part']
    queryset = RequestPart.objects.select_related(*custom_related_fields).all()
    serializer_class = RequestPartListSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = '__all__'
    search_fields = ['part__name', 'part__code']


class RequestPartCreateAPI(generics.CreateAPIView):
    """
    Creates a request part
    """
    queryset = RequestPart.objects.all()
    serializer_class = RequestPartCreateSerializer


class RequestPartUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the request part
    """
    queryset = RequestPart.objects.all()
    serializer_class = RequestPartCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.request.project.is_closed:
            return Response({"request_part": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.request.project.is_claim_continue():
            return Response({"request_part": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.inquiries.filter(quotations__quotation__confirmation__isnull=False):
            return Response(
                {"request_part": _("This request part can't be deleted due to it has been confirmed in quotations.")},
                status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class RequestPartDetailAPI(generics.RetrieveAPIView):
    """
    Returns the request part
    """
    custom_related_fields = ['request', 'part']
    queryset = RequestPart.objects.select_related(*custom_related_fields).all()
    serializer_class = RequestPartDetailSerializer


class InquiryList(QueryListAPIView):
    """
    Returns all inquiries
    Use GET parameters to filter queryset
    """
    custom_related_fields = ['project', 'supplier']
    queryset = Inquiry.objects.select_related(*custom_related_fields).all()
    serializer_class = InquiryListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class InquiryCreateAPI(generics.CreateAPIView):
    """
    Creates a inquiry
    """
    queryset = Inquiry.objects.all()
    serializer_class = InquiryCreateSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class InquiryUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the inquiry
    """
    queryset = Inquiry.objects.all()
    serializer_class = InquiryCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.project.is_closed:
            return Response({"inquiry": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.project.is_claim_continue():
            return Response({"inquiry": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.parts.filter(quotations__quotation__confirmation__isnull=False):
            return Response(
                {"inquiry": _(
                    "This inquiry can't be deleted due to its parts have been confirmed in quotations.")},
                status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class InquiryDetailAPI(generics.RetrieveAPIView):
    """
    Returns the inquiry
    """
    custom_related_fields = ['project', 'supplier', 'currency', 'creator']
    queryset = Inquiry.objects.select_related(*custom_related_fields).all()
    serializer_class = InquiryDetailSerializer


class InquiryPartList(QueryListAPIView):
    """
    Returns all inquiry parts
    Use GET parameters to filter queryset
    """
    custom_related_fields = ['inquiry', 'request_part']
    queryset = InquiryPart.objects.select_related(*custom_related_fields).all()
    serializer_class = InquiryPartListSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = '__all__'
    search_fields = ['request_part__part__name', 'request_part__part__code']
    
class InquiryPartAddList(QueryListAPIView):
    """
    Returns all inquiry parts may add in quotation
    Use GET parameters to filter queryset
    """
    custom_related_fields = ['inquiry', 'request_part']
    serializer_class = InquiryPartAddListSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = '__all__'
    search_fields = ['request_part__part__name', 'request_part__part__code']
    
    def get_serializer_context(self):
        pk = self.kwargs['pk']   
        quotation = get_object_or_404(Quotation,id=pk)
        return {"quotation": quotation}
    
    def get_queryset(self):
            pk = self.kwargs['pk']
            quotation = get_object_or_404(Quotation,id=pk)
            return InquiryPart.objects.all().filter(inquiry__project=quotation.project).order_by("created_at")   

class InquiryPartCreateAPI(generics.CreateAPIView):
    """
    Creates a inquiry part
    """
    queryset = InquiryPart.objects.all()
    serializer_class = InquiryPartCreateSerializer


class InquiryPartUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the inquiry part
    """
    queryset = InquiryPart.objects.all()
    serializer_class = InquiryPartCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.inquiry.project.is_closed:
            return Response({"inquiry_part": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.inquiry.project.is_claim_continue():
            return Response({"inquiry_part": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.quotations.filter(quotation__confirmation__isnull=False):
            return Response(
                {"inquiry_part": _("This inquiry part can't be deleted due to it has been confirmed in quotations.")},
                status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class InquiryPartDetailAPI(generics.RetrieveAPIView):
    """
    Returns the inquiry part
    """
    custom_related_fields = ['inquiry', 'request_part']
    queryset = InquiryPart.objects.select_related(*custom_related_fields).all()
    serializer_class = InquiryPartDetailSerializer


class QuotationList(QueryListAPIView):
    """
    Returns all quotations
    Use GET parameters to filter queryset
    """
    custom_related_fields = ['project']
    queryset = Quotation.objects.select_related(*custom_related_fields).all()
    serializer_class = QuotationListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class QuotationCreateAPI(generics.CreateAPIView):
    """
    Creates a quotation
    """
    queryset = Quotation.objects.all()
    serializer_class = QuotationCreateSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class QuotationUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the quotation
    """
    queryset = Quotation.objects.all()
    serializer_class = QuotationCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.project.is_closed:
            return Response({"quotation": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.project.is_claim_continue():
            return Response({"quotation": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if hasattr(instance, "confirmation"):
            return Response(
                {"quotation": _("This quotation can't be deleted due to it has been confirmed.")},
                status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class QuotationDetailAPI(generics.RetrieveAPIView):
    """
    Returns the quotation
    """
    custom_related_fields = ['project', 'currency', 'creator']
    queryset = Quotation.objects.select_related(*custom_related_fields).all()
    serializer_class = QuotationDetailSerializer


class QuotationPartList(QueryListAPIView):
    """
    Returns all quotation parts
    Use GET parameters to filter queryset
    """
    custom_related_fields = ['quotation', 'inquiry_part']
    queryset = QuotationPart.objects.select_related(*custom_related_fields).all()
    serializer_class = QuotationPartListSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = '__all__'
    search_fields = ['inquiry_part__request_part__part__name', 'inquiry_part__request_part__part__code']


class QuotationPartCreateAPI(generics.CreateAPIView):
    """
    Creates a quotation part
    """
    queryset = QuotationPart.objects.all()
    serializer_class = QuotationPartCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            print(serializer.data)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
class QuotationPartBulkCreateAPI(generics.CreateAPIView):
    """
    Creates multiple quotation parts
    """
    queryset = QuotationPart.objects.all()
    serializer_class = QuotationPartBulkSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data,list))
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
class QuotationPartBulkDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Updates and delete multiple quotation parts
    """
    queryset = Quotation.objects.all()
    serializer_class = QuotationCreateSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        quotationParts = instance.parts.all()
        print(quotationParts)
        if instance.project.is_closed:
            return Response({"quotation_part": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.project.is_claim_continue():
            return Response({"quotation_part": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if hasattr(instance, "confirmation"):
            return Response(
                {"quotation_part": _("This quotation part can't be deleted due to it is in a confirmed quotation.")},
                status=status.HTTP_400_BAD_REQUEST)
        if quotationParts:
            for part in quotationParts:
                if part.inquiry_part:
                    part.inquiry_part.is_added_in_quotation = False
                    part.inquiry_part.save()
            quotationParts.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
        


class QuotationPartUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the quotation part
    """
    queryset = QuotationPart.objects.all()
    serializer_class = QuotationPartCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.quotation.project.is_closed:
            return Response({"quotation_part": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.quotation.project.is_claim_continue():
            return Response({"quotation_part": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if hasattr(instance.quotation, "confirmation"):
            return Response(
                {"quotation_part": _("This quotation part can't be deleted due to it is in a confirmed quotation.")},
                status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class QuotationPartDetailAPI(generics.RetrieveAPIView):
    """
    Returns the quotation part
    """
    custom_related_fields = ['quotation', 'inquiry_part']
    queryset = QuotationPart.objects.select_related(*custom_related_fields).all()
    serializer_class = QuotationPartDetailSerializer


class OrderConfirmationList(QueryListAPIView):
    """
    Returns all order confirmations
    Use GET parameters to filter queryset
    """
    custom_related_fields = ['quotation']
    queryset = OrderConfirmation.objects.select_related(*custom_related_fields).all()
    serializer_class = OrderConfirmationListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class OrderConfirmationCreateAPI(generics.CreateAPIView):
    """
    Creates a order confirmation
    """
    queryset = OrderConfirmation.objects.all()
    serializer_class = OrderConfirmationCreateSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
        
class OrderNotConfirmationCreateAPI(generics.CreateAPIView):
    """
    Creates a order not confirmation
    """
    queryset = OrderNotConfirmation.objects.all()
    serializer_class = OrderNotConfirmationCreateSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class OrderConfirmationUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the order confirmation
    """
    queryset = OrderConfirmation.objects.all()
    serializer_class = OrderConfirmationCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.quotation.project.is_closed:
            return Response({"order_confirmation": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.quotation.project.is_claim_continue():
            return Response({"order_confirmation": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)    
        return super().destroy(request, *args, **kwargs)


class OrderConfirmationDetailAPI(generics.RetrieveAPIView):
    """
    Returns the order confirmation
    """
    queryset = OrderConfirmation.objects.all()
    serializer_class = OrderConfirmationDetailSerializer


class PurchaseOrderList(QueryListAPIView):
    """
    Returns all purchase orders
    Use GET parameters to filter queryset
    """
    custom_related_fields = ['project', 'order_confirmation', 'inquiry']
    queryset = PurchaseOrder.objects.select_related(*custom_related_fields).all()
    serializer_class = PurchaseOrderListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class PurchaseOrderCreateAPI(generics.CreateAPIView):
    """
    Creates a purchase order
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderCreateSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class PurchaseOrderUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the purchase order
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.project.is_closed:
            return Response({"purchase_order": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.project.is_claim_continue():
            return Response({"purchase_order": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)   
        return super().destroy(request, *args, **kwargs)


class PurchaseOrderDetailAPI(generics.RetrieveAPIView):
    """
    Returns the purchase order
    """
    custom_related_fields = ['project', 'order_confirmation', 'inquiry', 'creator', 'currency']
    queryset = PurchaseOrder.objects.select_related(*custom_related_fields).all()
    serializer_class = PurchaseOrderDetailSerializer


class PurchaseOrderPartList(QueryListAPIView):
    """
    Returns all purchase parts
    Use GET parameters to filter queryset
    """
    custom_related_fields = ['purchase_order', 'quotation_part']
    queryset = PurchaseOrderPart.objects.select_related(*custom_related_fields).all()
    serializer_class = PurchaseOrderPartListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class PurchaseOrderPartCreateAPI(generics.CreateAPIView):
    """
    Creates a purchase part
    """
    queryset = PurchaseOrderPart.objects.all()
    serializer_class = PurchaseOrderPartCreateSerializer


class PurchaseOrderPartListCreateAPI(generics.CreateAPIView):
    """
    Creates purchase parts by list
    very custom API
    """
    queryset = PurchaseOrderPart.objects.all()
    serializer_class = PurchaseOrderPartListCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ret = self.perform_create(serializer)
        headers = self.get_success_headers(ret)
        return Response(ret, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()


class PurchaseOrderPartUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the purchase part
    """
    queryset = PurchaseOrderPart.objects.all()
    serializer_class = PurchaseOrderPartCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.purchase_order.project.is_closed:
            return Response({"purchase_order_part": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.purchase_order.project.is_claim_continue():
            return Response({"purchase_order_part": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)        
        return super().destroy(request, *args, **kwargs)


class PurchaseOrderPartDetailAPI(generics.RetrieveAPIView):
    """
    Returns the purchase part
    """
    custom_related_fields = ['purchase_order', 'quotation_part']
    queryset = PurchaseOrderPart.objects.select_related(*custom_related_fields).all()
    serializer_class = PurchaseOrderPartDetailSerializer


class DeliveryList(QueryListAPIView):
    """
    Returns all deliveries
    Use GET parameters to filter queryset
    """
    custom_related_fields = ['country']
    queryset = Delivery.objects.select_related(*custom_related_fields).all()
    serializer_class = DeliveryListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'


class DeliveryCreateAPI(generics.CreateAPIView):
    """
    Creates a delivery
    """
    queryset = Delivery.objects.all()
    serializer_class = DeliveryCreateSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class DeliveryPartAddAPI(generics.CreateAPIView):
    """
    Adds a purchase order part to parts field of the Delivery model
    """
    serializer_class = DeliveryPartAddSerializer


class DeliveryPartRemoveAPI(generics.DestroyAPIView):
    """
    Removes a purchase order part from parts field of the Delivery model
    """

    def get_object(self, **kwargs):
        obj = get_object_or_404(Delivery, id=kwargs.get("delivery_pk"))
        purchase_order_part = get_object_or_404(obj.parts, id=kwargs.get("delivery_part_pk"))
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object(**kwargs)
        if instance.project.is_closed:
            return Response({"delivery": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.project.is_claim_continue():
            return Response({"delivery": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.is_delivered:
            return Response({"delivery": _("You can't modify the delivered delivery.")},
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance, **kwargs):
        instance.parts.remove(kwargs.get("delivery_part_pk"))
        instance.save()


class DeliveryUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the delivery
    """
    queryset = Delivery.objects.all()
    serializer_class = DeliveryCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.project.is_closed:
            return Response({"delivery": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.project.is_claim_continue():
            return Response({"delivery": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.is_delivered:
            return Response({"delivery": _("You can't modify the delivered delivery.")},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class DeliveryDetailAPI(generics.RetrieveAPIView):
    """
    Returns the delivery
    """
    queryset = Delivery.objects.all()
    serializer_class = DeliveryDetailSerializer


class DeliveryTransportationCreateAPI(generics.CreateAPIView):
    """
    Creates a delivery transportation
    """
    queryset = DeliveryTransportation.objects.all()
    serializer_class = DeliveryTransportationCreateSerializer


class DeliveryTransportationUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the delivery transportation
    """
    queryset = DeliveryTransportation.objects.all()
    serializer_class = DeliveryTransportationCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.delivery.project.is_closed:
            return Response({"delivery_transportation": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)

        if instance.delivery.project.is_claim_continue():
            return Response({"delivery_transportation": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)

        if instance.delivery.is_delivered:
            return Response({"delivery_transportation": _("You can't modify the delivered delivery.")},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class DeliveryTransportationDetailAPI(generics.RetrieveAPIView):
    """
    Returns the delivery transportation
    """
    queryset = DeliveryTransportation.objects.all()
    serializer_class = DeliveryTransportationDetailSerializer


class DeliveryTaxCreateAPI(generics.CreateAPIView):
    """
    Creates a delivery tax
    """
    queryset = DeliveryTax.objects.all()
    serializer_class = DeliveryTaxCreateSerializer


class DeliveryTaxUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the delivery tax
    """
    queryset = DeliveryTax.objects.all()
    serializer_class = DeliveryTaxCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.delivery.project.is_closed:
            return Response({"delivery_tax": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.delivery.project.is_claim_continue():
            return Response({"delivery_tax": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.delivery.is_delivered:
            return Response({"delivery_tax": _("You can't modify the delivered delivery.")},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class DeliveryTaxDetailAPI(generics.RetrieveAPIView):
    """
    Returns the delivery tax
    """
    queryset = DeliveryTax.objects.all()
    serializer_class = DeliveryTaxDetailSerializer


class DeliveryInsuranceCreateAPI(generics.CreateAPIView):
    """
    Creates a delivery insurance
    """
    queryset = DeliveryInsurance.objects.all()
    serializer_class = DeliveryInsuranceCreateSerializer


class DeliveryInsuranceUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the delivery insurance
    """
    queryset = DeliveryInsurance.objects.all()
    serializer_class = DeliveryInsuranceCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.delivery.project.is_closed:
            return Response({"delivery_insurance": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.delivery.project.is_claim_continue():
            return Response({"delivery_insurance": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.delivery.is_delivered:
            return Response({"delivery_insurance": _("You can't modify the delivered delivery.")},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class DeliveryInsuranceDetailAPI(generics.RetrieveAPIView):
    """
    Returns the delivery insurance
    """
    queryset = DeliveryInsurance.objects.all()
    serializer_class = DeliveryInsuranceDetailSerializer


class DeliveryCustomsCreateAPI(generics.CreateAPIView):
    """
    Creates a delivery customs
    """
    queryset = DeliveryCustoms.objects.all()
    serializer_class = DeliveryCustomsCreateSerializer


class DeliveryCustomsUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the delivery customs
    """
    queryset = DeliveryCustoms.objects.all()
    serializer_class = DeliveryCustomsCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.delivery.project.is_closed:
            return Response({"delivery_customs": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.delivery.project.is_claim_continue():
            return Response({"delivery_customs": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.delivery.is_delivered:
            return Response({"delivery_customs": _("You can't modify the delivered delivery.")},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class DeliveryCustomsDetailAPI(generics.RetrieveAPIView):
    """
    Returns the delivery customs
    """
    queryset = DeliveryCustoms.objects.all()
    serializer_class = DeliveryCustomsDetailSerializer


class DeliveryPackingCreateAPI(generics.CreateAPIView):
    """
    Creates a delivery packing
    """
    queryset = DeliveryPacking.objects.all()
    serializer_class = DeliveryPackingCreateSerializer


class DeliveryPackingUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update the delivery packing
    """
    queryset = DeliveryPacking.objects.all()
    serializer_class = DeliveryPackingCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.delivery.project.is_closed:
            return Response({"delivery_packing": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.delivery.project.is_claim_continue():
            return Response({"delivery_packing": _("You can't modify this project due to it claimed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        if instance.delivery.is_delivered:
            return Response({"delivery_packing": _("You can't modify the delivered delivery.")},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class DeliveryPackingDetailAPI(generics.RetrieveAPIView):
    """
    Returns the delivery packing
    """
    queryset = DeliveryPacking.objects.all()
    serializer_class = DeliveryPackingDetailSerializer

class ProjectClaimsFollowUpList(QueryListAPIView):
    """
    Returns all claims follow ups
    Use GET parameters to filter queryset
    """
    custom_related_fields = []
    queryset = ClaimsFollowUp.objects.select_related(*custom_related_fields).all()
    serializer_class = ClaimsFollowUpListSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = '__all__'

class ClaimsFollowUpCreateAPI(generics.CreateAPIView):
    """
    Creates a claims follow up
    """
    queryset = ClaimsFollowUp.objects.all()
    serializer_class = ClaimsFollowUpCreateSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
        
class ClaimsFollowUpUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns, delete or update a claims follow up
    """
    queryset = ClaimsFollowUp.objects.all()
    serializer_class = ClaimsFollowUpUpdateSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.delivery.project.is_closed:
            return Response({"file": _("You can't modify this project due to it has been closed.")},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)
    
class ClaimsFollowUpDetailAPI(generics.RetrieveAPIView):
    """
    Returns the claims follow up
    """
    custom_related_fields = []
    queryset = ClaimsFollowUp.objects.select_related(*custom_related_fields).all()
    serializer_class = ClaimsFollowUpDetailSerializer