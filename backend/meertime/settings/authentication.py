# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 7,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = ["user_manage.backends.EmailBackend"]

LOGIN_REDIRECT_URL = "/"

# Session Settings
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # Set to False in development if not using HTTPS
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_COOKIE_SAMESITE = "Lax"  # Prevents CSRF attacks while allowing normal links

# Session Security
SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Default, using DB for sessions
SESSION_SAVE_EVERY_REQUEST = True  # Update session expiry on each request
