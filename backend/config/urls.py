from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from tenants.views import TenantViewSet
from ingestion.views import DataSourceViewSet, RawDataFileViewSet
from emissions.views import NormalizedRecordViewSet

router = DefaultRouter()
router.register(r'tenants', TenantViewSet)
router.register(r'data-sources', DataSourceViewSet)
router.register(r'raw-files', RawDataFileViewSet, basename='rawfile')
router.register(r'records', NormalizedRecordViewSet, basename='record')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]