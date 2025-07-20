from django.urls import path
from . import views

app_name = "ticket"

urlpatterns = [
    path("", views.TicketListView.as_view(), name="tickets"),
    path("create/", views.ticketCreateView, name="tickets_add"),
    path("<int:pk>/update-status/", views.orderStatusUpdate, name="tickets_update_status"),
    path("<int:pk>/view/", views.TicketMessagesView, name="tickets_view"),
]