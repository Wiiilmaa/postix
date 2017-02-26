from django.conf.urls import include, url
from django.contrib import admin
from django.views.i18n import javascript_catalog

from .api import urls as apiurls
from .backoffice import urls as backofficeurls
from .desk import urls as deskurls
from .troubleshooter import urls as troubleshooterurls

admin.autodiscover()

js_info_dict = {
    'packages': (),
}

urlpatterns = [
    url(r'^jsi18n/$', javascript_catalog, js_info_dict),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(apiurls, namespace='api')),
    url(r'^backoffice/', include(backofficeurls, namespace='backoffice')),
    url(r'^troubleshooter/', include(troubleshooterurls, namespace='troubleshooter')),
    url(r'', include(deskurls, namespace='desk')),
]
