# tests/test_smoke.py
import os, django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "infportal.settings")
django.setup()

def test_homepage_ok():
    c = Client()
    r = c.get("/")
    assert r.status_code in (200, 301, 302)
