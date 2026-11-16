from django.urls import path

from . import views

urlpatterns = [
    path("wallets/<str:wallet_id>", views.get_wallet),
    path("wallets/<str:wallet_id>/deposit", views.deposit),
    path("wallets/<str:wallet_id>/withdraw", views.withdraw),
    path("wallets/<str:wallet>/transactions", views.transactions),
    path("transfer", views.create_transfer),
]
