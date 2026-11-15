from django.urls import path

from . import views

urlpatterns = [
    path("", views.list_movies),
    path("<str:movie_id>", views.movie_detail),
    path("<str:movie_id>/rate", views.rate_movie),
]
