"""is_it_keto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from isitketo.sitemaps import sitemaps

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("accounts/", include("allauth.urls")),
        path("", include("core.urls")),
        path(
            "sitemap.xml",
            sitemap,
            {"sitemaps": sitemaps},
            name="django.contrib.sitemaps.views.sitemap",
        ),
        path("privacy-policy", TemplateView.as_view(template_name="pages/privacy-policy.html"), name="privacy"),
        path("ads.txt", TemplateView.as_view(template_name="files/ads.txt", content_type="text/plain")),
        path("robots.txt", TemplateView.as_view(template_name="files/robots.txt", content_type="text/plain")),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
