from django.conf import settings
try:
    # official supabase client
    from supabase import create_client
except Exception:
    create_client = None
import requests

SUPABASE_URL = getattr(settings, 'SUPABASE_URL', None)
SUPABASE_KEY = getattr(settings, 'SUPABASE_KEY', None)

# Prefer official client when available, otherwise fall back to direct REST calls
_client = None
if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        _client = None

_headers = {
    "apikey": SUPABASE_KEY,
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

def fetch_from_supabase(endpoint: str):
    """Fetch rows from a table or a REST endpoint.

    endpoint can be either 'table' or 'table?select=*' style. If the official
    client is available, it will be used; otherwise a direct requests GET to
    /rest/v1/{endpoint} is performed.
    """
    if _client:
        # handle simple 'table?select=*' queries
        if '?' in endpoint:
            table, query = endpoint.split('?', 1)
            # currently only support simple select= clauses
            if query.startswith('select='):
                select_clause = query.split('select=', 1)[1]
                res = _client.table(table).select(select_clause).execute()
                return getattr(res, 'data', res)
        # default: select all
        res = _client.table(endpoint.split('?')[0]).select('*').execute()
        return getattr(res, 'data', res)

    # fallback: raw REST
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    response = requests.get(url, headers=_headers, timeout=10)
    response.raise_for_status()
    return response.json()


def insert_to_supabase(endpoint: str, data):
    """Insert data into a table. `endpoint` should be the table name."""
    if _client:
        res = _client.table(endpoint).insert(data).execute()
        return getattr(res, 'data', res)

    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    response = requests.post(url, json=data, headers=_headers, timeout=10)
    response.raise_for_status()
    return response.json()
