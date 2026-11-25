from django.urls import path

from . import views

urlpatterns = [
    path("evaluate", views.evaluate_return),
    path("customer/<str:customer_id>", views.customer_returns),
]
