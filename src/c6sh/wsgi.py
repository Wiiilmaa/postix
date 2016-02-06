import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "c6sh.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
