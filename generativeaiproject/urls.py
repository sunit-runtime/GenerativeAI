from generativeaiproject import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico")),
    path("", RedirectView.as_view(url="/submit/"), name="home"),
    path("", include("testflow.urls")),
    path("api/lang-graph/", include("LangGraphApplication.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
