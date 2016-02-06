from django.conf.urls import include, url
from django.contrib import admin
from .desk import urls as deskurls

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include(deskurls, namespace='desk')),
]
