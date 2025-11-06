import os
import sys
import json

# bootstrap django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_manager.settings')
import django
django.setup()

from django.conf import settings
import requests

def main():
    url = getattr(settings, 'SUPABASE_URL', None)
    key = getattr(settings, 'SUPABASE_KEY', None)
    if not url or not key:
        print('SUPABASE_URL or SUPABASE_KEY not set in settings.')
        sys.exit(2)

    try:
        r = requests.get(url, timeout=5)
        print('Root URL status:', r.status_code)
    except Exception as e:
        print('Failed to reach SUPABASE_URL:', e)

    # try REST v1 endpoint (will return 404 if no table specified, but shows connectivity)
    try:
        headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}'
        }
        r = requests.get(f"{url}/rest/v1/", headers=headers, timeout=5)
        print('/rest/v1/ status:', r.status_code)
        print('Response snippet:', r.text[:200])
    except Exception as e:
        print('REST endpoint request failed:', e)

if __name__ == '__main__':
    main()
