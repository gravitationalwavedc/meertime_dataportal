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
2. Update `.env` to add the email settings (can be copied from `.env.template`)
```python
# GMAIL Account settings, if it is False, then default settings would be used (in this case, Swinburne's SMTP)
GMAIL_SMTP=False
GMAIL_ACCOUNT=your_gmail_account@gmail.com
GMAIL_ACCOUNT_PASSWORD=gmail_account_password

# Meertime email for sending email (Swinburne)
MEERTIME_EMAIL=meertime_email@swin.edu.au
```
3. To use console backend for testing you can uncomment the following line in `/backend/meertime/settings/development.py`
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
4. Migrate
```python
python manage.py migrate  # This should give you a new set of user tables in the user_manage app
```
4. Create `meertime`, `meertime-svc` and another superuser
```python
python manage.py createsuperuser  # for the user 'meertime' with the old password :)
```
5. Remove superuser and staff status for `meertime` and `meertime-svc` user - using the admin console - Sorry, will add
the django admin requires a hashed password at this moment, which can be updated later.
6. To send bulk emails to the unrestricted provisional users, create a txt file in the directory of `manage.py` which 
contains the email addresses (one per line) named `unrestricted_user_emails.txt` and run the management command 
```python
python manage.py notify_provisional_users
```
