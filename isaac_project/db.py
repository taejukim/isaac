from isaac_project import env

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.db_name,
        'USER': env.db_user,
        'PASSWORD': env.db_password,
        'HOST': env.db_host,
        'PORT': env.db_port,
    }
}