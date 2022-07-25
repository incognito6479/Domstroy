from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_swagger.views import get_swagger_view  # new

from app.api.router import router
from app.api.views import CustomObtainAuthToken, CustomObtainAuthTokenMobile, TokenApiView
from project import settings

admin.site.site_title = "Domstroy"
admin.site.site_header = "Domstroy"
admin.site.index_title = "Domstroyga xush kelibsiz"

API_TITLE = 'Domstroy"'
API_DESCRIPTION = 'Domstroy'
yasg_schema_view = get_schema_view(
    openapi.Info(
        title="Domstroy API",
        default_version='v1',
        description="Domstroy API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="xolmomin@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
schema_view = get_swagger_view(title=API_TITLE)  # new

urlpatterns = [
    path('swagger/', yasg_schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', yasg_schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include('app.urls'), name='home'),
    path('__debug__/', include('debug_toolbar.urls')),
    path("api/v1/", include(router.urls)),
    path("api/v1/", include("app.api.urls")),
    path('api-auth-mobile/', CustomObtainAuthTokenMobile.as_view()),
    path('api-auth-token/', TokenApiView.as_view()),
    path('admin/', admin.site.urls),
    path('logout/', views.LogoutView.as_view()),
    # path("token", TokenGenerateView.as_view()),
    path('schema/view/', schema_view),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
               + static(settings.MEDIA_URL, document_root=settings.MEDIA_URL)
