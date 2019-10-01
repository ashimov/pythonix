from django.utils.module_loading import autodiscover_modules
from rest_framework_extensions.routers import ExtendedSimpleRouter


router = ExtendedSimpleRouter(trailing_slash=False)

autodiscover_modules('router')
