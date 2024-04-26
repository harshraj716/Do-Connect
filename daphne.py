import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # Replace 'myproject.settings' with your actual Django settings module

django.setup()
application = get_asgi_application()
