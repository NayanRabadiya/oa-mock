from django.urls import path

from . import views

urlpatterns = [
    path("tickets", views.tickets),
    path("tickets/overdue", views.overdue),
    path("tickets/<str:ticket_id>/assign", views.assign),
    path("tickets/<str:ticket_id>/status", views.change_status),
]
