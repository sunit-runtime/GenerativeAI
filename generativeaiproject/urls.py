"""
URL configuration for the generativeaiproject.
This module defines the URL patterns for the Django project, including custom error handlers and 
routes for various views such as submitting prompts, viewing results, user authentication, and 
password management.
Routes:
    - admin/: Admin site.
    - /: Redirects to the submit prompt page.
    - submit/: Submit a prompt.
    - results/<int:prompt_id>/: View results for a specific prompt.
    - login/: User login.
    - register/: User registration.
    - logout/: User logout.
    - resetPassword/: Send password reset email.
    - change-password/<str:token>/: Reset password using a token.
    - favicon.ico: Redirects to the favicon.
Custom Error Handlers:
    - handler404: Custom 404 page not found view.
    - handler500: Custom 500 internal server error view.
    - handler403: Custom 403 permission denied view.
    - handler400: Custom 400 bad request view.
Static Files:
    - Serves static files during development.
"""

from generativeaiproject import settings
from django.conf.urls.static import static
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
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
