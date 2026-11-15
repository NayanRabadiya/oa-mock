from django.urls import include, path

urlpatterns = [
    path("api/returns/", include("returns.urls")),
]
