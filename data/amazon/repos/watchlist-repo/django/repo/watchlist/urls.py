from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_watchlist),
    path("check/<str:movie_id>", views.check_watchlist_status),
    path("add", views.add_to_watchlist),
    path("remove", views.add_to_watchlist),
]
