import os
import sys

from template_python_django.settings_common import * # noqa F403
from template_python_django.settings_common import INSTALLED_APPS, DEBUG, DATAPUNT_API_URL
from template_python_django.settings_databases import LocationKey,\
    get_docker_host,\
    get_database_key,\
    OVERRIDE_HOST_ENV_VAR,\
    OVERRIDE_PORT_ENV_VAR

INSTALLED_APPS += [
    'template_python_django.health',
    'template_python_django.objectstore',
]

ROOT_URLCONF = 'template_python_django.urls'


WSGI_APPLICATION = 'template_python_django.wsgi.application'


DATABASE_OPTIONS = {
    LocationKey.docker: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'template_python_django'),
        'USER': os.getenv('DATABASE_USER', 'template_python_django'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': 'database',
        'PORT': '5432'
    },
    LocationKey.local: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'template_python_django'),
        'USER': os.getenv('DATABASE_USER', 'template_python_django'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': get_docker_host(),
        'PORT': '5412'
    },
    LocationKey.override: {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME', 'template_python_django'),
        'USER': os.getenv('DATABASE_USER', 'template_python_django'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'insecure'),
        'HOST': os.getenv(OVERRIDE_HOST_ENV_VAR),
        'PORT': os.getenv(OVERRIDE_PORT_ENV_VAR, '5432')
    },
}

DATABASES = {
    'default': DATABASE_OPTIONS[get_database_key()]
}

EL_HOST_VAR = os.getenv('ELASTIC_HOST_OVERRIDE')
EL_PORT_VAR = os.getenv('ELASTIC_PORT_OVERRIDE', '9200')


ELASTIC_OPTIONS = {
    LocationKey.docker: ["http://elasticsearch:9200"],
    LocationKey.local: [f"http://{get_docker_host()}:9200"],
    LocationKey.override: [f"http://{EL_HOST_VAR}:{EL_PORT_VAR}"],
}

ELASTIC_SEARCH_HOSTS = ELASTIC_OPTIONS[get_database_key()]

ELASTIC_INDICES = dict(
    template_python_django='template_python_django')

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'
if TESTING:
    for k, v in ELASTIC_INDICES.items():
        ELASTIC_INDICES[k] += '_test'

BATCH_SETTINGS = dict(
    batch_size=100000
)

# SWAGGER
SWAG_PATH = 'acc.api.data.amsterdam.nl/template_python_django/docs'

if DEBUG:
    SWAG_PATH = '127.0.0.1:8000/template_python_django/docs'

SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': '0.1',
    'api_path': '/',

    'enabled_methods': [
        'get',
    ],

    'api_key': '',
    'USE_SESSION_AUTH': False,
    'VALIDATOR_URL': None,

    'is_authenticated': False,
    'is_superuser': False,

    'unauthenticated_user': 'django.contrib.auth.models.AnonymousUser',
    'permission_denied_handler': None,
    'resource_access_handler': None,

    'protocol': 'https' if not DEBUG else '',
    'base_path': SWAG_PATH,

    'info': {
        'contact': 'atlas.basisinformatie@amsterdam.nl',
        'description': 'This is the template_python_django API server.',
        'license': 'Not known yet',
        'termsOfServiceUrl': 'https://data.amsterdam.nl/terms/',
        'title': 'template_python_django',
    },

    'doc_expansion': 'list',
    'SECURITY_DEFINITIONS': {
        'oauth2': {
            'type': 'oauth2',
            'authorizationUrl': DATAPUNT_API_URL + "oauth2/authorize",
            'flow': 'implicit',
            'scopes': {
                "MON/TPD": "Template_python_django",
            }
        }
    }
}

HEALTH_MODEL = 'dataset.Template_python_django'

# The following JWKS data was obtained in the authz project :  jwkgen -create -alg ES256
# This is a test public/private key def and added for testing .
JWKS_TEST_KEY = """
    {
        "keys": [
            {
                "kty": "EC",
                "key_ops": [
                    "verify",
                    "sign"
                ],
                "kid": "2aedafba-8170-4064-b704-ce92b7c89cc6",
                "crv": "P-256",
                "x": "6r8PYwqfZbq_QzoMA4tzJJsYUIIXdeyPA27qTgEJCDw=",
                "y": "Cf2clfAfFuuCB06NMfIat9ultkMyrMQO9Hd2H7O9ZVE=",
                "d": "N1vu0UQUp0vLfaNeM0EDbl4quvvL6m_ltjoAXXzkI3U="
            }
        ]
    }
"""

DATAPUNT_AUTHZ = {
    'JWKS': os.getenv('PUB_JWKS', JWKS_TEST_KEY)
}
