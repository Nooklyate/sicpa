import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')
APP_UPLOADS = os.path.join(APP_ROOT, 'uploads')
APP_CACHE = os.path.join(APP_ROOT, 'cache')
