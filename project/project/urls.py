"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
import yaml
from django.conf import settings
from django.contrib import admin
from django.urls import include, re_path
from django.urls import path
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter

from notes.views import NoteViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="Your API description",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)


def swagger_view(request):
    return schema_view.with_ui('swagger', cache_timeout=0)(request)


router = SimpleRouter()
router.register('notes', NoteViewSet, basename='note')
urlpatterns = [
    path('swagger/', swagger_view),
    # Другие маршруты вашего проекта
]
urlpatterns += [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('djoser.urls')),
    re_path('api/v1/auth/', include('djoser.urls.authtoken')),
    path('api/v1/', include(router.urls)),
]
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
