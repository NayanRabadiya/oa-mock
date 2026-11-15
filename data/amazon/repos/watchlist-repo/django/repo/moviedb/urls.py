from django.urls import include, path

urlpatterns = [
    path("api/auth/", include("accounts.urls")),
    path("api/movies/", include("movies.urls")),
    path("api/watchlist/", include("watchlist.urls")),
]
