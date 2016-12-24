c6sh
====

c6sh is the cashdesk system used at 33C3 to redeem preorder tickets and sell tickets.


Setup
-----

Install in a virtalenv of any kind::

  pip install --upgrade setuptools pip
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py createsuperuser

Optionally, import data::

  python manage.py import_presale pretix.json
  python manage.py import_member global.csv local.csv BLN


Development
-----------

Regenerate translation files::

  pip install django_extensions pytest
  python manage.py makemessages
  python manage.py makemessages --all -d djangojs
