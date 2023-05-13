# +++++++++++ DJANGO +++++++++++
# To use your own Django app use code like this:
import os
import sys

from django.contrib.staticfiles.handlers import StaticFilesHandler

# assuming your Django settings file is at '/home/myusername/mysite/mysite/settings.py'
path = '/home/valentinkelbakh/WarehouseDatabase'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

## Uncomment the lines below depending on your Django version
###### then, for Django >=1.5:
from django.core.wsgi import get_wsgi_application
#application = get_wsgi_application()
application = StaticFilesHandler(get_wsgi_application())
###### or, for older Django <=1.4
#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()