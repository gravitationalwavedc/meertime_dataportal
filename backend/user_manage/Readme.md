CUSTOM USER MODEL AND USER ROLES
================================

[ We need to perform some additional steps because we are going to change the USER model mid-project ]

This readme file describes the steps required for upgrading the existing django backend. We 
need to perform some checks and to run some SQL commands for smooth merge.

Steps
=====================

1. Execute these following commands from the mysql console
```
DELETE FROM meertime_custom_user.django_migrations where app='admin';
DROP TABLE `meertime_custom_user`.`django_admin_log`;
```
2. Populate the list of users that will get the email to activate their accounts in `unrestricted_user_emails.txt`
3. Migrate
```python
python manage.py migrate  # This should give you a new set of user tables in the user_manage app
```
3. Create `meertime`, `meertime-svc` and another supseruser
```python
python manage.py createsuperuser  # for the user 'meertime' with the old password :)
```
4. Remove superuser and staff status for `meertime` and `meertime-svc` user - using the admin console - Sorry, will add
the django admin requires a hashed password at this moment, which can be updated later.
5. To send bulk emails to the unrestricted provisional users, create a txt file in the directory of `manage.py` which 
contains the email addresses (one per line) named `unrestricted_user_emails.txt` and run the management command 
```python
python manage.py notify_provisional_users
```
