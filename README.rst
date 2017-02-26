postix
======

.. image:: https://travis-ci.org/c3cashdesk/postix.svg?branch=master
   :target: https://travis-ci.org/c3cashdesk/postix

.. image:: https://codecov.io/gh/c3cashdesk/postix/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/c3cashdesk/postix

postix (formerly c6sh) is the cashdesk system used at various events to redeem preorder tickets and sell tickets:

- MRMCD16
- 33C3


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

Run development server::

  python manage.py runserver

Open your browser at one of the following URLs:

* http://localhost:8000/admin/ for the Django admin

* http://localhost:8000/troubleshooter/ for the troubleshooter interface

* http://localhost:8000/backoffice/ for the backoffice interface

* http://localhost:8000/ for the cashdesk interface (requires an active cashdesk and session)

Configuration
-------------

You can configure some aspects of your installation by setting the following
environment variables:

* ``POSTIX_SECRET`` -- Secret key used for signing purposes

* ``POSTIX_DEBUG`` -- Turns on Django's debug mode if set to ``"True"``

* ``POSTIX_DB_TYPE`` -- Database backend, defaults to ``sqlite3``. Other options
  are ``mysql`` and ``postgres``

* ``POSTIX_DB_NAME`` -- Database name (or filename in case of SQLite). Defaults
  to ``db.sqlite3``
  
* ``POSTIX_DB_USER`` -- Database user

* ``POSTIX_DB_PASS`` -- Database password

* ``POSTIX_DB_HOST`` -- Database host

* ``POSTIX_DB_PORT`` -- Database port

* ``POSTIX_STATIC_URL`` -- Base URL for static files

* ``POSTIX_STATIC_ROOT`` -- Filesystem directory to plstore static files

Development
-----------

Regenerate translation files::

  pip install django_extensions pytest
  python manage.py makemessages
  python manage.py makemessages --all -d djangojs

Run linters and tests::

  isort -rc .
  flake8
  pytest
