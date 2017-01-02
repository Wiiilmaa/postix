c6sh
====

.. image:: https://travis-ci.org/c3cashdesk/c6sh.svg?branch=master
   :target: https://travis-ci.org/c3cashdesk/c6sh

.. image:: https://coveralls.io/repos/github/c3cashdesk/c6sh/badge.svg?branch=master
   :target: https://coveralls.io/github/c3cashdesk/c6sh?branch=master

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

Run development server::

  python manage.py runserver


Configuration
-------------

You can configure some aspects of your installation by setting the following
environment variables:

* ``C6SH_SECRET`` -- Secret key used for signing purposes

* ``C6SH_DEBUG`` -- Turns on Django's debug mode if set to ``"True"``

* ``C6SH_DB_TYPE`` -- Database backend, defaults to ``sqlite3``. Other options
  are ``mysql`` and ``postgres``

* ``C6SH_DB_NAME`` -- Database name (or filename in case of SQLite). Defaults
  to ``db.sqlite3``
  
* ``C6SH_DB_USER`` -- Database user

* ``C6SH_DB_PASS`` -- Database password

* ``C6SH_DB_HOST`` -- Database host

* ``C6SH_DB_HOST`` -- Database host

* ``C6SH_DB_PORT`` -- Database port

* ``C6SH_STATIC_URL`` -- Base URL for static files

* ``C6SH_STATIC_ROOT`` -- Filesystem directory to plstore static files

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
