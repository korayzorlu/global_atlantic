from django.urls import path, include

from .views.warehouse_views import *
from .views.part_item_views import *
from .views.dispatch_views import *

app_name = "warehouse"

urlpatterns = [
    path('warehouse_data/', WarehouseDataView.as_view(), name="warehouse_data"),
    path('warehouse_add/', WarehouseAddView.as_view(), name = "warehouse_add"),
    path('warehouse_update/<int:id>/', WarehouseUpdateView.as_view(), name = "warehouse_update"),
    path('warehouse_delete/<str:list>/', WarehouseDeleteView.as_view(), name = "warehouse_delete"),
    
    path('part_item_data/', PartItemDataView.as_view(), name="part_item_data"),
    path('part_item_add/', PartItemAddView.as_view(), name = "part_item_add"),
    path('part_item_update/<int:id>/', PartItemUpdateView.as_view(), name = "part_item_update"),
    path('part_item_delete/<str:list>/', PartItemDeleteView.as_view(), name = "part_item_delete"),

    path('dispatch_data/', DispatchDataView.as_view(), name="dispatch_data"),
    path('dispatch_add/', DispatchAddView.as_view(), name = "dispatch_add"),
    path('dispatch_update/<int:id>/', DispatchUpdateView.as_view(), name = "dispatch_update"),
    path('dispatch_delete/<str:list>/', DispatchDeleteView.as_view(), name = "dispatch_delete"),
    
    path('api/', include("warehouse.api.urls")),
]