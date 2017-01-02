# Setting up c6sh for local testing/development

## Initial setup

You will need to have python3 and some kind of virtual env helper installed. I'll assume
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) here, but you can use whatever you like.

First, clone the repository, set up your virtual environment and install the dependencies:

```bash
git clone git@github.com:c3cashdesk/c6sh.git
cd c6sh/src
mkvirtualenv -p /usr/bin/python3 c6sh
pip install -r requirements.txt
python manage.py migrate
```

Now you should have a working setup. You can verify this by running `python manage.py runserver`. With no errors
appearing, you should be able to visit a login page at http://localhost:8000/.

To activate the virtual env in a shell, you'll have to type `workon c6sh`. You can leave the environment with the
`deactivate` command. If you forget to activate your virtual env, you'll get an error like this:

```
Traceback (most recent call last):
  File "manage.py", line 8, in <module>
    from django.core.management import execute_from_command_line
ImportError: No module named 'django'
```

You should also create a superuser with `python manage.py createsuperuser`. Now you can access the admin area
(http://localhost:8000/admin), the backoffice app (http://localhost:8000/backoffice/), the troubleshooter app
(http://localhost:8000/troubleshooter) and the cashdesk app (http://localhost:8000/).


## Test data

To generate some basic data (5 cashdesks, one of them inactive, a handful of users including two superusers, two
products and two items) execute `python manage.py loaddata c6sh/fixtures/basic_fixtures.yaml`.


## Next steps

If you want to test any specific datasets, you can always create them yourself in the admin area
(http://localhost:8000/admin). Work through the normal workflow and any tricky situations you can imagine (or that have
happened in the past).

### Possibly, theoretically, working as intended:

 - creating new users, both cashdesk and backoffice users
 - starting new sessions with arbitrary non-negative amounts of products
    - several existing users start with 'r' (for testing autocompletion)
 - looking at the sessions overview
    - should work even when there are two sessions active on a cashdesk.


### TBD

 - adding items to a session
 - ending a session
    - generating a report
    - printing the report
 - modifying reports
 - statistics on sales/dashboard
