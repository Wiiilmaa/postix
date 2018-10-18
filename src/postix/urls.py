from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog

admin.autodiscover()

js_info_dict = {
    'packages': (),
}

urlpatterns = [
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('admin/', admin.site.urls),
    url(r'^api/', include('postix.api.urls', namespace='api')),
    url(r'^backoffice/', include('postix.backoffice.urls', namespace='backoffice')),
    url(r'^troubleshooter/', include('postix.troubleshooter.urls', namespace='troubleshooter')),
    url(r'', include('postix.desk.urls', namespace='desk')),
]
