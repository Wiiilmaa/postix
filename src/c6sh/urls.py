from django.conf.urls import include, url
from django.contrib import admin
from .backoffice import urls as backofficeurls
from .desk import urls as deskurls
from .api import urls as apiurls

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(apiurls, namespace='api')),
    url(r'^backoffice/', include(backofficeurls, namespace='backoffice')),
    url(r'', include(deskurls, namespace='desk')),
]
