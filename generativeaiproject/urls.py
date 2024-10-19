from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from testflow import views
from django.conf.urls import handler404, handler500, handler403, handler400
from testflow.views import (
    custom_page_not_found_view,
    custom_error_view,
    custom_permission_denied_view,
    custom_bad_request_view,
)

handler404 = custom_page_not_found_view
handler500 = custom_error_view
handler403 = custom_permission_denied_view
handler400 = custom_bad_request_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/submit/"), name="home"),
    path("submit/", views.submit_prompt, name="submit_prompt"),
    path("results/<int:prompt_id>/", views.prompt_results, name="prompt_results"),
    path("login/", views.user_login, name="login"),
    path("register/", views.user_register, name="register"),
    path("logout/", views.user_logout, name="logout"),
    path("resetPassword/", views.send_email, name="send_email"),
    path("change-password/<str:token>/", views.new_password, name="reset_password"),
]
