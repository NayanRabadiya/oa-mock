from django.urls import path

from . import views

urlpatterns = [
    path("books", views.list_books),
    path("loans", views.borrow_book),
    path("loans/<str:loan_id>/return", views.return_book),
]
