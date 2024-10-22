from django.urls import path
from . import views

urlpatterns = [
    path("get/", views.test, name="test"),
    path("collect_input", views.collect_input, name="collect_input"),
]
